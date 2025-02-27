from nzshm_model.psha_adapter.openquake import OpenquakeModelPshaAdapter

imtls = list(range(10))
imts = ["PGA", "SA(1.0)"]


def test_write_config(tmp_path, current_model, source_map):
    cache_folder = tmp_path / 'cache'
    target_folder = tmp_path / 'target'

    current_model.hazard_config.set_site_filepath('sites.csv')
    current_model.hazard_config.set_iml(imts, imtls)

    current_model.psha_adapter(OpenquakeModelPshaAdapter).write_config(cache_folder, target_folder, source_map)
    assert (target_folder / 'job.ini').exists()
    assert (target_folder / 'gsim_model.xml').exists()
    assert (target_folder / 'sources' / 'sources.xml').exists()
