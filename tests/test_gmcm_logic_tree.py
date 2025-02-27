from pathlib import Path

import pytest

from nzshm_model import get_model_version
from nzshm_model.logic_tree import GMCMLogicTree
from nzshm_model.psha_adapter.openquake import NrmlDocument
from nzshm_model.psha_adapter.openquake.simple_nrml import OpenquakeGMCMPshaAdapter

gmcm_nrml_filepath = Path(__file__).parent / 'fixtures' / 'gmcm_logic_tree_example.xml'
gmcm_json_filepath = Path(__file__).parent / 'fixtures' / 'gmcm_logic_tree_example.json'

adapter = get_model_version('NSHM_v1.0.4').gmm_logic_tree.psha_adapter(OpenquakeGMCMPshaAdapter)
gmcm_logic_tree_fromxml = adapter.gmcm_logic_tree_from_xml(gmcm_nrml_filepath)  # type: ignore
gmcm_logic_tree_fromjson = GMCMLogicTree.from_json(gmcm_json_filepath)


def test_gmcm_logic_tree_from_xml():
    doc = NrmlDocument.from_xml_file(gmcm_nrml_filepath)
    gmcm_logic_tree = gmcm_logic_tree_fromxml

    assert len(gmcm_logic_tree.branch_sets) == len(doc.logic_trees[0].branch_sets)
    # for i in range(len(gmcm_logic_tree.branch_sets)):
    #     assert (
    #         gmcm_logic_tree.branch_sets[i].tectonic_region_type
    #         == doc.logic_trees[0].branch_sets[i].applyToTectonicRegionType
    #     )

    assert len(gmcm_logic_tree.branch_sets[0].branches) == len(doc.logic_trees[0].branch_sets[0].branches)
    assert (
        gmcm_logic_tree.branch_sets[0].branches[0].weight
        == doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_weight
    )
    assert gmcm_logic_tree.branch_sets[0].branches[0].gsim_name == 'Stafford2022'
    expected_args = dict(mu_branch='Upper')
    assert gmcm_logic_tree.branch_sets[0].branches[0].gsim_args == expected_args


def test_serialize_gmcm_logic_tree():
    lt_as_dict = gmcm_logic_tree_fromjson.to_dict()
    gmcm_logic_tree = GMCMLogicTree.from_dict(lt_as_dict)
    assert gmcm_logic_tree == gmcm_logic_tree_fromjson


@pytest.mark.parametrize("gmcm_logic_tree", [gmcm_logic_tree_fromxml, gmcm_logic_tree_fromjson])
def test_float_args(gmcm_logic_tree):
    def is_number(value):
        return value.replace("-", "").replace(".", "").replace("e", "").isnumeric()

    for branch_set in gmcm_logic_tree.branch_sets:
        for branch in branch_set.branches:
            for value in branch.gsim_args.values():
                if is_number(str(value)):
                    assert isinstance(value, float)
