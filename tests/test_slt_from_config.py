#! test_module_import

# import itertools
import collections
from typing import Iterable, Generator, Dict, Union

## >>>> from runzi.execute.openquake.util

# Using a named tuple make the data much easier to work with...
# this is where we change source_model to use ~toshi_id~ (now inv_id and bg_id)
LogicTreeBranch = collections.namedtuple('LogicTreeBranch', 'tag inv_id bg_id weight')


def get_config_groups(logic_tree_permutations) -> Generator:
    for permutation in logic_tree_permutations[0][0]['permute']:
        yield permutation


def get_config_group(logic_tree_permutations: Iterable, group_tag: str) -> Union[Dict, None]:
    for group in get_config_groups(logic_tree_permutations):
        if group['group'].upper() == group_tag.upper():
            return group
    return None


def get_config_group_tag_permutations(logic_tree_permutations: Iterable, group_tag: str):
    group = get_config_group(logic_tree_permutations, group_tag)
    if group:
        for member in group['members']:
            yield member['tag']


class TestStructure:
    def setup(self):
        import nzshm_model

        self.model = nzshm_model
        self.model_version = self.model.get_model_version(self.model, 'NSHM_1.0.0')

    def test_slt_groups_v1_0_0(self):
        v1_0_0 = self.model.get_model_version(self.model, 'NSHM_1.0.0')

        groups = list(get_config_groups(v1_0_0['model'].slt_config.logic_tree_permutations))
        for slt in groups:
            print(f'group {slt}')
        assert len(groups) == 4

    def test_slt_get_group(self):
        group = get_config_group(self.model_version['model'].slt_config.logic_tree_permutations, 'HIK')
        print(group)
        assert group['group'] == 'Hik'

    def test_get_config_group_tag_permutations(self):
        group = list(
            get_config_group_tag_permutations(self.model_version['model'].slt_config.logic_tree_permutations, 'HIK')
        )
        print(group)
        # assert group['group'] == 'Hik'
