from collections import namedtuple
from unittest.mock import patch  # TODO: use pytest to patch?

import pytest

from nzshm_model.logic_tree.branch import Branch
from nzshm_model.logic_tree.correlation import Correlation, LogicTreeCorrelations
from nzshm_model.logic_tree.logic_tree_base import BranchSet, LogicTree

Fixtures = namedtuple(
    "Fixtures",
    """correlation1 correlation2 branchA1 branchA2 branchB1 branchB2
    branchsetA branchsetB logic_tree logic_tree_nocor logic_tree2""",
)


@pytest.fixture(scope='module')
@patch.multiple(LogicTree, __abstractmethods__=set())
@patch.multiple(LogicTreeCorrelations, __abstractmethods__=set())
@patch.multiple(Branch, __abstractmethods__=set())
def fixtures():
    branchA1 = Branch(branch_id="branchA1", weight=0.2)
    branchA2 = Branch(branch_id="branchA2", weight=0.2)
    branchA3 = Branch(branch_id="branchA3", weight=0.3)
    branchA4 = Branch(branch_id="branchA4", weight=0.3)
    branchB1 = Branch(branch_id="branchB1", weight=0.25)
    branchB2 = Branch(branch_id="branchB2", weight=0.75)
    branchC1 = Branch(branch_id="branchC1", weight=0.2)
    branchC2 = Branch(branch_id="branchC2", weight=0.8)

    branchsetA = BranchSet(short_name="A", long_name="branchsetA", branches=[branchA1, branchA2, branchA3, branchA4])
    branchsetB = BranchSet(short_name="B", long_name="branchsetB", branches=[branchB1, branchB2])
    branchsetC = BranchSet(short_name="C", long_name="branchsetC", branches=[branchC1, branchC2])

    correlation1 = Correlation(primary_branch=branchA1, associated_branches=[branchB1])
    correlation2 = Correlation(primary_branch=branchA2, associated_branches=[branchB2])
    correlation3 = Correlation(primary_branch=branchA3, associated_branches=[branchB1])
    correlation4 = Correlation(primary_branch=branchA4, associated_branches=[branchB2])
    correlations = LogicTreeCorrelations(correlation_groups=[correlation1, correlation2, correlation3, correlation4])

    logic_tree_nocor = LogicTree(title='logic_tree', branch_sets=[branchsetA, branchsetB, branchsetC])
    logic_tree = LogicTree(title='logic_tree', branch_sets=[branchsetA, branchsetB], correlations=correlations)
    logic_tree2 = LogicTree(
        title='logic_tree', branch_sets=[branchsetA, branchsetB, branchsetC], correlations=correlations
    )

    return Fixtures(
        correlation1=correlation1,
        correlation2=correlation2,
        branchA1=branchA1,
        branchA2=branchA2,
        branchB1=branchB1,
        branchB2=branchB2,
        branchsetA=branchsetA,
        branchsetB=branchsetB,
        logic_tree=logic_tree,
        logic_tree_nocor=logic_tree_nocor,
        logic_tree2=logic_tree2,
    )


def test_branchset(fixtures: Fixtures):
    # cannot create BranchSet if weights do not sum to 1.0
    with pytest.raises(ValueError):
        BranchSet(branches=[fixtures.branchA1, fixtures.branchB2])


def test_iterate_branchset(fixtures: Fixtures):
    for branch1, branch2 in zip(fixtures.branchsetA.branches, fixtures.branchsetA):
        assert branch1 == branch2


def test_correlation(fixtures: Fixtures):
    # we get the correct nubmer of total branches in a correlation
    assert len(fixtures.correlation1.all_branches) == 2


def test_check_correlations_validation(fixtures: Fixtures):
    # should not raise exeption
    LogicTreeCorrelations(correlation_groups=[fixtures.correlation1, fixtures.correlation2])

    # should raise exception same entry used twice
    with pytest.raises(ValueError):
        correlation2x = Correlation(primary_branch=fixtures.branchA1, associated_branches=[fixtures.branchB2])
        LogicTreeCorrelations(correlation_groups=[fixtures.correlation1, correlation2x])


def test__composite_branches(fixtures: Fixtures):

    assert len(list(fixtures.logic_tree_nocor.composite_branches)) == 4 * 2 * 2

    # branches not filtered by correlation
    assert len(list(fixtures.logic_tree._composite_branches())) == 4 * 2

    # branches filtered by correlation
    assert len(list(fixtures.logic_tree.composite_branches)) == 4

    # can correlate a subset of BranchSets
    assert len(list(fixtures.logic_tree2._composite_branches())) == 4 * 2 * 2

    assert len(list(fixtures.logic_tree2.composite_branches)) == 4 * 2


def test_composite_weights(fixtures: Fixtures):
    # weights sum to 1.0
    assert sum([branch.weight for branch in fixtures.logic_tree.composite_branches]) == pytest.approx(1.0)
    assert sum([branch.weight for branch in fixtures.logic_tree_nocor.composite_branches]) == pytest.approx(1.0)

    # weights are default from the primary branch
    for cg in fixtures.logic_tree.correlations.correlation_groups:
        assert cg.weight == cg.primary_branch.weight


def test_logic_tree_validation_of_corr(fixtures: Fixtures):
    # should not raise an execption
    correlation1 = Correlation(primary_branch=fixtures.branchA1, associated_branches=[fixtures.branchB1], weight=0.2)
    correlation2 = Correlation(primary_branch=fixtures.branchA2, associated_branches=[fixtures.branchB2], weight=0.2)
    correlations = LogicTreeCorrelations(correlation_groups=[correlation1, correlation2])
    fixtures.logic_tree.correlations = correlations

    # should not be able to set correlations with incorrect weights
    correlation1.weight = 1.0
    correlation2.weight = 1.0
    correlations = LogicTreeCorrelations(correlation_groups=[correlation1, correlation2])
    with pytest.raises(ValueError):
        fixtures.logic_tree.correlations = correlations
