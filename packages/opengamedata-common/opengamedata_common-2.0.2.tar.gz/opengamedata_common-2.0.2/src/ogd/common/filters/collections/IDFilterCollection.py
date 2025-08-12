## import standard libraries
from typing import List, Optional, Set
# import local files
from ogd.common.filters import *
from ogd.common.models.enums.FilterMode import FilterMode

class IDFilterCollection:
    """Dumb struct to hold filters for versioning information
    """
    def __init__(self,
                 session_filter: SetFilter[str] | NoFilter = NoFilter(),
                 player_filter : SetFilter[str] | NoFilter = NoFilter()):
        self._session_filter : SetFilter[str] | NoFilter = session_filter
        self._player_filter  : SetFilter[str] | NoFilter = player_filter

    def __str__(self) -> str:
        ret_val = "no versioning filters"
        if self.Sessions or self.Players:
            _sess_str = f"session(s) {self.Sessions}" if self.Sessions else None
            _ply_str = f"player(s) {self.Players}" if self.Players else None
            _ver_strs = ", ".join([elem for elem in [_sess_str, _ply_str] if elem is not None])
            ret_val = f"event filters: {_ver_strs}"
        return ret_val

    def __repr__(self) -> str:
        ret_val = f"<class {type(self).__name__} no filters>"
        if self.Sessions or self.Players:
            _sess_str = f"session(s) {self.Sessions}" if self.Sessions else None
            _ply_str = f"player(s) {self.Players}" if self.Players else None
            _ver_strs = " ^ ".join([elem for elem in [_sess_str, _ply_str] if elem is not None])
            ret_val = f"<class {type(self).__name__} {_ver_strs}>"
        return ret_val

    @property
    def Sessions(self) -> Filter[str]:
        return self._session_filter
    @Sessions.setter
    def Sessions(self, included_sessions:Optional[SetFilter | List[str] | Set[str]]) -> None:
        if included_sessions is None:
            self._session_filter = NoFilter()
        elif isinstance(included_sessions, SetFilter):
            self._session_filter = included_sessions
        elif isinstance(included_sessions, list) or isinstance(included_sessions, set):
            self._session_filter = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(included_sessions))

    @property
    def Players(self) -> Filter[str]:
        return self._player_filter
    @Players.setter
    def Players(self, included_players:Optional[SetFilter | List[str] | Set[str]]) -> None:
        if included_players is None:
            self._player_filter = NoFilter()
        elif isinstance(included_players, SetFilter):
            self._player_filter = included_players
        elif isinstance(included_players, list) or isinstance(included_players, set):
            self._player_filter = SetFilter(mode=FilterMode.INCLUDE, set_elements=set(included_players))

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
