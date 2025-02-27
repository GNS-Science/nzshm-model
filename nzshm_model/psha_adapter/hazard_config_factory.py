import json
from pathlib import Path
from typing import Dict, Union

from nzshm_model.psha_adapter.hazard_config import HazardConfig
from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig


class HazardConfigFactory:
    """
    Factory class used to get a HazardConfig type object without knowing the concrete type before runtime.

    Examples:
        >>> HazardConfigType = hazard_config_class_factory.get_hazard_config_class('openquake')
        >>> hazard_config = HazardConfigType()
        >>> HazardConfigType = hazard_config_class_factory.get_hazard_config_class_from_file(hazard_config.json)
        >>> hazard_config = HazardConfigType.from_json(hazard_config.json)
    """

    def __init__(self):
        self._config_types: Dict[str, type[HazardConfig]] = {}

    def register_config_class(self, type_name: str, config_type: type[HazardConfig]):
        self._config_types[type_name.casefold()] = config_type

    def get_hazard_config_class(self, type_name: str) -> type[HazardConfig]:
        """Get the concrete HazardConfig object."""
        config_type = self._config_types.get(type_name.casefold())
        if not config_type:
            raise ValueError(type_name)
        return config_type

    @staticmethod
    def detect_hazard_config_class_from_file(file_path: Union[str, Path]) -> str:
        """Get the concrete HazardConfig type from the json file representation of the object."""
        with Path(file_path).open() as config_file:
            data = json.load(config_file)
            return data["hazard_type"].casefold()

    def get_hazard_config_class_from_file(self, file_path: Union[str, Path]) -> type[HazardConfig]:
        """Get the concrete HazardConfig object by detecting the type from the json file
        representation of the object."""
        type_name = self.detect_hazard_config_class_from_file(file_path)
        return self.get_hazard_config_class(type_name)


hazard_config_class_factory = HazardConfigFactory()
hazard_config_class_factory.register_config_class('openquake', OpenquakeConfig)
