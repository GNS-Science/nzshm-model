import importlib.resources as resources
import pytest

from nzshm_common.location import CodedLocation

from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig
from nzshm_model.psha_adapter.openquake.simple_nrml import OpenquakeConfigPshaAdapter

from nzshm_model.psha_adapter.openquake.hazard_config_compat import DEFAULT_HAZARD_CONFIG, ENTRIES_INVARIANT


@pytest.mark.parametrize("ini_filename", ["job_0.ini", "job_1.ini", "job_2.ini", "job_3.ini"])
def test_read_oqini(ini_filename):
    
    fixtures_dir = resources.files('tests.psha_adapter.openquake.fixtures.openquake_hazard_configs')
    ini_filepath =  fixtures_dir / ini_filename

    config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
    locations = [CodedLocation(lat, lon, 0.001) for lat, lon in zip(range(10), range(10))]
    vs30s = [v / 10.0 for v in range(len(locations))]
    config.set_sites(locations, vs30=vs30s)
    adapter: OpenquakeConfigPshaAdapter = config.psha_adapter(OpenquakeConfigPshaAdapter)
    assert adapter.config_from_oq_ini(ini_filepath)


def test_read_oqini_roundtrip(tmp_path):

    config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
    for entry in ENTRIES_INVARIANT:
        config.set_parameter(*entry)

    locations = [CodedLocation(lat, lon, 0.001) for lat, lon in zip(range(10), range(10))]
    vs30s = [v / 10.0 for v in range(len(locations))]
    config.set_sites(locations, vs30=vs30s)

    adapter: OpenquakeConfigPshaAdapter = config.psha_adapter(OpenquakeConfigPshaAdapter)
    ini_filepath = adapter.write_config(tmp_path)
    config_from_ini: OpenquakeConfig = adapter.config_from_oq_ini(ini_filepath)

    # which equality should be used?
    assert config_from_ini.compatible_hash_digest() == config.compatible_hash_digest()
    assert config_from_ini == config