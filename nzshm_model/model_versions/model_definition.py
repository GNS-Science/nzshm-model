from dataclasses import dataclass
from typing import TypedDict, Generic
from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig
from nzshm_model.psha_adapter.hazard_config import HazardConfigType
from pathlib import Path

# @dataclass
# class ModelDefinition:

#     version: str
#     title: str
#     slt_json: Path
#     gmm_json: Path
#     hazard_config: OpenquakeConfig

class ModelDefinition(TypedDict, Generic[HazardConfigType]):
    version: str
    title: str
    slt_json: Path
    gmm_json: Path
    hazard_config: HazardConfigType
