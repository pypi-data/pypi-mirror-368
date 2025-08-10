from typing_extensions import TypedDict
from mexc.core import FuturesClientMixin, FuturesResponse, lazy_validator

class Data(TypedDict):
  symbol: str
  fundingRate: float
  maxFundingRate: float
  minFundingRate: float
  collectCycle: int
  nextSettleTime: int
  timestamp: int

validate_response = lazy_validator(FuturesResponse[Data])

class FundingRate(FuturesClientMixin):
  async def funding_rate(self, symbol: str, validate: bool | None = None) -> FuturesResponse[Data]:
    """Get the funding rate for a given symbol.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`.
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-contract-funding-rate)
    """
    r = await self.request('GET', f'/api/v1/contract/funding_rate/{symbol}')
    return validate_response(r.text) if self.validate(validate) else r.json()