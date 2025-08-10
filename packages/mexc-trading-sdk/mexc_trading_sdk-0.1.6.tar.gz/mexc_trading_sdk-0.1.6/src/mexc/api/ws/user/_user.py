from dataclasses import dataclass
from .my_trades import MyTrades

@dataclass
class UserStream(MyTrades):
  ...