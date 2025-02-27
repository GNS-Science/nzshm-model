#! nshm_v1_0_0.py
"""
This module defines a factory function for generating an `NshmModel` object for the model version NSHM_v1.0.0.
The dict returned by the function is passed as keyword arguments to the `NshmModel` constructor:

    >>> from nzshm_model import NshmModel
    >>> from nzshm_model.model_versions.nshm_v1_0_0 import model_args_factory
    >>> model = NshmModel(**model_args_factory())

NB library users will typically never use this, rather they will obtain a model instance
using function: `nzshm_model.get_model_version`.
"""
from typing import Any, Dict


def model_args_factory() -> Dict[str, Any]:
    return dict(
        version='NSHM_v1.0.0',
        title="Initial version",
        slt_json="nshm_v1.0.0_v2.json",
        gmm_json="gmcm_nshm_v1.0.0.json",
        hazard_config_json="oq_config_nshm_v1.0.0.json",
    )
