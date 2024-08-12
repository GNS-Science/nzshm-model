from abc import ABC, abstractmethod
from nzshm_model.psha_adapter import PshaAdapterInterface
from typing import Type, Optional, Dict


class HazardConfig(ABC):

    @abstractmethod
    def is_complete(self) -> bool:
        pass

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs: Optional[Dict]) -> "PshaAdapterInterface":
        """get a PSHA adapter for this instance.

        Arguments:
            provider: the adapter class
            **kwargs: additional arguments required by the provider class

        Returns:
            a PSHA Adapter instance
        """
        return provider(model=self)
