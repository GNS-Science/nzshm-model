from typing import TYPE_CHECKING, Optional

from . import nshm_v1_0_0, nshm_v1_0_4

if TYPE_CHECKING:
    from .model import NshmModel


versions = {
    "NSHM_v1.0.0": nshm_v1_0_0.model,
    "NSHM_v1.0.4": nshm_v1_0_4.model,
}


def get_model_version(version_id: str) -> Optional['NshmModel']:
    """
    Retrieve a model by a specific version

    Parameters:
        version_id: The unique identifier for the model version.

    Yields:
        The specified model version. if found, or None if the version does not exist.
    """
    return versions.get(version_id)
