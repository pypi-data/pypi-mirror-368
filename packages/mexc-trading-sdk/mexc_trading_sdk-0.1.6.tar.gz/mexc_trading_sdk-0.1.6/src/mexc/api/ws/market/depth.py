from typing_extensions import Literal
from dataclasses import dataclass
from mexc.api.ws import SocketClientMixin

def channel_name(symbol: str, level: Literal[5, 10, 20]):
  return f'spot@public.limit.depth.v3.api.pb@{symbol}@{level}'
  
@dataclass
class Book:

  @dataclass
  class Entry:
    price: str
    qty: str

    @classmethod
    def from_proto(cls, proto):
      return cls(
        price=proto.price,
        qty=proto.quantity
      )

  asks: list[Entry]
  bids: list[Entry]

  @classmethod
  def from_proto(cls, proto):
    return cls(
      asks=[cls.Entry.from_proto(entry) for entry in proto.asks],
      bids=[cls.Entry.from_proto(entry) for entry in proto.bids]
    )
  
@dataclass
class Depth(SocketClientMixin):
  async def depth(self, symbol: str, level: Literal[5, 10, 20]):
    async for proto in self.ws.subscribe(channel_name(symbol, level)):
      yield Book.from_proto(proto.publicLimitDepths)