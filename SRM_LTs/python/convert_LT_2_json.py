import json
import sys
from pathlib import Path

lt_path = Path(sys.argv[1])

lt = __import__(lt_path.stem)

out_file_name = Path('../json/',lt_path.stem + '.json')

# lt.gtdata['data']['node1']['children']['edges'] = lt.gtdata['data']['node1']['children']['edges'] + lt.gtdata_new['data']['node1']['children']['edges']


data = dict(
            # gmm_correlations=lt.gmm_correlations,
            src_correlations=lt.src_correlations,
            logic_tree_permutations=lt.logic_tree_permutations,
            hazard_solutions=lt.gtdata
            )

with open(out_file_name,'w') as jsonfile:
    json.dump(data,jsonfile,indent=2)
