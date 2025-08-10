from dataclasses import dataclass, field
from .client import ClientMixin

MEXC_UI_BASE = 'https://www.mexc.com'

@dataclass
class UIMixin(ClientMixin):
  u_id: str = ''
  ui_base: str = field(default=MEXC_UI_BASE, kw_only=True)

  async def ui_request(
    self, method: str, path: str, params: dict | None = None, *,
    headers: dict | None = None, cookies: dict | None = None,
    json=None,
  ):
    return await self.client.request(method, self.ui_base + path, params=params, headers=headers, cookies={
      'u_id': self.u_id,
      **(cookies or {}),
    }, json=json)
  