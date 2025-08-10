from dataclasses import dataclass
from .candles import Candles
from .funding_rate import FundingRate

@dataclass
class MarketData(
  FundingRate,
  Candles,
):
  ...