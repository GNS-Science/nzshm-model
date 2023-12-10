"""
test ability to migrate a v1 slt to v2
"""

# from pathlib import Path

import nzshm_model
from nzshm_model.source_logic_tree.version2 import SourceLogicTree


def test_migrate_NSHM_v1_0_4():

    # get a published v1 logic tree

    slt = nzshm_model.get_model_version('NSHM_v1.0.4').source_logic_tree()

    v2 = SourceLogicTree.from_source_logic_tree(slt)

    assert v2.version == slt.version
    # assert v2.fault_systems[0].short_name == slt.fault_systems[0].short_name
    # assert 0
