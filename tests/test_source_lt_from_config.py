from pathlib import Path
from nzshm_model.logic_tree import SourceLogicTree, InversionSource


def test_slt_from_config():
    slt_config_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample.json'
    slt = SourceLogicTree.from_user_config(slt_config_path)

    assert len(list(slt.combined_branches)) == 4
    assert len(list(slt._combined_branches())) == 4*2

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