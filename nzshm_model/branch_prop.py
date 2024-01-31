from typing import TYPE_CHECKING

from nzshm_model import get_model_version

if TYPE_CHECKING:
    from nzshm_model.logic_tree import InversionSource, SourceBranchSet


def get_branch_set(model_version: str, branch_set_short_name: str) -> "SourceBranchSet":
    """
    Get a branch set by the specific model version and short name

    Examples:
        >>>  for b in get_branch_set("NSHM_v1.0.4", 'CRU').branches:
                print(b.sources[0].inversion_id, b.values, b.weight)
        >>>
        U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNzIy [dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s0.66] 0.0168335471189857
        U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNzE3 [dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s1.0] 0.0408928149352719
        U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNzQx [dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s1.41] 0.0216771620919014

    Parameters:
        model_version: The version of model
        branch_set_short_name: The short_name of branch_set (eg.HIK, CRU, PUY, SLAB)

    Yields:
        The details of specified branch set, including weight, values, sources and etc
    """
    model = get_model_version(model_version)
    if model is not None:
        slt = model.source_logic_tree().branch_sets
        try:
            return next(filter(lambda item: item.short_name == branch_set_short_name, slt))
        except StopIteration:
            raise ValueError("The branch " + branch_set_short_name + " was not found.")
    else:
        raise ValueError("The model " + model_version + " is not valid.")


if __name__ == '__main__':
    for each in get_branch_set("NSHM_v1.0.4", 'CRU').branches:
        source = each.sources[0]
        if isinstance(source, InversionSource):
            print(source.inversion_id, each.values, each.weight)
