"""
This module contains base classes (some of which are abstract) common to both **Source** and
**Ground Motion Model (GMM)** logic trees.
"""
import copy
import json
import math
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field, fields
from functools import reduce
from itertools import product
from operator import mul
from pathlib import Path
from typing import Any, Dict, Generator, Iterator, List, Type, Union

import dacite

from nzshm_model.psha_adapter import PshaAdapterInterface

from .branch import Branch, CompositeBranch
from .correlation import LogicTreeCorrelations

# TODO:
# - move values to the base class?
# - move logic for creating light branchSet and LogicTree when creating FilteredBranchs to
#    the initializer of FilteredBranch?
# - FilteredBranch doesn't need to be a data class as it should not be serialized and doesn't contain many arguments
# - should we use FilteredBranch for correlation so the branches can be traced back to the BranchSet?


@dataclass
class BranchSet:
    """
    A group of branches that comprise their own sub-logic tree. Also known as a fault system logic
    tree (for source logic trees).

    Arguments:
        short_name:
        long_name:
        branches: the branches that make up the branch set
    """

    short_name: str = ''
    long_name: str = ''
    branches: Sequence[Any] = field(default_factory=list)

    def __post_init__(self):
        if not self._validate_weights():
            raise ValueError("weights of BranchSet must sum to 1.0")

    def _validate_weights(self) -> bool:
        """
        verify that weighs sum to 1.0
        """
        weight = 0.0
        if not self.branches:  # empty BranchSet
            return True
        for b in self.branches:
            weight += b.weight
        return math.isclose(weight, 1.0)


