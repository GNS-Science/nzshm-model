import math
from typing import TYPE_CHECKING, List

from .correlation import Correlation, LogicTreeCorrelations

if TYPE_CHECKING:
    from .logic_tree_base import BranchSet, LogicTree, LogicTreeType


##############################
# VALIDATORS
##############################
def _validate_branchset_weights(branch_set: 'BranchSet') -> None:
    """
    verify that weighs sum to 1.0
    """
    weight = 0.0
    if not branch_set.branches:  # empty BranchSet
        return
    for b in branch_set.branches:
        weight += b.weight
    if not math.isclose(weight, 1.0):
        raise ValueError("weights of BranchSet must sum to 1.0")


def _validate_names(logic_tree: 'LogicTree') -> None:
    # do not allow duplicate branch_set.shortname:branch.name
    branch_names = [f"{branch.branch_set.short_name}:{branch.branch_id}" for branch in logic_tree]
    if len(set(branch_names)) != len(branch_names):
        raise ValueError("branch_set.short_name:branch.branch_id must be unique")


def _validate_correlation_weights(logic_tree: 'LogicTree') -> None:
    # check that the weights total 1.0
    weight_total = 0.0
    for branch in logic_tree.composite_branches:
        weight_total += branch.weight
    if not math.isclose(weight_total, 1.0):
        raise ValueError("the weights of the logic tree do not sum to 1.0 when correlations are applied")


def _validate_correlations_format(correlations: List[str]) -> None:
    # check that the correlations are lists of stings with ":"
    for correlation in correlations:
        for branch in correlation:
            if not isinstance(branch, str):
                raise ValueError("branch names in correlations must be strings")
            if ":" not in branch:
                raise ValueError("names in correlations must be 'branch_set.shortname:branch.name' format")


##############################
# SERIALIZE / DESERIALIZE
##############################
def _correlation_encoding(branch_set, branch):
    return f"{branch_set.short_name}:{branch.branch_id}"


def _add_corellations(logic_tree: 'LogicTreeType', correlations: List[str]) -> 'LogicTreeType':

    branches = [branch for branch in logic_tree]
    # branch_names = [f"{fbranch.branch_set.short_name}:{fbranch.name}" for fbranch in branches]
    branch_names = [_correlation_encoding(fbranch.branch_set, fbranch) for fbranch in branches]
    correlation_groups = []
    for correlation in correlations:
        primary_branch = branches[branch_names.index(correlation[0])].to_branch()
        assoc_branches = [branches[branch_names.index(b)].to_branch() for b in correlation[1:]]
        correlation_groups.append(
            Correlation(
                primary_branch=primary_branch,
                associated_branches=assoc_branches,
            )
        )
    logic_tree.correlations = LogicTreeCorrelations(correlation_groups)

    return logic_tree


def _serialise_correlations(logic_tree: 'LogicTree') -> List[List[str]]:
    def find_branch_set(logic_tree, branch):
        for fbranch in logic_tree:
            if fbranch.to_branch() == branch:
                return fbranch.branch_set

    correlations = []
    for cor in logic_tree.correlations.correlation_groups:
        correlation = []
        correlation.append(_correlation_encoding(find_branch_set(logic_tree, cor.primary_branch), cor.primary_branch))
        for branch in cor.associated_branches:
            correlation.append(_correlation_encoding(find_branch_set(logic_tree, branch), branch))
        correlations.append(correlation)
    return correlations
