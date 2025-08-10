from typing_extensions import TypeVar
from dataclasses import dataclass, field

T = TypeVar('T')

def lazy_validator(Type: type[T]):
  from functools import cache
  @cache
  def adapter():
    from pydantic import TypeAdapter
    return TypeAdapter(Type) # type: ignore
  
  def validate(data: str) -> T:
    return adapter().validate_json(data)

  return validate

DEFAULT_VALIDATE = True
# import importlib.util
# if importlib.util.find_spec('pydantic') is not None:
#   DEFAULT_VALIDATE = True
# else:
#   DEFAULT_VALIDATE = False

@dataclass
class ValidationMixin:
  default_validate: bool = field(default=DEFAULT_VALIDATE, kw_only=True)

  def validate(self, validate: bool | None) -> bool:
    return self.default_validate if validate is None else validate