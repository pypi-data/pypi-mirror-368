## import standard libraries
import abc
from typing import Optional
## import local files
from ogd.common.schemas.Schema import Schema
from ogd.common.utils.typing import Map

## @class LocationSchema
class LocationSchema(Schema):

    # *** ABSTRACTS ***

    @property
    @abc.abstractmethod
    def Location(self) -> str:
        """Gets a string representation of the full location.

        :return: A string representation of the full location.
        :rtype: str
        """
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, other_elements:Optional[Map]=None):
        super().__init__(name=name, other_elements=other_elements)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***
