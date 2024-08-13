import warnings
from pathlib import Path

from nzshm_model.psha_adapter.openquake import OpenquakeSimplePshaAdapter

imtls = list(range(10))
imts = ["PGA", "SA(1.0)"]


def test_write_config(tmp_path, current_model):
    source_map = {}
    for branch in current_model.source_logic_tree:
        for source in branch.sources:
            nrml_id = source.nrml_id
            source_map[nrml_id] = [
                Path(f"path/to/{nrml_id}.xml"),
            ]

    cache_folder = tmp_path / 'cache'
    target_folder = tmp_path / 'target'

    current_model.hazard_config.set_sites('sites.csv')
    current_model.hazard_config.set_iml(imts, imtls)

    current_model.psha_adapter(OpenquakeSimplePshaAdapter).write_config(cache_folder, target_folder, source_map)
    assert (target_folder / 'job.ini').exists()
    assert (target_folder / 'gsim_model.xml').exists()
    assert (target_folder / 'sources' / 'sources.xml').exists()


def test_write_config_warn(tmp_path, current_model):
    source_map = {}
    for branch in current_model.source_logic_tree:
        for source in branch.sources:
            nrml_id = source.nrml_id
            source_map[nrml_id] = [
                Path(f"path/to/{nrml_id}.xml"),
            ]

    cache_folder = tmp_path / 'cache'
    target_folder = tmp_path / 'target'
    with warnings.catch_warnings(record=True) as wngs:
        current_model.psha_adapter(OpenquakeSimplePshaAdapter).write_config(cache_folder, target_folder, source_map)
        assert len(wngs) > 0, len(wngs)
        assert "not complete" in str(wngs[-1].message)
