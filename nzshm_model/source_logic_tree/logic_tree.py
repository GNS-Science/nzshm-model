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
    value_options: Union[List[int], List[str], List[bool], List[Tuple[float, float]]]


@dataclass
class BranchAttributeValue(BranchAttribute):
    value: Union[int, str, bool, Tuple[float, float]]

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
    """
    Branch is a graph 'edge` connecting two nodes)
    """

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


class SourceLogicTreeLeaf:
    """
    str: fault_system hikurangi/hik, puysegur/puy, crustal/cru, itraslab/slab
    tuple: b_n_pair
    float: c (area-magnitude scaling)
    float: s (moment rate scaling)
    str deformation_model: hik locked, geodetic, geologic
    bool: time_dependence
    float: weight
    str: nrml_id_inv
    str: nrml_id_bg
    """
