## import standard libraries
import logging
from typing import Optional, Set, TypeVar
# import local files
from ogd.common.utils.Logger import Logger
from ogd.common.filters.Filter import Filter
from ogd.common.models.enums.FilterMode import FilterMode

T = TypeVar("T")
class SetFilter(Filter[T]):
    def __init__(self, mode:FilterMode=FilterMode.NOFILTER, set_elements:Set[T]=set()):
        super().__init__(mode=mode)
        self._set = set(set_elements)

    def __str__(self) -> str:
        ret_val : str

        match self.FilterMode:
            case FilterMode.EXCLUDE:
                ret_val = f"not in set of {len(self._set)} elements"
            case FilterMode.INCLUDE:
                ret_val = f"in set of {len(self._set)} elements"
            case FilterMode.NOFILTER:
                ret_val = "unfiltered"
        
        return ret_val
    
    def __repr__(self) -> str:
        _types = set(type(elem).__name__ for elem in self._set)
        _type_str = " | ".join(_types)
        return f"<class {type(self).__name__} {self.FilterMode}:Set[{_type_str}] with {len(self._set)} elements>"

    @property
    def AsSet(self) -> Optional[Set[T]]:
        return self._set if self.FilterMode != FilterMode.NOFILTER else None

    @property
    def Min(self) -> None:
        return None

    @property
    def Max(self) -> None:
        return None
