#! python test_logic_tree.py

# import dataclasses
# import itertools
from pathlib import Path

from nzshm_model.logic_tree import SourceLogicTree, Correlation, LogicTreeCorrelations

# import pytest


def test_v2_source_tree_from_json_no_correlations():
    config = Path(__file__).parent / 'fixtures' / 'source_logic_tree_sample_2.json'
    slt = SourceLogicTree.from_json(config)
    cor1 = Correlation(
        primary_branch=slt.branch_sets[0].branches[0],
        associated_branches=[slt.branch_sets[1].branches[0]],
    )
    cor2 = Correlation(
        primary_branch=slt.branch_sets[0].branches[1],
        associated_branches=[slt.branch_sets[1].branches[1]],
    )
    slt.correlations = LogicTreeCorrelations([cor1, cor2])

    for branch in slt.combined_branches:
        print(branch)
        print('')
    assert len(list(slt.combined_branches)) == 2