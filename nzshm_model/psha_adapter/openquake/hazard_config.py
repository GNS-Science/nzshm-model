#!python3 hazard_config.py
"""
Module supporting managed openquake configuration files

 - uses https://docs.python.org/3/library/configparser.html to do the heavy lifting
 - migrated from runzi /runzi/execute/openquake/util/oq_hazard_config.py

"""
import ast
import configparser
import copy
import json
import math
from itertools import chain
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, TextIO, Tuple, Type, Union, cast

from nzshm_common import CodedLocation

from nzshm_model.psha_adapter.hazard_config import HazardConfig, HazardConfigType

from .hazard_config_compat import check_invariants, compatible_hash_digest


# the z1pt0 and z2pt5 functions have been ported from openquake (openquake.hazardlib.site) to avoid incompatibility
# as the openquake API changes
def calculate_z1pt0(vs30: float) -> float:
    """
    Calculates z1.0 (depth to 1.0 km/s velocity horizon) in m. Assumes the California/global
    constants, not the Japan specific ones.

    Ref: Chiou, B. S.-J. and Youngs, R. R., 2014. 'Update of the Chiou and Youngs NGA model for the
    average horizontal component of peak ground motion and response spectra.' Earthquake Spectra,
    30(3), pp.1117–1153.

    Arguments:
        vs30: time averaged shear wave velocity from 0 to 30m depth (m/s)

    Returns:
        depth to 1.0 km/s velocity horizon in m
    """

    c1_glo = 571**4.0
    c2_glo = 1360.0**4.0
    return math.exp((-7.15 / 4.0) * math.log((vs30**4 + c1_glo) / (c2_glo + c1_glo)))


def calculate_z2pt5(vs30: float) -> float:
    """
    Calculates z2.5 (depth to 2.5 km/s velocity horizon) in km. Assumes the California constants,
    not the Japan specific ones.

    Ref: Campbell, K.W. & Bozorgnia, Y., 2014. 'NGA-West2 ground motion model for the average
    horizontal components of PGA, PGV, and 5pct damped linear acceleration response spectra.'
    Earthquake Spectra, 30(3), pp.1087–1114.

    Arguments:
        vs30: time averaged shear wave velocity from 0 to 30m depth (m/s)

    Returns:
        depth to 2.5 km/s velocity horizon in km
    """
    c1_glo = 7.089
    c2_glo = -1.144
    return math.exp(c1_glo + math.log(vs30) * c2_glo)


