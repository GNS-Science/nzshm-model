import tempfile
from pathlib import Path

from nzshm_model import get_model_version
from nzshm_model.psha_adapter.openquake import OpenquakeSimplePshaAdapter

CURRENT_MODEL = 'NSHM_v1.0.4'

imtls = list(range(10))
imts = ["PGA", "SA(1.0)"]


def test_write_config():
    def mockreturn(file_id, destination):
        return file_id

    model = get_model_version(CURRENT_MODEL)
    model.hazard_config.set_sites('sites.csv')
    model.hazard_config.set_iml(imts, imtls)
    source_map = {}
    for branch in model.source_logic_tree:
        for source in branch.sources:
            nrml_id = source.nrml_id
            source_map[nrml_id] = [
                Path(f"path/to/{nrml_id}.xml"),
            ]

    with tempfile.TemporaryDirectory() as tmpdir:
        cache_folder = Path(tmpdir) / 'cache'
        target_folder = Path(tmpdir) / 'target'
        model.psha_adapter(OpenquakeSimplePshaAdapter).write_config(cache_folder, target_folder, source_map)
        assert (target_folder / 'job.ini').exists()
        assert (target_folder / 'gsim_model.xml').exists()
        assert (target_folder / 'sources' / 'sources.xml').exists()
