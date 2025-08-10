from dataclasses import dataclass
from decimal import Decimal
from trading_sdk.spot.user_data.balances import Balances as BalancesTDK, Balance
from mexc.sdk import SdkMixin

@dataclass
class Balances(BalancesTDK, SdkMixin):
  async def balances(self, *currencies: str) -> dict[str, Balance]:
    r = await self.client.spot.account()
    if 'code' in r:
      raise RuntimeError(r)
    else:
      return {
        b['asset']: Balance(
          free=Decimal(b['free']),
          locked=Decimal(b['locked'])
        )
        for b in r['balances']
      }
