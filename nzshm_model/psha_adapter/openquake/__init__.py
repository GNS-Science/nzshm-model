"""
This package provides a psha_adapter implementation for the openquake PSHA.

Classes:
    OpenquakeConfig: a concrete psha_adapter for openquake hazard configuration

Attributes:
    DEFAULT_HAZARD_CONFIG: the base hazard configuration for NZHSM

"""

from .hazard_config import OpenquakeConfig
from .hazard_config_compat import DEFAULT_HAZARD_CONFIG
from .logic_tree import NrmlDocument
from .simple_nrml import (
    OpenquakeConfigPshaAdapter,
    OpenquakeGMCMPshaAdapter,
    OpenquakeModelPshaAdapter,
    OpenquakeSourcePshaAdapter,
    gmcm_branch_from_element_text,
)
