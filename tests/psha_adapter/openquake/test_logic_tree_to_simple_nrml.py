#! python test_logic_tree.py

from pathlib import Path

import pytest

from nzshm_model.psha_adapter import OpenquakeSimplePshaAdapter
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
