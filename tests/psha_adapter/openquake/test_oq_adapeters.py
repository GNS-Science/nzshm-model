from nzshm_model import get_model_version
from nzshm_model.psha_adapter.openquake.simple_nrml import OpenquakeGMCMPshaAdapter, OpenquakeSimplePshaAdapter, OpenquakeSourcePshaAdapter, OpenquakeConfigAdapter


def test_adapters():

    model = get_model_version()
    source_adapter = model.source_logic_tree.adapter(OpenquakeSourcePshaAdapter)
    gmcm_adapter = model.gmm_logic_tree.adapter(OpenquakeGMCMPshaAdapter)
    config_adapter = model.hazard_config.adapter(OpenquakeConfigAdapter)

    adapter = model.psha_adapter(OpenquakeSimplePshaAdapter)

    adapter.write_config()