#! python test_logic_tree.py

import dataclasses

import nzshm_model
from nzshm_model.source_logic_tree.logic_tree import (
    Branch,
    BranchAttribute,
    BranchAttributeValue,
    FaultSystemLogicTree,
    SourceLogicTree,
)


def test_direct_bav():
    bav = BranchAttributeValue(
        name='dm', long_name='deformation model', value_options=['geodetic', 'Geologic'], value="geodetic"
    )
    print(bav)
    assert bav.value == "geodetic"


def test_direct_bav_no_options():
    bav = BranchAttributeValue(name='dm', long_name='deformation model', value="geodetic")
    print(bav)
    assert bav.value == "geodetic"


def test_init():
    ba = BranchAttribute(name='C', long_name='area-magnitude scaling', value_options=[4.0])
    print(ba)

    bao = BranchAttributeValue.from_branch_attribute(ba, 4)
    print(bao)

    b = Branch(values=[bao], weight=0.5, inversion_source='ABC')
    print(b)

    f = FaultSystemLogicTree('Hik', 'Hikurangi', [b])
    print(f)
    assert f.branches[0].values[0].value == 4


def test_fslt_example():
    model_v1_0_0 = nzshm_model.get_model_version('NSHM_1.0.0')['model']
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
    model_v1_0_0 = nzshm_model.get_model_version('NSHM_1.0.0')['model']
    slt = SourceLogicTree(fault_system_branches=[model_v1_0_0.build_crustal_branches()])
    print(slt)
    assert slt.fault_system_branches[0].branches[-1].values[0].name == 'C'


def test_serialise_slt():
    model_v1_0_0 = nzshm_model.get_model_version('NSHM_1.0.0')['model']
    slt = SourceLogicTree(fault_system_branches=[model_v1_0_0.build_crustal_branches()])

    slt_dict = dataclasses.asdict(slt)
    print(slt_dict)
    assert (
        slt.fault_system_branches[0].branches[-1].values[0].name
        == slt_dict['fault_system_branches'][0]['branches'][-1]['values'][0]['name']
    )