#! logic_tree_version_2.py

"""
Define source logic tree structures used in NSHM.
"""
import copy
import json
import pathlib
import warnings
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Type, Union, Optional

import dacite

from nzshm_model.psha_adapter import PshaAdapterInterface

from nzshm_model.logic_tree_base import (
    LogicTree,
    Branch,
    BranchSet,
    FilteredBranch,
)

from .. import BranchAttributeValue
from ..core import FaultSystemLogicTreeBase, FaultSystemLogicTreeSpec
from ..version1 import SourceLogicTree as SourceLogicTreeV1


@dataclass
class InversionSource:
    nrml_id: str
    rupture_rate_scaling: Union[float, None] = None  # TODO: needed at this level??
    inversion_id: Union[str, None] = ""
    rupture_set_id: Union[str, None] = ""
    inversion_solution_type: Union[str, None] = ""
    type: str = "inversion"


@dataclass
class DistributedSource:
    nrml_id: str
    rupture_rate_scaling: Union[float, None] = None  # TODO: needed at this level??
    type: str = "distributed"


@dataclass
class SourceBranch(Branch):
    values: List[BranchAttributeValue] = field(default_factory=list)
    sources: List[Union[DistributedSource, InversionSource]] = field(default_factory=list)
    rupture_rate_scaling: float = 1.0

    def filtered_branch(self, logic_tree, branch_set):
        return SourceFilteredBranch(logic_tree=logic_tree, branch_set=branch_set, **self.__dict__)

    def tag(self):
        return str(self.values)


@dataclass
class SourceBranchSet(BranchSet):
    branches: List[SourceBranch] = field(default_factory=list)


@dataclass
class SourceLogicTreeSpec:
    fault_systems: List[FaultSystemLogicTreeSpec] = field(default_factory=list)


# this should never be serialised, only used for filtering
@dataclass
class SourceFilteredBranch(FilteredBranch, SourceBranch):
    logic_tree: Optional['SourceLogicTree'] = None
    branch_set: Optional['SourceBranchSet'] = None

@dataclass
class SourceLogicTree(LogicTree):
    branch_sets: List[SourceBranchSet] = field(default_factory=list)
    filtered_branch_type = SourceFilteredBranch
    logic_tree_version: Union[int, None] = 2

    # correlations: List[SourceLogicTreeCorrelation] = field(
    #     default_factory=list
    # )  # to use for selecting branches and re-weighting when logic trees are correlated

    def derive_spec(self) -> SourceLogicTreeSpec:
        raise NotImplementedError()
        # slt_spec = SourceLogicTreeSpec()
        # for fslt in self.fault_systems:
        #     slt_spec.fault_systems.append(FaultSystemLogicTree.derive_spec(fslt))
        # return slt_spec

    @classmethod
    def from_dict(cls, data: Dict):
        ltv = data.get("logic_tree_version")
        if not ltv == 2:
            raise ValueError(f"supplied json `logic_tree_version={ltv}` is not supported.")
        return super(SourceLogicTree, cls).from_dict(data)

    @staticmethod
    def from_source_logic_tree(original_slt: "SourceLogicTreeV1") -> "SourceLogicTree":
        """
        Migrate from old version slt.
        """
        if not isinstance(original_slt, SourceLogicTreeV1):
            raise ValueError(f"supplied object of {type(original_slt)} is not supported.")
        slt = SourceLogicTree(version=original_slt.version, title=original_slt.title)
        for fslt in original_slt.fault_systems:
            new_fslt = SourceBranchSet(short_name=fslt.short_name, long_name=fslt.long_name)
            for branch in fslt.branches:
                # TODO: handle rate scaling
                new_branch = SourceBranch(values=copy.deepcopy(branch.values), weight=branch.weight)
                if branch.onfault_nrml_id:
                    new_branch.sources.append(
                        InversionSource(
                            nrml_id=branch.onfault_nrml_id,
                            inversion_id=branch.inversion_solution_id,
                            rupture_set_id=branch.rupture_set_id,
                        )
                    )
                if branch.distributed_nrml_id:
                    new_branch.sources.append(DistributedSource(nrml_id=branch.distributed_nrml_id))
                new_fslt.branches.append(new_branch)
            slt.branch_sets.append(new_fslt)
        return slt

    @property
    def fault_system_lts(self):
        """
        API alias for branch_sets
        """
        warnings.warn("Please use branch_sets property instead", DeprecationWarning)
        return self.branch_sets

    @property
    def fault_systems(self):
        """
        API alias for branch_sets
        """
        warnings.warn("Please use branch_sets property instead", DeprecationWarning)
        return self.branch_sets

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs):
        return provider(source_logic_tree=self)
