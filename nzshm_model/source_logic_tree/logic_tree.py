#! logic_tree.py

"""
Classes to define logic tree structures
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Union


@dataclass
class BranchAttribute:
    name: str
    long_name: str
    value_options: Union[List[int], List[str], List[bool], List[Tuple[float, float]]] = field(default_factory=list)


@dataclass
class BranchAttributeValue(BranchAttribute):
    value: Union[int, str, bool, Tuple[float, float]] = None

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
    inversion_source: str = ""
    distributed_source: str = ""


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


