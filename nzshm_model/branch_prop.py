"""
Helper functions to give easy access to the main SLT dataclasses.
"""

from typing import Iterator, List, Union

from nzshm_model.logic_tree import SourceBranch, SourceBranchSet
from nzshm_model.model_version import get_model_version


def get_source_branch_sets(
    model_version: str, short_names: Union[List[str], str, None] = None
) -> Iterator['SourceBranchSet']:
    """
    get the SourceBranchSets for the specific model version, and branch set name(s).

    Examples:
        >>>  for branch_set in get_branch_sets("NSHM_v1.0.4", ['CRU', 'PUY']):
                print(branch_set.short_name, len(branch_set.branches))
        >>>
        CRU 36
        PUY 3

    Parameters:
        model_version: version of the model
        short_names: list of short_names for branch_set (eg. HIK, CRU, PUY, SLAB)

    Yields:
        iterator of branch_set objects
    """
    if isinstance(short_names, str):
        list_short_names: List[str] = [short_names]
    else:
        list_short_names = short_names if short_names is not None else []

    model = get_model_version(model_version)
    if model is None:
        raise ValueError(model_version + " is not a valid model version.")

    if not short_names:  # User passes either an empty list or None
        for branch_set in model.source_logic_tree().branch_sets:
            yield branch_set
    else:
        # user has passes a list of short_names
        for branch_set in filter(
            lambda item: item.short_name in list_short_names, model.source_logic_tree().branch_sets
        ):
            yield branch_set


def get_source_branches(model_version: str, short_names: list = None) -> Iterator['SourceBranch']:
    """
    get the SourceBranches for the specific model and branch set(s)

    Examples:
        >>>  for branch in get_source_branches("NSHM_v1.0.4", ['CRU', 'PUY']):
                print(branch.tag, branch.weight)
        >>>
        [dm0.7, bN[0.902, 4.6], C4.0, s0.28] 0.21
        ...
    """
    for branch_set in get_source_branch_sets(model_version, short_names):
        for branch in branch_set.branches:
            yield (branch)


if __name__ == '__main__':
    b = next(get_source_branches('NSHM_v1.0.4', ['CRU', 'PUY']))
    print(b)
    print(b.weight, b.tag)
