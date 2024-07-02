#! python test_logic_tree.py

# import dataclasses
# import itertools
from pathlib import Path

from nzshm_model.logic_tree import Correlation, LogicTreeCorrelations, SourceLogicTree

# import pytest


def test_v2_source_tree_from_json_no_correlations():
    config = Path(__file__).parent / 'fixtures' / 'source_logic_tree_sample_2.json'
    slt = SourceLogicTree.from_json(config)

    # without correlations there are 4 composite branches
    assert len(list(slt.composite_branches)) == 4

    cor1 = Correlation(
        primary_branch=slt.branch_sets[0].branches[0],
        associated_branches=[slt.branch_sets[1].branches[0]],
    )
    cor2 = Correlation(
        primary_branch=slt.branch_sets[0].branches[1],
        associated_branches=[slt.branch_sets[1].branches[1]],
    )
    slt.correlations = LogicTreeCorrelations([cor1, cor2])

    # with correlations there are 2 composite branches
    for branch in slt.composite_branches:
        print(branch)
        print('')
    assert len(list(slt.composite_branches)) == 2
