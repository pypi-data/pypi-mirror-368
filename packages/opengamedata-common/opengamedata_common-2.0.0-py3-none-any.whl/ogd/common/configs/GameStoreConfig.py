# import standard libraries
from typing import Dict, Final, LiteralString, Optional, Self
# import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.configs.storage.DataStoreConfig import DataStoreConfig
from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.schemas.locations.DatabaseLocationSchema import DatabaseLocationSchema
from ogd.common.utils.typing import Map

class GameStoreConfig(Schema):
    """A simple Schema structure containing configuration information for a particular game's data.
    
    When given to an interface, this schema is treated as the location from which to retrieve data.
    When given to an outerface, this schema is treated as the location in which to store data.
    (note that some interfaces/outerfaces, such as debugging i/o-faces, may ignore the configuration)
    Key properties of this schema are:
    - `Name` : Typically, the name of the Game whose source configuration is indicated by this schema
    - `Source` : A data source where game data is stored
    - `DatabaseName` : The name of the specific database within the source that contains this game's data
    - `TableName` : The neame of the specific table within the database holding the given game's data
    - `TableConfig` : A schema indicating the structure of the table containing the given game's data.

    TODO : use a TableConfig for the table_schema instead of just the name of the schema, like we do with source_schema.
    TODO : Implement and use a smart Load(...) function of TableConfig to load schema from given name, rather than FromFile.
    """

    _DEFAULT_GAME_ID     : Final[LiteralString] = "UNKNOWN GAME"
    _DEFAULT_SOURCE_NAME : Final[LiteralString] = "OPENGAMEDATA_BQ"
    _DEFAULT_SCHEMA_NAME : Final[LiteralString] = "OPENGAMEDATA_BIGQUERY"
    _DEFAULT_DB_NAME     : Final[LiteralString] = "UNKNOWN GAME"
    _DEFAULT_TABLE_NAME  : Final[LiteralString] = "_daily"
    _DEFAULT_TABLE_LOC   : Final[DatabaseLocationSchema] = DatabaseLocationSchema(
        name="DefaultTableLocation",
        database_name=_DEFAULT_DB_NAME,
        table_name=_DEFAULT_TABLE_NAME
    )

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, game_id:Optional[str],
                 source_name:Optional[str],
                 schema_name:Optional[str],
                 table_location:Optional[DatabaseLocationSchema],
                 source:Optional[DataStoreConfig]=None, schema:Optional[TableSchema]=None,
                 other_elements:Optional[Map]=None):
        """Constructor for the `GameStoreConfig` class.
        
        If optional params are not given, data is searched for in `other_elements`.

        Expected format:

        ```
        {
            "source" : "DATA_SOURCE_NAME",
            "schema" : "TABLE_SCHEMA_NAME",
            "database": "db_name",
            "table" : "table_name"
        },
        ```

        :param name: _description_
        :type name: str
        :param game_id: _description_
        :type game_id: Optional[str]
        :param source_name: _description_
        :type source_name: Optional[str]
        :param schema_name: _description_
        :type schema_name: Optional[str]
        :param table_location: _description_
        :type table_location: Optional[DatabaseLocationSchema]
        :param other_elements: _description_
        :type other_elements: Optional[Map]
        """
        unparsed_elements : Map = other_elements or {}

        self._game_id        : str                       = game_id or name
        self._source_name    : str                       = source_name    or self._parseSourceName(unparsed_elements=unparsed_elements)
        self._config         : Optional[DataStoreConfig] = source
        self._schema_name    : str                       = schema_name    or self._parseSchemaName(unparsed_elements=unparsed_elements)
        self._schema         : Optional[TableSchema]     = schema
        self._table_location : DatabaseLocationSchema    = table_location or self._parseTableLocation(unparsed_elements=unparsed_elements)

        super().__init__(name=name, other_elements=other_elements)

    @property
    def GameID(self) -> str:
        """Property to get the Game ID (also called App ID) associated with the given game source

        By convention, this is a human-readable simplification of the games name, in CONSTANT_CASE format

        :return: _description_
        :rtype: str
        """
        return self._game_id

    @property
    def StoreName(self) -> str:
        return self._source_name

    @property
    def StoreConfig(self) -> Optional[DataStoreConfig]:
        return self._config
    @StoreConfig.setter
    def StoreConfig(self, source:DataStoreConfig):
        self._config = source

    @property
    def TableSchemaName(self) -> str:
        return self._schema_name

    @property
    def Table(self) -> Optional[TableSchema]:
        return self._schema
    @Table.setter
    def Table(self, schema:TableSchema):
        self._schema = schema

    @property
    def TableLocation(self) -> DatabaseLocationSchema:
        return self._table_location

    @property
    def DatabaseName(self) -> str:
        return self._table_location.DatabaseName

    @property
    def TableName(self) -> Optional[str]:
        return self._table_location.TableName

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @property
    def AsMarkdown(self) -> str:
        ret_val : str

        ret_val = f"{self.Name}: _{self.TableSchemaName}_ format, source {self.StoreName} : {self.TableLocation.Location}"
        return ret_val

    @classmethod
    def Default(cls) -> "GameStoreConfig":
        return GameStoreConfig(
            name="DefaultGameStoreConfig",
            game_id=cls._DEFAULT_GAME_ID,
            source_name=cls._DEFAULT_SOURCE_NAME,
            source=None,
            schema_name=cls._DEFAULT_SCHEMA_NAME,
            schema=None,
            table_location=cls._DEFAULT_TABLE_LOC,
            other_elements={}
        )

    @classmethod
    def _fromDict(cls, name:str, unparsed_elements:Map,
                  key_overrides:Optional[Dict[str, str]]=None,
                  default_override:Optional[Self]=None) -> "GameStoreConfig":
        """Create a GameStoreConfig from a given dictionary

        TODO : Add example of what format unparsed_elements is expected to have.
        TODO : data_sources shouldn't really be a param here. Better to have e.g. a way to register the list into GameStoreConfig class, or something.

        :param name: _description_
        :type name: str
        :param all_elements: _description_
        :type all_elements: Dict[str, Any]
        :param logger: _description_
        :type logger: Optional[logging.Logger]
        :param data_sources: _description_
        :type data_sources: Dict[str, DataStoreConfig]
        :return: _description_
        :rtype: GameStoreConfig
        """
        return GameStoreConfig(name=name, game_id=None, source_name=None, schema_name=None,
                                table_location=None, other_elements=unparsed_elements)

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    @staticmethod
    def _parseSourceName(unparsed_elements:Map) -> str:
        return GameStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["source", "source_name"],
            to_type=str,
            default_value=GameStoreConfig._DEFAULT_SOURCE_NAME,
            remove_target=True
        )

    @staticmethod
    def _parseSchemaName(unparsed_elements:Map) -> str:
        return GameStoreConfig.ParseElement(
            unparsed_elements=unparsed_elements,
            valid_keys=["schema"],
            to_type=str,
            default_value=GameStoreConfig._DEFAULT_SCHEMA_NAME,
            remove_target=True
        )

    @staticmethod
    def _parseTableLocation(unparsed_elements:Map) -> DatabaseLocationSchema:
        return DatabaseLocationSchema.FromDict(
            name="TableLocation",
            unparsed_elements=unparsed_elements,
            default_override=GameStoreConfig._DEFAULT_TABLE_LOC
        )

    # *** PRIVATE METHODS ***
