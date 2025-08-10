from typing_extensions import Literal
from dataclasses import dataclass
from mexc.api.ws import SocketClientMixin

Interval = Literal['Min1', 'Min5', 'Min15', 'Min30', 'Min60', 'Hour4', 'Hour8', 'Day1', 'Week1', 'Month1']

def channel_name(symbol: str, interval: Interval):
  return f'spot@public.kline.v3.api.pb@{symbol}@{interval}'

@dataclass
class Candle:
  interval: str
  windowStart: int
  openingPrice: str
  closingPrice: str
  highestPrice: str
  lowestPrice: str
  volume: str
  amount: str
  windowEnd: int

  @classmethod
  def from_proto(cls, proto):
    return cls(
      interval=proto.interval,
      windowStart=proto.windowStart,
      openingPrice=proto.openingPrice,
      closingPrice=proto.closingPrice,
      highestPrice=proto.highestPrice,
      lowestPrice=proto.lowestPrice,
      volume=proto.volume,
      amount=proto.amount,
      windowEnd=proto.windowEnd
    )
  
@dataclass
class Candles(SocketClientMixin):
  async def candles(self, symbol: str, interval: Interval):
    async for proto in self.ws.subscribe(channel_name(symbol, interval)):
      yield Candle.from_proto(proto.publicSpotKline)
