#! logic_tree_version_2.py

"""
Define source logic tree structures used in NSHM.
"""
import json
import pathlib
from dataclasses import dataclass, field
from typing import Dict, List, Type, Union

import dacite

from nzshm_model.psha_adapter import PshaAdapterInterface

from ..logic_tree import BranchAttributeValue


@dataclass
class InversionSource:
    nrml_id: str
    rupture_rate_scaling: Union[float, None]
    inversion_id: Union[str, None] = ""
    rupture_set_id: Union[str, None] = ""
    inversion_solution_type: Union[str, None] = ""
    type: str = "inversion"


@dataclass
class DistributedSource:
    nrml_id: str
    rupture_rate_scaling: Union[float, None]
    type: str = "distributed"

    # onfault_nrml_id: Union[str, None] = ""
    # distributed_nrml_id: Union[str, None] = ""
    # inversion_solution_id: Union[str, None] = ""
    # inversion_solution_type: Union[str, None] = ""
    # rupture_set_id: Union[str, None] = ""


@dataclass
class Branch:
    values: List[BranchAttributeValue] = field(default_factory=list)
    sources: List[Union[DistributedSource, InversionSource]] = field(default_factory=list)
    weight: float = 1.0
    rupture_rate_scaling: float = 1.0

    def tag(self):
        return str(self.values)


@dataclass
class FaultSystemLogicTree:
    short_name: str
    long_name: str
    branches: List['Branch'] = field(default_factory=list)

    def derive_spec(self) -> 'FaultSystemLogicTreeSpec':
        raise NotImplementedError()


@dataclass
class FaultSystemLogicTreeSpec:
    short_name: str
    long_name: str
    branches: List['BranchAttributeValue'] = field(default_factory=list)


@dataclass
class SourceLogicTreeSpec:
    fault_systems: List[FaultSystemLogicTreeSpec] = field(default_factory=list)


@dataclass
class SourceLogicTree:
    logic_tree_version: Union[int, None]
    version: str
    title: str
    fault_systems: List[FaultSystemLogicTree] = field(default_factory=list)
    # correlations: List[SourceLogicTreeCorrelation] = field(
    #     default_factory=list
    # )  # to use for selecting branches and re-weighting when logic trees are correlated

    def derive_spec(self) -> SourceLogicTreeSpec:
        raise NotImplementedError()
        # slt_spec = SourceLogicTreeSpec()
        # for fslt in self.fault_systems:
        #     slt_spec.fault_systems.append(FaultSystemLogicTree.derive_spec(fslt))
        # return slt_spec

    @staticmethod
    def from_dict(data: Dict):
        ltv = data.get("logic_tree_version")
        if not ltv == 2:
            raise ValueError(f"supplied json `logic_tree_version={ltv}` is not supported.")
        return dacite.from_dict(data_class=SourceLogicTree, data=data, config=dacite.Config(strict=True))

    @staticmethod
    def from_json(json_path: Union[pathlib.Path, str]):
        data = json.load(open(json_path))
        return SourceLogicTree.from_dict(data)

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs):
        return provider(self)
