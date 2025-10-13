"""
tests for the OpenquakeConfiguration class
"""

import configparser
import io

# import tomli
import pytest
from nzshm_common.location import CodedLocation

import nzshm_model.psha_adapter.openquake.hazard_config as oqhc
from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig
from nzshm_model.psha_adapter.openquake.hazard_config_compat import (
    DEFAULT_HAZARD_CONFIG,
    check_invariants,
    compatible_config,
    compatible_hash_digest,
)

measures = ['PGA', 'SA(0.5)']

min_expected = """
[general]
ps_grid_spacing = 30
calculation_mode = classical

[logic_tree]
number_of_logic_tree_samples = 0

[erf]
rupture_mesh_spacing = 5
width_of_mfd_bin = 0.1
complex_fault_mesh_spacing = 10.0
area_source_discretization = 10.0

[site_params]
sites_csv = grid-NZ-0.2-0.0003.nb1.nz34.csv
reference_vs30_type = measured
reference_vs30_value = 750
reference_depth_to_1pt0km_per_sec = 44.0 // z1_0
reference_depth_to_2pt5km_per_sec = 0.6  // Z2_5

[calculation]
source_model_logic_tree_file = ./sources/source_model.xml
gsim_logic_tree_file = ./NZ_NSHM_GMM_LT_final_EE.xml
investigation_time = 1.0

truncation_level = 4
maximum_distance = {'Active Shallow Crust': [(4.0, 0), (5.0, 100.0), (6.0, 200.0), (9.5, 300.0)],
                        'Subduction Interface': [(5.0, 0), (6.0, 200.0), (10, 500.0)],
                        'Subduction Intraslab': [(5.0, 0), (6.0, 200.0), (10, 500.0)]}

intensity_measure_types_and_levels  = {"PGA": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(0.1)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(0.2)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(0.3)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(0.4)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(0.5)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(0.7)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(1.0)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(1.5)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(2.0)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(3.0)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(4.0)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], "SA(5.0)": [0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0], }

[output]
individual_curves = true
"""  # noqa


def test_get_iml():
    config = OpenquakeConfig()
    imts = ["PGA", "SA(0.5)"]
    imtls = list(range(10))
    config.set_iml(imts, imtls)
    assert (imts, imtls) == config.get_iml()


def test_get_iml_disagg():
    config = OpenquakeConfig()
    imt = "PGA"
    imtl = 0.1
    config.set_iml_disagg(imt, imtl)
    assert (imt, imtl) == config.get_iml_disagg()


def test_is_complete():
    config = OpenquakeConfig()
    assert not config.is_complete()

    imts = ["PGA", "SA(0.5)"]
    imtls = list(range(10))
    config.set_iml(imts, imtls)
    assert config.is_complete()

    config = OpenquakeConfig()
    imt = "PGA"
    imtl = 0.1
    config.set_iml_disagg(imt, imtl)
    assert config.is_complete()


def test_str():
    config = OpenquakeConfig()
    assert str(config)


def test_config_from_runzi(iml):
    config = (
        OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
        .set_description("hello world")
        .set_site_filepath("./sites.csv")
        .set_source_logic_tree_file("./hello.slt")
        .set_gsim_logic_tree_file("./gsim_model.xml")
        .set_uniform_site_params(750)
    )
    config.set_iml(iml['imts'], iml['imtls'])

    assert config.config['general']['description'] == "hello world"


def test_get(iml):
    config = (
        OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
        .set_description("hello world")
        .set_site_filepath("./sites.csv")
        .set_source_logic_tree_file("./hello.slt")
        .set_gsim_logic_tree_file("./gsim_model.xml")
        .set_uniform_site_params(750)
    )
    config.set_iml(iml['imts'], iml['imtls'])

    assert config.get_iml() == (iml['imts'], iml['imtls'])
    assert str(config.get_site_filepath()) == "sites.csv"
    assert config.get_uniform_site_params()[0] == 750
    assert config.set_parameter("foo", "bar", "foobar")
    assert config.get_parameter("foo", "bar") == "foobar"

    config.clear_iml()
    assert not config.get_iml()


