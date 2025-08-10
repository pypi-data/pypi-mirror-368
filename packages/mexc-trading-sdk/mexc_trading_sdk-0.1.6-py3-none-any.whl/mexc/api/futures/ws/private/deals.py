from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel
from mexc.api.futures.ws import AuthedSocketMixin

class Side(Enum):
  open_long = 1
  close_short = 2
  open_short = 3
  close_long = 4

class Deal(BaseModel):
  category: int
  externalOid: str
  fee: Decimal
  feeCurrency: str
  id: str
  isSelf: bool
  orderId: str
  positionMode: int
  price: Decimal
  profit: Decimal
  side: Side
  symbol: str
  taker: bool
  timestamp: int
  vol: Decimal
  """Base asset amount, in volume units"""

@dataclass
class Deals(AuthedSocketMixin):
  async def deals(self):
    async for msg in self.client.subscribe('personal.order.deal'):
      yield Deal.model_validate(msg.data)