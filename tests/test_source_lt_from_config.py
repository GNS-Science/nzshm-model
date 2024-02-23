from pathlib import Path
from nzshm_model.logic_tree import SourceLogicTree


def test_slt_from_config():
    slt_config_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample.json'
    slt = SourceLogicTree.from_user_config(slt_config_path)

    assert len(list(slt.combined_branches)) == 4
    assert len(list(slt._combined_branches)) == 4*2