@dataclass
class LogicTree(ABC):
    """
    Logic tree baseclass. Contains information about branch sets and correlations between branches of the branch sets.

    The correlations are enforced when forming composite branches (combinations of branches from different branch sets).

    Arguments:
        title: title of the logic tree
        version: version string
        branch_sets: list of branch sets that make up the logic tree
        correlations: any correlations between branches of the branch_sets

    """

    title: str = ''
    version: str = ''
    branch_sets: List[Any] = field(default_factory=list)
    correlations: LogicTreeCorrelations = field(default_factory=LogicTreeCorrelations)

    def __post_init__(self) -> None:
        self._validate_correlations()

    def __setattr__(self, __name: str, __value: Any) -> None:
        super().__setattr__(__name, __value)
        if __name == "correlations":
            self._validate_correlations()

    def _validate_correlations(self) -> None:
        # check that the weights total 1.0
        weight_total = 0.0
        for branch in self.combined_branches:
            weight_total += branch.weight
        if not math.isclose(weight_total, 1.0):
            raise ValueError("the weights of the logic tree do not sum to 1.0 when correlations are applied")

    def _combined_branches(self) -> Generator[CompositeBranch, None, None]:
        """
        yields all composite (combined) branches of the branch_sets without applying correlations.
        """
        for branches in product(*[branch_set.branches for branch_set in self.branch_sets]):
            yield CompositeBranch(branches=branches)

    @property
    def combined_branches(self) -> Generator[CompositeBranch, None, None]:
        """
        yields all composite (combined) branches of the branch_sets enforcing correlations
        """
        for combined_branch in self._combined_branches():
            # if the comp_branch contains a branch listed as the 0th element of the correlations, only
            # yeild if the other branches are present
            # weight is automatically calculated by CompositeBranch if not explicitly assigned
            # (as we would with correlations)
            correlation_match = [branch_pri in combined_branch for branch_pri in self.correlations.primary_branches()]
            if any(correlation_match):
                i_cor = correlation_match.index(
                    True
                )  # index of the correlation that matches a branch in _combined_branches()
                if not all(br in combined_branch for br in self.correlations[i_cor].all_branches):
                    continue
                weights = [self.correlations[i_cor].weight] + [
                    branch.weight for branch in combined_branch if branch not in self.correlations[i_cor].all_branches
                ]
                combined_branch.weight = reduce(mul, weights, 1.0)
            yield combined_branch

    @classmethod
    def from_json(cls, json_path: Union[Path, str]) -> 'LogicTree':
        """
        Create LogicTree object from json file or string

        Parameters:
            json_path: path to json file

        Returns:
            logic_tree
        """
        with Path(json_path).open() as jsonfile:
            data = json.load(jsonfile)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict) -> 'LogicTree':
        """
        Create LogicTree object from dict

        Parameters:
            data: dict representation of LogicTree object

        Returns:
            logic_tree
        """
        return dacite.from_dict(data_class=cls, data=data, config=dacite.Config(strict=True))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    # would like this to actully do the work, but not sure how to pass the logic trees wihtout knowning the type.
    # Could check for type in PshaAdaptorInterface, but then we have a circular import.
    @abstractmethod
    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs):
        """
        Provide an adapter object for translating LogicTrees to/from specific formats

        Parameters:
            provider: the interface object that defines a specific implimenation
            **kwargs:

        Returns:
            An adapter object
        """
        pass

    def __all_branches__(self) -> Generator['FilteredBranch', None, None]:
        """
        Yield all branches from all BranchSets, each with a shallow copy of its LogicTree and BranchSet parents
        for use in filtering.

        NB this class is never used for serialising models.
        """

        def get_fields(obj):
            return {
                field.name: copy.deepcopy(getattr(obj, field.name))
                for field in fields(obj)
                if field.name not in ('branches', 'branch_sets')
            }

        lt_fields = get_fields(self)
        for branch_set in self.branch_sets:
            bs_fields = get_fields(branch_set)
            for branch in branch_set.branches:
                bs_lite = type(branch_set)(**bs_fields, branches=[type(branch)()])
                lt_lite = type(self)(**lt_fields)
                # b_fields = get_fields(branch)
                yield branch.filtered_branch(
                    branch_set=bs_lite,
                    logic_tree=lt_lite,
                )

    @classmethod
    def from_branches(cls, branches: Iterator['FilteredBranch']) -> 'LogicTree':
        """
        Build a complete LogicTree from a iterable of branches.

        We expect that all the branches have come from a single LogicTree.

        Parameters:
            branches: the branches used to build the LogicTree
        """

        def match_branch_set(slt: LogicTree, fb):
            for branch_set in slt.branch_sets:
                if fb.branch_set.short_name == branch_set.short_name:
                    return branch_set

        version = None
        for fb in branches:
            # ensure an slt
            if version is None:
                logic_tree = cls(version=fb.logic_tree.version, title=fb.logic_tree.title)
                version = fb.logic_tree.version
            else:
                assert version == fb.logic_tree.version

            # ensure an branch_set
            bs = match_branch_set(logic_tree, fb)
            if not bs:
                bs = type(fb.branch_set)(short_name=fb.branch_set.short_name, long_name=fb.branch_set.long_name)
                logic_tree.branch_sets.append(bs)
            bs.branches.append(fb.to_branch())
        return logic_tree

    def __iter__(self):
        self.__current_branch = 0
        self.__branch_list = list(self.__all_branches__())
        return self

    def __next__(self):
        if self.__current_branch >= len(self.__branch_list):
            raise StopIteration
        else:
            self.__current_branch += 1
            return self.__branch_list[self.__current_branch - 1]


@dataclass
class FilteredBranch(Branch):
    """
    A branch type that points back to it's logic tree and branch set. Should never be serialized, only
    used for filtering
    """

    logic_tree: LogicTree = field(default_factory=LogicTree)
    branch_set: BranchSet = field(default_factory=BranchSet)

    def to_branch(self) -> Branch:
        """
        Produce the Branch object (does not point back to it's logic tree and branch set)

        Returns:
            branch: the Branch object
        """
        branch_attributes = {k: v for k, v in self.__dict__.items() if k not in ('branch_set', 'logic_tree')}
        return type(self.branch_set.branches[0])(**branch_attributes)
