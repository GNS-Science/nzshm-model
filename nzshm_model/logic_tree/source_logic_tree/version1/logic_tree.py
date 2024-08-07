#! logic_tree.py

"""
Define source logic tree structures used in NSHM.
"""
import json
import pathlib
from copy import deepcopy
from dataclasses import dataclass, field
from functools import reduce
from itertools import product
from math import isclose
from operator import add, mul
from typing import Dict, Iterable, List, Union

import dacite

from .. import BranchAttributeValue
from ..fault_system_branch_set import BranchSetBase, BranchSetSpec


@dataclass
class Branch:
    values: List[BranchAttributeValue]
    weight: float = 1.0
    onfault_nrml_id: Union[str, None] = ""
    distributed_nrml_id: Union[str, None] = ""
    inversion_solution_id: Union[str, None] = ""
    inversion_solution_type: Union[str, None] = ""
    rupture_set_id: Union[str, None] = ""


@dataclass
class FaultSystemLogicTree(BranchSetBase):
    branches: List[Branch] = field(default_factory=list)


@dataclass
class SourceLogicTreeCorrelation:
    primary_short_name: str
    secondary_short_name: str
    primary_values: List[BranchAttributeValue]
    secondary_values: List[BranchAttributeValue]

    # these methods enforce set compairson
    def is_primary(self, bavs: Iterable[BranchAttributeValue]) -> bool:
        return all([item in self.primary_values for item in bavs])

    def is_secondary(self, bavs: Iterable[BranchAttributeValue]) -> bool:
        return all([item in self.secondary_values for item in bavs])


@dataclass
class SourceLogicTreeSpec:
    fault_system_lts: List[BranchSetSpec] = field(default_factory=list)


@dataclass
class SourceLogicTree:
    version: str
    title: str
    fault_system_lts: List[FaultSystemLogicTree] = field(default_factory=list)
    correlations: List[SourceLogicTreeCorrelation] = field(
        default_factory=list
    )  # to use for selecting branches and re-weighting when logic trees are correlated

    @property
    def fault_systems(self):
        return self.fault_system_lts

    def derive_spec(self) -> SourceLogicTreeSpec:
        slt_spec = SourceLogicTreeSpec()
        for fslt in self.fault_system_lts:
            slt_spec.fault_system_lts.append(FaultSystemLogicTree.derive_spec(fslt))
        return slt_spec

    @staticmethod
    def from_dict(data: Dict):
        ltv = data.get("logic_tree_version")
        if ltv:
            raise ValueError(f"supplied json `logic_tree_version={ltv}` is not supported.")
        return dacite.from_dict(data_class=SourceLogicTree, data=data, config=dacite.Config(strict=True))

    @staticmethod
    def from_json(json_path: Union[pathlib.Path, str]):
        data = json.load(open(json_path))
        return SourceLogicTree.from_dict(data)


@dataclass
class CompositeBranch:
    """Combination of all fault type branches"""

    branches: List[Branch]
    weight: float = 1.0

    def __post_init__(self) -> None:
        self.weight = reduce(mul, [branch.weight for branch in self.branches])


@dataclass
class FlattenedSourceLogicTree:
    """Flattened source logic tree containing all CompositeBranch combinations"""

    version: str
    title: str
    branches: List[CompositeBranch]

    def __post_init__(self) -> None:
        total_weight = reduce(add, [branch.weight for branch in self.branches])
        if not isclose(total_weight, 1.0):
            raise Exception('logic tree weights do not add to 1.0 (sum is %s)' % total_weight)

    @classmethod
    def from_source_logic_tree(cls, slt: SourceLogicTree):

        slt_copy = deepcopy(slt)  # don't want to change weights of origional logic tree object
        branches = [fslt.branches for fslt in slt_copy.fault_system_lts]

        def yield_cor(branches, slt_copy):
            nnames = [[faultsys_lt.short_name] * len(faultsys_lt.branches) for faultsys_lt in slt_copy.fault_system_lts]
            for cb, names in zip(product(*branches), product(*nnames)):
                has_correlation = False
                for cor in slt_copy.correlations:
                    sindex = names.index(cor.secondary_short_name)
                    if cor.is_secondary(cb[sindex].values):
                        has_correlation = True
                        pindex = names.index(cor.primary_short_name)
                        if cor.is_primary(cb[pindex].values):
                            cb[sindex].weight = 1.0
                            yield CompositeBranch(list(cb))
                if not has_correlation:
                    yield CompositeBranch(list(cb))

        if slt.correlations:
            return cls(slt.version, slt.title, list(yield_cor(branches, slt_copy)))
        else:
            return cls(slt.version, slt.title, [CompositeBranch(list(cb)) for cb in product(*branches)])

    def __repr__(self):
        return f'{self.__class__} title {self.title} number of branches: {len(self.branches)}'
