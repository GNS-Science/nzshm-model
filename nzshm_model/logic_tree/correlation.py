"""
Classes for enforcing correlations between branches in logic trees
"""

import collections
import collections.abc
from dataclasses import dataclass, field
from typing import Generator, List, Optional, Sequence, overload

from .branch import Branch


@dataclass
class Correlation:
    """
    A correlation between **BranchSet**s of a logic tree. Correlations are used when buiding combinations of branches
    from differnt **BranchSet**s.

    For example, if a logic tree contains branchets A and B each with branches A1, A2 and B1, B2, respectivly, then
    a correlation A1, B1 will only allow A1-B1 not A1-B2 as valid composite branches.

    The primary_brach will not appear in combination with any branches except those identified in associated_branches
    for the relevent **BranchSet**s

    Arguments:
        primary_branch: the branch that **MUST** be correlated with the associated brances.
        associated_branches: list of branches that the primary_branch must always be coupled with.
        weight: weight used for composite branch formed by correlation. Defaults to weight of primary_branch
    """

    primary_branch: Branch = field(default_factory=Branch)
    associated_branches: List[Branch] = field(default_factory=list)
    weight: Optional[float] = None

    def __post_init__(self):
        self.weight = self.primary_branch.weight if not self.weight else self.weight

    @property
    def all_branches(self) -> List[Branch]:
        """
        list of all branches in a correlation; both the primary branch and the assiciated branches

        Returns:
            list of branches in correlation
        """
        return [self.primary_branch] + self.associated_branches


@dataclass(frozen=True)
class LogicTreeCorrelations(collections.abc.Sequence):
    """
    All correlations for a logic tree.

    Arguments:
        correlation_groups: list of correlations to be applied to the logic tree branch sets.
    """

    correlation_groups: List[Correlation] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_correlations(self)

    def primary_branches(self) -> Generator[Branch, None, None]:
        """
        Yield the primary branches of all correlation_groups

        Returns:
            branches
        """
        for cor in self.correlation_groups:
            yield cor.primary_branch

    @overload
    def __getitem__(self, i: int) -> Correlation: ...  # noqa: E704

    @overload
    def __getitem__(self, i: slice) -> Sequence[Correlation]: ...  # noqa: E704

    def __getitem__(self, i):
        if isinstance(i, slice):
            raise TypeError("LogicTreeCorrelations does not support slicing")
        return self.correlation_groups[i]

    def __len__(self) -> int:
        return len(self.correlation_groups)


def _validate_correlations(ltcs: LogicTreeCorrelations) -> None:
    """
    check that there are no repeats in the 0th element of each correlation
    """
    prim_branches = list(ltcs.primary_branches())
    if len([branch for branch in prim_branches if prim_branches.count(branch) > 1]) != 0:
        raise ValueError("there is a repeated branch in the 0th element of the correlations")
