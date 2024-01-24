from pathlib import Path

import pytest

from nzshm_model.logic_tree import SourceLogicTree

# import pytest


@pytest.fixture(scope='module')
def source_logic_tree():
    config = Path(__file__).parent / 'fixtures' / 'source_logic_tree_sample_0.json'
    yield SourceLogicTree.from_json(config)


def test_slt_aliases(source_logic_tree):
    assert source_logic_tree.branch_sets[0] == source_logic_tree.fault_systems[0]

    assert source_logic_tree.fault_system_lts[0] == source_logic_tree.fault_systems[0]

    for filt_branch in source_logic_tree:
        assert filt_branch.fslt == filt_branch.branch_set
        assert filt_branch.slt == filt_branch.logic_tree
        break


def test_deprication_warning(source_logic_tree):
    with pytest.warns(DeprecationWarning):
        source_logic_tree.fault_systems

    with pytest.warns(DeprecationWarning):
        source_logic_tree.fault_system_lts

    with pytest.warns(DeprecationWarning):
        for filt_branch in source_logic_tree:
            filt_branch.fslt

    with pytest.warns(DeprecationWarning):
        for filt_branch in source_logic_tree:
            filt_branch.slt
