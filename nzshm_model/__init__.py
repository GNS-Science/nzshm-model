"""
The main nzshm_model package

Attributes:
    CURRENT_VERSION (str): the version string for the currently published NSHM model.
    versions (Dict[str, str]): a mapping from model version string to its module name.
"""
from .model import NshmModel
from .model_version import versions

# Python package version is different than the NSHM MODEL version !!
__version__ = '0.7.0'


CURRENT_VERSION = "NSHM_v1.0.4"


def get_model_version(version: str = CURRENT_VERSION) -> 'NshmModel':
    """
    A simple wrapper for the underlying NshmModel static method

    Returns:
        the model instance.
    """
    return NshmModel.get_model_version(version)
