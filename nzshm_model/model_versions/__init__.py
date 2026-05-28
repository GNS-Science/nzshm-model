from dataclasses import dataclass


@dataclass(frozen=True)
class ModelVersionSpec:
    """Metadata for a single registered NSHM model version."""

    version: str
    title: str
    slt_json: str
    gmm_json: str
    hazard_config_json: str


versions: dict[str, ModelVersionSpec] = {
    "NSHM_v1.0.0": ModelVersionSpec(
        version="NSHM_v1.0.0",
        title="Initial version",
        slt_json="nshm_v1.0.0_v2.json",
        gmm_json="gmcm_nshm_v1.0.0.json",
        hazard_config_json="oq_config_nshm_v1.0.0.json",
    ),
    "NSHM_v1.0.4": ModelVersionSpec(
        version="NSHM_v1.0.4",
        title="NSHM version 1.0.4, corrected fault geometry",
        slt_json="nshm_v1.0.4_v2.json",
        gmm_json="gmcm_nshm_v1.0.4.json",
        hazard_config_json="oq_config_nshm_v1.0.4.json",
    ),
}
