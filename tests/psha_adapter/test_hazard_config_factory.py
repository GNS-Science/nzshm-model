import importlib.resources as resources
from pathlib import Path

import pytest

from nzshm_model.psha_adapter.hazard_config_factory import hazard_config_class_factory
from nzshm_model.psha_adapter.openquake.hazard_config import OpenquakeConfig

fixtures_dir = resources.files('tests.psha_adapter.fixtures')


def test_types():

    hazard_config_class_factory.get_hazard_config_class('openquake')
    hazard_config_class_factory.get_hazard_config_class('OpEnQuAkE')


def test_wrong_type():

    with pytest.raises(ValueError):
        hazard_config_class_factory.get_hazard_config_class('microsoft word')


def test_class_name_from_file():

    config_filepath = Path(fixtures_dir / 'hazard_config.json')
    config_type = hazard_config_class_factory.detect_hazard_config_class_from_file(config_filepath)
    assert config_type == 'openquake'


def test_class_from_file():

    config_filepath = Path(fixtures_dir / 'hazard_config.json')
    config_class = hazard_config_class_factory.get_hazard_config_class_from_file(config_filepath)
    assert config_class == OpenquakeConfig
