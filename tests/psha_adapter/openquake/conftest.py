from pathlib import Path

import pytest


@pytest.fixture
def source_map(current_model):
    smap = {}
    for branch in current_model.source_logic_tree:
        for source in branch.sources:
            nrml_id = source.nrml_id
            smap[nrml_id] = [
                Path(f"path/to/{nrml_id}.xml"),
            ]
    return smap
