from dataclasses import dataclass
from .market import Market
from .user import UserStream

@dataclass
class Streams(Market, UserStream):
  ...
