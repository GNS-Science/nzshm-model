#! nshm_v1_0_4.py
"""
This module defines a factory function for generating an NshmModel object for the model version NSHM_v1.0.4.
The dict returned by the function is passed as keyword arguments to the NshmModel constructor:

    >>> from nzshm_model import NshmModel
    >>> from nzshm_model.model_versions.nshm_v1_0_4 import model_args_factory
    >>> model = NshmModel(**model_args_factory())

NB library users will typically never use this, rather they will obtain a model instance
using function: `nzshm_model.get_model_version`.
"""
from typing import Any, Dict
from pathlib import Path

from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig
from nzshm_model.psha_adapter.openquake.hazard_config_compat import DEFAULT_HAZARD_CONFIG
from .model_definition import ModelDefinition


def model_args_factory() -> ModelDefinition:
    return ModelDefinition(
        version='NSHM_v1.0.4',
        title="NSHM version 1.0.4, corrected fault geometry",
        slt_json=Path("nshm_v1.0.4_v2.json"),
        gmm_json=Path("gmcm_nshm_v1.0.4.json"),
        hazard_config=OpenquakeConfig(DEFAULT_HAZARD_CONFIG),
    )
