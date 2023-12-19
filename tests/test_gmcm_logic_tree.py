import unittest
from pathlib import Path

from nzshm_model.gmcm_logic_tree.logic_tree import GMCMLogicTree
from nzshm_model.psha_adapter.openquake import NrmlDocument
from nzshm_model.psha_adapter.openquake.simple_nrml import OpenquakeSimplePshaAdapter


class TestGMCMLogicTree(unittest.TestCase):
    def setUp(self) -> None:
        self.gmcm_nrml_filepath = Path(__file__).parent / 'fixtures' / 'gmcm_logic_tree_example.xml'
        self.gmcm_json_filepath = Path(__file__).parent / 'fixtures' / 'gmcm_logic_tree_example.json'

        adapter = GMCMLogicTree().psha_adapter(OpenquakeSimplePshaAdapter)
        self.gmcm_logic_tree_fromxml = adapter.logic_tree_from_xml(self.gmcm_nrml_filepath)
        # self.gmcm_logic_tree_fromxml = GMCMLogicTree.from_xml(self.gmcm_nrml_filepath)
        self.gmcm_logic_tree_fromjson = GMCMLogicTree.from_json(self.gmcm_json_filepath)

        return super().setUp()

    def test_gmcm_logic_tree_from_xml(self):
        doc = NrmlDocument.from_xml_file(self.gmcm_nrml_filepath)
        gmcm_logic_tree = self.gmcm_logic_tree_fromxml

        assert len(gmcm_logic_tree.branch_sets) == len(doc.logic_trees[0].branch_sets)
        for i in range(len(gmcm_logic_tree.branch_sets)):
            assert (
                gmcm_logic_tree.branch_sets[i].tectonic_region_type
                == doc.logic_trees[0].branch_sets[i].applyToTectonicRegionType
            )

        assert len(gmcm_logic_tree.branch_sets[0].branches) == len(doc.logic_trees[0].branch_sets[0].branches)
        assert (
            gmcm_logic_tree.branch_sets[0].branches[0].weight
            == doc.logic_trees[0].branch_sets[0].branches[0].uncertainty_weight
        )
        assert gmcm_logic_tree.branch_sets[0].branches[0].gsim_clsname == 'Stafford2022'
        expected_args = dict(mu_branch='Upper')
        assert gmcm_logic_tree.branch_sets[0].branches[0].gsim_args == expected_args

    def test_gmcm_logic_tree_from_json(self):
        gmcm_logic_tree = self.gmcm_logic_tree_fromjson

        assert gmcm_logic_tree == self.gmcm_logic_tree_fromxml

    def test_serialize_gmcm_logic_tree(self):
        lt_as_dict = self.gmcm_logic_tree_fromjson.to_dict()
        gmcm_logic_tree = GMCMLogicTree.from_dict(lt_as_dict)
        assert gmcm_logic_tree == self.gmcm_logic_tree_fromjson
