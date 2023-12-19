from pathlib import Path

from nzshm_model.psha_adapter import NrmlDocument
from nzshm_model.gmcm_logic_tree.logic_tree import GMCMLogicTree

def test_gmcm_logic_tree_from_xml():
    gmcm_nrml_filepath = Path(__file__).parent / 'fixtures' / 'gmcm_logic_tree_example.xml'
    doc = NrmlDocument.from_xml_file(gmcm_nrml_filepath)

    gmcm_logic_tree = GMCMLogicTree.from_xml(gmcm_nrml_filepath)
    assert len(gmcm_logic_tree.branch_sets) == len(doc.logic_trees[0].branch_sets)
    for i in range(len(gmcm_logic_tree.branch_sets)):
        assert gmcm_logic_tree.branch_sets[i].tectonic_region_type == doc.logic_trees[0].branch_sets[i].applyToTectonicRegionType
    
    assert len(gmcm_logic_tree.branch_sets[0].branches) == len(doc.logic_trees[0].branch_sets[0].branches)
    assert gmcm_logic_tree.branch_sets[0].branches[0].weight == doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_weight
    assert gmcm_logic_tree.branch_sets[0].branches[0].gsim_clsname == 'Stafford2022'
    expected_args = dict(
        mu_branch='Upper'
    )
    assert gmcm_logic_tree.branch_sets[0].branches[0].gsim_args == expected_args
