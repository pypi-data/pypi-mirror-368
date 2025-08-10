from dataclasses import dataclass, field
from functools import wraps
import httpx
from .validation import ValidationMixin

MEXC_SPOT_API_BASE = 'https://api.mexc.com'
MEXC_FUTURES_API_BASE = 'https://contract.mexc.com'

class Client:
  async def __aenter__(self):
    self._client = httpx.AsyncClient()
    await self._client.__aenter__()
    return self
  
  async def __aexit__(self, *args):
    if self._client is not None:
      await self._client.__aexit__(*args)
      self._client = None

  @property
  def client(self) -> httpx.AsyncClient:
    client = getattr(self, '_client', None)
    if client is None:
      raise RuntimeError('Please use as context manager: `async with ...: ...`')
    return client
  
  @staticmethod
  def with_client(fn):
    @wraps(fn)
    async def wrapper(self, *args, **kwargs):
      if getattr(self, '_client', None) is None:
        async with self:
          return await fn(self, *args, **kwargs)
      else:
        return await fn(self, *args, **kwargs)
      
    return wrapper

  @with_client
  async def request(
    self, method: str, url: str, params: dict | None = None, *,
    headers: dict | None = None, cookies: dict | None = None,
    json=None,
  ):
    return await self.client.request(method, url, params=params, headers={
      'User-Agent': 'trading-sdk',
      **(headers or {}),
    }, cookies=cookies, json=json)

@dataclass
class ClientMixin(ValidationMixin):
  base_url: str = field(default=MEXC_SPOT_API_BASE, kw_only=True)
  client: Client = field(kw_only=True, default_factory=Client)

  async def __aenter__(self):
    await self.client.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self, method: str, path: str, params: dict | None = None, *,
    headers: dict | None = None, cookies: dict | None = None,
    json=None,
  ):
    return await self.client.request(method, self.base_url + path, params=params, headers={
      'User-Agent': 'trading-sdk',
      **(headers or {}),
    }, cookies=cookies, json=json)
  
@dataclass
class FuturesClientMixin(ClientMixin):
  base_url: str = field(default=MEXC_FUTURES_API_BASE, kw_only=True)