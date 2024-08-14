#! python test_logic_tree.py
import json
from pathlib import Path

import pytest

import nzshm_model.psha_adapter.openquake.simple_nrml
from nzshm_model import NshmModel, get_model_version
from nzshm_model.logic_tree import GMCMLogicTree, SourceLogicTree
from nzshm_model.psha_adapter.openquake import OpenquakeGMCMPshaAdapter, OpenquakeModelPshaAdapter

FIXTURE_PATH = Path(__file__).parent.parent.parent / "fixtures"


@pytest.mark.skip("WIP")
def test_source_logic_tree_to_source_xml_basic():

    config = FIXTURE_PATH / 'source_logic_tree_sample_0.json'
    slt = SourceLogicTree.from_json(config)

    print(slt)
    target = FIXTURE_PATH  # noqa
    src_xml = slt.psha_adapter(provider=OpenquakeModelPshaAdapter).write_config(Path('/tmp/DEMO'))  # noqa
    # assert 0


@pytest.mark.skip("WIP")
def test_fetch_resources(monkeypatch, tmp_path):
    def mockreturn(file_id, destination):
        return file_id

    config = FIXTURE_PATH / 'source_logic_tree_sample_2.json'
    slt = SourceLogicTree.from_json(config)

    monkeypatch.setattr(nzshm_model.psha_adapter.openquake.simple_nrml, "fetch_toshi_source", mockreturn)
    result = [
        {'id': _id, 'path': filepath, 'um': um}
        for _id, filepath, um in slt.psha_adapter(provider=OpenquakeModelPshaAdapter).fetch_resources(tmp_path)
    ]

    with Path('test.json').open('w') as jsonfile:
        json.dump(result, jsonfile)


# @pytest.mark.skip("WIP: need way to compare xml without being exact (or create fixture for exact match)")
def test_gmcm_logic_tree_to_xml(tmp_path):

    # xml_filepath = Path(__file__).parent / 'fixtures' / 'gmcm_logic_tree_example_b.xml'
    gmcm_json_filepath = Path(__file__).parent / 'fixtures' / 'gmcm_logic_tree_example.json'
    slt_json_filepath = FIXTURE_PATH / 'source_logic_tree_sample_2.json'

    gmcm_logic_tree = GMCMLogicTree.from_json(gmcm_json_filepath)
    model_v104 = get_model_version('NSHM_v1.0.4')
    model = NshmModel(
        "version",
        "title",
        slt_json_filepath,
        gmcm_json_filepath,
        model_v104._gmm_xml,
        model_v104.hazard_config,
    )
    adapter = model.gmm_logic_tree.psha_adapter(OpenquakeGMCMPshaAdapter)
    # gmcm_logic_tree_expected = adapter.logic_tree_from_xml(xml_filepath)
    # adapter = gmcm_logic_tree
    xml_str = adapter.build_gmcm_xml()
    # gmcm_logic_tree_deserialized = adapter.logic_tree_from_xml(xml_filepath)

    with Path(Path(__file__).parent / 'fixtures' / 'gmcm.xml').open('w') as xmlfile:
        xmlfile.write(adapter.build_gmcm_xml())

    with (tmp_path / 'gmcm_lt.xml').open('w') as xmlfile:
        xmlfile.write(xml_str)
    gmcm_logic_tree_deserialized = adapter.gmcm_logic_tree_from_xml(tmp_path / 'gmcm_lt.xml')

    assert gmcm_logic_tree_deserialized == gmcm_logic_tree
