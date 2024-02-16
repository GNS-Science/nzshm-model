import unittest
import pytest
# from pathlib import Path
from unittest.mock import patch, Mock

from nzshm_model.logic_tree.logic_tree_base import LogicTree, LogicTreeCorrelations, Branch, BranchSet
from nzshm_model.logic_tree import SourceLogicTree
from nzshm_model.logic_tree.source_logic_tree import SourceLogicTreeV1
from nzshm_model.logic_tree import SourceLogicTree


class CorrelationTests(unittest.TestCase):

    @patch.multiple(LogicTree, __abstractmethods__=set())
    @patch.multiple(LogicTreeCorrelations, __abstractmethods__=set())
    @patch.multiple(Branch, __abstractmethods__=set())
    def setUp(self) -> None:

        self.branchA1 = Branch(name="branchA1", weight=0.2)
        self.branchA2 = Branch(name="branchA2", weight=0.2)
        self.branchA3 = Branch(name="branchA3", weight=0.3)
        self.branchA4 = Branch(name="branchA4", weight=0.3)
        self.branchB1 = Branch(name="branchB1", weight=0.25)
        self.branchB2 = Branch(name="branchB2", weight=0.75)

        self.branchsetA = BranchSet(short_name="A", long_name="branchsetA", branches = [self.branchA1, self.branchA2, self.branchA3, self.branchA4])
        self.branchsetB = BranchSet(short_name="B", long_name="branchsetB", branches = [self.branchB1, self.branchB2])

        self.correlation1 = [self.branchA1, self.branchB1]
        self.correlation2 = [self.branchA2, self.branchB2]
        self.correlation3 = [self.branchA3, self.branchB1]
        self.correlation4 = [self.branchA4, self.branchB2]
        self.correlations = LogicTreeCorrelations(correlations=[self.correlation1, self.correlation2, self.correlation3, self.correlation4])

        self.logic_tree = LogicTree(title='logic_tree', branch_sets=[self.branchsetA, self.branchsetB], correlations=self.correlations)

    def test_check_correlations(self):

        # should not raise exeption
        correlations = LogicTreeCorrelations(correlations=[self.correlation1, self.correlation2])

        # should raise exception
        with pytest.raises(ValueError) as valueerror:
            correlation2x = [self.branchA1, self.branchB2]
            correlations = LogicTreeCorrelations(correlations=[self.correlation1, correlation2x])

    def test__combined_branches_nocorr(self):
        assert len(list(self.logic_tree._combined_branches())) == 4*2

    def test_combined_branches(self):
        assert len(list(self.logic_tree.combined_branches)) == 4

    def test_correlation_weights(self):
        assert sum([branch.weight for branch in self.logic_tree.combined_branches]) == pytest.approx(1.0)


# class LogicTreeTests(unittest.TestCase):