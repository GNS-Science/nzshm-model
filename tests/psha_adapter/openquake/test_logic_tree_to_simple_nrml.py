#! python test_logic_tree.py

from pathlib import Path

import pytest

from nzshm_model.gmcm_logic_tree import GMCMLogicTree
from nzshm_model.psha_adapter.openquake import OpenquakeSimplePshaAdapter
from nzshm_model.source_logic_tree.version2 import SourceLogicTree

FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures"


@pytest.mark.skip("WIP")
def test_source_logic_tree_to_source_xml_basic():

    config = FIXTURE_PATH / 'source_logic_tree_sample_0.json'
    slt = SourceLogicTree.from_json(config)

    print(slt)
    target = FIXTURE_PATH  # noqa
    src_xml = slt.psha_adapter(provider=OpenquakeSimplePshaAdapter).write_config(Path('/tmp/DEMO'))  # noqa
    # assert 0


@pytest.mark.skip("WIP: need way to compare xml without being exact (or create fixture for exact match)")
def test_gmcm_logic_tree_to_xml():

    gmcm_json_filepath = Path(__file__).parent.parent.parent / 'fixtures' / 'gmcm_logic_tree_example.json'
    gmcm_nrml_filepath = Path(__file__).parent.parent.parent / 'fixtures' / 'gmcm_logic_tree_example_b.xml'

    gmcm_logic_tree = GMCMLogicTree.from_json(gmcm_json_filepath)
    adapter = gmcm_logic_tree.psha_adapter(OpenquakeSimplePshaAdapter)

    with gmcm_nrml_filepath.open() as gmcm_expected_file:
        xml_expected = gmcm_expected_file.read()
        xml_output = adapter.build_gmcm_xml()
        assert xml_output == xml_expected
