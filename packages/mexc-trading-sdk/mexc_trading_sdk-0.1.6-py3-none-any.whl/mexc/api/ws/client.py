from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
import json
import websockets
from pydantic import BaseModel
from dslog import Logger
from .proto import parse_proto

MEXC_SOCKET_URL = 'wss://wbs-api.mexc.com/ws'

class Response(BaseModel):
  id: int
  code: int
  msg: str

RESTART = object()

@dataclass
class Context:
  conn: websockets.ClientConnection
  pinger: asyncio.Task
  listener: asyncio.Task
  restarter: asyncio.Task

@dataclass
class SocketClient:
  url: str = MEXC_SOCKET_URL
  ping_every: timedelta = timedelta(seconds=15)
  restart_every: timedelta = timedelta(hours=23)
  restart: asyncio.Event = field(default_factory=asyncio.Event)
  replies: asyncio.Queue[Response] = field(default_factory=asyncio.Queue)
  subscribers: dict[str, asyncio.Queue] = field(default_factory=dict)
  ctx: Context | None = None
  log: Logger = field(default_factory=Logger.empty)

  @property
  async def conn(self) -> websockets.ClientConnection:
    ctx = self.ctx or await self.start()
    return ctx.conn

  async def start(self):
    if self.ctx is None:
      conn = await websockets.connect(self.url)
      self.ctx = Context(
        conn=conn,
        pinger=asyncio.create_task(self.pinger()),
        listener=asyncio.create_task(self.listener(conn)),
        restarter=asyncio.create_task(self.restarter()),
      )
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
      self.log('Received WS message:', msg, level='DEBUG')
      try:
        data = Response.model_validate_json(msg)
        self.replies.put_nowait(data)
      except:
        proto = parse_proto(msg) # type: ignore
        channel = proto.channel # type: ignore
        if queue := self.subscribers.get(channel):
          queue.put_nowait(proto)

  async def pinger(self):
    self.log('Starting pinger...', level='DEBUG')
    while True:
      self.log('Sending PING...', level='DEBUG')
      await self.request('PING')
      await asyncio.sleep(self.ping_every.total_seconds())

  async def restarter(self):
    self.log('Starting restarter...', level='DEBUG')
    self.restart.set()
    await asyncio.sleep(self.restart_every.total_seconds())
    if self.ctx is not None:
      self.log('Restarting...', level='DEBUG')
      self.restart.clear()
      for q in self.subscribers.values():
        q.put_nowait(RESTART)

      self.ctx.pinger.cancel()
      self.ctx.listener.cancel()
      await self.ctx.conn.close()
      self.ctx = None
      await self.start()
      self.restart.set()
    else:
      self.log('No context, skipping restart...', level='DEBUG')

  async def request(self, method: str, params=None):
    conn = await self.conn
    obj = {'method': method }
    if params is not None:
      obj['params'] = params
    await conn.send(json.dumps(obj))
    return await self.replies.get()
  
  async def subscribe(self, channel: str):
    if channel in self.subscribers:
      raise ValueError(f'Channel {channel} already subscribed')
    queue = asyncio.Queue()
    self.subscribers[channel] = queue
    
    while True:
      self.log(f'Subscribing to {channel}...', level='DEBUG')
      r = await self.request('SUBSCRIPTION', [channel])
      if r.msg != channel:
        raise ValueError(f'Failed to subscribe to {channel}: {r.msg}')
      while True:
        val = await queue.get()
        if val is RESTART:
          await self.restart.wait()
          break
        else:
          yield val

@dataclass
class SocketClientMixin:
  ws: SocketClient = field(kw_only=True, default_factory=SocketClient)

  async def __aenter__(self):
    await self.ws.__aenter__()
    return self
  
  async def __aexit__(self, *args):
    await self.ws.__aexit__(*args)