def test_configuration_round_trip(iml):

    nc = (
        OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
        .set_site_filepath('./sites.csv')
        .set_parameter("general", "ps_grid_spacing", "20")
    )

    # levels1 = 'logscale(0.005, 4.00, 30)'

    nc.set_iml(iml['imts'], iml['imtls'])
    nc.set_uniform_site_params(250)
    nc.set_parameter("erf", "rupture_mesh_spacing", "42")

    out = io.StringIO()  # aother fake file
    nc.write(out)
    out.seek(0)
    nc2 = OpenquakeConfig.read_file(out)

    assert nc == nc2

    out.seek(0)
    for n, line in enumerate(out.readlines()):
        print(n, line, end="")

    print()
    print(str(nc))
    print(nc.config.get('general', 'random_seed'))
    # assert 0


def test_default_config():
    config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)  # the default config
    expected = configparser.ConfigParser()
    expected.read_dict(DEFAULT_HAZARD_CONFIG)
    assert config.config == expected


def test_set_maximum_distance():
    config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)  # the default config
    dists = {'Active Shallow Crust': 300.0, 'Volcanic': 300, 'Subduction Interface': 400, 'default': 400}
    config.set_maximum_distance(dists)
    assert config.config.get("calculation", "maximum_distance") == str(dists)


@pytest.fixture(scope='function')
def example_config():
    example = configparser.ConfigParser()
    example.read_file(io.StringIO(min_expected))
    config = OpenquakeConfig(example)
    yield config


def test_uniform_site_params():
    # default z values
    config = OpenquakeConfig()
    vs30_in = 100
    config.set_uniform_site_params(vs30_in)
    vs30, z1pt0, z2pt5 = config.get_uniform_site_params()
    assert vs30 == vs30_in
    assert z1pt0 == pytest.approx(round(oqhc.calculate_z1pt0(vs30_in), 0))
    assert z2pt5 == pytest.approx(round(oqhc.calculate_z2pt5(vs30_in), 1))

    # user specified z values
    config = OpenquakeConfig()
    vs30_in, z1pt0_in, z2pt5_in = (100, 490.0, 2.2)
    config.set_uniform_site_params(vs30_in, z1pt0_in, z2pt5_in)
    vs30, z1pt0, z2pt5 = config.get_uniform_site_params()
    assert vs30 == vs30_in
    assert z1pt0 == pytest.approx(round(z1pt0_in, 0))
    assert z2pt5 == pytest.approx(round(z2pt5_in, 1))


def test_unset_uniform_site_params():
    config = OpenquakeConfig()
    vs30_in = 100
    config.set_uniform_site_params(vs30_in)
    config.unset_uniform_site_params()
    vs30, z1pt0, z2pt5 = config.get_uniform_site_params()
    assert vs30 is None
    assert z1pt0 is None
    assert z2pt5 is None


def test_site_errors(locations):
    config = OpenquakeConfig()
    n_locs = len(locations)

    # vs30 values must be Iterable type
    with pytest.raises(TypeError):
        config.set_sites(locations, vs30=1)

    # vs30 must have same lenth as locations
    with pytest.raises(ValueError):
        config.set_sites(locations, vs30=[100] * (n_locs + 1))

    # cannot set site specific vs30 if uniform is specified
    config = OpenquakeConfig()
    config.set_uniform_site_params(100)

    assert config.set_sites(locations)

    vs30 = list(range(n_locs))
    with pytest.raises(KeyError):
        config.set_sites(locations, vs30=vs30)

    # cannot set uniform vs30 if site specific
    config = OpenquakeConfig()
    config.set_sites(locations, vs30=vs30)
    with pytest.raises(KeyError):
        config.set_uniform_site_params(100)


