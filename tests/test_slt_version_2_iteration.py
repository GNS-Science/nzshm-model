"""
test migration from slt v1 to v2
"""
from pathlib import Path

import pytest

import nzshm_model
from nzshm_model.source_logic_tree import SourceLogicTree, SourceLogicTreeV1

# from nzshm_model.source_logic_tree.version2 import Branch


@pytest.fixture(scope='module')
def slt_version_1():
    # get a published v1 logic tree
    data = nzshm_model.get_model_version('NSHM_v1.0.4')._data
    yield SourceLogicTreeV1.from_dict(data)


@pytest.fixture(scope='module')
def slt_version_2():
    config = Path(__file__).parent / 'fixtures' / 'source_logic_tree_sample_0.json'
    yield SourceLogicTree.from_json(config)


def test_source_logic_tree_v2_is_iterable(slt_version_2):
    for obj in slt_version_2:
        assert obj


def test_source_logic_tree_v2_is_branch_iterable(slt_version_2):
    for obj in slt_version_2:
        # assert isinstance(obj, Branch)
        assert isinstance(obj, SourceLogicTree)


def test_source_logic_tree_v2_iterable_size(slt_version_2):
    assert len(list(slt_version_2)) == 1
    assert len(next(iter(slt_version_2)).fault_systems[0].branches[0].sources) == 2


def test_source_logic_tree_v2_iterates_source_logic_tree(slt_version_2):
    assert (
        next(iter(slt_version_2)).fault_systems[0].branches[0].sources[0]
        == slt_version_2.fault_systems[0].branches[0].sources[0]
    )
    print(list(slt_version_2)[0])
    # assert 0
