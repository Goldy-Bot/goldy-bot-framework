from __future__ import annotations
from typing import Generic, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Tuple, Any

__all__ = (
    "DictHelper",
)

T = TypeVar("T")

class DictHelper(Generic[T]): # TODO: Better name for this.
    def __init__(self, data: T, **kwargs) -> None:
        self.data = data

        self.data.update(kwargs)

    @classmethod
    def strip(cls, dict_helpers: List[DictHelper] | Tuple[DictHelper]) -> List[Any]:
        return [x.data for x in dict_helpers]