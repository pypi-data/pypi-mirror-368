from ._api import MEXC
from .spot import Spot
from .wallet import Wallet
from .futures import Futures
from .ws import Streams
from . import spot, wallet, futures, ws

__all__ = [
  'MEXC',
  'Spot', 'Wallet', 'Futures', 'Streams',
  'spot', 'wallet', 'futures', 'ws',
]