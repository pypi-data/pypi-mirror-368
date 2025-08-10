from dataclasses import dataclass
from .currency_info import CurrencyInfo
from .deposit_addresses import DepositAddresses
from .withdraw import Withdraw
from .cancel_withdraw import CancelWithdraw

@dataclass
class Wallet(CurrencyInfo, DepositAddresses, Withdraw, CancelWithdraw):
  ...