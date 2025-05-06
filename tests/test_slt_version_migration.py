"""
test migration from slt v1 to v2
"""

import importlib.resources as resources
import json

import pytest

from nzshm_model.logic_tree.source_logic_tree import SourceLogicTree, SourceLogicTreeV1


@pytest.fixture(scope='module')
def slt_version_1():
    # get a published v1 logic tree
    data_filepath = resources.files('nzshm_model.resources') / 'SRM_JSON' / 'nshm_v1.0.4.json'
    with data_filepath.open() as datafile:
        data = json.load(datafile)
    yield SourceLogicTreeV1.from_dict(data)


def test_migrate_NSHM_v1_0_4(slt_version_1):
    v2 = SourceLogicTree.from_source_logic_tree(slt_version_1)
    assert v2.version == slt_version_1.version


def test_migrate_serialize_deserialize(slt_version_1, tmp_path):

    slt_filepath = tmp_path / 'slt.json'
    v2 = SourceLogicTree.from_source_logic_tree(slt_version_1)
    v2.to_json(slt_filepath)
    v2_deserialized = SourceLogicTree.from_json(slt_filepath)

    assert v2_deserialized == v2


def test_migrate_NSHM_v1_0_4_fault_systems(slt_version_1):
    v2 = SourceLogicTree.from_source_logic_tree(slt_version_1)
    assert v2.branch_sets[0].short_name == slt_version_1.fault_systems[0].short_name


def test_migrate_NSHM_v1_0_4_branches(slt_version_1):
    v2 = SourceLogicTree.from_source_logic_tree(slt_version_1)
    assert len(v2.branch_sets[0].branches) == len(slt_version_1.fault_systems[0].branches)
    assert len(v2.branch_sets[0].branches) == len(slt_version_1.fault_system_lts[0].branches)  # old attributes
    assert v2.branch_sets[0].branches[0].weight == slt_version_1.fault_systems[0].branches[0].weight
