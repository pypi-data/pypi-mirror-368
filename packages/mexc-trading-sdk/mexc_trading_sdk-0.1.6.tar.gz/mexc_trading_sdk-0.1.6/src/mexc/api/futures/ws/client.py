from typing_extensions import Any, Coroutine, TypeVar
from dataclasses import dataclass, field
import asyncio
from datetime import timedelta
import json
import websockets
from pydantic import BaseModel
from dslog import Logger

MEXC_FUTURES_SOCKET_URL = 'wss://contract.mexc.com/edge'
RESTART = object()

class Response(BaseModel):
  channel: str
  data: Any
  ts: int

@dataclass
class Context:
  conn: websockets.ClientConnection
  pinger: asyncio.Task
  listener: asyncio.Task
  restarter: asyncio.Task

T = TypeVar('T')

# async def wait_for(coro: Coroutine[Any, Any, T], timeout_secs: float) -> T:
#   task = asyncio.create_task(coro)
#   done, _ = await asyncio.wait([task], timeout=timeout_secs)
#   if task in done:
#     return task.result()
#   else:
#     task.cancel()
#     raise asyncio.TimeoutError()
  
@dataclass
class SocketClient:
  url: str = MEXC_FUTURES_SOCKET_URL
  ping_every: timedelta = timedelta(seconds=15)
  restart_every: timedelta = timedelta(hours=23)
  conn_timeout: timedelta = timedelta(seconds=5)
  restart: asyncio.Event = field(default_factory=asyncio.Event)
  replies: asyncio.Queue[Response] = field(default_factory=asyncio.Queue)
  pong: asyncio.Event = field(default_factory=asyncio.Event)
  subscribers: dict[str, asyncio.Queue[Response]] = field(default_factory=dict)
  ctx: Context | None = None
  log: Logger = field(default_factory=Logger.empty)

  @property
  async def conn(self) -> websockets.ClientConnection:
    ctx = self.ctx or await self.start()
    return ctx.conn

  async def start(self):
    if self.ctx is None:
      self.log('Starting...')
      async def connect():
        return await websockets.connect(self.url)
      conn = await asyncio.wait_for(connect(), self.conn_timeout.total_seconds())
      self.log('Connection succeeded.')
      self.ctx = Context(
        conn=conn,
        pinger=asyncio.create_task(self.pinger()),
        listener=asyncio.create_task(self.listener(conn)),
        restarter=asyncio.create_task(self.restarter()),
      )
    else:
      self.log('Called start but context is not None', level='TRACE')
    return self.ctx

  async def __aenter__(self):
    await self.start()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    if self.ctx is not None:
      self.ctx.pinger.cancel()
      self.ctx.listener.cancel()
      self.ctx.restarter.cancel()
      await self.ctx.conn.__aexit__(exc_type, exc_value, traceback)
      self.ctx = None

  async def listener(self, ws: websockets.ClientConnection):
    self.log('Starting listener...', level='DEBUG')
    while True:
      msg = await ws.recv()
      self.log('Received WS message:', msg, level='TRACE')
      r = Response.model_validate_json(msg)
      if r.channel.startswith('push.'):
        if (q := self.subscribers.get(r.channel)) is not None:
          q.put_nowait(r)
        else:
          self.log(f'No subscriber for channel {r.channel}, skipping...', level='TRACE')
      elif r.channel == 'pong':
        self.log('Received PONG', level='TRACE')
        self.pong.set()
      else:
        self.replies.put_nowait(r)

  async def pinger(self):
    self.log('Starting pinger...', level='DEBUG')
    while True:
      self.log('Sending PING...', level='TRACE')
      self.pong.clear()
      await self.send('ping')
      try:
        await asyncio.wait_for(self.pong.wait(), self.ping_every.total_seconds())
      except asyncio.TimeoutError:
        self.log('PING timeout, restarting connection...', level='WARNING')
        asyncio.create_task(self.restart_conn())
        return
      await asyncio.sleep(self.ping_every.total_seconds())

  async def restart_conn(self):
    if self.ctx is not None:
      self.log('Restarting...', level='DEBUG')
      self.restart.clear()
      for q in self.subscribers.values():
        q.put_nowait(RESTART) # type: ignore

      self.ctx.pinger.cancel()
      self.ctx.listener.cancel()
      self.ctx.restarter.cancel()

      self.log('Closing connection...')
      try:
        await asyncio.wait_for(self.ctx.conn.close(), self.conn_timeout.total_seconds())
        self.log('Connection closed.')
      except asyncio.TimeoutError:
        self.log('Connection close timeout, skipping...')

      self.ctx = None
      await self.start()
      self.restart.set()
    else:
      self.log('No context, skipping restart...', level='DEBUG')

  async def restarter(self):
    self.log('Starting restarter...', level='DEBUG')
    self.restart.set()
    await asyncio.sleep(self.restart_every.total_seconds())
    asyncio.create_task(self.restart_conn())

  async def send(self, method: str, param=None, **kwargs):
    conn = await self.conn
    obj = {
      'method': method,
      'param': param,
      **kwargs
    }
    self.log('Sending:', obj, level='TRACE')
    await conn.send(json.dumps(obj))

  async def request(self, method: str, param=None, **kwargs):
    await self.send(method, param, **kwargs)
    return await self.replies.get()

  async def subscribe(self, channel: str, param=None, **kwargs):
    queue_name = f'push.{channel}'
    if queue_name in self.subscribers:
      raise ValueError(f'Channel {channel} already subscribed')
    queue = asyncio.Queue()
    self.subscribers[queue_name] = queue
    
    while True:
      self.log(f'Subscribing to {channel}...', level='DEBUG')
      r = await self.request(f'sub.{channel}', param, **kwargs)
      if r.data == 'success':
        self.log(f'Subscribed to {channel}', level='DEBUG')
      else:
        raise ValueError(f'Failed to subscribe to {channel}: {r.data}')
      while True:
        val = await queue.get()
        if val is RESTART:
          await self.restart.wait()
          break
        else:
          yield val

  async def unsubscribe(self, channel: str, param=None, **kwargs):
    self.log(f'Unsubscribing from {channel}...', level='DEBUG')
    await self.send(f'unsub.{channel}', param, **kwargs)