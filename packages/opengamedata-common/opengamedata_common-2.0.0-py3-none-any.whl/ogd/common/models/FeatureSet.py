## import standard libraries
from typing import List
# import local files
from ogd.common.filters.collections import *
from ogd.common.models.Feature import Feature
from ogd.common.utils.typing import ExportRow

class FeatureSet:
    """Dumb struct that primarily just contains an ordered list of events.
       It also contains information on any filters used to define the dataset, such as a date range or set of versions.
    """

    def __init__(self, features:List[Feature], filters:DatasetFilterCollection) -> None:
        self._features = features
        self._filters = filters

    def __iadd__(self, features:List[Feature]):
        self.Features += features

    def __len__(self):
        return len(self.Features)

    @property
    def Features(self) -> List[Feature]:
        return self._features
    @Features.setter
    def Features(self, features:List[Feature]):
        self._features = features

    @property
    def PopulationFeatures(self) -> List[Feature]:
        return [feature for feature in self.Features if feature.PlayerID == "*" and feature.SessionID == "*"]
    @property
    def PlayerFeatures(self) -> List[Feature]:
        return [feature for feature in self.Features if feature.PlayerID != "*"]
    @property
    def SessionFeatures(self) -> List[Feature]:
        return [feature for feature in self.Features if feature.SessionID != "*"]

    @property
    def FeatureLines(self) -> List[ExportRow]:
        return [feature.ColumnValues for feature in self.Features]
    @property
    def PopulationLines(self) -> List[ExportRow]:
        return [feature.ColumnValues for feature in self.PopulationFeatures]
    @property
    def PlayerLines(self) -> List[ExportRow]:
        return [feature.ColumnValues for feature in self.PlayerFeatures]
    @property
    def SessionLines(self) -> List[ExportRow]:
        return [feature.ColumnValues for feature in self.SessionFeatures]

    @property
    def Filters(self) -> DatasetFilterCollection:
        return self._filters

    @property
    def AsMarkdown(self):
        _filters_clause = "* ".join([f"{key} : {val}" for key,val in self.Filters.AsDict.items()])
        return f"## Feature Dataset\n\n{_filters_clause}"

    def ClearFeatures(self):
        self._features = []