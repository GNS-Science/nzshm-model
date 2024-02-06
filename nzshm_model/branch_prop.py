from typing import List

from nzshm_model import get_model_version
from nzshm_model.logic_tree import InversionSource, SourceBranchSet

# if TYPE_CHECKING:
#     from nzshm_model.logic_tree import SourceBranchSet


def get_branch_set(model_version: str, branch_set_short_name_list: list = None) -> List['SourceBranchSet']:
    """
    Get a branch set by the specific model version and short name

    Examples:
        >>>  for item in get_branch_set("NSHM_v1.0.4", ['CRU', 'PUY']):
                for each_branch in item.branches:
                    each_source = each_branch.sources[0]
                    if isinstance(each_source, InversionSource):
                        print(each_source.inversion_id, each_branch.values, each_branch.weight)
                    else:
                        print("There are no InversionSource, so VALUES and WEIGHT are: ")
                        print(each_branch.values, each_branch.weight)
        >>>
        CRU:
        U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNzIy [dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s0.66] 0.0168335471189857
        U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNzE3 [dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s1.0] 0.0408928149352719
        U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNzQx [dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s1.41] 0.0216771620919014
        PUY:
        U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTI5MTM3OA== [dm0.7, bN[0.902, 4.6], C4.0, s0.28] 0.21
        U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTI5MTM4Mg== [dm0.7, bN[0.902, 4.6], C4.0, s1.0] 0.52
        U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTI5MTM4Ng== [dm0.7, bN[0.902, 4.6], C4.0, s1.72] 0.27

    Parameters:
        model_version: The version of model
        branch_set_short_name_list: The list of short_name for branch_set (eg.HIK, CRU, PUY, SLAB)

    Yields:
        The details of branch sets, including weight, values, sources and etc, including weight, values, sources and etc
    """
    model = get_model_version(model_version)
    if model is not None:
        slt = model.source_logic_tree().branch_sets
        if branch_set_short_name_list is None:
            branch_set_short_name_list = []
        if type(branch_set_short_name_list) == str:
            branch_set_short_name_list = [branch_set_short_name_list]
        if len(branch_set_short_name_list) == 0:
            return slt
        else:
            output = []
            for each_short_name in branch_set_short_name_list:
                try:
                    output.append(next(filter(lambda item: item.short_name == each_short_name, slt)))
                except StopIteration:
                    raise ValueError("The branch " + each_short_name + " was not found.")
            return output
    else:
        raise ValueError("The model " + model_version + " is not valid.")


# if __name__ == '__main__':
#     for item in get_branch_set("NSHM_v1.0.4", ['CRU', 'PUY']):
#         print(item.short_name + ": ")
#         for each_branch in item.branches:
#             each_source = each_branch.sources[0]
#             if isinstance(each_source, InversionSource):
#                 print(each_source.inversion_id, each_branch.values, each_branch.weight)
#             else:
#                 print("There are no InversionSource, so VALUES and WEIGHT are: ")
#                 print(each_branch.values, each_branch.weight)


def get_branches(model_version: str, branch_set_short_name_list: list = None):
    model = get_model_version(model_version)
    if model is not None:
        slt = model.source_logic_tree().branch_sets
        if branch_set_short_name_list is None or len(branch_set_short_name_list) == 0:
            branch_set_short_name_list = ['CRU', 'PUY', 'HIK', 'SLAB']
        if type(branch_set_short_name_list) == str:
            branch_set_short_name_list = [branch_set_short_name_list]
        for each_short_name in branch_set_short_name_list:
            try:
                output = [next(filter(lambda item: item.short_name == each_short_name, slt))]
            except StopIteration:
                raise ValueError("The branch " + each_short_name + " was not found.")
            for item in output:
                print(item.short_name + ": ")
                for each_branch in item.branches:
                    each_source = each_branch.sources[0]
                    if isinstance(each_source, InversionSource):
                        print(each_source.inversion_id, each_branch.values, each_branch.weight)
                    else:
                        print("There are no InversionSource, so VALUES and WEIGHT are: ")
                        print(each_branch.values, each_branch.weight)
        return "Branches retrieved successfully"
    else:
        raise ValueError("The model " + model_version + " is not valid.")


# result = get_branches('NSHM_v1.0.4',['CRU','PUY'])
# print(result)
