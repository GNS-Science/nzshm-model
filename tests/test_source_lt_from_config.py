import json
from pathlib import Path

import pytest

from nzshm_model.logic_tree import InversionSource, SourceLogicTree


@pytest.fixture()
def slt_dict():
    slt_json_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample.json'
    with slt_json_path.open() as slt_file:
        return json.load(slt_file)


def test_slt_from_config(slt_dict):
    slt = SourceLogicTree.from_dict(slt_dict)
    assert len(list(slt.composite_branches)) == 4
    assert len(list(slt._composite_branches())) == 4 * 2

    assert slt.branch_sets[2].branches[0].branch_id == ""
    assert slt.branch_sets[2].short_name == ""
    assert slt.branch_sets[0].branches[0].branch_id == "PUY1"
    assert slt.branch_sets[1].short_name == "HIK"
    assert slt.branch_sets[0].branches[1].weight == 0.8
    assert len(slt.branch_sets[0].branches[0].sources) == 4
    assert isinstance(slt.branch_sets[0].branches[0].sources[2], InversionSource)
    assert slt.branch_sets[1].branches[2].sources[0].nrml_id == "MNO"
    assert slt.correlations.correlation_groups[0].primary_branch == slt.branch_sets[1].branches[0]
    assert slt.correlations.correlation_groups[0].associated_branches == [slt.branch_sets[0].branches[0]]


def test_slt_from_config_errors0(slt_dict):
    # branch weights of branch set must sum to 1.0
    slt_dict["branch_sets"][0]["branches"][0]["weight"] = 0.3
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_dict(slt_dict)
    print(value_error.value)


def test_slt_from_config_errors1(slt_dict):
    # source type and member type should match
    # NB: the type member is not in the documentation, but a user could set it to the wrong value mistakenly
    slt_dict["branch_sets"][1]["branches"][2]["sources"][0]["type"] = "inversion"
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_dict(slt_dict)
    print(value_error.value)


def test_slt_from_config_errors2(slt_dict):
    # branches named in correlations must exist in the logic tree
    slt_dict["correlations"][0][0] = ["HIK:HIK10"]
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_dict(slt_dict)
    print(value_error.value)


def test_slt_from_config_errors3(slt_dict):
    # cannot repeat primary branch in correlations
    slt_dict["correlations"][1][0] = slt_dict["correlations"][0][0]
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_dict(slt_dict)
    print(value_error.value)


def test_slt_from_config_errors4(slt_dict):
    # every branch must have at least one source
    # slt_dict["branch_sets"][1][3]["sources"] = []
    del slt_dict["branch_sets"][1]["branches"][3]["sources"]
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_dict(slt_dict)
    print(value_error.value)


def test_slt_from_config_errors5(slt_dict):
    # don't accept duplicate branch_set.short_name:branch.branch_id
    slt_dict["branch_sets"][1]["short_name"] = "PUY"
    slt_dict["branch_sets"][1]["branches"][1]["branch_id"] = "PUY1"
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_dict(slt_dict)
    print(value_error.value)


def test_slt_from_config_errors6(slt_dict):
    # correlations must name branches in the LT
    slt_dict["correlations"][0][0] = "HIK:HIK10"
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_dict(slt_dict)
    print(value_error.value)


def test_slt_from_config_errors7(slt_dict):
    # correlations must name branches in the LT
    slt_dict["correlations"][0][0] = 1
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_dict(slt_dict)
    print(value_error.value)


def test_slt_from_config_errors8(slt_dict):
    # correlations must name branches in the LT
    slt_dict["correlations"][0][0] = "HIKHIK1"
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_dict(slt_dict)
    print(value_error.value)
