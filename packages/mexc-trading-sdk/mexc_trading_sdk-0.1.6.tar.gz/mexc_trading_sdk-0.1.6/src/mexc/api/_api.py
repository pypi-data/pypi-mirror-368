from dataclasses import dataclass
from dslog import Logger
from mexc.core import AuthedClient, MEXC_SPOT_API_BASE, MEXC_FUTURES_API_BASE
from .spot import Spot
from .wallet import Wallet
from .futures import Futures
from .ws import Streams, MEXC_SOCKET_URL

@dataclass
class MEXC:
  client: AuthedClient
  spot: Spot
  wallet: Wallet
  futures: Futures
  streams: Streams
  
  async def __aenter__(self):
    await self.client.__aenter__()
    return self
  
  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)
    try:
      await self.streams.__aexit__(exc_type, exc_value, traceback)
    except:
      ...

  def __init__(
    self, client: AuthedClient, *,
    spot_base_url: str = MEXC_SPOT_API_BASE,
    futures_base_url: str = MEXC_FUTURES_API_BASE,
    ws_base_url: str = MEXC_SOCKET_URL,
    log: Logger = Logger.empty(),
  ):
    self.client = client
    self.spot = Spot(client=client, base_url=spot_base_url)
    self.wallet = Wallet(client=client)
    self.futures = Futures(client=client, base_url=futures_base_url)
    self.streams = Streams(http=client, ws_url=ws_base_url, api_url=spot_base_url, log=log)

  @classmethod
  def new(
    cls, api_key: str, api_secret: str, *,
    spot_base_url: str = MEXC_SPOT_API_BASE,
    futures_base_url: str = MEXC_FUTURES_API_BASE,
    ws_base_url: str = MEXC_SOCKET_URL,
    log: Logger = Logger.empty(),
  ):
    client = AuthedClient(api_key=api_key, api_secret=api_secret)
    return cls(client=client, spot_base_url=spot_base_url, futures_base_url=futures_base_url, ws_base_url=ws_base_url, log=log)

  @classmethod
  def env(
    cls, *,
    spot_base_url: str = MEXC_SPOT_API_BASE,
    futures_base_url: str = MEXC_FUTURES_API_BASE,
    ws_base_url: str = MEXC_SOCKET_URL,
    log: Logger = Logger.empty(),
  ):
    client = AuthedClient.env()
    return cls(client=client, spot_base_url=spot_base_url, futures_base_url=futures_base_url, ws_base_url=ws_base_url, log=log)