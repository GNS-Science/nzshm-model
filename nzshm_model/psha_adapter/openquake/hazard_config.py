#!python3 hazard_config.py
"""
Module supporting managed openquake configuration files

 - uses https://docs.python.org/3/library/configparser.html to do the heavy lifting
 - migrated from runzi /runzi/execute/openquake/util/oq_hazard_config.py

"""
import ast
import configparser
import copy
import logging
import pathlib
from typing import Dict, List, TextIO, Union

from .hazard_config_compat import check_invariants, compatible_hash_digest

log = logging.getLogger(__name__)

try:
    from openquake.hazardlib.site import calculate_z1pt0, calculate_z2pt5
except ImportError:
    log.warning(
        """warning openquake module dependency not available, maybe you want to install
                with nzshm-model[openquake]"""
    )


class OpenquakeConfig:
    """Helper class to manage openquake configuration files.

    Examples:
        >>> from nzshm_model.psha_adapter.openquake import (
                OpenquakeConfig,\\
                DEFAULT_HAZARD_CONFIG\\
            )
        ...
        >>> oq_config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)\\
        >>>        .set_description("Hello openquake")\\
        >>>        .set_sites("./sites.csv")\\
        >>>        .set_source_logic_tree_file(str(sources_filepath))\\
        >>>        .set_gsim_logic_tree_file("./gsim_model.xml")\\
        >>>        .set_vs30(750)
        ...
        >>> oq_config.config.get('general', 'description')
        ... Hello openquake
    """

    def __init__(self, default_config: Union[configparser.ConfigParser, Dict, None] = None):
        if isinstance(default_config, configparser.ConfigParser):
            self.config = copy.deepcopy(default_config)
            return

        self.config = configparser.ConfigParser()
        if isinstance(default_config, dict):
            self.config.read_dict(default_config)
        return

    def __eq__(self, other) -> bool:
        if isinstance(other, OpenquakeConfig):
            return self.config == other.config
        return NotImplemented

    @staticmethod
    def read_file(config_file: TextIO) -> 'OpenquakeConfig':
        """produce a OpenquakeConfig from a file-like object

        Arguments:
            config_file: an file-like object with valid .ini contents.

        Returns:
            a new OpenquakeConfig instance.
        """
        config = configparser.ConfigParser()
        config.read_file(config_file)
        return OpenquakeConfig(config)

    def set_source_logic_tree_file(self, source_lt_filepath: Union[str, pathlib.Path]) -> 'OpenquakeConfig':
        """setter for source_model file

        Arguments:
            source_lt_filepath: the path to the source model file.

        Returns:
            the OpenquakeConfig instance.
        """
        self.set_parameter("calculation", "source_model_logic_tree_file", str(source_lt_filepath))
        return self

    def set_parameter(self, section: str, key: str, value: str):
        """a setter for arbitrary string values

        Arguments:
            section: the config table name eg.[site_params]
            key: the key name
            value: the value to set

        Returns:
            the OpenquakeConfig instance.
        """
        assert isinstance(value, str)
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        return self

    def unset_parameter(self, section, key):
        """remove a table entry

        Arguments:
            section: the config table name eg.[site_params]
            key: the key name

        Returns:
            the OpenquakeConfig instance.
        """
        if section in self.config:
            self.config.remove_option(section, key)
        return self

    def set_maximum_distance(self, value: dict[str, int]):
        """set the maximum distance, which is a dictionary

        e.g. `{'Active Shallow Crust': 300.0, 'Volcanic': 300, 'Subduction Interface': 400, 'default': 400}`

        Arguments:
            value: mapping of trt_names and distances

        Returns:
            the OpenquakeConfig instance.
        """
        value_new = {}
        for trt, dist in value.items():
            if isinstance(dist, str):
                value_new[trt] = [tuple(dm) for dm in ast.literal_eval(dist)]
            else:
                value_new[trt] = dist
        self.config.set("calculation", "maximum_distance", str(value_new))
        return self

    def set_sites(self, site_model_filename: Union[str, pathlib.Path]) -> 'OpenquakeConfig':
        """setter for site_model file

        Arguments:
            site_model_filename: the path to the source model file.

        Returns:
            the OpenquakeConfig instance.
        """
        self.set_parameter('site_params', 'site_model_file', str(site_model_filename))
        return self

    # TODO disagg configs might warrant a separate class, and separate defaults ??
    def set_disagg_site_model(self):
        self.clear_sites()
        self.set_parameter('site_params', 'site_model_file', 'site.csv')
        return self

    def set_disagg_site(self, lat, lon):
        self.clear_sites()
        self.set_parameter('site_params', 'sites', f'{lon} {lat}')
        return self

    def set_iml_disagg(self, imt, level):
        self.set_parameter('disagg', 'iml_disagg', str({imt: level}))
        return self

    def clear_iml(self):
        """remove intensity_measure_types_and_levels

        Returns:
            the OpenquakeConfig instance.
        """
        self.unset_parameter('calculation', 'intensity_measure_types_and_levels')
        return self

    def set_iml(self, measures: List[str], levels: List[float]) -> 'OpenquakeConfig':
        """setter for intensity_measure_types_and_levels

        sets the same levels for all intensity measures.

        Arguments:
            measures: the IML types e.g `['PGA', 'SA(0.5)', ...]
            levels: the IML levels as floats  e.g. [0.01, 0.02, 0.04, ...]

        Returns:
            the OpenquakeConfig instance.
        """
        self.clear_iml()
        new_iml = '{'
        for m in measures:
            new_iml += f'"{m}": {str(levels)}, '
        new_iml += '}'

        self.config['calculation']['intensity_measure_types_and_levels'] = new_iml
        return self

    def set_vs30(self, vs30: float):
        """setter for intensity_measure_types_and_levels

        sets the vs30 and supplementary values. These may be overidden later

        Arguments:
            vs30: the desired vs30

        Returns:
            the OpenquakeConfig instance.
        """

        sect = self.config['site_params']
        # clean up old settings
        for setting in [
            'reference_vs30_type',
            'reference_vs30_value',
            'reference_depth_to_1pt0km_per_sec',
            'reference_depth_to_2pt5km_per_sec',
        ]:
            sect.pop(setting, None)

        if vs30 == 0:
            return self

        sect['reference_vs30_type'] = 'measured'
        sect['reference_vs30_value'] = str(vs30)
        sect['reference_depth_to_1pt0km_per_sec'] = str(round(calculate_z1pt0(vs30), 0))
        sect['reference_depth_to_2pt5km_per_sec'] = str(round(calculate_z2pt5(vs30), 1))
        return self

    def set_gsim_logic_tree_file(self, filepath):
        self.set_parameter('calculation', 'gsim_logic_tree_file', filepath)
        return self

    def set_description(self, description):
        self.set_parameter('general', 'description', description)
        return self

    def write(self, tofile: TextIO) -> None:
        """write the OpenquakeConfig to a file-like object

        Arguments:
            tofile: a file-like object
        """
        self.config.write(tofile)

    def compatible_hash_digest(self) -> str:
        """get a shake_256 hash digest for the compatablity config

        We want to ensure that, for this config:

         - all the invariant entries exist
         - entries that will not break calcluation compatibility are ignored

        Returns:
            the 12 character hash_digest.
        """
        check_invariants(self.config)
        return compatible_hash_digest(self.config)
