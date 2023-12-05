import pathlib
from abc import ABC, abstractmethod
from typing import Union


class PshaAdapterInterface(ABC):
    """
    Defines methods to be provided by a PSHA adapter class implementation.
    """

    def __init__(self, source_logic_tree):
        self._source_logic_tree = source_logic_tree

    @abstractmethod
    def fetch_resources(self, target_folder):
        pass

    @abstractmethod
    def write_config(self, target_folder: Union[pathlib.Path, str]) -> pathlib.Path:
        pass
