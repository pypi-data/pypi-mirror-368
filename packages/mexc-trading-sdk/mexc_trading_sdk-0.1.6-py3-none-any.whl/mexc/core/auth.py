from dataclasses import dataclass, field
from urllib.parse import urlencode, quote
import hashlib
import hmac
from .client import Client, MEXC_FUTURES_API_BASE, MEXC_SPOT_API_BASE
from .validation import ValidationMixin

def sign(payload: str, *, secret: str) -> str:
  return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

@dataclass
class AuthedClient(Client):
  api_key: str
  api_secret: str

  @classmethod
  def env(cls):
    import os
    return cls(
      api_key=os.environ['MEXC_ACCESS_KEY'],
      api_secret=os.environ['MEXC_SECRET_KEY'],
    )

  @property
  def headers(self) -> dict:
    return { 'X-MEXC-APIKEY': self.api_key }

  def sign(self, query_string: str) -> str:
    return sign(query_string, secret=self.api_secret)
  
  def signed_query(self, params: dict) -> str:
    def fix(v):
      # fix bools, which would show otherwise as "hello=True" instead of "hello=true"
      if isinstance(v, bool):
        return str(v).lower()
      else:
        return v
    fixed_params = [(k, fix(v)) for k, v in params.items()]
    query = urlencode(fixed_params, quote_via=quote)
    return query + '&signature=' + self.sign(query)
  
  async def authed_request(
    self, method: str, path: str, params: dict = {}, *,
    json: dict | None = None,
  ):
    return await self.request(method, path, headers=self.headers, params=params, json=json)
  
  async def signed_request(self, method: str, path: str, params: dict = {}):
    return await self.request(method, path + '?' + self.signed_query(params), headers=self.headers)
  
@dataclass
class AuthedMixin(ValidationMixin):
  base_url: str = field(default=MEXC_SPOT_API_BASE, kw_only=True)
  client: AuthedClient

  @classmethod
  def new(cls, api_key: str, api_secret: str, *, base_url: str = MEXC_SPOT_API_BASE):
    return cls(
      base_url=base_url,
      client=AuthedClient(api_key=api_key, api_secret=api_secret),
    )
  
  @classmethod
  def env(cls, *, base_url: str = MEXC_SPOT_API_BASE):
    return cls(
      base_url=base_url,
      client=AuthedClient.env(),
    )

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
  
  async def authed_request(
    self, method: str, path: str, params: dict = {}, *,
    json: dict | None = None,
  ):
    return await self.client.authed_request(method, self.base_url + path, params=params, json=json)  
  
  async def signed_request(self, method: str, path: str, params: dict = {}):
    return await self.client.signed_request(method, self.base_url + path, params)


@dataclass
class FuturesAuthedMixin(AuthedMixin):
  base_url: str = field(default=MEXC_FUTURES_API_BASE, kw_only=True)