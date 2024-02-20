from dataclasses import dataclass, field
from typing import Any, Dict, List, Type

from nzshm_model.logic_tree.logic_tree_base import Branch, BranchSet, FilteredBranch, LogicTree
from nzshm_model.psha_adapter import PshaAdapterInterface


@dataclass
class GMCMBranch(Branch):
    gsim_name: str = ""
    gsim_args: Dict[str, Any] = field(default_factory=dict)

    def filtered_branch(self, logic_tree, branch_set):
        return GMCMFilteredBranch(logic_tree=logic_tree, branch_set=branch_set, **self.__dict__)


@dataclass
class GMCMBranchSet(BranchSet):
    tectonic_region_type: str = ""  # need a default becasue base class has a memeber with a default
    branches: List[GMCMBranch] = field(default_factory=list)


@dataclass
class GMCMLogicTree(LogicTree):
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

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs):
        return provider(gmcm_logic_tree=self)


@dataclass
class GMCMFilteredBranch(FilteredBranch, GMCMBranch):
    logic_tree: 'GMCMLogicTree' = field(default_factory=GMCMLogicTree)
    branch_set: 'GMCMBranchSet' = field(default_factory=GMCMBranchSet)
