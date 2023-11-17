#! python test_logic_tree.py

from pathlib import Path

import pytest
from lxml import objectify

from nzshm_model.nrml.logic_tree import NrmlDocument

FIXTURE_PATH = Path(__file__).parent / "fixtures" 

def test_nrml_gmm_logic_tree():

    gmm_logic_tree_path =  FIXTURE_PATH / "TEST_GMM_LT.xml"

    doc = NrmlDocument.from_xml_file(gmm_logic_tree_path)

    logic_trees = list(doc.logic_trees)
    assert len(logic_trees) == 1

    crustal_branch = logic_trees[0].branch_sets[0]
    assert crustal_branch.applyToTectonicRegionType == "Active Shallow Crust"
    assert crustal_branch.branchSetID == "bs_crust"

    assert len(crustal_branch.branches) == 1

    # assert crustal_branch.branches[0].uncertainty_weight == 1.0

    #         for branch in ltbs.branches:
    #             print(branch.uncertainty_models)
    #             print(branch.uncertainty_weight)

    # assert 0


@pytest.mark.parametrize("fixture_file, branch_set_id, branch_id, uncertainty_weight, uncertainty_model", [
    pytest.param("TEST_SRC_LT_example_1.xml", 
        "BS-NONCE1", 
        "CR_3km",
        1.0,
        "SW52ZXJzaW9uU29sdXRpb246MTAwMTkx-ruptures.xml",
        id='example_1'), 
    pytest.param("TEST_SRC_LT_example_2.xml", 
        "BS-NONCE1", 
        "SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEwNjQ2NA==|RmlsZToxMDY1MzM=|SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEwNjQ5Mg==|RmlsZToxMDY1NTQ=|SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEwNjUwNg==|RmlsZToxMDY1NTM=",
        0.0833333,
        "U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTA2MzYw-ruptures.xml",
        id='example_2')    
])
def test_nrml_srm_logic_tree_1(fixture_file, branch_set_id, branch_id, uncertainty_weight, uncertainty_model):

    srm_logic_tree_path =  FIXTURE_PATH / fixture_file
    doc = NrmlDocument.from_xml_file(srm_logic_tree_path)
    logic_trees = list(doc.logic_trees)
    
    #logic tree 0
    assert len(doc.logic_trees) == 1
    assert doc.logic_trees[0].logicTreeID == "Combined"

    # branch_set 0
    assert len(doc.logic_trees[0].branch_sets) == 1
    assert doc.logic_trees[0].branch_sets[0].branchSetID == branch_set_id

    # branch 0
    assert len(doc.logic_trees[0].branch_sets[0].branches) == 1
    assert doc.logic_trees[0].branch_sets[0].branches[0].branchID == branch_id

    #branch uncertainty weight
    assert doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_weight == pytest.approx(uncertainty_weight)

    #branch uncertainty models
    assert uncertainty_model in doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_models[0].text

