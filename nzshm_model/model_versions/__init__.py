from dataclasses import dataclass

from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig

from .nshm_v1_0_0 import model_args_factory as model_args_nshm_v1_0_0
from .nshm_v1_0_4 import model_args_factory as model_args_nshm_v1_0_4

versions = {
    "NSHM_v1.0.0": model_args_nshm_v1_0_0,
    "NSHM_v1.0.4": model_args_nshm_v1_0_4,
}
