"""
Classes for defining logic tree branches
"""

from abc import ABC, abstractmethod
from functools import reduce
from operator import mul
from typing import TYPE_CHECKING, List, Sequence, TypeVar

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator

if TYPE_CHECKING:
    from .logic_tree_base import BranchSet, FilteredBranch, LogicTree

BranchType = TypeVar("BranchType", bound="Branch")

_CONFIG = ConfigDict(extra="forbid", arbitrary_types_allowed=True)


class Branch(BaseModel, ABC):
    """
    Abstract baseclass for logic tree branches

    Arguments:
        name: a name for the branch
        weight: a weight for the branch
    """

    model_config = _CONFIG

    branch_id: str = ""
    weight: float = 1.0

    @abstractmethod
    def filtered_branch(self, logic_tree: 'LogicTree', branch_set: 'BranchSet') -> 'FilteredBranch':
        """Produce a new filtered branch with the properties of the branch."""
        pass


class CompositeBranch(BaseModel):
    """
    A logic tree branch comprised of combinations of branches from one or more branch sets.

    Arguments:
        branches: the component branches (branches from branch sets) in the composite branch
        weight: the weight of the composite branch
    """

    model_config = _CONFIG

    branches: List[Branch] = Field(default_factory=list)
    weight: float = 1.0

    _counter: int = PrivateAttr(0)

    @model_validator(mode="after")
    def _set_weight(self) -> "CompositeBranch":
        self.weight = reduce(mul, [branch.weight for branch in self.branches], 1.0)
        return self

    def __iter__(self):
        self._counter = 0
        return self

    def __next__(self):
        if self._counter >= len(self.branches):
            raise StopIteration
        else:
            self._counter += 1
            return self.branches[self._counter - 1]
