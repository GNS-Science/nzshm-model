#! python test_logic_tree.py

# import dataclasses
# import itertools
from pathlib import Path

from nzshm_model.logic_tree import SourceLogicTree

# import pytest


def test_v2_source_tree_from_json_no_correlations():
    config = Path(__file__).parent / 'fixtures' / 'source_logic_tree_sample_0.json'
    slt = SourceLogicTree.from_json(config)
    print(slt)
    # slt_spec = slt.derive_spec()
    # print(slt_spec)
    assert slt.logic_tree_version == 2
    assert slt.version == 'SLT_v9p0p0'
    assert slt.title == 'a SRM logic tree'
    assert slt.branch_sets[0].short_name == 'PUY'
    assert slt.branch_sets[0].long_name == 'Puysegur'
    assert slt.branch_sets[0].branches[0].values[0].name == 'dm'
    assert slt.branch_sets[0].branches[0].values[0].value == '0.7'
    # , bN[0.902, 4.6], C4.0, s0.28]
    # InversionSource
    assert slt.branch_sets[0].branches[0].sources[0].type == 'inversion'
    assert slt.branch_sets[0].branches[0].sources[0].nrml_id == 'SW52ZXJzaW9uU29sdXRpb25Ocm1sOjExODcxNw=='
    assert slt.branch_sets[0].branches[0].sources[0].rupture_rate_scaling == 0.9


def test_serialize_source_logic_tree():
    slt_json_path = Path(__file__).parent / 'fixtures' / 'slt_config_sample.json'
    slt_orig = SourceLogicTree.from_json(slt_json_path)
    slt_dict = slt_orig.to_dict()
    slt_from_dict = SourceLogicTree.from_dict(slt_dict)

    assert slt_orig == slt_from_dict
