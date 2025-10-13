"""
This module contains base classes (some of which are abstract) common to both **Source** and
**Ground Motion Model (GMM)** logic trees.
"""

import copy
import json
from abc import ABC
from dataclasses import asdict, dataclass, field, fields
from functools import reduce
from itertools import product
from operator import mul
from pathlib import Path
from typing import Any, Dict, Generator, Generic, Iterator, List, Optional, Type, TypeVar, Union

import dacite

import nzshm_model.logic_tree.helpers as helpers
from nzshm_model.psha_adapter import PshaAdapterInterface

from .branch import Branch, BranchType, CompositeBranch
from .correlation import LogicTreeCorrelations

# TODO:
# - move values to the base class?
# - move logic for creating light branchSet and LogicTree when creating FilteredBranchs to
#    the initializer of FilteredBranch?
# - FilteredBranch doesn't need to be a data class as it should not be serialized and doesn't contain many arguments
# - should we use FilteredBranch for correlation so the branches can be traced back to the BranchSet?

# https://github.com/python/mypy/issues/8495
# This can be done more simply with typing.Self in python3.11+
LogicTreeType = TypeVar("LogicTreeType", bound="LogicTree")
BranchSetType = TypeVar("BranchSetType", bound="BranchSet")
FilteredBranchType = TypeVar("FilteredBranchType", bound="FilteredBranch")


@dataclass
class BranchSet(Generic[BranchType]):
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
    branches: List[BranchType] = field(default_factory=list)

    def __post_init__(self):
        helpers._validate_branchset_weights(self)

    def __str__(self) -> str:
        string = f'short_name: {self.short_name}, long_name: {self.long_name}\n'
        string += '======BRANCHES======\n'
        return string + '\n'.join([str(branch) for branch in self])

    def __iter__(self: BranchSetType) -> BranchSetType:
        self.__counter = 0
        return self

    def __next__(self) -> BranchType:
        if self.__counter >= len(self.branches):
            raise StopIteration
        else:
            self.__counter += 1
            return self.branches[self.__counter - 1]


@dataclass
class LogicTree(ABC, Generic[FilteredBranchType]):
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
        # TODO: branch set short_names should be unique (see from_branches())
        helpers._validate_correlation_weights(self)

    def __setattr__(self, __name: str, __value: Any) -> None:
        super().__setattr__(__name, __value)
        if __name == "correlations":
            helpers._validate_correlation_weights(self)

    def __str__(self) -> str:
        string = f'LogicTree type: {type(self)}\n'
        string += f'title: {self.title}, version:{self.version}\n'
        string += '==========BRANCH SETS==========\n\n'
        string += '\n\n'.join([str(bs) for bs in self.branch_sets])
        return string

    def _composite_branches(self) -> Generator[CompositeBranch, None, None]:
        """
        Yields all composite (combined) branches of the branch_sets without applying correlations.

        Returns:
            composite_branches: the CompositeBranches of the combined logic tree BranchSets
        """
        for branches in product(*[branch_set.branches for branch_set in self.branch_sets]):
            yield CompositeBranch(branches=branches)

    @property
    def composite_branches(self) -> Generator[CompositeBranch, None, None]:
        """
        Yields all composite (combined) branches of the branch_sets enforcing correlations.

        Returns:
            composite_branches: the CompositeBranches of the combined logic tree BranchSets
        """
        for composite_branch in self._composite_branches():
            # if the comp_branch contains a branch listed as the 0th element of the correlations, only
            # yeild if the other branches are present
            # weight is automatically calculated by CompositeBranch if not explicitly assigned
            # (as we would with correlations)
            correlation_match = [branch_pri in composite_branch for branch_pri in self.correlations.primary_branches()]
            if any(correlation_match):
                # index of the correlation that matches a branch in _composite_branches()
                i_cor = correlation_match.index(True)
                if not all(br in composite_branch for br in self.correlations[i_cor].all_branches):
                    continue
                weights = [self.correlations[i_cor].weight] + [
                    branch.weight for branch in composite_branch if branch not in self.correlations[i_cor].all_branches
                ]
                composite_branch.weight = reduce(mul, weights, 1.0)
            yield composite_branch

    @classmethod
    def from_json(cls: Type[LogicTreeType], json_path: Union[Path, str]) -> LogicTreeType:
        """
        Create LogicTree object from json file

        See docs/api/logic_tree/source_logic_tree_config_format.md and
        api/logic_tree/gmcm_logic_tree_config_format.md

        Parameters:
            json_path: path to json file

        Returns:
            logic_tree
        """
        with Path(json_path).open() as jsonfile:
            data = json.load(jsonfile)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls: Type[LogicTreeType], data: Dict) -> LogicTreeType:
        """
        Create LogicTree object from dict.

        See docs/api/logic_tree/source_logic_tree_config_format.md and
        api/logic_tree/gmcm_logic_tree_config_format.md

        Parameters:
            data: dict representation of LogicTree object

        Returns:
            logic_tree
        """
        if not data.get('correlations'):
            logic_tree = cls._from_dict(data)
            # do not need to validate names as that is only necessary if there are correlations
            return logic_tree

        correlations = data.pop('correlations')
        helpers._validate_correlations_format(correlations)
        logic_tree = cls._from_dict(data)
        helpers._validate_names(logic_tree)
        logic_tree = helpers._add_corellations(logic_tree, correlations)

        return logic_tree

    @classmethod
    def _from_dict(cls: Type[LogicTreeType], data: Dict) -> LogicTreeType:
        """
        Create LogicTree object from dict. Input dict must be a direct asdict() serialisation of the LogicTree object

        Parameters:
            data: dict representation of LogicTree object

        Returns:
            logic_tree
        """

        config = dacite.Config(strict=True, cast=[tuple])
        return dacite.from_dict(data_class=cls, data=data, config=config)

    def _to_dict(self) -> Dict[str, Any]:
        """
        Create dict representation of logic tree. This creates an exact dict of the class and is not
        used for serialisation.

        Returns:
            dict:
        """
        return asdict(self)

    def to_dict(self) -> Dict[str, Any]:
        """Create dictionary representation of logic tree used for serialisation.

        Returns:
            logic_tree_dict: dictionary representaion of logic tree
        """

        # do not need to validate names as that is only necessary if there are correlations
        data = self._to_dict()
        if not self.correlations:
            del data["correlations"]
            return data

        helpers._validate_names(self)
        data["correlations"] = helpers._serialise_correlations(self)
        return data

    def to_json(self, file_path: Union[Path, str]) -> None:
        """Serialze logic tree as json file.

        Parameters:
            file_path: path to json file to be written
        """
        file_path = Path(file_path)
        with file_path.open('w') as jsonfile:
            json.dump(self.to_dict(), jsonfile, indent=2)

    def __all_branches__(self) -> Generator[FilteredBranchType, None, None]:
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
    def from_branches(cls, branches: Iterator[FilteredBranchType]) -> 'LogicTree':
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

    def __next__(self) -> FilteredBranchType:
        if self.__current_branch >= len(self.__branch_list):
            raise StopIteration
        else:
            self.__current_branch += 1
            return self.__branch_list[self.__current_branch - 1]

    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs: Optional[Dict]) -> "PshaAdapterInterface":
        """get a PSHA adapter for this instance.

        Arguments:
            provider: the adapter class
            **kwargs: additional arguments required by the provider class

        Returns:
            a PSHA Adapter instance
        """
        return provider(target=self)


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
