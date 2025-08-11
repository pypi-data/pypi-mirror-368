from typing import Any, Dict, Set

from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.storage.outerfaces.Outerface import Outerface
from ogd.common.storage.outerfaces.CSVOuterface import CSVOuterface
from ogd.common.storage.outerfaces.DebugOuterface import DebugOuterface
from ogd.common.storage.outerfaces.DictionaryOuterface import DictionaryOuterface

class OuterfaceFactory:
    @staticmethod
    def FromConfig(config:GameStoreConfig, export_modes:Set[ExportMode], repository:DatasetRepositoryConfig, dataset_id:str)-> Outerface:
        if config.StoreConfig:
            match (config.StoreConfig.Type.upper()):
                case "FILE" | "CSV" | "TSV":
                    return CSVOuterface(config=config, export_modes=export_modes, repository=repository, dataset_id=dataset_id)
                case "DEBUG":
                    return DebugOuterface(config=config, export_modes=export_modes)
                case "DICT" | "DICTIONARY" | "API":
                    return DictionaryOuterface(config=config, export_modes=export_modes, out_dict=None)
                case _:
                    raise ValueError(f"Could not generate Interface from GameStoreConfig, the underlying StoreConfig was unrecognized type {config.StoreConfig.Type}!")
        else:
            raise ValueError("Could not generate Interface from GameStoreConfig, the underlying StoreConfig was null!")

    @staticmethod
    def FromDict(name:str, all_elements:Dict[str, Any], export_modes:Set[ExportMode], repository:DatasetRepositoryConfig, dataset_id:str)-> Outerface:
        config = GameStoreConfig.FromDict(name=name, unparsed_elements=all_elements)
        return OuterfaceFactory.FromConfig(config=config, export_modes=export_modes, repository=repository, dataset_id=dataset_id)
