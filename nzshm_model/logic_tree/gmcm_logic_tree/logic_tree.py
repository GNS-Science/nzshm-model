"""
Defines ground motion characterisation model logic tree structures used in NSHM.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Type

from nzshm_model.logic_tree.logic_tree_base import Branch, BranchSet, FilteredBranch, LogicTree
from nzshm_model.psha_adapter import PshaAdapterInterface


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

    def filtered_branch(self, logic_tree, branch_set) -> 'GMCMFilteredBranch':
        """get a filtered branch containing reference to parent instances.

        Arguments:
            logic_tree: the gmcm logic tree containing the branch
            branch_set: the branch set containing the branch

        Returns:
            a BMCMFilteredBranch instance
        """
        return GMCMFilteredBranch(logic_tree=logic_tree, branch_set=branch_set, **self.__dict__)


@dataclass
class GMCMBranchSet(BranchSet):
    """A list of GMCM branches that apply to a particular tectonic region.

    Attributes:
        tectonic_region_type: the tectonic region type TRT that the branch set applies to.
        branches: list of branches.
    """

    tectonic_region_type: str = ""  # need a default becasue base class has a memeber with a default
    branches: List[GMCMBranch] = field(default_factory=list)


@dataclass
class GMCMLogicTree(LogicTree):
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

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs) -> "PshaAdapterInterface":
        """get a PSHA adapter for this instance.

        Arguments:
            provider: the adapter class
            **kwargs: additional arguments required by the provider class

        Returns:
            a PSHA Adapter instance
        """
        return provider(gmcm_logic_tree=self)

    # @classmethod
    # def from_user_config(cls, config_path: Union[Path, str]) -> 'GMCMLogicTree':
    #     raise NotImplementedError("from_user_config not implimented for GMCMLogicTree")


@dataclass
class GMCMFilteredBranch(FilteredBranch, GMCMBranch):
    logic_tree: 'GMCMLogicTree' = field(default_factory=GMCMLogicTree)
    branch_set: 'GMCMBranchSet' = field(default_factory=GMCMBranchSet)
