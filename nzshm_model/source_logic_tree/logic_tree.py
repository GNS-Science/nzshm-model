#! logic_tree.py

"""
Classes to define logic tree structures
"""

from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class Branch:
    """
    Branch is a graph 'edge` connecting two nodes)
    """

    value: Union[int, float, bool, str]  # value of the Branch
    weight: float  # weight of the branch
    branch_level: Union[None, 'BranchLevel'] = field(default=None)
    # leaf: Union[None, 'LogicTreeLeaf'] = field(init=False, default=None)

    def __post_init__(self):
        if self.branch_level:
            self.branch_level.branches.append(self)


@dataclass
class BranchLevel:
    """
    BranchLevel is contains common LTB attributes and a list of the Branches
    """

    name: str
    long_name: str
    branches: List['Branch'] = field(init=False, default_factory=list)


# @dataclass
# class LogicTreeLeaf:
#     """
#     Leaf connects a Branch to external representations
#     """

#     branch: Union[None, 'Branch'] = None
#     inversion_source: str = ""
#     distributed_source: str = ""

#     @property
#     def name(self) -> str:
#         if self.branch and self.branch.branch_level:
#             return self.branch.branch_level.name
#         return ""


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


class SourceLogicTreeCorrelation:
    """
    List[SourceLogicTreeBranch]: branch_sets
    """


class FaultSystemLogicTree:
    """
    List[BranchLevel]: branch_levels
    """


class SourceLogicTree:
    """
    List[SourceLogicTreeCorrelation]: correlations
    List[FaultSystemLogicTree]:
    str: weight_master (SourceLogicTreeBranch.fault_system to use for weighting when logic trees are correlated)
    """
