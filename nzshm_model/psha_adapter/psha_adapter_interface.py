import pathlib
from abc import ABC, abstractmethod
from typing import Dict, Union


class PshaAdapterInterface(ABC):
    """
    Defines methods to be provided by a PSHA adapter class implementation.
    """

    def __init__(self, source_logic_tree=None, gmcm_logic_tree=None):
        self._source_logic_tree = source_logic_tree
        self._gmcm_logic_tree = gmcm_logic_tree

    @abstractmethod
    def fetch_resources(self, cache_folder):
        """pull required data from api and store in target_folder"""
        pass

    @abstractmethod
    def unpack_resources(self, cache_folder: Union[pathlib.Path, str], target_folder: Union[pathlib.Path, str]):
        """unpack resources from cache_folder to target folder returning mapping of unpacked filepaths"""
        pass

    @abstractmethod
    def config(self):
        """Get the PSHA config file"""
        pass

    @abstractmethod
    def write_config(
        self,
        cache_folder: Union[pathlib.Path, str],
        target_folder: Union[pathlib.Path, str],
        resource_map: Dict[str, list[pathlib.Path]],
    ) -> pathlib.Path:
        """Build an openquake config from given input arguments"""
        pass
