from mexc.core import AuthedMixin, timestamp as ts, ApiError, \
  lazy_validator
from .cancel_order import CanceledOrder

Response: type[list[CanceledOrder] | ApiError] = list[CanceledOrder] | ApiError # type: ignore
validate_response = lazy_validator(Response)

class CancelAllOrders(AuthedMixin):
  async def cancel_all_orders(
    self, symbol: str, *,
    recvWindow: int | None = None,
    timestamp: int | None = None,
    validate: bool | None = None,
  ) -> ApiError | list[CanceledOrder]:
    """Cancel all open orders (of your account) for a given symbol.
    
    - `symbol`: The symbol being traded, e.g. `BTCUSDT`
    - `recvWindow`: If the server receives the request after `timestamp + recvWindow`, it will be rejected (default: 5000).
    - `timestamp`: The timestamp for the request, in milliseconds (default: now).
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#cancel-all-open-orders-on-a-symbol)
    """
    params: dict = {
      'symbol': symbol,
      'timestamp': timestamp or ts.now(),
    }
    if recvWindow is not None:
      params['recvWindow'] = recvWindow
    r = await self.signed_request('DELETE', '/api/v3/openOrders', params)
    return validate_response(r.text) if self.validate(validate) else r.json()