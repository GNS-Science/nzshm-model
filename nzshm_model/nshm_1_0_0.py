#! v1_0_0.py

import itertools

import nzshm_model.source_logic_tree.SLT_v8_gmm_v2_final as slt_config  # NOQA F401
from nzshm_model.source_logic_tree.logic_tree import (  # SourceLogicTree,
    Branch,
    BranchAttribute,
    BranchAttributeValue,
    FaultSystemLogicTree,
)


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
