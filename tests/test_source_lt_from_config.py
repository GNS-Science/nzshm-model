from pathlib import Path

import pytest

from nzshm_model.logic_tree import InversionSource, SourceLogicTree


def test_slt_from_config():
    slt_config_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample.json'
    slt = SourceLogicTree.from_user_config(slt_config_path)

    assert len(list(slt.combined_branches)) == 4
    assert len(list(slt._combined_branches())) == 4 * 2

    assert slt.branch_sets[2].branches[0].name == ""
    assert slt.branch_sets[2].short_name == ""
    assert slt.branch_sets[0].branches[0].name == "PUY1"
    assert slt.branch_sets[1].short_name == "HIK"
    assert slt.branch_sets[0].branches[1].weight == 0.8
    assert len(slt.branch_sets[0].branches[0].sources) == 4
    assert isinstance(slt.branch_sets[0].branches[0].sources[2], InversionSource)
    assert slt.branch_sets[1].branches[2].sources[0].nrml_id == "MNO"
    assert slt.correlations.correlation_groups[0].primary_branch == slt.branch_sets[1].branches[0]
    assert slt.correlations.correlation_groups[0].associated_branches == [slt.branch_sets[0].branches[0]]


def test_slt_from_config_errors():

    # branch weights of branch set must sum to 1.0
    slt_config_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample_error1.json'
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_user_config(slt_config_path)
    print(value_error.value)

    slt_config_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample_error2.json'
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_user_config(slt_config_path)
    print(value_error.value)

    # source type and member type should match
    # NB: the type member is not in the documentation, but a user could set it to the wrong value mistakenly
    slt_config_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample_error3.json'
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_user_config(slt_config_path)
    print(value_error.value)

    # branches named in correlations must exist in the logic tree
    slt_config_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample_error4.json'
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_user_config(slt_config_path)
    print(value_error.value)

    # cannot repeat primary branch in correlations
    slt_config_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample_error5.json'
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_user_config(slt_config_path)
    print(value_error.value)

    # every branch must have at least one source
    slt_config_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample_error6.json'
    with pytest.raises(ValueError) as value_error:
        SourceLogicTree.from_user_config(slt_config_path)
    print(value_error.value)
