"""OGD-Common Typing Utilities

This module contains several typedefs for convenience when type-hinting within other modules.
It also contains a `conversions` class that works to reasonably robustly convert various data types among each other using standard Python approaches.
"""
## import standard libraries
import abc
import datetime
from typing import Any, Dict, List, TypeVar, Tuple
## import local files
from ogd.common.models.SemanticVersion import SemanticVersion

type Map        = Dict[str, Any] # type alias: we'll call any dict using string keys a "Map"
type ExportRow  = List[Any]
type Pair[A, B] = Tuple[A, B]
type Version    = int | str | SemanticVersion
type Date       = datetime.datetime | datetime.date

class Comparable:
    @abc.abstractmethod
    def __lt__(self, other:Any) -> bool:
        pass
    @abc.abstractmethod
    def __gt__(self, other:Any) -> bool:
        pass
ComparableType = TypeVar("ComparableType", bound=Comparable)
