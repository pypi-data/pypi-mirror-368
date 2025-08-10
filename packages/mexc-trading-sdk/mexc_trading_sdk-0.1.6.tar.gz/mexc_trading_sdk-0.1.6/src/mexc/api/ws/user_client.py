from dataclasses import dataclass, field
from datetime import timedelta
import asyncio
from pydantic import BaseModel
from dslog import Logger
from mexc.core import timestamp as ts, AuthedClient, MEXC_SPOT_API_BASE
from .client import SocketClient, MEXC_SOCKET_URL

class ListenResponse(BaseModel):
  listenKey: str

@dataclass
class Context:
  ws: SocketClient
  listen_key: str
  pinger: asyncio.Task

@dataclass
class UserStreamMixin:
  http: AuthedClient
  api_url: str = MEXC_SPOT_API_BASE
  ws_url: str = MEXC_SOCKET_URL
  keep_alive_every: timedelta = timedelta(minutes=30)
  log: Logger = field(default_factory=Logger.empty)
  ctx: Context | None = None
  
  async def listen_key(self):
    r = await self.http.signed_request('POST', self.api_url + '/api/v3/userDataStream', {
      'timestamp': ts.now(),
    })
    return ListenResponse.model_validate_json(r.text).listenKey
  
  async def refresh_key(self, key: str):
    r = await self.http.signed_request('PUT', self.api_url + '/api/v3/userDataStream', {
      'listenKey': key,
      'timestamp': ts.now(),
    })
    return ListenResponse.model_validate_json(r.text).listenKey
  
  async def delete_key(self, key: str):
    r = await self.http.signed_request('DELETE', self.api_url + '/api/v3/userDataStream', {
      'listenKey': key,
      'timestamp': ts.now(),
    })
    return ListenResponse.model_validate_json(r.text).listenKey

  async def start(self):
    if self.ctx is None:
      self.log('Fetching listen key...', level='DEBUG')
      key = await self.listen_key()
      self.log('Listening to', key, level='DEBUG')
      ws = await SocketClient(url=self.ws_url + f'?listenKey={key}', log=self.log).__aenter__()
      pinger = asyncio.create_task(self.pinger(key))
      self.ctx = Context(ws=ws, listen_key=key, pinger=pinger)
    return self.ctx
  
  async def __aenter__(self):
    await self.start()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    if self.ctx is not None:
      self.ctx.pinger.cancel()
      await self.ctx.ws.__aexit__(exc_type, exc_value, traceback)
      await self.delete_key(self.ctx.listen_key)
      self.ctx = None

  async def pinger(self, key: str):
    while True:
      await asyncio.sleep(self.keep_alive_every.total_seconds())
      await self.refresh_key(key)

  async def subscribe(self, channel: str):
    ctx = await self.start()
    async for msg in ctx.ws.subscribe(channel):
      yield msg