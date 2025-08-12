## import standard libraries
# import local files
from ogd.common.filters.collections.EventFilterCollection import EventFilterCollection
from ogd.common.filters.collections.IDFilterCollection import IDFilterCollection
from ogd.common.filters.collections.SequencingFilterCollection import SequencingFilterCollection
from ogd.common.filters.collections.VersioningFilterCollection import VersioningFilterCollection

class DatasetFilterCollection:
    def __init__(self,
                 id_filters:IDFilterCollection=IDFilterCollection(),
                 sequence_filters:SequencingFilterCollection=SequencingFilterCollection(),
                 version_filters:VersioningFilterCollection=VersioningFilterCollection(),
                 event_filters:EventFilterCollection=EventFilterCollection()):
        self._id_filters = id_filters
        self._sequence_filters = sequence_filters
        self._version_filters=version_filters
        self._event_filters = event_filters

    @property
    def IDFilters(self):
        return self._id_filters
    
    @property
    def Sequences(self):
        return self._sequence_filters
    
    @property
    def Versions(self):
        return self._version_filters
    
    @property
    def Events(self):
        return self._event_filters

    @property
    def AsDict(self):
        return {
            "session_id" : self.IDFilters.Sessions,
            "player_id" : self.IDFilters.Players
        }
