from pathlib import Path

from nzshm_model import all_model_versions, get_model_version

trts = {
    '0.7': ("Subduction Interface",),
    'TL': ("Subduction Interface",),
    'geodetic': ("Active Shallow Crust",),
    'uniform': ("Subduction Intraslab",),
}


for model_version in all_model_versions():
    model = get_model_version(model_version)
    slt = model.source_logic_tree
    for branch_set in slt.branch_sets:
        for branch in branch_set.branches:
            branch.tectonic_region_types = trts[branch_set.branches[0].values[0].value]
        for i, branch in enumerate(branch_set.branches):
            branch.branch_id = str(i)
    filepath = Path(__file__).parent.parent / 'resources' / 'SRM_JSON' / (model_version.lower() + '_v2.json')
    slt.to_json(filepath)
