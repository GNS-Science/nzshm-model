# import pytest

# from nzshm_model.branch_prop import get_source_branch_sets, get_source_branches


# def test_get_source_branch_sets_with_list():
#     branch_sets = list(get_source_branch_sets('NSHM_v1.0.4', ['CRU', 'PUY']))
#     assert len(branch_sets) == 2
#     assert branch_sets[0].short_name == 'PUY'
#     assert branch_sets[1].short_name == 'CRU'


# def test_get_source_branch_sets_with_single():
#     branch_sets = list(get_source_branch_sets('NSHM_v1.0.4', 'CRU'))
#     assert len(branch_sets) == 1
#     assert branch_sets[0].short_name == 'CRU'


# def test_get_source_branch_sets_with_null():
#     assert len(list(get_source_branch_sets('NSHM_v1.0.4', []))) == 4
#     assert len(list(get_source_branch_sets('NSHM_v1.0.4'))) == 4


# def test_get_source_branch_sets_invalid_model_version():
#     with pytest.raises(ValueError, match=r'.* is not a valid'):
#         next(get_source_branch_sets('', ['CRU', 'PUY']))


# def test_get_source_branch_sets_with_invalid_branch():
#     with pytest.raises(StopIteration):
#         next(get_source_branch_sets('NSHM_v1.0.4', ['XXX']))


# def test_get_first_crustal_branches():
#     cru_branches = next(get_source_branch_sets('NSHM_v1.0.4', 'CRU')).branches
#     assert next(get_source_branches('NSHM_v1.0.4', 'CRU')) == cru_branches[0]


# def test_get_source_branches_invalid_model_version():
#     with pytest.raises(ValueError, match=r'.* is not a valid'):
#         # a
#         next(get_source_branches('', ['CRU', 'PUY']))

#     with pytest.raises(ValueError, match=r'.* is not a valid'):
#         # b
#         list(get_source_branches('', ['CRU', 'PUY']))

#     with pytest.raises(ValueError, match=r'.* is not a valid'):
#         # c for next
#         for b in get_source_branches('', ['CRU', 'PUY']):
#             pass


# def test_get_source_branches_with_invalid_branch():
#     with pytest.raises(StopIteration):
#         next(get_source_branches('NSHM_v1.0.4', ['XXX']))
