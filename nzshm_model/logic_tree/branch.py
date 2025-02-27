"""
Classes for defining logic tree branches
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import reduce
from operator import mul
from typing import TYPE_CHECKING, Sequence, TypeVar

if TYPE_CHECKING:
    from .logic_tree_base import BranchSet, FilteredBranch, LogicTree

BranchType = TypeVar("BranchType", bound="Branch")


@dataclass
class Branch(ABC):
    """
    Abstract baseclass for logic tree branches

    Arguments:
        name: a name for the branch
        weight: a weight for the branch
    """

    branch_id: str = ""
    weight: float = 1.0

    @abstractmethod
    def filtered_branch(self, logic_tree: 'LogicTree', branch_set: 'BranchSet') -> 'FilteredBranch':
        """
        Produce a new filtered branch with the properties of the branch

        Parameters:
            logic_tree: The logic tree that the branch belongs to
            branch_set: The branch est that the branch belongs to

        Returns:
            a filtered branch
        """
        pass


@dataclass
class CompositeBranch:
    """
    A logic tree branch comprised of combinations of branches from one or more branch sets.

    Arguments:
        branches: the component branches (branches from branch sets) in the composite branch
        weight: the weight of the composite branch
    """

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
