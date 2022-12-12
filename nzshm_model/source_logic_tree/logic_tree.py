#! logic_tree.py

"""
Classes to define logic tree structures
"""

from dataclasses import dataclass, field
from typing import Any, List, Union


@dataclass
class BranchAttribute:
    name: str
    long_name: str
    value_options: List[Any] = field(default_factory=list)


@dataclass
class BranchAttributeValue(BranchAttribute):
    value: Any = None

    @staticmethod
    def from_branch_attribute(ba: BranchAttribute, value):
        return BranchAttributeValue(ba.name, ba.long_name, ba.value_options, value)

    @staticmethod
    def all_from_branch_attribute(ba: BranchAttribute):
        for opt in ba.value_options:
            yield BranchAttributeValue(ba.name, ba.long_name, ba.value_options, opt)

    def __repr__(self):
        return f"{self.name}{self.value}"


@dataclass
class Branch:
    values: List[BranchAttributeValue]
    weight: float = 1.0
    inversion_nrml_id: Union[str, None] = ""
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
