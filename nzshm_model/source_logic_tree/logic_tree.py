#! logic_tree.py

"""
Classes to define logic tree structures
"""

from dataclasses import dataclass, field
from typing import Any, List, Union


@dataclass
class BranchAttributeSpec:
    name: str
    long_name: str
    value_options: List[Any] = field(default_factory=list)


@dataclass
class BranchAttributeValue:
    name: str
    long_name: str
    value: Any = None

    @staticmethod
    def from_branch_attribute(ba: BranchAttributeSpec, value):
        return BranchAttributeValue(ba.name, ba.long_name, value)

    @staticmethod
    def all_from_branch_attribute(ba: BranchAttributeSpec):
        for opt in ba.value_options:
            yield BranchAttributeValue(ba.name, ba.long_name, opt)

    def __repr__(self):
        return f"{self.name}{self.value}"


@dataclass
class Branch:
    values: List[BranchAttributeValue]
    weight: float = 1.0
    onfault_nrml_id: Union[str, None] = ""
    distributed_nrml_id: Union[str, None] = ""
    inversion_solution_id: Union[str, None] = ""
    inversion_solution_type: Union[str, None] = ""


@dataclass
class FaultSystemLogicTree:
    short_name: str
    long_name: str
    branches: List['Branch'] = field(default_factory=list)

    def validate_weights(self) -> bool:
        weight = 0.0
        for b in self.branches:
            weight += b.weight
        return weight == 1.0


class SourceLogicTreeCorrelation:
    """
    List[SourceLogicTreeBranch]: branch_sets
    """

    pass


@dataclass
class SourceLogicTree:
    version: str
    title: str
    fault_system_branches: List[FaultSystemLogicTree] = field(default_factory=list)
    correlations: List[SourceLogicTreeCorrelation] = field(
        default_factory=list
    )  # to use for weighting when logic trees are correlated
