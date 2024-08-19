from pathlib import Path

import pytest
from nzshm_common import CodedLocation


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


@pytest.fixture
def locations():
    return [CodedLocation(lat, lon, 0.001) for lat, lon in zip(range(10), range(10))]


@pytest.fixture
def iml():
    _4_sites_levels = [
        0.01,
        0.02,
        0.04,
        0.06,
        0.08,
        0.1,
        0.2,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        0.8,
        0.9,
        1.0,
        1.2,
        1.4,
        1.6,
        1.8,
        2.0,
        2.2,
        2.4,
        2.6,
        2.8,
        3.0,
        3.5,
        4,
        4.5,
        5.0,
    ]
    _4_sites_measures = [
        'PGA',
        "SA(0.1)",
        "SA(0.2)",
        "SA(0.3)",
        "SA(0.4)",
        "SA(0.5)",
        "SA(0.7)",
        "SA(1.0)",
        "SA(1.5)",
        "SA(2.0)",
        "SA(3.0)",
        "SA(4.0)",
        "SA(5.0)",
    ]
    return {'imts': _4_sites_measures, 'imtls': _4_sites_levels}
