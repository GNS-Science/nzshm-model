# from .openquake import NrmlDocument, OpenquakeSimplePshaAdapter
from typing import Any

from .psha_adapter_interface import (
    ConfigPshaAdapterInterface,
    GMCMPshaAdapterInterface,
    ModelPshaAdapterInterface,
    PshaAdapterInterface,
    SourcePshaAdapterInterface,
)


class PshaAdapterMixin:
    """Mixin providing the psha_adapter() convenience method.

    Inherit from this to get a consistent adapter-dispatch method without
    duplicating the one-liner body across LogicTree, HazardConfig, and NshmModel.
    """

    def psha_adapter(self, provider: type[PshaAdapterInterface], **kwargs: Any) -> PshaAdapterInterface:
        """Return a PSHA adapter for this object.

        Arguments:
            provider: the adapter class to instantiate
            **kwargs: additional arguments (currently unused; reserved for future use)

        Returns:
            a PSHA adapter instance with ``target=self``
        """
        return provider(target=self)
