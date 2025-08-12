from typing import Any, Dict

from ogd.common.schemas.tables.TableSchema import TableSchema
from ogd.common.schemas.tables.EventTableSchema import EventTableSchema
from ogd.common.schemas.tables.FeatureTableSchema import FeatureTableSchema

class TableSchemaFactory:
    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any])-> TableSchema:
        table_type = str(all_elements.get("table_type", "NOT FOUND"))
        # _table_type       = TableType.FromString(_table_type_str) if _table_type_str is not None else TableType.EVENT
        match (table_type.upper()):
            case "EVENT":
                return EventTableSchema.FromDict(name=name, unparsed_elements=all_elements)
            case "FEATURE":
                return FeatureTableSchema.FromDict(name=name, unparsed_elements=all_elements)
            case _:
                raise ValueError(f"Could not generate TableSchema from dictionary, table_type had invalid value {table_type}")