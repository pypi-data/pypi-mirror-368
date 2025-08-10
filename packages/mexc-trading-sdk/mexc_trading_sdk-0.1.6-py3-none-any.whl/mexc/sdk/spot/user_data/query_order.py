from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.spot.user_data.query_order import QueryOrder as QueryOrderTDK, OrderState
from mexc.core import timestamp
from mexc.sdk import SdkMixin

@dataclass
class QueryOrder(QueryOrderTDK, SdkMixin):
  async def query_order(self, symbol: str, *, id: str) -> OrderState:
    r = await self.client.spot.query_order(symbol, orderId=id)
    if 'code' in r:
      raise RuntimeError(r)
    else:
      return OrderState(
        id=r['orderId'],
        price=Decimal(r['price']),
        qty=Decimal(r['origQty']),
        filled_qty=Decimal(r['executedQty']),
        time=timestamp.parse(r['time']),
        side=r['side'],
        status=r['status']
      )
