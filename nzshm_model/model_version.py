"""
The model version module defines the availabe models

Attributes:
    versions (Dict[str, str]): a mapping from model version string to its module name

"""

from typing import List

from .model import NshmModel
from .model_versions import versions

CURRENT_VERSION = "NSHM_v1.0.4"


def all_model_versions() -> List[str]:
    """
    get the list of available model versions
    """
    return list(versions.keys())


def get_model_version(version: str = CURRENT_VERSION) -> 'NshmModel':
    """
    A simple wrapper for the underlying NshmModel static method

    Returns:
        the model instance.
    """
    return NshmModel.get_model_version(version)
