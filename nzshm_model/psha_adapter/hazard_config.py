from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Optional, Sequence, Type

from nzshm_model.psha_adapter import ConfigPshaAdapterInterface

if TYPE_CHECKING:
    from nzshm_common import CodedLocation


class HazardConfig(ABC):
    @abstractmethod
    def is_complete(self) -> bool:
        pass

    @abstractmethod
    def set_sites(self, locations: Sequence['CodedLocation'], **kwargs) -> 'HazardConfig':
        pass

    def psha_adapter(
        self, provider: Type[ConfigPshaAdapterInterface], **kwargs: Optional[Dict]
    ) -> "ConfigPshaAdapterInterface":
        """get a PSHA adapter for this instance.

        Arguments:
            provider: the adapter class
            **kwargs: additional arguments required by the provider class

        Returns:
            a PSHA Adapter instance
        """
        return provider(target=self)
