# Changelog

## [0.6.0] 2023-12-21
### Added
 - GMCM logic tree classes for ground motion model serialization and deserialization (as json or xml)
 - OpenQuake specific adaptor for GMCM logic tree classes (nrml)

### Changed
 - PshaAdaptorInterface used for both source and ground motion logic trees

## [0.5.3] 2023-12-21
### Added
 - added backward_compatible property `fault_system_lts`  with deprecation warning.

## [0.5.2] 2023-12-14
### Changed
 - Updated GMCM logic tree nrml files to reflect new OpenQuake class names and arguments for NZ NSHM gsims

## [0.5.1] 2023-12-14
### Changed
 - SourceLogicTree.from_branches() returns logic tree with Branch objects rather than FilterdBranch objects
 - remove whitespace from logic tree file paths for compatability with OpenQuake

## [0.5.0] 2023-12-12
## Added
 - support caching of downloads
 - build sources xml
 - migration of version1 to version2 SLT
 - iterate branches with SourceLogicTree
 - build new SLT from branches iterable
 - scripts/cli config command demonstrates building openquake config from an SLT

## [0.4.1] - 2023-12-05
## Added
 - new scripts/cli module for PSHA related tasks, starting with fetch_sources
 - psha_adapter pattern, with openquake package as first example

## Changed
 - new package structure for psha_adapter(s)

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
