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
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, TextIO, Tuple, Union

from nzshm_model.psha_adapter.hazard_config import HazardConfig

from .hazard_config_compat import check_invariants, compatible_hash_digest

if TYPE_CHECKING:
    from nzshm_common import CodedLocation

log = logging.getLogger(__name__)

try:
    from openquake.hazardlib.site import calculate_z1pt0, calculate_z2pt5
except ImportError:
    log.warning(
        """warning openquake module dependency not available, maybe you want to install
                with nzshm-model[openquake]"""
    )


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

    def __init__(self, default_config: Union[configparser.ConfigParser, Dict, None] = None):

        self._site_parameters: Optional[Dict[str, Tuple]] = None
        self._locations: Optional[Tuple['CodedLocation']] = None

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
        return bool(self.get_iml())

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

    def set_source_logic_tree_file(self, source_lt_filepath: Union[str, pathlib.Path]) -> 'OpenquakeConfig':
        """setter for source_model file

        Arguments:
            source_lt_filepath: The path to the source model file.

        Returns:
            The OpenquakeConfig instance.
        """
        self.set_parameter("calculation", "source_model_logic_tree_file", str(source_lt_filepath))
        return self

    def set_parameter(self, section: str, key: str, value: str) -> 'OpenquakeConfig':
        """a setter for arbitrary string values

        Arguments:
            section: The config table name eg.[site_params].
            key: The key name.
            value: The value to set.

        Returns:
            The OpenquakeConfig instance.
        """
        assert isinstance(value, str)
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
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

    def set_sites(self, locations: Sequence['CodedLocation'], **site_parameters) -> 'OpenquakeConfig':
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
        for k, v in site_parameters.items():
            if not isinstance(v, Sequence):
                raise TypeError("all keyword arguments must be sequence type")
            if not len(v) == len(locations):
                raise ValueError("all keyword arguments must have the same lenth as locations")
            self._site_parameters[k] = tuple(v)

        self._locations = tuple(locations)
        return self

    def set_site_filepath(self, site_file: Union[str, pathlib.Path]) -> 'OpenquakeConfig':
        """
        Set the path to the site_model_file.
        """

        self.set_parameter('site_params', 'site_model_file', str(site_file))
        return self

    def get_site_filepath(self) -> Optional[pathlib.Path]:
        value = self.get_parameter('site_params', 'site_model_file')
        return pathlib.Path(value) if value else None

    @property
    def locations(self) -> Optional[Tuple['CodedLocation']]:
        return self._locations

    @property
    def site_parameters(self) -> Optional[Dict[str, tuple]]:
        return self._site_parameters

    def get_iml(self) -> Optional[Tuple[List[str], List[float]]]:
        """
        Get the intensity measure types and levels. Returns None if not set.

        Returns:
            IMTs: The intensity measure types.
            IMTLs: The intensity measure levels.
        """

        value = self.get_parameter('calculation', 'intensity_measure_types_and_levels')
        if not value:
            return None

        imls = ast.literal_eval(value)
        imts = list(imls.keys())
        imtls = list([float(imtl) for imtl in next(iter(imls.values()))])

        return imts, imtls

    # TODO disagg configs might warrant a separate class, and separate defaults ??
    def set_disagg_site_model(self) -> 'OpenquakeConfig':
        raise NotImplementedError()
        # self.set_parameter('site_params', 'site_model_file', 'site.csv')
        return self

    def set_disagg_site(self, lat, lon) -> 'OpenquakeConfig':
        raise NotImplementedError()
        # self.set_parameter('site_params', 'sites', f'{lon} {lat}')
        return self

    def set_iml_disagg(self, imt, level) -> 'OpenquakeConfig':
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

    def set_gsim_logic_tree_file(self, filepath: Union[str, pathlib.Path]) -> 'OpenquakeConfig':
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
