"""
This module defines the interface to be provided by a PshaAdapter implementation.
"""

import pathlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


class PshaAdapterInterface(ABC):
    """
    Defines methods to be provided by a PSHA adapter class implementation.
    """

    @abstractmethod
    def __init__(self, target: Any):
        """
        Create a new PshaAdapterInterface object.

        Parameters:
            target: the object (e.g. SourceLogicTree) to be adapted to the specific hazard engine
        """
        pass

    @abstractmethod
    def write_config(self, *args, **kwargs) -> pathlib.Path:
        pass


class SourcePshaAdapterInterface(PshaAdapterInterface):
    """
    Defines methods to be provided by a PSHA source model adapter class implementation.
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
    def write_config(
        self,
        cache_folder: Union[pathlib.Path, str],
        target_folder: Union[pathlib.Path, str],
        resource_map: Optional[Dict[str, list[pathlib.Path]]] = None,
    ) -> pathlib.Path:
        """Build PSHA source input files"""
        pass


class GMCMPshaAdapterInterface(PshaAdapterInterface):
    """
    Defines methods to be provided by a PSHA ground motion model adapter class implementation.
    """

    @abstractmethod
    def write_config(self, target_folder: Union[pathlib.Path, str]) -> pathlib.Path:
        """Build PSHA GMCM input files"""
        pass


class ConfigPshaAdapterInterface(PshaAdapterInterface):
    """
    Defines methods to be provided by a PSHA ground motion model adapter class implementation.
    """

    @abstractmethod
    def write_config(self, target_folder: Union[pathlib.Path, str]) -> pathlib.Path:
        """Build PSHA calculation config input files"""
        pass


class ModelPshaAdapterInterface(PshaAdapterInterface):
    """
    Defines methods to be provided by a PSHA model adapter class implementation.
    """

    @abstractmethod
    def write_config(
        self,
        cache_folder: Union[pathlib.Path, str],
        target_folder: Union[pathlib.Path, str],
        resource_map: Optional[Dict[str, list[pathlib.Path]]] = None,
    ) -> pathlib.Path:
        """Build all PSHA input files"""
        pass
