"""
Defines ground motion characterisation model logic tree structures used in NSHM.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from nzshm_model.logic_tree.logic_tree_base import Branch, BranchSet, FilteredBranch, LogicTree


@dataclass
class GMCMBranch(Branch):
    """
    A branch of the GMCM logic tree

    Identifies the ground motion model (gsim) and any arguments


    Attributes:
        gsim_name: the name of the ground motion model
        gsim_args: a dict of argument names and values
    """

    gsim_name: str = ""
    gsim_args: Dict[str, Any] = field(default_factory=dict)
    tectonic_region_type: str = ""  # need a default becasue base class has a memeber with a default

    def filtered_branch(self, logic_tree, branch_set) -> 'GMCMFilteredBranch':
        """get a filtered branch containing reference to parent instances.

        Arguments:
            logic_tree: the gmcm logic tree containing the branch
            branch_set: the branch set containing the branch

        Returns:
            a BMCMFilteredBranch instance
        """
        return GMCMFilteredBranch(logic_tree=logic_tree, branch_set=branch_set, **self.__dict__)

    @property
    def registry_identity(self):
        arg_vals = []
        for k, v in self.gsim_args.items():
            arg_vals.append(f"{k}={v}")
        return f"{self.gsim_name}({', '.join(arg_vals)})"


# TODO: protect from users changing TRT
@dataclass
class GMCMBranchSet(BranchSet[GMCMBranch]):
    """A list of GMCM branches that apply to a particular tectonic region.

    Attributes:
        tectonic_region_type: the tectonic region type TRT that the branch set applies to.
        branches: list of branches.
    """

    branches: List[GMCMBranch] = field(default_factory=list)

    def __post_init__(self):
        trts = {branch.tectonic_region_type for branch in self.branches}
        if len(trts) > 1:
            raise ValueError("all tectonic_region_types in a branch set must be the same")

    @property
    def tectonic_region_type(self) -> str:
        return self.branches[0].tectonic_region_type if self.branches else ""


@dataclass
class GMCMLogicTree(LogicTree['GMCMFilteredBranch']):
    """A dataclass representing the ground motion characterisation model logic tree.

    Attributes:
        branch_sets: list of GMCM branch sets that comprise the logic tree.
    """

    # should we enforce that there is only one branch_set per TRT?
    branch_sets: List[GMCMBranchSet] = field(default_factory=list)

    def __post_init__(self):
        self._fix_args()

    def _fix_args(self) -> 'GMCMLogicTree':
        """Replace string representations of numeric arguments with floats"""

        def is_number(value):
            return value.replace("-", "").replace(".", "").replace("e", "").isnumeric()

        for branch_set in self.branch_sets:
            for branch in branch_set.branches:
                for k, v in branch.gsim_args.items():
                    if (isinstance(v, str)) and (is_number(v)):
                        branch.gsim_args[k] = float(v)

        return self


@dataclass
class GMCMFilteredBranch(FilteredBranch, GMCMBranch):
    logic_tree: 'GMCMLogicTree' = field(default_factory=GMCMLogicTree)
    branch_set: 'GMCMBranchSet' = field(default_factory=GMCMBranchSet)
