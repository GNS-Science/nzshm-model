# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`nzshm-model` is a Python package for the New Zealand National Seismic Hazard Model (NSHM). It provides logic tree abstractions for seismic source and ground motion models, PSHA engine adapters (OpenQuake), CLI tools, and a branch registry system using shake_256 hashing.

## Common Commands

```bash
# Install (with all dev dependencies)
poetry install -E test -E doc -E dev

# Run all tests (multi-Python via tox)
poetry run tox

# Run tests directly
poetry run pytest tests/

# Run a single test file
poetry run pytest tests/test_model.py

# Run a specific test
poetry run pytest tests/test_model.py::TestLoadModel::test_load_model_104

# Format code
poetry run tox -e format
# or: poetry run black nzshm_model tests && poetry run isort nzshm_model tests

# Lint
poetry run tox -e lint
# or: poetry run flake8 && poetry run mypy nzshm_model tests

# Security audit
poetry run tox -e audit

# Build package
poetry build

# Bump version (patch/minor/major)
poetry run bump2version patch
```

## Code Style

- **Black** formatter: line-length=120, skip-string-normalization
- **isort**: multi_line_output=3, line_length=120
- **flake8**: max-line-length=120, max-complexity=18
- **mypy**: ignore_missing_imports=true
- Target Python: >=3.10

## Architecture

### Core Model (`nzshm_model/model.py`)

`NshmModel` is the central class, generic over `HazardConfigType`. It bundles:
- `source_logic_tree` (SourceLogicTree) — seismic rate model branches
- `gmm_logic_tree` / `gmcm_logic_tree` (GMCMLogicTree) — ground motion model branches
- `hazard_config` — engine-specific hazard calculation parameters

Load a model version via `NshmModel.get_model_version("NSHM_v1.0.4")`. All available versions are registered in `nzshm_model/model_versions/__init__.py`.

### Logic Tree Hierarchy (`nzshm_model/logic_tree/`)

Abstract base `LogicTree` → concrete `SourceLogicTree` and `GMCMLogicTree`. Each contains `BranchSet[BranchType]` collections holding weighted `Branch` instances.

- **SourceBranch**: contains `InversionSource` and `DistributedSource` references plus rupture scaling
- **GMCMBranch**: ground motion model specification
- **BranchAttributeValue/Spec**: metadata describing branch parameter choices
- **SourceLogicTreeV1**: deprecated v1 format kept for backwards compatibility

### PSHA Adapter Pattern (`nzshm_model/psha_adapter/`)

Strategy pattern for writing model data to different PSHA engine formats:
- `PshaAdapterInterface` (ABC) → `SourcePshaAdapterInterface`, `GMCMPshaAdapterInterface`, `ConfigPshaAdapterInterface`, `ModelPshaAdapterInterface`
- Concrete implementation: `openquake/` subpackage (OpenquakeConfig, OpenquakeSourcePshaAdapter)
- Usage: `model.psha_adapter(OpenquakeSourcePshaAdapter)` to get engine-specific output

### Branch Registry (`nzshm_model/branch_registry.py`)

Singleton-pattern `Registry` providing identity lookup for branches via shake_256 hash digests. Backed by CSV files in `resources/` (source_branches.csv, gmm_branches.csv).

### Model Versions (`nzshm_model/model_versions/`)

Each version (e.g., `nshm_v1_0_4.py`) is a factory module that constructs an `NshmModel` from JSON/resource files. Current version: `NSHM_v1.0.4` (defined in `model_version.py`).

### Resources (`nzshm_model/resources/`)

JSON configs and CSV registries: `SRM_JSON/` (source rate models), `GMM_JSON/` (ground motion models), `GMM_LTs/` (logic trees), `HAZARD_CONFIG_JSON/`, and branch registry CSVs.

### CLI Tools (`nzshm_model/scripts/`)

Two Click-based entry points:
- `model` (`cli.py`): fetch, convert, unpack, config commands for OpenQuake integration
- `slt` (`slt.py`): ls, to_json, hash_sources, hash_gmms for inspecting logic trees

## Key Dependencies

- **dacite**: dictionary → dataclass conversion (used throughout for deserialization)
- **lxml**: XML processing for NRML/OpenQuake output
- **nzshm-common**: shared NSHM utilities (locations, etc.)
- **click** (optional): CLI framework
- **boto3 + nshm-toshi-client** (optional): Toshi API integration for fetching remote resources