class TestConfigCompatability:
    def test_compatible_check_invariants(self, example_config):
        assert check_invariants(example_config.config)

    def test_compatible_check_invariant_missing_raises(self, example_config):
        example_config.config.remove_option('general', 'calculation_mode')
        with pytest.raises(ValueError):
            check_invariants(example_config.config)

    def test_compatible_check_invariant_bad_value_raises(self, example_config):
        example_config.config.set('general', 'calculation_mode', 'freddy flinstone')
        with pytest.raises(ValueError):
            check_invariants(example_config.config)

    def test_compatible_config(self, example_config):
        example_config.set_site_filepath('./sites.csv')
        compat = compatible_config(example_config.config)
        assert compat.get('site_params', 'sites_csv', fallback=None) is None
        assert compat.get('site_params', 'site_model_file', fallback=None) is None

    def test_compatible_hash_digest(self, example_config):
        example_config.set_site_filepath('./sites.csv')
        digest = compatible_hash_digest(example_config.config)
        print(digest)
        assert digest == "06f026df641e"

    def test_class_instance_hash_digest(self, example_config):
        assert example_config.compatible_hash_digest() == "06f026df641e"


@pytest.mark.skip("toml is not fully compatible due to use of quoted strings. Let's check if openquake supports this")
def test_toml_conversion():
    config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)  # the default config

    out = io.StringIO()
    config.write(out)
    out.seek(0)

    for n, line in enumerate(out.readlines()):
        print(n, line)

    tc = tomli.loads(out.getvalue())  # noqa

    assert tc['general']['random_seed'] == 25

    """
    assert 0
    io1 = io.StringIO()
    io2 = io.StringIO()
    self.config.write(io1)
    other.config.write(io2)


    # return tomli.loads(io1.getvalue()) == tomli.loads(io2.getvalue())
    # print('io1', len(io1.getvalue()), io1.getvalue()[:10], f'|{io1.getvalue()[-10:]}|')
    # print('io2', len(io2.getvalue()), io2.getvalue()[:10], f'|{io2.getvalue()[-10:]}|')
    print('io1', io1.getvalue().replace(' ', '.'))
    print('io2', io2.getvalue().replace(' ', '.'))

    d = difflib.Differ()
    result = list(d.compare(io1.getvalue().splitlines(keepends=True), io2.getvalue().splitlines(keepends=True)))
    pprint(result)

    return io2.getvalue() == io1.getvalue()
    """


def test_write_read_oq_config(tmp_path):
    config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)

    json_filepath = tmp_path / 'hazard_config.json'
    config.to_json(json_filepath)

    config_from_file = OpenquakeConfig().from_json(json_filepath)

    assert config_from_file.config.sections() == config.config.sections()
    for section in config.config.sections():
        assert config_from_file.config.options(section) == config.config.options(section)
        for option in config.config.options(section):
            assert config_from_file.config.get(section, option) == config.config.get(section, option)

    assert config_from_file.locations == config.locations
    assert config_from_file._site_parameters == config._site_parameters


def test_write_read_oq_config_site_params(tmp_path):
    config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)
    locations = [CodedLocation(lat, lon, 0.001) for lat, lon in zip(range(10), range(10))]
    vs30s = [v / 10.0 for v in range(len(locations))]
    config.set_sites(locations, vs30=vs30s)

    json_filepath = tmp_path / 'hazard_config.json'
    config.to_json(json_filepath)

    config_from_file = OpenquakeConfig().from_json(json_filepath)

    assert config_from_file.config.sections() == config.config.sections()
    for section in config.config.sections():
        assert config_from_file.config.options(section) == config.config.options(section)
        for option in config.config.options(section):
            assert config_from_file.config.get(section, option) == config.config.get(section, option)

    assert config_from_file._site_parameters == config._site_parameters
    assert config_from_file.locations == config.locations
