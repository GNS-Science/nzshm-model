"""
support for managing NSHM compatability in openquake caclulations
"""

import configparser
import copy
import hashlib
import io

DEFAULT_HAZARD_CONFIG: dict = dict(
    general=dict(
        random_seed=25,
        calculation_mode='classical',
        ps_grid_spacing=30,
    ),
    logic_tree=dict(
        number_of_logic_tree_samples=0,
    ),
    erf=dict(
        rupture_mesh_spacing=4,
        width_of_mfd_bin=0.1,
        complex_fault_mesh_spacing=10.0,
        area_source_discretization=10.0,
    ),
    site_params=dict(
        reference_vs30_type='measured',
    ),
    calculation=dict(
        investigation_time=1.0,
        truncation_level=4,
        maximum_distance={
            'Active Shallow Crust': [(4.0, 0), (5.0, 100.0), (6.0, 200.0), (9.5, 300.0)],
            'Subduction Interface': [(5.0, 0), (6.0, 200.0), (10, 500.0)],
            'Subduction Intraslab': [(5.0, 0), (6.0, 200.0), (10, 500.0)],
        },
    ),
    output=dict(
        individual_curves='true',
    ),
)

ENTRIES_IGNORED = [
    ('general', 'description'),
    ('general', 'random_seed'),
    ('site_params', 'sites_csv'),
    ('site_params', 'sites'),
    ('site_params', 'site_model_file'),
    ('site_params', 'reference_vs30_value'),
    ('site_params', 'reference_depth_to_1pt0km_per_sec'),  # aka z1
    ('site_params', 'reference_depth_to_2pt5km_per_sec'),  # aka z2.5
    ('erf', 'concurrent_tasks'),
    ('calculation', 'source_model_logic_tree_file'),
    ('calculation', 'gsim_logic_tree_file'),
    ('calculation', 'intensity_measure_types_and_levels'),
]

ENTRIES_INVARIANT = [
    ('general', 'calculation_mode', 'classical'),
    ('logic_tree', 'number_of_logic_tree_samples', '0'),
    ('site_params', 'reference_vs30_type', 'measured'),
    (
        'calculation',
        'investigation_time',
        '1.0',
    ),
    ('output', 'individual_curves', 'true'),
]


def check_invariants(config: configparser.ConfigParser) -> bool:
    """check a configuration has all the expected invariant entries"""
    for table, key, value in ENTRIES_INVARIANT:
        try:
            invariant = config.get(table, key)
        except configparser.NoOptionError:
            raise ValueError(f'Expected entry "[{table}]" "{key}"" with value {value} was not found.')
        if invariant == value:
            continue
        raise ValueError(
            f'Expected entry "[{table}]" "{key}"" with value {value} was not found. Got {invariant} instead.'
        )
    return True


def compatible_config(config: configparser.ConfigParser) -> configparser.ConfigParser:
    clean_config = copy.deepcopy(config)
    for table, key in ENTRIES_IGNORED:
        clean_config.remove_option(table, key)
    return clean_config


def compatible_hash_digest(config: configparser.ConfigParser, digest_len: int = 12) -> str:
    """return a 12 character hexdigest for the config"""

    if digest_len % 2 > 0:
        raise ValueError('len: {digest_len} is not divisible by 2')

    check_invariants(config)  # raises an error if not sucessful
    compat = compatible_config(config)
    value = io.StringIO()
    compat.write(value)
    return hashlib.shake_256(value.getvalue().encode()).hexdigest(int(digest_len / 2))
