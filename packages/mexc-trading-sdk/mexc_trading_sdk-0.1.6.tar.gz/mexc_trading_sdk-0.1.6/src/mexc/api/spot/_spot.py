from dataclasses import dataclass
from mexc.core import AuthedClient
from .trading import Trading
from .user_data import UserData
from .market_data import MarketData

@dataclass
class Spot(
  Trading,
  UserData,
  MarketData,
):
  client: AuthedClient # type: ignore