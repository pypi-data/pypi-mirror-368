# standard imports
from datetime import date
from typing import Final, Optional

class DatasetKey:
    """
    DatasetKey dumb struct.

    TODO : Rework this to be more like other schemas.
    """

    # *** BUILT-INS & PROPERTIES ***

    _DEFAULT_KEY     : Final[str] = "DEFAULT_GAME_20000101_to_20000131"
    _DEFAULT_GAME_ID : Final[str] = "UNKOWN_GAME"

    """Simple little class to make logic with dataset keys easier
    """
    def __init__(self, raw_key:str):
        self._game_id    : str
        self._from_date  : Optional[date] = None
        self._to_date    : Optional[date] = None

    # 1. Get Game ID from key
        _pieces = raw_key.split("_")
        self._game_id = "_".join(_pieces[:-3]) if len(_pieces) >= 4 else "INVALID DATASET KEY"
    # 2. Get Dates from key
        # If this _dataset_key matches the expected format,
        # i.e. split is: ["GAME", "ID", "PARTS",..., "YYYYMMDD", "to", "YYYYMMDD"]
        # Technically, the dates aren't required, and we could have a player ID instead.
        # In that case, we just don't have dates built into the Key.
        # File API should be prepared to account for this.
        if len(_pieces[-3]) == 8:
            _from_year  = int(_pieces[-3][0:4])
            _from_month = int(_pieces[-3][4:6])
            _from_day   = int(_pieces[-3][6:8])
            self._from_date = date(year=_from_year, month=_from_month, day=_from_day)
        if len(_pieces[-1]) == 8:
            _to_year    = int(_pieces[-1][0:4])
            _to_month   = int(_pieces[-1][4:6])
            _to_day     = int(_pieces[-1][6:8])
            self._to_date = date(year=_to_year, month=_to_month, day=_to_day)
        self._original_key = raw_key

    def __str__(self):
        return self._original_key
    
    @property
    def IsValid(self) -> bool:
        return  self._from_date  is not None \
            and self._to_date is not None
    @property
    def GameID(self) -> str:
        return self._game_id
    @property
    def DateFrom(self) -> Optional[date]:
        return self._from_date
    @property
    def DateTo(self) -> Optional[date]:
        return self._to_date

    # *** PUBLIC STATICS ***

    @classmethod
    def Default(cls) -> "DatasetKey":
        return DatasetKey(
            raw_key=cls._DEFAULT_KEY,
        )

    @staticmethod
    def FromDateRange(game_id:Optional[str], start_date:date, end_date:date):
        return DatasetKey(raw_key=f"{game_id or DatasetKey._DEFAULT_GAME_ID}_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}")

    @staticmethod
    def FromID(game_id:Optional[str], ID:str):
        return DatasetKey(raw_key=f"{game_id or DatasetKey._DEFAULT_GAME_ID}_{ID}")

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
