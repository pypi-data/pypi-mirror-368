from typing_extensions import TypedDict

class ApiError(TypedDict):
  msg: str
  code: int
