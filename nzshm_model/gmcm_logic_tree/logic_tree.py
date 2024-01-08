import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Type, Iterator

from nzshm_model.psha_adapter import PshaAdapterInterface
from nzshm_model.logic_tree_base import (
    LogicTree,
    Branch,
    BranchSet,
    FilteredBranch,
)


@dataclass
class GMCMBranch(Branch):
    gsim_name: str = ""
    gsim_args: Dict[str, Any] = field(default_factory=dict)


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

    def __flattened_branches__(self):
        """
        Produce list of Flattened branches, each with a shallow copy of it's slt and fslt parents
        for use in filtering.

        NB this class is never used for serialising models.
        """
        for branch_set in self.branch_sets:
            for branch in branch_set.branches:
                # we give bs_light a list of branches so that the derived type can be identified and used by the base class
                bs_lite = GMCMBranchSet(tectonic_region_type=branch_set.tectonic_region_type, branches=[GMCMBranch(weight=1.0)])
                lt_lite = GMCMLogicTree(title=self.title, version=self.version)
                yield GMCMFilteredBranch(
                    weight=branch.weight,
                    gsim_name=branch.gsim_name,
                    gsim_args=copy.deepcopy(branch.gsim_args),
                    branch_set=bs_lite,
                    logic_tree=lt_lite,
                )

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs):
        return provider(gmcm_logic_tree=self)

    @staticmethod
    def from_branches(branches: Iterator['GMCMFilteredBranch']) -> 'GMCMLogicTree':
        """
        Build a complete GMCMLogicTree from a iterable od branches.

        We expect that all the branhches have come from a single logic tree.
        """

        def match_branch_set(lt: GMCMLogicTree, fbranch):
            for branch_set in lt.branch_sets:
                if fbranch.branch_set.tectonic_region_type == branch_set.tectonic_region_type:
                    return branch_set

        version = None
        for fb in branches:
            # ensure an slt
            if version is None:
                gmcm_lt = GMCMLogicTree(version=fb.logic_tree.version, title=fb.logic_tree.title)
                version = fb.logic_tree.version
            else:
                assert version == fb.logic_tree.version

            # ensure an fslt
            bs = match_branch_set(gmcm_lt, fb)
            if not bs:
                bs = GMCMBranchSet(tectonic_region_type=fb.branch_set.tectonic_region_type)
                gmcm_lt.branch_sets.append(bs)
            bs.branches.append(fb.to_branch())
        return gmcm_lt


@dataclass
class GMCMFilteredBranch(FilteredBranch, GMCMBranch):
    branch_set: GMCMBranchSet = GMCMBranchSet()
    logic_tree: GMCMLogicTree = GMCMLogicTree()
