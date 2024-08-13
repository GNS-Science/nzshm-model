from nzshm_model import get_model_version
from nzshm_model.psha_adapter.openquake.simple_nrml import OpenquakeGMCMPshaAdapter, OpenquakeSimplePshaAdapter, OpenquakeSourcePshaAdapter, OpenquakeConfigPshaAdapter


def test_adapters():

    model = get_model_version()
    source_adapter = model.source_logic_tree.psha_adapter(OpenquakeSourcePshaAdapter)
    gmcm_adapter = model.gmm_logic_tree.psha_adapter(OpenquakeGMCMPshaAdapter)
    config_adapter = model.hazard_config.psha_adapter(OpenquakeConfigPshaAdapter)

    adapter = model.psha_adapter(OpenquakeSimplePshaAdapter)

    # adapter.write_config()