#! python test_logic_tree.py

from nzshm_model.source_logic_tree.logic_tree import (
    BranchAttribute,
    BranchAttributeValue,
    Branch,
    FaultSystemLogicTree,
    SourceLogicTree,
)
import itertools


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


def build_crustal_branches():
    # define the branch attributes for our FaultSystemLogicTree
    C = BranchAttributeValue.all_from_branch_attribute(
        BranchAttribute(name='C', long_name='area-magnitude scaling', value_options=[4])
    )
    s = BranchAttributeValue.all_from_branch_attribute(
        BranchAttribute(name='s', long_name='moment rate scaling', value_options=[0.5, 1.0])
    )
    bN = BranchAttributeValue.all_from_branch_attribute(
        BranchAttribute(name='bN', long_name='bN pair', value_options=[(0.87, 25), (0.95, 19.2)])
    )
    dm = BranchAttributeValue.all_from_branch_attribute(
        BranchAttribute(name='dm', long_name='deformation model', value_options=['Geodetic', 'Geologic'])
    )

    crustal_branches = FaultSystemLogicTree('Cru', 'Crustal')
    for (a, b, c, d) in itertools.product(C, s, bN, dm):
        crustal_branches.branches.append(Branch(values=[a, b, c, d], weight=0.125, inversion_source='ABC'))
    return crustal_branches


def test_fslt_example():
    fslt = build_crustal_branches()
    print(fslt)
    assert fslt.branches[-1].values[0].name == 'C'
    assert fslt.branches[-1].values[0].long_name == 'area-magnitude scaling'
    assert fslt.branches[-1].values[0].value == 4

    assert fslt.branches[-1].values[1].value == 1.0
    assert fslt.branches[-1].values[2].value == (0.95, 19.2)
    assert fslt.branches[-1].values[3].value == 'Geologic'

    assert fslt.validate_weights()


def test_full_slt():
    slt = SourceLogicTree(fault_system_branches=[build_crustal_branches()])
    print(slt)
    assert slt.fault_system_branches[0].branches[-1].values[0].name == 'C'
