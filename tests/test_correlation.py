import unittest

from nzshm_model.logic_tree.source_logic_tree import (
    BranchAttributeSpec,
    BranchAttributeValue,
    SourceLogicTreeCorrelation,
)


class TestFlattenedSourceLogicTree(unittest.TestCase):
    def test_correlation_compare(self):

        bn = BranchAttributeSpec(name='bN', long_name='bN pair', value_options=[[1.0, 2.0], [0.9, 3.0]])
        c = BranchAttributeSpec(name='C', long_name='area-magnitude-scaling', value_options=[1.0, 2.0])

        primary = [
            BranchAttributeValue.from_branch_attribute(bn, bn.value_options[0]),
            BranchAttributeValue.from_branch_attribute(c, c.value_options[0]),
        ]
        secondary = [
            BranchAttributeValue.from_branch_attribute(bn, bn.value_options[1]),
            BranchAttributeValue.from_branch_attribute(c, c.value_options[1]),
        ]

        correlation = SourceLogicTreeCorrelation('A', 'B', primary, secondary)

        self.assertTrue(correlation.is_primary(primary))
        self.assertFalse(correlation.is_primary(secondary))
        self.assertFalse(correlation.is_secondary(primary))
        self.assertTrue(correlation.is_secondary(secondary))