class OpenquakeConfig(HazardConfig):
    """Helper class to manage openquake configuration files.

    Examples:
        >>> from nzshm_model.psha_adapter.openquake import (
                OpenquakeConfig,\\
                DEFAULT_HAZARD_CONFIG\\
            )
        ...
        >>> oq_config = OpenquakeConfig(DEFAULT_HAZARD_CONFIG)\\
        >>>        .set_description("Hello openquake")\\
        >>>        .set_site_filepath("./sites.csv")\\
        >>>        .set_source_logic_tree_file(str(sources_filepath))\\
        >>>        .set_gsim_logic_tree_file("./gsim_model.xml")\\
        >>>        .set_vs30(750)
        ...
        >>> oq_config.config.get('general', 'description')
        ... Hello openquake
    """

    hazard_type = "openquake"

    def __init__(self, default_config: Union[configparser.ConfigParser, Dict, None] = None):

        self._site_parameters: Optional[Dict[str, Tuple]] = None
        self._locations: Optional[Tuple[CodedLocation]] = None

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

    def is_complete(self) -> bool:
        return bool(self.get_iml() or self.get_iml_disagg())

    def _config_to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = dict()
        for section in self.config.sections():
            data[section] = dict()
            for k, v in self.config[section].items():
                data[section][k] = v
        return data

    def _locations_to_strs(self) -> List[str]:
        if not self.locations:
            return []
        return [loc.code for loc in self.locations]

    def to_dict(self) -> Dict[str, Any]:
        config_dict: Dict[str, Any] = dict(config=self._config_to_dict())
        config_dict['locations'] = self._locations_to_strs()
        config_dict['site_parameters'] = self._site_parameters
        config_dict['hazard_type'] = self.hazard_type
        return config_dict

    @classmethod
    def from_dict(cls: Type[HazardConfigType], data: Dict) -> 'OpenquakeConfig':
        site_parameters = data.pop('site_parameters')
        locations = data.pop('locations')
        hazard_config = cast('OpenquakeConfig', cls(data['config']))
        if site_parameters:
            hazard_config._site_parameters = hazard_config._deserialze_site_params(site_parameters)
        if locations:
            hazard_config._locations = hazard_config._deserialize_locations(locations)

        return hazard_config

    @classmethod
    def from_json(cls: Type[HazardConfigType], file_path: Union[Path, str]) -> 'OpenquakeConfig':
        with Path(file_path).open('r') as jsonfile:
            data = json.load(jsonfile)
        return cast('OpenquakeConfig', cls.from_dict(data))

    @staticmethod
    def _deserialze_site_params(site_parameters):
        data = dict()
        for k, v in site_parameters.items():
            data[k] = tuple(v)
        return data

    @staticmethod
    def _deserialize_locations(locations):
        # check that all coordinates have the same resolution
        def get_resolution(x):
            return 10 ** -(len(x) - x.find('.') - 1)

        all_coords = list(chain.from_iterable([loc.split('~') for loc in locations]))
        if len(set(map(get_resolution, all_coords))) != 1:
            raise Exception("not all coordinates have the same resolution")

        resolution = get_resolution(all_coords[0])
        ll_pairs = [[float(ll_str) for ll_str in loc.split('~')] for loc in locations]
        return tuple([CodedLocation.from_tuple(loc, resolution) for loc in ll_pairs])

    @staticmethod
    def read_file(config_file: TextIO) -> 'OpenquakeConfig':
        """produce a OpenquakeConfig from a file-like object

        Arguments:
            config_file: An file-like object with valid .ini contents.

        Returns:
            A new OpenquakeConfig instance.
        """
        config = configparser.ConfigParser()
        config.read_file(config_file)
        return OpenquakeConfig(config)

    def set_source_logic_tree_file(self, source_lt_filepath: Union[str, Path]) -> 'OpenquakeConfig':
        """setter for source_model file

        Arguments:
            source_lt_filepath: The path to the source model file.

        Returns:
            The OpenquakeConfig instance.
        """
        self.set_parameter("calculation", "source_model_logic_tree_file", str(source_lt_filepath))
        return self

    def set_parameter(self, section: str, key: str, value: Any) -> 'OpenquakeConfig':
        """a setter for arbitrary values

        Arguments:
            section: The config table name eg.[site_params].
            key: The key name.
            value: The value to set.

        Returns:
            The OpenquakeConfig instance.
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        return self

    def get_parameter(self, section: str, key: str) -> Optional[str]:
        """A getter for arbitrary values.

        Arguments:
            section: The config table name eg.[site_params].
            key: The key name.

        Returns:
            The value for section and key or None if the entry does not exist.
        """
        if self.config.has_option(section, key):
            return self.config.get(section, key)
        return None

    def unset_parameter(self, section, key) -> 'OpenquakeConfig':
        """remove a table entry

        Arguments:
            section: The config table name eg.[site_params].
            key: The key name.

        Returns:
            The OpenquakeConfig instance.
        """
        if section in self.config:
            self.config.remove_option(section, key)
        return self

    def set_maximum_distance(self, value: dict[str, int]) -> 'OpenquakeConfig':
        """Set the maximum distance, which is a dictionary

        e.g. `{'Active Shallow Crust': 300.0, 'Volcanic': 300, 'Subduction Interface': 400, 'default': 400}`

        Arguments:
            value: Mapping of trt_names and distances.

        Returns:
            The OpenquakeConfig instance.
        """
        value_new = {}
        for trt, dist in value.items():
            if isinstance(dist, str):
                value_new[trt] = [tuple(dm) for dm in ast.literal_eval(dist)]
            else:
                value_new[trt] = dist
        self.config.set("calculation", "maximum_distance", str(value_new))
        return self

    def set_sites(self, locations: Iterable[CodedLocation], **site_parameters) -> 'OpenquakeConfig':
        """Setter for site_model file.

        If a vs30 values are specified, but a uniform vs30 has already been set a ValueError will be raised.

        Arguments:
            locations: The surface locations of the sites.
            kwargs: Additional site parameters to include in the OpenQuake site file.
                    Argument names will be used in the site file header. All entries
                    must be a sequence of the same length as locations.  See
                    https://docs.openquake.org/oq-engine/manual/latest/user-guide/inputs/site-model-inputs.html
                    for a list of valid site parameters.

        Returns:
            The OpenquakeConfig instance.
        """

        if 'vs30' in site_parameters and self.config.has_option('site_params', 'reference_vs30_value'):
            raise KeyError(
                "Cannot set site specific vs30, z1.0, or, z2.5: configuration specifies uniform site conditions."
            )
        if 'z1pt0' in site_parameters and self.config.has_option('site_params', 'reference_depth_to_1pt0km_per_sec'):
            raise KeyError(
                "Cannot set site specific vs30, z1.0, or, z2.5: configuration specifies uniform site conditions."
            )
        if 'z2pt5' in site_parameters and self.config.has_option('site_params', 'reference_depth_to_2pt5km_per_sec'):
            raise KeyError(
                "Cannot set site specific vs30, z1.0, or, z2.5: configuration specifies uniform site conditions."
            )

        self._site_parameters = {}
        locations = tuple(locations)
        for k, v in site_parameters.items():
            values = tuple(v)
            if not isinstance(v, Iterable):
                raise TypeError("all keyword arguments must be iterable type")
            if not len(values) == len(locations):
                raise ValueError("all keyword arguments must have the same number of elements as locations")
            self._site_parameters[k] = values

        self._locations = locations
        return self

    def set_site_filepath(self, site_file: Union[str, Path]) -> 'OpenquakeConfig':
        """
        Set the path to the site_model_file.
        """

        self.set_parameter('site_params', 'site_model_file', str(site_file))
        return self

    def get_site_filepath(self) -> Optional[Path]:
        value = self.get_parameter('site_params', 'site_model_file')
        return Path(value) if value else None

    @property
    def locations(self) -> Optional[Tuple[CodedLocation]]:
        return self._locations

    @property
    def site_parameters(self) -> Optional[Dict[str, tuple]]:
        return self._site_parameters

    def get_iml(self) -> Optional[Tuple[List[str], List[float]]]:
        """
        Get the intensity measure types and levels. Returns None if not set.

        Returns:
            a tuple of (IMTs, IMTLs) where IMTs is a list of intensity measure types and
            IMTLs is a list of intensity measure levels
        """

        value = self.get_parameter('calculation', 'intensity_measure_types_and_levels')
        if not value:
            return None

        imls = ast.literal_eval(value)
        imts = list(imls.keys())
        imtls = list([float(imtl) for imtl in next(iter(imls.values()))])

        return imts, imtls

    def get_iml_disagg(self) -> Optional[Tuple[str, float]]:
        """Get the intensity measure type and level for the disaggregation. Returns None if not set.

        Returns:
            a tuple of (IMT, and IMTL) where IMT is a intensity measure type and IMTL is an intensity measure level
        """
        value = self.get_parameter('disagg', 'iml_disagg')
        if not value:
            return None

        iml_imtl = ast.literal_eval(value)
        return list(iml_imtl.items())[0]

    # TODO disagg configs might warrant a separate class, and separate defaults ??
    def set_disagg_site_model(self) -> 'OpenquakeConfig':
        raise NotImplementedError()
        # self.set_parameter('site_params', 'site_model_file', 'site.csv')
        return self

    def set_disagg_site(self, lat, lon) -> 'OpenquakeConfig':
        raise NotImplementedError()
        # self.set_parameter('site_params', 'sites', f'{lon} {lat}')
        return self

    def set_iml_disagg(self, imt: str, level: float) -> 'OpenquakeConfig':
        self.set_parameter('disagg', 'iml_disagg', str({imt: level}))
        return self

    def clear_iml(self) -> 'OpenquakeConfig':
        """Remove intensity_measure_types_and_levels.

        Returns:
            The OpenquakeConfig instance.
        """
        self.unset_parameter('calculation', 'intensity_measure_types_and_levels')
        return self

    def set_iml(self, measures: List[str], levels: List[float]) -> 'OpenquakeConfig':
        """Setter for intensity_measure_types_and_levels

        Sets the same levels for all intensity measures.

        Arguments:
            measures: The IML types e.g `['PGA', 'SA(0.5)', ...].
            levels: The IML levels as floats  e.g. [0.01, 0.02, 0.04, ...].

        Returns:
            The OpenquakeConfig instance.
        """
        self.clear_iml()
        new_iml = '{'
        for m in measures:
            new_iml += f'"{m}": {str(levels)}, '
        new_iml += '}'

        if not self.config.has_section('calculation'):
            self.config.add_section('calculation')
        self.config['calculation']['intensity_measure_types_and_levels'] = new_iml
        return self

    def unset_uniform_site_params(self) -> 'OpenquakeConfig':
        """
        Remove the uniform site parameters from the configuration. This will unset the values for
        'reference_vs30_type', 'reference_vs30_value', 'reference_depth_to_1pt0km_per_sec', and
        'reference_depth_to_2pt5km_per_sec' in the 'site_params' section.
        """
        if not self.config.has_section('site_params'):
            return self

        sect = self.config['site_params']
        for setting in [
            'reference_vs30_type',
            'reference_vs30_value',
            'reference_depth_to_1pt0km_per_sec',
            'reference_depth_to_2pt5km_per_sec',
        ]:
            sect.pop(setting, None)

        return self

    def set_uniform_site_params(
        self, vs30: float, z1pt0: Optional[float] = None, z2pt5: Optional[float] = None
    ) -> 'OpenquakeConfig':
        """
        Setter for vs30, z1.0, and z2.5 site parameters.

        This will set the vs30, z1.0, and z2.5 site parameters for all sites. If z1pt0 and/or z2pt5
        are not specified they will be calculated from vs30. z1.0 is caculated using Chiou & Youngs
        (2014) California model and z2.5 is caclualted using Campbell & Bozorgnia 2014 NGA-West2 model.

        Arguments:
            vs30: the desired vs30
            z1pt0: the desired z1.0 depth in m
            z2pt5: the desired z2.5 depth in km

        Returns:
            The OpenquakeConfig instance.

        References:
            Campbell, K.W. & Bozorgnia, Y., 2014.
            'NGA-West2 ground motion model for the average horizontal components of
            PGA, PGV, and 5pct damped linear acceleration response spectra.' Earthquake Spectra,
            30(3), pp.1087–1114.

            Chiou, Brian & Youngs, Robert. (2014).
            'Update of the Chiou and Youngs NGA Model for the Average Horizontal Component of Peak
            Ground Motion and Response Spectra.' Earthquake Spectra. 30. 1117-1153.
        """

        if (site_parameters := (self.site_parameters)) and 'vs30' in site_parameters:
            raise KeyError("vs30 is already set as a site specific parameter")

        # clean up old settings
        self.unset_uniform_site_params()
        if not self.config.has_section('site_params'):
            self.config.add_section('site_params')
        sect = self.config['site_params']

        sect['reference_vs30_type'] = 'measured'
        sect['reference_vs30_value'] = str(vs30)

        if z1pt0:
            sect['reference_depth_to_1pt0km_per_sec'] = str(round(z1pt0, 0))
        elif 'calculate_z1pt0' in globals():
            sect['reference_depth_to_1pt0km_per_sec'] = str(round(calculate_z1pt0(vs30), 0))

        if z2pt5:
            sect['reference_depth_to_2pt5km_per_sec'] = str(round(z2pt5, 1))
        elif 'calculate_z2pt5' in globals():
            sect['reference_depth_to_2pt5km_per_sec'] = str(round(calculate_z2pt5(vs30), 1))

        return self

    def get_uniform_site_params(self) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        The uniform site parameters of the model. Returns None if not set.

        Returns:
            (vs30, z1pt0, z2pt5) where vs30 is the vs30 applied to all sites, z1pt0 is the z1.0 reference
            depth in m, and z2pt5 is the z2.5 reference depth in km.
        """

        if not self.config.has_section('site_params'):
            return None, None, None

        value = self.get_parameter('site_params', 'reference_vs30_value')
        vs30 = float(value) if value else None

        value = self.config.get('site_params', 'reference_depth_to_1pt0km_per_sec', fallback=None)
        z1pt0 = float(value) if value else None

        value = self.config.get('site_params', 'reference_depth_to_2pt5km_per_sec', fallback=None)
        z2pt5 = float(value) if value else None

        return vs30, z1pt0, z2pt5

    def set_gsim_logic_tree_file(self, filepath: Union[str, Path]) -> 'OpenquakeConfig':
        """Setter for ground motion model file.

        Arguments:
            filepath: The path to the ground motion model file.

        Returns:
            The OpenquakeConfig instance.
        """
        self.set_parameter('calculation', 'gsim_logic_tree_file', str(filepath))
        return self

    def set_description(self, description) -> 'OpenquakeConfig':
        self.set_parameter('general', 'description', description)
        return self

    def write(self, tofile: TextIO) -> None:
        """Write the OpenquakeConfig to a file-like object.

        Arguments:
            tofile: A file-like object.
        """
        self.config.write(tofile)

    def compatible_hash_digest(self) -> str:
        """Get a shake_256 hash digest for the compatablity config.

        We want to ensure that, for this config:

         - all the invariant entries exist
         - entries that will not break calcluation compatibility are ignored

        Returns:
            The 12 character hash_digest.
        """
        check_invariants(self.config)
        return compatible_hash_digest(self.config)
