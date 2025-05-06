import importlib.resources as resources

import pytest
from nzshm_common.location import CodedLocation

from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig
from nzshm_model.psha_adapter.openquake.hazard_config_compat import DEFAULT_HAZARD_CONFIG
from nzshm_model.psha_adapter.openquake.simple_nrml import OpenquakeConfigPshaAdapter


@pytest.fixture
def basic_config():
    return [CodedLocation(lat, lon, 0.001) for lat, lon in zip(range(10), range(10))]


@pytest.fixture(scope="function")
def config_site_specific(locations) -> OpenquakeConfig:

    config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)

    imts = ["PGA", "SA(0.5)"]
    imtls = [float(i) for i in list(range(10))]
    config.set_iml(imts, imtls)

    vs30s = [(v + 1.0) / 10.0 for v in range(len(locations))]
    config.set_sites(locations, vs30=vs30s)

    return config


@pytest.fixture(scope="function")
def config_uniform_sites(locations) -> OpenquakeConfig:

    config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)

    imts = ["PGA", "SA(0.5)"]
    imtls = [float(i) for i in list(range(10))]
    config.set_iml(imts, imtls)

    config.set_sites(locations)
    config.set_uniform_site_params(vs30=500)

    return config


@pytest.mark.parametrize("ini_filename", ["job_0.ini", "job_1.ini", "job_2.ini", "job_3.ini"])
def test_read_oqini(ini_filename):

    fixtures_dir = resources.files('tests.psha_adapter.openquake.fixtures.openquake_hazard_configs')
    ini_filepath = fixtures_dir / ini_filename

    config = OpenquakeConfig()
    adapter: OpenquakeConfigPshaAdapter = config.psha_adapter(OpenquakeConfigPshaAdapter)
    assert adapter.read_config(ini_filepath)


# NB locations and site parameters are not preserved in round trip.
# This is because when writing an ini file they are seperate files
@pytest.mark.parametrize("config", ("config_site_specific", "config_uniform_sites"))
def test_read_oqini_roundtrip(tmp_path, config, request):

    config = request.getfixturevalue(config)
    adapter: OpenquakeConfigPshaAdapter = config.psha_adapter(OpenquakeConfigPshaAdapter)
    ini_filepath = adapter.write_config(tmp_path)
    config_from_ini: OpenquakeConfig = adapter.read_config(ini_filepath)

    # which equality should be used?
    assert config_from_ini.compatible_hash_digest() == config.compatible_hash_digest()
    assert config_from_ini == config
