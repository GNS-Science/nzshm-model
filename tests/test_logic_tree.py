#! python test_logic_tree.py

import dataclasses
import importlib.resources as resources
import itertools
from pathlib import Path

import pytest

from nzshm_model.logic_tree.source_logic_tree.branch_attribute import BranchAttributeSpec
from nzshm_model.logic_tree.source_logic_tree.version1.logic_tree import (
    Branch,
    BranchAttributeValue,
    CompositeBranch,
    FaultSystemLogicTree,
    FlattenedSourceLogicTree,
    SourceLogicTree,
    SourceLogicTreeCorrelation,
)
from nzshm_model.logic_tree.source_logic_tree.version1.slt_config import from_config


def test_composite_branch():
    ba0 = BranchAttributeSpec(name='C', long_name='area-magnitude scaling', value_options=[4.0])
    ba1 = BranchAttributeSpec(name='b', long_name='GR b value', value_options=[1.0])
    print(ba0, ba1)

    bav0 = BranchAttributeValue.from_branch_attribute(ba0, 4)
    bav1 = BranchAttributeValue.from_branch_attribute(ba1, 1.0)
    print(bav0, bav1)

    b0 = Branch(values=[bav0], weight=0.25, onfault_nrml_id='ABC')
    b1 = Branch(values=[bav1], weight=0.5, onfault_nrml_id='XYZ')
    print(b0, b1)

    cb = CompositeBranch([b0, b1], 10.0)
    assert cb.weight == pytest.approx(0.25 * 0.5)


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


def build_crustal_branches():
    # define the branch attributes for our FaultSystemLogicTree
    C = BranchAttributeValue.all_from_branch_attribute(
        BranchAttributeSpec(name='C', long_name='area-magnitude scaling', value_options=[4])
    )
    s = BranchAttributeValue.all_from_branch_attribute(
        BranchAttributeSpec(name='s', long_name='moment rate scaling', value_options=[0.5, 1.0])
    )
    bN = BranchAttributeValue.all_from_branch_attribute(
        BranchAttributeSpec(name='bN', long_name='bN pair', value_options=[(0.87, 25), (0.95, 19.2)])
    )
    dm = BranchAttributeValue.all_from_branch_attribute(
        BranchAttributeSpec(name='dm', long_name='deformation model', value_options=['Geodetic', 'Geologic'])
    )

    crustal_branches = FaultSystemLogicTree('Cru', 'Crustal')
    for a, b, c, d in itertools.product(C, s, bN, dm):
        crustal_branches.branches.append(Branch(values=[a, b, c, d], weight=0.125, onfault_nrml_id='ABC'))
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

    slt = SourceLogicTree('NSHM_1.0.0', 'initial', fault_system_lts=[build_crustal_branches()])
    print(slt)
    assert slt.fault_system_lts[0].branches[-1].values[0].name == 'C'


def test_serialise_slt():

    slt = SourceLogicTree('NSHM_1.0.0', 'initial', fault_system_lts=[build_crustal_branches()])

    slt_dict = dataclasses.asdict(slt)
    print(slt_dict)
    assert (
        slt.fault_system_lts[0].branches[-1].values[0].name
        == slt_dict['fault_system_lts'][0]['branches'][-1]['values'][0]['name']
    )


class TestSourceLogicTreeSpecification:
    def test_slt_v8(self):
        config = resources.files('nzshm_model.resources') / 'SRM_LTs' / 'python' / 'SLT_v8_gmm_v2_final.py'
        slt = from_config(config)

        slt_spec = slt.derive_spec()

        print(slt_spec)
        assert slt_spec.fault_system_lts[0].branches[0].name == 'dm'
        assert slt_spec.fault_system_lts[0].branches[0].long_name == 'deformation model'
        assert slt_spec.fault_system_lts[0].branches[0].value_options == ['0.7']

        assert slt_spec.fault_system_lts[2].branches[0].name == 'dm'
        assert slt_spec.fault_system_lts[2].branches[0].long_name == 'deformation model'
        assert slt_spec.fault_system_lts[2].branches[0].value_options == ['geodetic', 'geologic']

    def test_large_SLT_example_A_crustal(self):
        config = Path(__file__).parent / 'fixtures' / 'large_SLT_example_A.py'
        slt = from_config(config)

        # print(slt)
        slt_spec = slt.derive_spec()

        print(slt_spec)
        assert slt_spec.fault_system_lts[0].short_name == "PUY"
        assert slt_spec.fault_system_lts[0].branches[0].name == 'dm'
        assert slt_spec.fault_system_lts[0].branches[0].long_name == 'deformation model'
        assert slt_spec.fault_system_lts[0].branches[0].value_options == ['']

        assert slt_spec.fault_system_lts[2].short_name == "CRU"
        assert slt_spec.fault_system_lts[2].branches[0].name == 'dm'
        assert slt_spec.fault_system_lts[2].branches[0].long_name == 'deformation model'
        assert slt_spec.fault_system_lts[2].branches[0].value_options == ['geologic']


class TestFlattenedSourceLogicTree:
    def setup_method(self):
        ba0 = BranchAttributeSpec(name='C', long_name='area-magnitude scaling', value_options=[4.0, 4.1, 4.2])
        ba1 = BranchAttributeSpec(name='C', long_name='area-magnitude scaling', value_options=[4.1, 4.2, 4.3])

        self.bavs0 = list(BranchAttributeValue.all_from_branch_attribute(ba0))
        self.bavs1 = list(BranchAttributeValue.all_from_branch_attribute(ba1))
        branches0 = [Branch([bav], 1.0 / 3.0) for bav in self.bavs0]
        branches1 = [Branch([bav], 1.0 / 3.0) for bav in self.bavs1]

        self.fault_system0 = FaultSystemLogicTree('A', 'fault system A', branches0)
        self.fault_system1 = FaultSystemLogicTree('B', 'fault system B', branches1)

    def test_flattened_slt(self):

        slt = SourceLogicTree('v1', 'slt', [self.fault_system0, self.fault_system1])
        flattened_lt = FlattenedSourceLogicTree.from_source_logic_tree(slt)
        assert len(flattened_lt.branches) == 9
        assert sum([b.weight for b in flattened_lt.branches]) == pytest.approx(1.0)

    def test_correlated_flattened_slt(self):

        correlations = [
            SourceLogicTreeCorrelation('A', 'B', [bav0], [bav1]) for bav0, bav1 in zip(self.bavs0, self.bavs1)
        ]

        slt = SourceLogicTree('v1', 'correlated slt', [self.fault_system0, self.fault_system1])
        slt.correlations = correlations
        flattened_lt = FlattenedSourceLogicTree.from_source_logic_tree(slt)

        assert len(flattened_lt.branches) == 3
        assert sum([b.weight for b in flattened_lt.branches]) == pytest.approx(1.0)
