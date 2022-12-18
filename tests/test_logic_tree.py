#! python test_logic_tree.py

import dataclasses
from pathlib import Path

import nzshm_model
from nzshm_model.source_logic_tree.logic_tree import (
    Branch,
    BranchAttributeSpec,
    BranchAttributeValue,
    FaultSystemLogicTree,
    SourceLogicTree,
)
from nzshm_model.source_logic_tree.slt_config import from_config


def test_direct_bav():
    bav = BranchAttributeValue(name='dm', long_name='deformation model', value="geodetic")
    print(bav)
    assert bav.value == "geodetic"


def test_direct_bav_no_options():
    bav = BranchAttributeValue(name='dm', long_name='deformation model', value="geodetic")
    print(bav)
    assert bav.value == "geodetic"


def test_init():
    ba = BranchAttributeSpec(name='C', long_name='area-magnitude scaling', value_options=[4.0])
    print(ba)

    bao = BranchAttributeValue.from_branch_attribute(ba, 4)
    print(bao)

    b = Branch(values=[bao], weight=0.5, onfault_nrml_id='ABC')
    print(b)

    f = FaultSystemLogicTree('Hik', 'Hikurangi', [b])
    print(f)
    assert f.branches[0].values[0].value == 4


def test_fslt_example():
    model_v1_0_0 = nzshm_model.get_model_version('NSHM_1.0.0')
    fslt = model_v1_0_0.build_crustal_branches()

    print(fslt)
    assert fslt.branches[-1].values[0].name == 'C'
    assert fslt.branches[-1].values[0].long_name == 'area-magnitude scaling'
    assert fslt.branches[-1].values[0].value == 4

    assert fslt.branches[-1].values[1].value == 1.0
    assert fslt.branches[-1].values[2].value == (0.95, 19.2)
    assert fslt.branches[-1].values[3].value == 'Geologic'

    assert fslt.validate_weights()


def test_full_slt():
    model_v1_0_0 = nzshm_model.get_model_version('NSHM_1.0.0')
    slt = SourceLogicTree('NSHM_1.0.0', 'initial', fault_system_branches=[model_v1_0_0.build_crustal_branches()])
    print(slt)
    assert slt.fault_system_branches[0].branches[-1].values[0].name == 'C'


def test_serialise_slt():
    model_v1_0_0 = nzshm_model.get_model_version('NSHM_1.0.0')
    slt = SourceLogicTree('NSHM_1.0.0', 'initial', fault_system_branches=[model_v1_0_0.build_crustal_branches()])

    slt_dict = dataclasses.asdict(slt)
    print(slt_dict)
    assert (
        slt.fault_system_branches[0].branches[-1].values[0].name
        == slt_dict['fault_system_branches'][0]['branches'][-1]['values'][0]['name']
    )


class TestSourceLogicTreeSpecification:
    def test_slt_v8(self):
        config = Path(__file__).parent.parent / 'nzshm_model' / 'source_logic_tree' / 'SLT_v8_gmm_v2_final.py'
        slt = from_config(config)

        slt_spec = slt.derive_spec()

        print(slt_spec)
        assert slt_spec.fault_system_branches[0].branches[0].name == 'dm'
        assert slt_spec.fault_system_branches[0].branches[0].long_name == 'deformation model'
        assert slt_spec.fault_system_branches[0].branches[0].value_options == ['0.7']

        assert slt_spec.fault_system_branches[2].branches[0].name == 'dm'
        assert slt_spec.fault_system_branches[2].branches[0].long_name == 'deformation model'
        assert slt_spec.fault_system_branches[2].branches[0].value_options == ['geodetic', 'geologic']

    def test_large_SLT_example_A_crustal(self):
        config = Path(__file__).parent / 'fixtures' / 'large_SLT_example_A.py'
        slt = from_config(config)

        # print(slt)
        slt_spec = slt.derive_spec()

        print(slt_spec)
        assert slt_spec.fault_system_branches[0].short_name == "PUY"
        assert slt_spec.fault_system_branches[0].branches[0].name == 'dm'
        assert slt_spec.fault_system_branches[0].branches[0].long_name == 'deformation model'
        assert slt_spec.fault_system_branches[0].branches[0].value_options == ['']

        assert slt_spec.fault_system_branches[2].short_name == "CRU"
        assert slt_spec.fault_system_branches[2].branches[0].name == 'dm'
        assert slt_spec.fault_system_branches[2].branches[0].long_name == 'deformation model'
        assert slt_spec.fault_system_branches[2].branches[0].value_options == ['geologic']
