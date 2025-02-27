import importlib.resources as resources
import json

from nzshm_model.logic_tree import SourceLogicTree
from nzshm_model.logic_tree.source_logic_tree import SourceLogicTreeV1
from nzshm_model.logic_tree.source_logic_tree.version1.logic_tree import FlattenedSourceLogicTree


def test_v2_correlations():

    slt_filepath = resources.files('nzshm_model.resources') / "SRM_JSON" / "nshm_v1.0.4.json"
    with slt_filepath.open() as slt_file:
        slt_v1 = SourceLogicTreeV1.from_dict(json.load(slt_file))
    slt_v2 = SourceLogicTree.from_source_logic_tree(slt_v1)

    assert len(FlattenedSourceLogicTree.from_source_logic_tree(slt_v1).branches) == len(list(slt_v2.composite_branches))
    for branch_v1, branch_v2 in zip(
        FlattenedSourceLogicTree.from_source_logic_tree(slt_v1).branches, slt_v2.composite_branches
    ):
        values_v1 = [b.values for b in branch_v1.branches]
        values_v2 = [b.values for b in branch_v2.branches]
        assert values_v1 == values_v2
        assert branch_v1.weight == branch_v2.weight
