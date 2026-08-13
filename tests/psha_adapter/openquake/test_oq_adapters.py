import csv
import warnings

import pytest
from nzshm_common import CodedLocation

from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig
from nzshm_model.psha_adapter.openquake.hazard_config_compat import DEFAULT_HAZARD_CONFIG
from nzshm_model.psha_adapter.openquake.simple_nrml import (
    OpenquakeConfigPshaAdapter,
    OpenquakeGMCMPshaAdapter,
    OpenquakeSourcePshaAdapter,
)


def test_source_adapter(tmp_path, current_model, source_map):
    cache_folder = tmp_path / 'cache'
    target_folder = tmp_path / 'target'
    source_adapter = current_model.source_logic_tree.psha_adapter(OpenquakeSourcePshaAdapter)
    source_filepath = source_adapter.write_config(cache_folder, target_folder, source_map)
    assert source_filepath.exists()


def test_gmcm_adapter(tmp_path, current_model):
    target_folder = tmp_path / 'target'
    gmcm_adapter = current_model.gmm_logic_tree.psha_adapter(OpenquakeGMCMPshaAdapter)
    gmcm_filepath = gmcm_adapter.write_config(target_folder)
    assert gmcm_filepath.exists()


def test_config_adapter(tmp_path, locations):
    target_folder = tmp_path / 'target'
    hazard_config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
    hazard_config.set_sites(locations)
    config_adapter = hazard_config.psha_adapter(OpenquakeConfigPshaAdapter)
    job_filepath = config_adapter.write_config(target_folder)
    assert (target_folder / 'sites.csv').exists()
    assert job_filepath.exists()


def test_config_sitefile(tmp_path, locations):
    site_file = tmp_path / 'sites1.csv'
    hazard_config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
    vs30s = [v / 10.0 for v in range(len(locations))]
    hazard_config.set_sites(locations, vs30=vs30s)
    config_adapter = hazard_config.psha_adapter(OpenquakeConfigPshaAdapter)
    config_adapter.write_site_file(site_file)
    assert site_file.exists()
    with site_file.open() as fin:
        reader = csv.reader(fin)
        header = next(reader)
        assert header == ['lon', 'lat', 'vs30']
        for loc, vs30, row in zip(locations, vs30s, reader, strict=False):
            assert row[0] == str(loc.lon)
            assert row[1] == str(loc.lat)
            assert row[2] == str(vs30)


@pytest.mark.filterwarnings("default")
def test_config_sitefile_deduplicated(tmp_path):
    site_file = tmp_path / 'sites_dup.csv'
    coords = [(-41.3, 174.7), (-41.2, 174.8), (-41.3, 174.7)]
    locations = [CodedLocation(lat, lon, 0.1) for lat, lon in coords]
    hazard_config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
    with pytest.warns(UserWarning, match="duplicate"):
        hazard_config.set_sites(locations)
    config_adapter = hazard_config.psha_adapter(OpenquakeConfigPshaAdapter)
    config_adapter.write_site_file(site_file)

    with site_file.open() as fin:
        reader = csv.reader(fin)
        next(reader)
        rows = [tuple(row) for row in reader]

    assert len(rows) == 2
    assert len(set(rows)) == len(rows)


def test_config_sitefile_mixed_resolution(tmp_path):
    """a coarse grid combined with finer named sites has no coincident points and writes cleanly"""
    site_file = tmp_path / 'sites_mixed.csv'
    locations = [CodedLocation(-41.3, 174.7, 0.1), CodedLocation(-41.25, 174.85, 0.001)]
    hazard_config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        hazard_config.set_sites(locations)
    config_adapter = hazard_config.psha_adapter(OpenquakeConfigPshaAdapter)
    config_adapter.write_site_file(site_file)

    with site_file.open() as fin:
        reader = csv.reader(fin)
        assert next(reader) == ['lon', 'lat']
        rows = [tuple(row) for row in reader]

    assert len(rows) == 2
    assert len(set(rows)) == len(rows)


@pytest.mark.filterwarnings("default")
def test_write_config_warn(tmp_path, locations):
    target_folder = tmp_path / 'target'
    hazard_config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
    hazard_config.set_sites(locations)
    config_adapter = hazard_config.psha_adapter(OpenquakeConfigPshaAdapter)
    with warnings.catch_warnings(record=True) as wngs:
        config_adapter.write_config(target_folder)
        assert len(wngs) > 0, len(wngs)
        assert "not complete" in str(wngs[-1].message)
