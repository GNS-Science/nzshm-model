# Changelog

## [0.4.0] - 2023-11-22
## Changed
 - refactor into resources package
 - fix incorrect version info on v1.0.0 and v1.0.4 SLT json
 - remove twine from project
 - Revert "correlation values stored as sets"

## Added
 - new model class to make model definitions DRY;
 - new nrml package to make classnames more compatible with GEM conventions
 - gmm_logic_tree added to models
-  SRM logic trees for various model hazard aggregations (in resources/SRM_LTs)

## [0.3.1] - 2023-11-14
## Fixed
 - correlations use list comparison rather than cast to set to avoid unhashable type TypeError

## [0.3.0] - 2023-04-03
## Added
  - rupture_set_id to branch
## Changed
  - renamed `nshm_1.0.0` to `nshm_v1.0.0`
  - renamed `nshm_1.0.4` to `nshm_v1.0.4`

## [0.2.0] - 2023-04-03
## Added
  - new NSHM_1.0.4 model
  - correlations between fault systems
## Changed
  - flattened logic trees using combinations of fault system logic tree branches
  - renamed field on SourceLogicTree `fault_system_branches` to `fault_system_lts`
  - ensure logic tree classes are JSON serialisable

## [0.1.1] - 2022-12-19

## Changed
 - refactored project structure for packaging
 - scripts moved to /scripts package
 - changelog format for bump2version
 - remove docs build

## Added
 - poetry with: pytest, coverage, tox, flake8, mypy, black, isort, bump2version
 - github actions for CI/CD
 - source_logic_tree feature

## [0.0.1] - 2022-10-04
Initial release of the NZ NSHM 2022 revision
