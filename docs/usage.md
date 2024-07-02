## Get the list of available models

```python3
>>> import nzshm_model as nm
>>> nm.all_model_versions()
['NSHM_v1.0.0', 'NSHM_v1.0.4']
>>>
```

## Work with a specific model

```python3
>>> model = nm.get_model_version("NSHM_v1.0.4")
print(model.title)
>>>
NSHM version 1.0.4, corrected fault geometry
```

## Iterate over the Crustal branches

```python3
>>> for branch_set in model.get_source_branch_sets('CRU'): # NB also allows passing a list of short_names
>>>     for branch in branch_set.branches:
>>>          print(branch_set.long_name, branch.weight, branch.tag)
Crustal 0.0168335471189857 [dmgeodetic, tdFalse, bN[0.823, 2.7], C4.2, s0.66]
...
```

## Inspect a branch

```python3
>>> branch
SourceBranch(weight=0.00286782725429677, values=[dmgeologic, tdTrue, bN[1.089, 4.6], C4.2, s1.41], sources=[InversionSource(nrml_id='SW52ZXJzaW9uU29sdXRpb25Ocm1sOjEyOTE1MzE=', rupture_rate_scaling=None, inversion_id='U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNzc4', rupture_set_id='RmlsZToxMDAwODc=', inversion_solution_type='', type='inversion'), DistributedSource(nrml_id='RmlsZToxMzA3MzE=', rupture_rate_scaling=None, type='distributed')], rupture_rate_scaling=1.0)

```
