from dataclasses import dataclass
from datetime import timedelta
import asyncio
from dslog import Logger
from mexc.core.auth import sign
from mexc.core import timestamp as ts
from .client import SocketClient, MEXC_FUTURES_SOCKET_URL, RESTART

@dataclass(kw_only=True)
class AuthedSocketClient(SocketClient):
  api_key: str
  api_secret: str

  @classmethod
  def env(
    cls, *, url: str = MEXC_FUTURES_SOCKET_URL,
    ping_every: timedelta = timedelta(seconds=15),
    restart_every: timedelta = timedelta(hours=23),
    conn_timeout: timedelta = timedelta(seconds=5),
    log: Logger = Logger.empty(),
  ):
    import os
    return cls(
      api_key=os.environ['MEXC_ACCESS_KEY'],
      api_secret=os.environ['MEXC_SECRET_KEY'],
      url=url,
      ping_every=ping_every,
      restart_every=restart_every,
      conn_timeout=conn_timeout,
      log=log,
    )
  
  async def __aenter__(self):
    await super().__aenter__()
    await self.login()
    return self
  
  async def login(self):
    t = ts.now()
    signature = sign(f'{self.api_key}{t}', secret=self.api_secret)
    r = await self.request('login', {
      'apiKey': self.api_key,
      'reqTime': t,
      'signature': signature,
    })
    if r.data != 'success':
      raise ValueError(f'Failed to login: {r.data}')
    return r
  
  async def subscribe(self, channel: str, param=None, **kwargs):
    queue_name = f'push.{channel}'
    if queue_name in self.subscribers:
      raise ValueError(f'Channel {channel} already subscribed')
    queue = asyncio.Queue()
    self.subscribers[queue_name] = queue

    while True:
      val = await queue.get()
      if val is RESTART:
        await self.restart.wait()
        continue
      else:
        yield val

@dataclass
class AuthedSocketMixin:
  client: AuthedSocketClient

  @classmethod
  def env(
    cls, *, url: str = MEXC_FUTURES_SOCKET_URL,
    ping_every: timedelta = timedelta(seconds=15),
    restart_every: timedelta = timedelta(hours=23),
    log: Logger = Logger.empty(),
  ):
    return cls(client=AuthedSocketClient.env(url=url, ping_every=ping_every, restart_every=restart_every, log=log))

  async def __aenter__(self):
    await self.client.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)