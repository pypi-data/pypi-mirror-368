from dataclasses import dataclass
from trading_sdk.spot.trading.edit_order import EditOrder as EditOrderTDK
from trading_sdk.types import Num
from mexc.api.spot.trading.place_order import LimitOrder
from mexc.sdk import SdkMixin

@dataclass
class EditOrder(EditOrderTDK, SdkMixin):
  async def edit_order(self, symbol: str, *, id: str, qty: Num) -> str:
    state = await self.client.spot.cancel_order(symbol, orderId=id)
    if 'code' in state:
      raise RuntimeError(state)
    r = await self.client.spot.place_order(symbol, LimitOrder(
      type='LIMIT',
      side=state['side'],
      price=state['price'],
      quantity=f"{qty:f}"
    ))
    if 'code' in r:
      raise RuntimeError(r)
    else:
      return r['orderId']