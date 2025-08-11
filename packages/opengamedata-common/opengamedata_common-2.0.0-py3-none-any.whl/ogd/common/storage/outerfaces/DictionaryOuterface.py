## import standard libraries
from typing import Any, Dict, List, Optional, override, Set

# import local files
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.schemas.datasets.DatasetSchema import DatasetSchema
from ogd.common.storage.outerfaces.Outerface import Outerface
from ogd.common.utils.typing import ExportRow

type OutputDict = Dict[str, Dict[str, List[str] | List[ExportRow]]]
class DictionaryOuterface(Outerface):

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, config:GameStoreConfig, export_modes:Set[ExportMode], out_dict:Optional[OutputDict]):
        """Constructor for a DictionaryOuterface, which provides a dictionary for each kind of data being processed

        :param game_id: The name of the game whose data is being exported
        :type game_id: str
        :param config: A GameStoreConfig indicating where output data should be stored. Ignored by the DictionaryOuterface class.
        :type config: GameStoreConfig
        :param export_modes: A set of all export modes that should be enabled.
        :type export_modes: Set[ExportMode]
        :param out_dict: The dictionary to which outputs are written by the DictionaryOuterface
        :type out_dict: Dict[str, Dict[str, Union[List[str], List[ExportRow]]]]
        """
        super().__init__(config=config, export_modes=export_modes)
        self._out      : OutputDict = out_dict or self._defaultOutDict()
        self._raw_evts : List[ExportRow] = []
        self._all_evts : List[ExportRow] = []
        self._sess     : List[ExportRow] = []
        self._plrs     : List[ExportRow] = []
        self._pops     : List[ExportRow] = []
        self._meta     : Dict[str, Any]  = {}
        # self.Open()

    # *** IMPLEMENT ABSTRACTS ***
    
    @property
    def Connector(self) -> None:
        return None

    def _removeExportMode(self, mode:ExportMode):
        match mode:
            case ExportMode.EVENTS:
                self._raw_evts = []
                self._out['raw_events']  = { "cols" : [], "vals" : self._raw_evts }
            case ExportMode.DETECTORS:
                self._all_evts = []
                self._out['all_events']  = { "cols" : [], "vals" : self._all_evts }
            case ExportMode.SESSION:
                self._sess = []
                self._out['sessions']    = { "cols" : [], "vals" : self._sess }
            case ExportMode.PLAYER:
                self._plrs = []
                self._out['players']     = { "cols" : [], "vals" : self._plrs }
            case ExportMode.POPULATION:
                self._pops = []
                self._out['populations'] = { "cols" : [], "vals" : self._pops }

    @override
    def _writeGameEventsHeader(self, header:List[str]) -> None:
        self._out['raw_events']['cols'] = header

    @override
    def _writeAllEventsHeader(self, header:List[str]) -> None:
        self._out['all_events']['cols'] = header

    @override
    def _writeSessionHeader(self, header:List[str]) -> None:
        self._out['sessions']['cols'] = header

    @override
    def _writePlayerHeader(self, header:List[str]) -> None:
        self._out['players']['cols'] = header

    @override
    def _writePopulationHeader(self, header:List[str]) -> None:
        self._out['populations']['cols'] = header

    @override
    def _writeGameEventLines(self, events:List[ExportRow]) -> None:
        # I'm always a bit fuzzy on when Python will copy vs. store reference,
        # but tests indicate if we just update self._evts, self._out is updated automatically
        # since it maps to self._evts.
        # Similar for the other functions here.
        self._raw_evts += events

    @override
    def _writeAllEventLines(self, events:List[ExportRow]) -> None:
        # I'm always a bit fuzzy on when Python will copy vs. store reference,
        # but tests indicate if we just update self._evts, self._out is updated automatically
        # since it maps to self._evts.
        # Similar for the other functions here.
        self._all_evts += events

    @override
    def _writeSessionLines(self, sessions:List[ExportRow]) -> None:
        self._sess += sessions

    @override
    def _writePlayerLines(self, players:List[ExportRow]) -> None:
        self._plrs += players

    @override
    def _writePopulationLines(self, populations:List[ExportRow]) -> None:
        self._pops += populations

    @override
    def _writeMetadata(self, dataset_schema:DatasetSchema):
        self._meta = dataset_schema.AsMetadata

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _defaultOutDict(self) -> OutputDict:
        return {
            'raw_events'  : { "cols" : [], "vals" : self._raw_evts },
            'all_events'  : { "cols" : [], "vals" : self._all_evts },
            'sessions'    : { "cols" : [], "vals" : self._sess },
            'players'     : { "cols" : [], "vals" : self._plrs },
            'populations' : { "cols" : [], "vals" : self._pops }
        }
