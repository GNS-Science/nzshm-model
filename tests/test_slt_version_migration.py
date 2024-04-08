"""
test migration from slt v1 to v2
"""
import pytest

import nzshm_model
from nzshm_model.logic_tree.source_logic_tree import SourceLogicTree, SourceLogicTreeV1


@pytest.fixture(scope='module')
def slt_version_1():
    # get a published v1 logic tree
    data = nzshm_model.get_model_version('NSHM_v1.0.4')._data
    yield SourceLogicTreeV1.from_dict(data)


def test_migrate_NSHM_v1_0_4(slt_version_1):
    v2 = SourceLogicTree.from_source_logic_tree(slt_version_1)
    assert v2.version == slt_version_1.version


def test_migrate_NSHM_v1_0_4_fault_systems(slt_version_1):
    v2 = SourceLogicTree.from_source_logic_tree(slt_version_1)
    assert v2.branch_sets[0].short_name == slt_version_1.fault_systems[0].short_name


def test_migrate_NSHM_v1_0_4_branches(slt_version_1):
    v2 = SourceLogicTree.from_source_logic_tree(slt_version_1)
    assert len(v2.branch_sets[0].branches) == len(slt_version_1.fault_systems[0].branches)
    assert len(v2.branch_sets[0].branches) == len(slt_version_1.fault_system_lts[0].branches)  # old attributes
    assert v2.branch_sets[0].branches[0].weight == slt_version_1.fault_systems[0].branches[0].weight
