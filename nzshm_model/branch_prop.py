"""
Helper functions to give easy access to the main SLT dataclasses.
"""

from typing import Iterator, List, Union

from nzshm_model.logic_tree import SourceBranch, SourceBranchSet
from nzshm_model.model_version import get_model_version


def get_source_branch_sets(model_version: str, short_names: Union[List[str], str, None] = None) -> Iterator['SourceBranchSet']:
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
    # if type(short_names) == str:
    list_short_names: List[str] = [short_names] if type(short_names) == str else short_names

    model = get_model_version(model_version)
    if model is None:
        raise ValueError(model_version + " is not a valid model version.")

    if not short_names:  # User passes either an empty list or None
        for branch_set in model.source_logic_tree().branch_sets:
            yield branch_set
    else:
        # user has passes a list of short_names
        for branch_set in filter(lambda item: item.short_name in list_short_names, model.source_logic_tree().branch_sets):
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


# def get_branches(model_version: str, branch_set_short_name_list: list = None):
#     model = get_model_version(model_version)
#     if model is not None:
#         slt = model.source_logic_tree().branch_sets
#         if branch_set_short_name_list is None or len(branch_set_short_name_list) == 0:
#             branch_set_short_name_list = ['CRU', 'PUY', 'HIK', 'SLAB']
#         if type(branch_set_short_name_list) == str:
#             branch_set_short_name_list = [branch_set_short_name_list]
#         for each_short_name in branch_set_short_name_list:
#             try:
#                 output = [next(filter(lambda item: item.short_name == each_short_name, slt))]
#             except StopIteration:
#                 raise ValueError("The branch " + each_short_name + " was not found.")
#             for item in output:
#                 print(item.short_name + ": ")
#                 for each_branch in item.branches:
#                     each_source = each_branch.sources[0]
#                     if isinstance(each_source, InversionSource):
#                         print(each_source.inversion_id, each_branch.values, each_branch.weight)
#                     else:
#                         print("There are no InversionSource, so VALUES and WEIGHT are: ")
#                         print(each_branch.values, each_branch.weight)
#         return "Branches retrieved successfully"
#     else:
#         raise ValueError("The model " + model_version + " is not valid.")


if __name__ == '__main__':
    b = next(get_source_branches('NSHM_v1.0.4', ['CRU', 'PUY']))
    print(b)
    print(b.weight, b.tag)
