"""
This module contains abstract base classes common to both **Source** and
**Ground Motion Model (GMM)** logic trees.
"""
import copy
import json
import math
from abc import ABC, ABCMeta, abstractmethod
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field, fields
from functools import reduce
from itertools import product
from operator import mul
from pathlib import Path
from typing import Any, Dict, Generator, Iterator, List, Type, Union, overload

import dacite

from nzshm_model.psha_adapter import PshaAdapterInterface


# no default value for weight out of convenience since the subclasses have default values for their own members.
# What do we think?
@dataclass
class Branch(ABC):
    name: str = ""
    weight: float = 1.0

    @abstractclassmethod
    def filtered_branch(self, logic_tree: 'LogicTree', branch_set: 'BranchSet'):
        """
        Produce a new filtered branch with the properties of the branch
        """
        pass


# should we have long and short names in the base class?
# should the type for branches be List[Any]?
@dataclass
class BranchSet:
    short_name: str = ''
    long_name: str = ''
    branches: Sequence[Any] = field(default_factory=list)

    def validate_weights(self) -> bool:
        weight = 0.0
        for b in self.branches:
            weight += b.weight
        return weight == 1.0


@dataclass
class Correlation:
    primary_branch: Branch = field(default_factory=Branch)
    associated_branches: List[Branch] = field(default_factory=list)

    @property
    def all_branches(self) -> List[Branch]:
        return [self.primary_branch] + self.associated_branches


# TODO: don't like that correlations = LogicTreeCorrelations(); correlations.correlations, feels like an awkward API
# does this need to be abstract?
@dataclass(frozen=True)
class LogicTreeCorrelations(Sequence):
    correlations: List[Correlation] = field(default_factory=list)
    weights: List[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        # check that the list of correlations is correct
        self.check_correlations()

        # check that the number of weights supplied matches the number of correlations
        if (self.weights) and (len(self.weights) != len(self.correlations)):
            raise ValueError("length of weights must equal the number of correlations")

    def primary_branches(self) -> Generator[Branch, None, None]:
        for cor in self.correlations:
            yield cor.primary_branch

    def check_correlations(self) -> None:
        # check that there are no repeats in the 0th element of each correlation
        prim_branches = list(self.primary_branches())
        if [branch for branch in prim_branches if prim_branches.count(branch) > 1]:
            raise ValueError("there is a repeated branch in the 0th element of the correlations")

    @overload
    def __getitem__(self, i: int) -> Correlation:
        ...

    @overload
    def __getitem__(self, i: slice) -> Sequence[Correlation]:
        ...

    def __getitem__(self, i):
        if isinstance(i, slice):
            raise TypeError("LogicTreeCorrelations does not support slicing")
        return self.correlations[i]

    def __len__(self) -> int:
        return len(self.correlations)


@dataclass
class CompositeBranch:
    branches: Sequence[Branch] = field(default_factory=list)
    weight: float = 1.0

    def __post_init__(self) -> None:
        self.weight = reduce(mul, [branch.weight for branch in self.branches], 1.0)

    def __iter__(self):
        self.__counter = 0
        return self

    def __next__(self):
        if self.__counter >= len(self.branches):
            raise StopIteration
        else:
            self.__counter += 1
            return self.branches[self.__counter - 1]


@dataclass
class LogicTree(ABC):
    title: str = ''
    version: str = ''
    branch_sets: List[Any] = field(default_factory=list)
    correlations: LogicTreeCorrelations = field(default_factory=LogicTreeCorrelations)

    def __post_init__(self) -> None:
        self.check_correlations()

    def __setattr__(self, __name: str, __value: Any) -> None:
        super().__setattr__(__name, __value)
        if __name == "correlations":
            # self.correlations = __value
            self.check_correlations()
        # else:

    def check_correlations(self) -> None:
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
            correlation_match = [branch_pri in combined_branch for branch_pri in self.correlations.primary_branches()]
            if any(correlation_match):
                i_cor = correlation_match.index(
                    True
                )  # index of the correlation that matches a branch in _combined_branches()
                if not all(compbr in self.correlations[i_cor].all_branches for compbr in combined_branch):
                    continue
                else:
                    # set the weight
                    if self.correlations.weights:
                        combined_branch.weight = self.correlations.weights[i_cor]
                    else:
                        combined_branch.weight = self.correlations[
                            i_cor
                        ].primary_branch.weight  # weight of primary branch of relevent correlation
            yield combined_branch

    @classmethod
    def from_json(cls, json_path: Union[Path, str]) -> 'LogicTree':
        with Path(json_path).open() as jsonfile:
            data = json.load(jsonfile)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict) -> 'LogicTree':
        return dacite.from_dict(data_class=cls, data=data, config=dacite.Config(strict=True))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    # would like this to actully do the work, but not sure how to pass the logic trees wihtout knowning the type.
    # Could check for type in PshaAdaptorInterface, but then we have a circular import.
    @abstractmethod
    def psha_adapter(self, provider: Type[PshaAdapterInterface], **kwargs):
        pass

    def __all_branches__(self):
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


# this should never be serialised, only used for filtering
@dataclass
class FilteredBranch(Branch, metaclass=ABCMeta):
    logic_tree: LogicTree = field(default_factory=LogicTree)
    branch_set: BranchSet = field(default_factory=BranchSet)

    def to_branch(self) -> Branch:
        branch_attributes = {k: v for k, v in self.__dict__.items() if k not in ('branch_set', 'logic_tree')}
        return type(self.branch_set.branches[0])(**branch_attributes)
