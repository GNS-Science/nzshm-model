import json
from abc import ABC, abstractmethod
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from nzshm_model.psha_adapter import ConfigPshaAdapterInterface

if TYPE_CHECKING:
    from nzshm_common import CodedLocation

HazardConfigType = TypeVar('HazardConfigType', bound='HazardConfig')


class HazardConfig(ABC):
    hazard_type = "abstract"  # every child class should specify its type for use in loading from file

    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @abstractmethod
    def is_complete(self) -> bool:
        pass

    @abstractmethod
    def set_sites(self, locations: Sequence['CodedLocation'], **kwargs) -> 'HazardConfig':
        pass

    def to_json(self, file_path: Path | str) -> None:
        """serialized HazardConfig object to json file

        Args:
            file_path: path to file to be written
        """

        data = self.to_dict()
        with Path(file_path).open('w') as jsonfile:
            json.dump(data, jsonfile, indent=2)
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert HazardConfig object to dict

        Returns:
            dict representation of object
        """
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls: type[HazardConfigType], data: dict) -> HazardConfigType:
        """
        create a HazardConfig object from a dictionary

        Args:
            data: the dictionary representation of the HazardConfig object

        Returns:
            a HazardConfig object
        """
        pass

    @classmethod
    @abstractmethod
    def from_json(cls: type[HazardConfigType], file_path: Path | str) -> HazardConfigType:
        pass

    def psha_adapter(
        self, provider: type[ConfigPshaAdapterInterface], **kwargs: dict | None
    ) -> "ConfigPshaAdapterInterface":
        """get a PSHA adapter for this instance.

        Arguments:
            provider: the adapter class
            **kwargs: additional arguments required by the provider class

        Returns:
            a PSHA Adapter instance
        """
        return provider(target=self)
