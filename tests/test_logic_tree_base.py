from collections import namedtuple
from unittest.mock import patch  # TODO: use pytest to patch?

import pytest

from nzshm_model.logic_tree.logic_tree_base import Branch, BranchSet, Correlation, LogicTree, LogicTreeCorrelations

Fixtures = namedtuple("Fixtures", "correlation1 correlation2 branchA1 branchB2 branchsetA branchsetB logic_tree")


@pytest.fixture(scope='module')
@patch.multiple(LogicTree, __abstractmethods__=set())
@patch.multiple(LogicTreeCorrelations, __abstractmethods__=set())
@patch.multiple(Branch, __abstractmethods__=set())
def fixtures():
    branchA1 = Branch(name="branchA1", weight=0.2)
    branchA2 = Branch(name="branchA2", weight=0.2)
    branchA3 = Branch(name="branchA3", weight=0.3)
    branchA4 = Branch(name="branchA4", weight=0.3)
    branchB1 = Branch(name="branchB1", weight=0.25)
    branchB2 = Branch(name="branchB2", weight=0.75)

    branchsetA = BranchSet(short_name="A", long_name="branchsetA", branches=[branchA1, branchA2, branchA3, branchA4])
    branchsetB = BranchSet(short_name="B", long_name="branchsetB", branches=[branchB1, branchB2])

    correlation1 = Correlation(primary_branch=branchA1, associated_branches=[branchB1])
    correlation2 = Correlation(primary_branch=branchA2, associated_branches=[branchB2])
    correlation3 = Correlation(primary_branch=branchA3, associated_branches=[branchB1])
    correlation4 = Correlation(primary_branch=branchA4, associated_branches=[branchB2])
    correlations = LogicTreeCorrelations(correlations=[correlation1, correlation2, correlation3, correlation4])

    logic_tree = LogicTree(title='logic_tree', branch_sets=[branchsetA, branchsetB], correlations=correlations)

    return Fixtures(
        correlation1=correlation1,
        correlation2=correlation2,
        branchA1=branchA1,
        branchB2=branchB2,
        branchsetA=branchsetA,
        branchsetB=branchsetB,
        logic_tree=logic_tree,
    )


# @patch.multiple(LogicTreeCorrelations, __abstractmethods__=set())
# @patch.multiple(LogicTree, __abstractmethods__=set())
def test_check_correlations(fixtures: Fixtures):

    # should not raise exeption
    correlations = LogicTreeCorrelations(correlations=[fixtures.correlation1, fixtures.correlation2])

    # should raise exception
    with pytest.raises(ValueError):
        correlation2x = Correlation(primary_branch=fixtures.branchA1, associated_branches=[fixtures.branchB2])
        correlations = LogicTreeCorrelations(correlations=[fixtures.correlation1, correlation2x])
        print(correlations)


def test__combined_branches_nocorr(fixtures: Fixtures):
    # branches not filtered by correlation
    assert len(list(fixtures.logic_tree._combined_branches())) == 4 * 2


def test_combined_branches(fixtures: Fixtures):
    # branches are filtered by correlation
    assert len(list(fixtures.logic_tree.combined_branches)) == 4


def test_correlation_weights(fixtures: Fixtures):
    # weights sum to 1.0
    assert sum([branch.weight for branch in fixtures.logic_tree.combined_branches]) == pytest.approx(1.0)


def test_correlation_mutability(fixtures: Fixtures):

    # should not raise an execption
    correlations = LogicTreeCorrelations(
        correlations=[fixtures.correlation1, fixtures.correlation2], weights=[0.2, 0.2]
    )
    fixtures.logic_tree.correlations = correlations

    # should not be able to set correlations that do not work
    correlations = LogicTreeCorrelations(
        correlations=[fixtures.correlation1, fixtures.correlation2], weights=[1.0, 1.0]
    )
    with pytest.raises(ValueError):
        fixtures.logic_tree.correlations = correlations
