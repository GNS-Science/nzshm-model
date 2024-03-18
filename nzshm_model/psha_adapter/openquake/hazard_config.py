#!python3 hazard_config.py
"""
Class to manage openquake configuration files

 - uses https://docs.python.org/3/library/configparser.html to do the heavy lifting
 - migrated from runzi /runzi/execute/openquake/util/oq_hazard_config.py

"""
import logging
import configparser
import copy

from typing import TextIO, Union, Dict

from openquake.hazardlib.site import calculate_z1pt0, calculate_z2pt5
from .hazard_config_compat import check_invariants, compatible_hash_digest, DEFAULT_HAZARD_CONFIG

log = logging.getLogger(__name__)


class OpenquakeConfig():
    """Help class to manage openquake configuration files"""

    def __init__(self, default_config: Union[configparser.ConfigParser, Dict, None] = None):
        if isinstance(default_config, configparser.ConfigParser):
            self.config = copy.deepcopy(default_config)
            return

        self.config = configparser.ConfigParser()
        if isinstance(default_config, dict):
            self.config.read_dict(default_config)
        return

    def __eq__(self, other: 'OpenquakeConfig') -> bool:
        if isinstance(other, OpenquakeConfig):
            return self.config == other.config
        return NotImplemented

    @staticmethod
    def read_file(config_file:TextIO) -> 'OpenquakeConfig':
        config = configparser.ConfigParser()
        config.read_file(config_file)
        return OpenquakeConfig(config)

    def set_source_logic_tree_file(self, source_lt_filepath):
        self.set_parameter("calculation", "source_model_logic_tree_file", source_lt_filepath)
        return self

    def set_parameter(self, parameter_table, parameter_name, value):
        self.unset_parameter(parameter_table, parameter_name)
        if (parameter_table == "calculation") & (parameter_name == "maximum_distance"):
            self.set_maximum_distance(value)
        else:
            if not self.config.has_section(parameter_table):
                self.config.add_section(parameter_table)
            self.config[parameter_table][parameter_name] = str(value)
        return self

    def unset_parameter(self, parameter_table, parameter_name):
        if parameter_table not in self.config:
            return
        else:
            self.config[parameter_table].pop(parameter_name, None)

    def set_maximum_distance(self, value):
        import ast
        value_new = {}
        for trt, dist in value.items():
            if isinstance(dist, str):
                value_new[trt] = [tuple(dm) for dm in ast.literal_eval(dist)]
            else:
                value_new[trt] = [tuple(dm) for dm in dist]
        self.config["calculation"]["maximum_distance"] = str(value_new)
        return self

    def set_sites(self, site_model_filename):
        self.set_parameter('site_params', 'site_model_file', site_model_filename)
        return self

    #TODO disagg configs might warrant a separate class, and separate defaults ??
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
        self.config['calculation'].pop('intensity_measure_types_and_levels', None)
        return self

    def set_iml(self, measures: list, levels: object):
        self.clear_iml()
        new_iml = '{'
        for m in measures:
            new_iml += f'"{m}": {str(levels)}, '
        new_iml += '}'

        self.config['calculation']['intensity_measure_types_and_levels'] = new_iml
        return self

    def set_vs30(self, vs30):

        sect = self.config['site_params']
        # clean up old settings
        for setting in [
            'reference_vs30_type', 'reference_vs30_value',
            'reference_depth_to_1pt0km_per_sec', 'reference_depth_to_2pt5km_per_sec'
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

    def write(self, tofile):
        self.config.write(tofile)

    def compatible_hash_digest(self):
        check_invariants(self.config)
        return compatible_hash_digest(self.config)

