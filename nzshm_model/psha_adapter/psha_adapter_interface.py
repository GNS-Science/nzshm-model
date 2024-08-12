"""
This module defines the interface to be provided by a PshaAdapter implementation.
"""
import pathlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Union

if TYPE_CHECKING:
    from nzshm_model import NshmModel


class PshaAdapterInterface(ABC):
    """
    Defines methods to be provided by a PSHA adapter class implementation.
    """

    @abstractmethod
    def fetch_resources(self, cache_folder):
        """pull required data from api and store in target_folder"""
        pass

    @abstractmethod
    def unpack_resources(self, cache_folder: Union[pathlib.Path, str], target_folder: Union[pathlib.Path, str]):
        """unpack resources from cache_folder to target folder returning mapping of unpacked filepaths"""
        pass

    @abstractmethod
    def sources_document(self):
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
