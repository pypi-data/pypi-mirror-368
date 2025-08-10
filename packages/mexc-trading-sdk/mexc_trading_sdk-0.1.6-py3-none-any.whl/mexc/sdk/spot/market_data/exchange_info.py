from dataclasses import dataclass
from decimal import Decimal
import httpx
from pydantic import ValidationError
from trading_sdk import ApiError, NetworkFailure
from trading_sdk.spot.market_data.exchange_info import ExchangeInfo as ExchangeInfoTDK, Info
from mexc.sdk import SdkMixin

@dataclass
class ExchangeInfo(ExchangeInfoTDK, SdkMixin):
  async def exchange_infos(self, *symbols: str) -> dict[str, Info]:
    try:
      r = await self.client.spot.exchange_info(*symbols)
    except httpx.HTTPError as e:
      raise NetworkFailure(detail=e)
    except ValidationError as e:
      raise ApiError(detail=e)
    
    if 'code' in r:
      raise ApiError(r)
    else:
      return {
        k: Info(
          base=v['baseAsset'],
          quote=v['quoteAsset'],
          tick_size=Decimal(1) / Decimal(10 ** v['quotePrecision']),
          step_size=Decimal(v['baseSizePrecision']),
        ) for k, v in r.items()
      }
