from typing_extensions import TypedDict
from mexc.core import ClientMixin, ApiError, lazy_validator

class ServerTime(TypedDict):
  serverTime: int

Response: type[ServerTime | ApiError] = ServerTime | ApiError # type: ignore
validate_response = lazy_validator(Response)

class Time(ClientMixin):
  async def time(self, validate: bool | None = None) -> ApiError | ServerTime:
    """Get the server time.
    
    - `validate`: Whether to validate the response against the expected schema (default: True).

    > [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#check-server-time)
    """
    r = await self.request('GET', '/api/v3/time')
    return validate_response(r.text) if self.validate(validate) else r.json()