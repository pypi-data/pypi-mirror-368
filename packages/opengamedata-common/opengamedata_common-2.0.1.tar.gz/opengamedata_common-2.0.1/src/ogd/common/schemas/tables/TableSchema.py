## import standard libraries
import abc
import json
import logging
from pathlib import Path
from typing import Any, Dict, Final, List, Optional, Tuple, TypeAlias
## import local files
from ogd.common.schemas.tables import presets
from ogd.common.schemas.Schema import Schema
from ogd.common.schemas.tables.ColumnSchema import ColumnSchema
from ogd.common.schemas.tables.ColumnMapSchema import ColumnMapSchema, ColumnMapElement
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Map, conversions

ColumnMapIndex   : TypeAlias = Optional[int | List[int] | Dict[str,int]]

## @class TableSchema
class TableSchema(Schema):
    """Dumb struct to hold info about the structure of data for a particular game, from a particular source.
        In particular, it contains an ordered list of columns in the data source table,
        and a mapping of those columns to the corresponding elements of a formal OGD structure.
    """

    _DEFAULT_SCHEMA_PATH : Final[Path] = Path(presets.__file__).parent
    _DEFAULT_COLUMNS     : Final[List[ColumnSchema]] = []

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def ColumnMap(self) -> ColumnMapSchema:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name,
                 columns:Optional[List[ColumnSchema]],
                 other_elements:Optional[Map]=None
        ):
        """Constructor for the TableSchema class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "column_map": {
                "session_id"           : "session_id",
                "app_id"               : null,
                "timestamp"            : ["client_time", "client_time_ms"],
                ...
            },

            "columns": [
                {
                    "name": "session_id",
                    "readable": "Session ID",
                    "description": "ID for the play session",
                    "type": "str"
                },
                {
                    "name": "client_time",
                    ...
                },
        },
        ```

        :param schema_name: The filename for the table schema JSON.
        :type schema_name: str
        :param schema_path: Path to find the given table schema file, defaults to "./schemas/tables/presets/"
        :type schema_path: str, optional
        :param is_legacy: [description], defaults to False
        :type is_legacy: bool, optional
        """
        unparsed_elements : Map = other_elements or {}

        # declare and initialize vars
        # self._schema            : Optional[Dict[str, Any]] = all_elements
        self._table_columns : List[ColumnSchema] = columns    or self._parseColumns(unparsed_elements=unparsed_elements)

        # after loading the file, take the stuff we need and store.
        super().__init__(name=name, other_elements=other_elements)

    @property
    def Columns(self) -> List[ColumnSchema]:
        return self._table_columns

    @property
    def ColumnNames(self) -> List[str]:
        """Function to get the names of all columns in the schema.

        :return: Names of each column in the schema.
        :rtype: List[str]
        """
        return [col.Name for col in self._table_columns]

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    @classmethod
    def FromFile(cls, schema_name:str, schema_path:str | Path=_DEFAULT_SCHEMA_PATH) -> "TableSchema":
        ret_val : Schema

        schema_path = schema_path
        ret_val = cls._fromFile(schema_name=schema_name, schema_path=Path(schema_path))
        if isinstance(ret_val, TableSchema):
            return ret_val
        else:
            raise ValueError(f"TableSchema's call to _fromFile yielded a Schema of different type ({type(ret_val)})!")

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
    
    def _formatMappedColumn(self, index:ColumnMapIndex):
        """Takes a column mapping index, and returns a nicely-formatted string of the columns included in the index.

        If the index is just an int, it will return the name of the column:
        > "ColumnName"

        If the index is a list, it will return a comma-separated list of the column names:
        > "ColumnName1, ColumnName2"

        If the index is a dict, it will return a JSON-formatted string mapping keys to column names:
        > { "key1" : "ColumnName1", "key2" : "ColumnName2 }

        :param index: _description_
        :type index: ColumnMapIndex
        :raises TypeError: _description_
        :return: _description_
        :rtype: _type_
        """
        ret_val : str

        if isinstance(index, int):
            ret_val = self.ColumnNames[index]
        elif isinstance(index, list):
            ret_val = ", ".join([self.ColumnNames[idx] for idx in index])
        elif isinstance(index, dict):
            ret_val = json.dumps({key: self.ColumnNames[i] for key,i in index.items()})
        else:
            raise TypeError(f"Column mapping can not be type {type(index)}!")
        
        return ret_val
    
    def _indexFromMapping(self, mapping:ColumnMapElement) -> ColumnMapIndex:
        ret_val : ColumnMapIndex

        if isinstance(mapping, str):
            ret_val = self.ColumnNames.index(mapping)
        elif isinstance(mapping, list):
            ret_val = [self.ColumnNames.index(col_name) for col_name in mapping]
        elif isinstance(mapping, dict):
            ret_val = {key:self.ColumnNames.index(val) for key,val in mapping}

        return ret_val

    def _valueFromRow(self, row:Tuple, indices:Optional[ColumnMapIndex], concatenator:str, fallback:Any) -> Any:
        ret_val : Any
        if indices is not None:
            if isinstance(indices, int):
                # if there's a single index, use parse to get the value it is stated to be
                # print(f"About to parse value {row[indices]} as type {self.Columns[indices]},\nFull list from row is {row},\nFull list of columns is {self.Columns},\nwith names {self.ColumnNames}")
                ret_val = conversions.ConvertToType(value=row[indices], to_type=self.Columns[indices].ValueType)
            elif isinstance(indices, list):
                ret_val = concatenator.join([str(row[index]) for index in indices])
            elif isinstance(indices, dict):
                ret_val = {}
                for key,column_index in indices.items():
                    if column_index > len(row):
                        Logger.Log(f"Got column index of {column_index} for column {key}, but row only has {len(row)} columns!", logging.ERROR)
                    _val = conversions.ConvertToType(value=row[column_index], to_type=self._table_columns[column_index].ValueType)
                    ret_val.update(_val if isinstance(_val, dict) else {key:_val})
        else:
            ret_val = fallback
        return ret_val

    @staticmethod
    def _parseColumns(unparsed_elements:Map) -> List[ColumnSchema]:
        ret_val : List[ColumnSchema]

        _column_json_list = TableSchema.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["columns"],
            to_type=list,
            default_value=None,
            remove_target=True
        )
        if _column_json_list:
            ret_val = [ColumnSchema.FromDict(name=column.get("name", "UNKNOWN COLUMN NAME"), unparsed_elements=column) for column in _column_json_list]
        else:
            ret_val = TableSchema._DEFAULT_COLUMNS

        return ret_val
