from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from trading_sdk.spot.trading.cancel_order import CancelOrder as CancelOrderTDK
from trading_sdk.spot.user_data.query_order import OrderState
from mexc.sdk import SdkMixin

@dataclass
class CancelOrder(CancelOrderTDK, SdkMixin):
  async def cancel_order(self, symbol: str, *, id: str) -> OrderState:
    r = await self.client.spot.cancel_order(symbol, orderId=id)
    if 'code' in r:
      raise RuntimeError(r)
    else:
      return OrderState(
        id=r['orderId'],
        price=Decimal(r['price']),
        qty=Decimal(r['origQty']),
        filled_qty=Decimal(r['executedQty']),
        side=r['side'],
        time=datetime.now(),
        status=r['status']
      )