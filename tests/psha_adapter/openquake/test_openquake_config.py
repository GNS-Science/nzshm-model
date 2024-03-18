"""
tests for the OpenquakeConfiguration class
"""
import io
from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig


_4_sites_levels = [
    0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
    1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0
]
_4_sites_measures = [
    'PGA', "SA(0.1)", "SA(0.2)", "SA(0.3)", "SA(0.4)", "SA(0.5)", "SA(0.7)",
    "SA(1.0)", "SA(1.5)", "SA(2.0)", "SA(3.0)", "SA(4.0)", "SA(5.0)"
]

def test_config_from_runzi():
    config = OpenquakeConfig()\
        .set_description("hello world")\
        .set_sites("./sites.csv")\
        .set_source_logic_tree_file("./hello.slt")\
        .set_gsim_logic_tree_file("./gsim_model.xml")\
        .set_vs30(750)
    config.set_iml(_4_sites_measures, _4_sites_levels)

    assert config.config['general']['description'] == "hello world"

def test_configuration_round_trip():

    nc = OpenquakeConfig()\
        .set_sites('./sites.csv')\
        .set_parameter("general", "ps_grid_spacing", 20)

    measures = ['PGA', 'SA(0.5)']
    levels0 = [
        0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
        1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.5, 4, 4.5, 5.0
    ]
    # levels1 = 'logscale(0.005, 4.00, 30)'

    nc.set_iml(_4_sites_measures, _4_sites_levels)
    nc.set_vs30(250)
    nc.set_parameter("erf", "rupture_mesh_spacing", 42)

    out = io.StringIO()  # aother fake file
    nc.write(out)
    out.seek(0)
    nc2 = OpenquakeConfig.read_file(out)

    assert nc == nc2

    # for l in out:
    #     print(l, end="")

    # assert 0