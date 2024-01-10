#! python test_logic_tree.py

import tempfile
from pathlib import Path

import pytest

from nzshm_model.logic_tree import GMCMLogicTree, SourceLogicTree
from nzshm_model.psha_adapter.openquake import OpenquakeSimplePshaAdapter

FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures"


@pytest.mark.skip("WIP")
def test_source_logic_tree_to_source_xml_basic():

    config = FIXTURE_PATH / 'source_logic_tree_sample_0.json'
    slt = SourceLogicTree.from_json(config)

    print(slt)
    target = FIXTURE_PATH  # noqa
    src_xml = slt.psha_adapter(provider=OpenquakeSimplePshaAdapter).write_config(Path('/tmp/DEMO'))  # noqa
    # assert 0


# @pytest.mark.skip("WIP: need way to compare xml without being exact (or create fixture for exact match)")
def test_gmcm_logic_tree_to_xml():

    # xml_filepath = Path(__file__).parent / 'fixtures' / 'gmcm_logic_tree_example_b.xml'
    json_filepath = Path(__file__).parent / 'fixtures' / 'gmcm_logic_tree_example.json'
    gmcm_logic_tree = GMCMLogicTree.from_json(json_filepath)
    adapter = gmcm_logic_tree.psha_adapter(OpenquakeSimplePshaAdapter)
    # gmcm_logic_tree_expected = adapter.logic_tree_from_xml(xml_filepath)
    # adapter = gmcm_logic_tree
    xml_str = adapter.build_gmcm_xml()
    # gmcm_logic_tree_deserialized = adapter.logic_tree_from_xml(xml_filepath)

    with Path(Path(__file__).parent / 'fixtures' / 'gmcm.xml').open('w') as xmlfile:
        xmlfile.write(adapter.build_gmcm_xml())

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(Path(tmpdir, 'gmcm_lt.xml'), 'w') as xmlfile:
            xmlfile.write(xml_str)
        gmcm_logic_tree_deserialized = adapter.logic_tree_from_xml(Path(tmpdir, 'gmcm_lt.xml'))

    assert gmcm_logic_tree_deserialized == gmcm_logic_tree
