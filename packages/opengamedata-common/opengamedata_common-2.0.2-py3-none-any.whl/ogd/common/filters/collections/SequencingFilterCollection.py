## import standard libraries
from datetime import date, datetime
from typing import Optional
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.utils.typing import Pair

class SequencingFilterCollection:
    """Dumb struct to hold filters for timing information

    For now, it just does timestamps and session index, if need be we may come back and allow filtering by timezone offset
    """
    def __init__(self,
                 timestamp_filter     : RangeFilter[datetime | date] | NoFilter      = NoFilter(),
                 session_index_filter : SetFilter[int] | RangeFilter[int] | NoFilter = NoFilter()):
        """Constructor for the TimingFilterCollection structure.

        Accepts a collection of filters to be applied on timing of data.
        Each defaults to "no filter," meaning no results will be removed based on the corresponding versioning data.

        :param log_ver_filter: The filter to apply to log version, defaults to NoFilter()
        :type log_ver_filter: Filter, optional
        :param app_ver_filter: The filter to apply to app version, defaults to NoFilter()
        :type app_ver_filter: Filter, optional
        :param branch_filter: The filter to apply to app branch, defaults to NoFilter()
        :type branch_filter: Filter, optional
        """
        self._timestamp_filter     : RangeFilter[datetime | date] | NoFilter      = timestamp_filter
        self._session_index_filter : SetFilter[int] | RangeFilter[int] | NoFilter = session_index_filter

    def __str__(self) -> str:
        ret_val = "no timestamp filters"
        if self.Timestamps or self.SessionIndices:
            _times_str = f"time(s) {self.Timestamps}" if self.Timestamps else None
            _idxes_str = f"event index(s) {self.SessionIndices}" if self.SessionIndices else None
            _ver_strs = ", ".join([elem for elem in [_times_str, _idxes_str] if elem is not None])
            ret_val = f"timestamp filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        if self.Timestamps or self.SessionIndices:
            _times_str = f"time(s) {self.Timestamps}" if self.Timestamps else None
            _idxes_str = f"event index(s) {self.SessionIndices}" if self.SessionIndices else None
            _ver_strs = ", ".join([elem for elem in [_times_str, _idxes_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def Timestamps(self) -> Filter[datetime | date]:
        return self._timestamp_filter
    @Timestamps.setter
    def Timestamps(self, allowed_times:Optional[RangeFilter[datetime | date] | NoFilter | slice | Pair]) -> None:
        if allowed_times is None or isinstance(allowed_times, NoFilter):
            self._timestamp_filter = NoFilter()
        elif isinstance(allowed_times, RangeFilter):
            self._timestamp_filter = allowed_times
        elif isinstance(allowed_times, slice):
            self._timestamp_filter = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, slice=allowed_times)
        elif isinstance(allowed_times, tuple):
            self._timestamp_filter = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_times[0], maximum=allowed_times[1])

    @property
    def SessionIndices(self) -> Filter[int]:
        return self._session_index_filter
    @SessionIndices.setter
    def SessionIndices(self, allowed_indices:Optional[SetFilter[int] | RangeFilter[int] | NoFilter | slice | Pair[int, int]]) -> None:
        if allowed_indices is None or isinstance(allowed_indices, NoFilter):
            self._session_index_filter = NoFilter()
        elif isinstance(allowed_indices, Filter):
            self._session_index_filter = allowed_indices
        elif isinstance(allowed_indices, slice):
            self._session_index_filter = RangeFilter.FromSlice(mode=FilterMode.INCLUDE, slice=allowed_indices)
        elif isinstance(allowed_indices, tuple):
            self._session_index_filter = RangeFilter(mode=FilterMode.INCLUDE, minimum=allowed_indices[0], maximum=allowed_indices[1])

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
