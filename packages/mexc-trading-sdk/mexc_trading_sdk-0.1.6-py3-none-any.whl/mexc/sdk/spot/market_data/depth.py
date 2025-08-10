from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.spot.market_data.depth import Depth as DepthTDK, Book
from mexc.sdk import SdkMixin

@dataclass
class Depth(DepthTDK, SdkMixin):
  async def depth(self, symbol: str, *, limit: int | None = None) -> Book:
    r = await self.client.spot.depth(symbol, limit=limit)
    if 'code' in r:
      raise RuntimeError(r)
    else:
      return Book(
        asks=[Book.Entry(
          price=Decimal(p.price),
          qty=Decimal(p.qty)
        ) for p in r['asks']],
        bids=[Book.Entry(
          price=Decimal(p.price),
          qty=Decimal(p.qty)
        ) for p in r['bids']],
      )
