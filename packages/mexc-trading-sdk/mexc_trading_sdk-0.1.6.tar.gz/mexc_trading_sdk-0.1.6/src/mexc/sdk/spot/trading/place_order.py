from dataclasses import dataclass
from trading_sdk.types import fmt_num
from trading_sdk.spot.trading.place_order import PlaceOrder as PlaceOrderTDK, Order as OrderTDK
from mexc.api.spot.trading.place_order import Order, LimitOrder, MarketOrder
from mexc.sdk import SdkMixin

def parse_order(order: OrderTDK) -> Order:
  if order['type'] == 'LIMIT':
    return LimitOrder(
      type='LIMIT',
      side=order['side'],
      price=fmt_num(order['price']),
      quantity=fmt_num(order['qty'])
    )
  elif order['type'] == 'MARKET':
    return MarketOrder(
      type='MARKET',
      side=order['side'],
      quantity=fmt_num(order['qty'])
    )

@dataclass
class PlaceOrder(PlaceOrderTDK, SdkMixin):
  async def place_order(self, symbol: str, order: OrderTDK) -> str:
    r = await self.client.spot.place_order(symbol, parse_order(order))
    if 'code' in r:
      raise RuntimeError(r)
    else:
      return r['orderId']