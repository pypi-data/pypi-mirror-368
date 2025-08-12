# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical Development Rules

### Package Management - UV ONLY

- **ONLY use uv, NEVER pip**
- Installation: `uv add package`
- Running tools: `uv run tool`
- Upgrading: `uv add --dev package --upgrade-package package`
- **FORBIDDEN**: `uv pip install`, `@latest` syntax
- Project setup: `make install` (installs environment and pre-commit hooks)

### Code Quality Standards (Non-negotiable)

- **Type hints required for all code** - use the most specific types possible
- **Public APIs must have Google-style docstrings** with thorough explanations
- Functions must be focused and small
- Follow existing patterns exactly
- Line length: 120 characters maximum
- Aim for high test coverage (90% or higher)

### CI Failure Resolution Order

1. **Formatting issues** (ruff format)
2. **Type errors** (mypy)
3. **Linting issues** (ruff check)
4. **Dependency issues** (deptry)

## Development Commands

### Setup and Installation

```bash
make install           # Install virtual environment and pre-commit hooks
```

### Code Quality and Testing

```bash
make check            # Run all quality checks (linting, mypy, deptry)
uv run pre-commit run -a  # Run pre-commit hooks on all files
make test             # Run pytest with coverage
uv run mypy src/isospec_data_tools  # Type checking
uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml  # Full test command
```

### Building and Publishing

```bash
make build            # Build wheel file
make docs             # Build and serve documentation
make docs-test        # Test documentation build
```

### Single Test Execution

```bash
uv run python -m pytest tests/test_analysis/test_stat_analyzer.py::TestStatisticalAnalyzer::test_specific_method -v
```

## Architecture Overview

### Core Package Structure

The `isospec_data_tools` package is organized into four main modules:

1. **`analysis/`** - Statistical analysis and data processing

   - `StatisticalAnalyzer`: ANCOVA, t-tests, chi-square tests with multiple comparison corrections
   - `DataWrangler`: Data normalization, filtering, and imputation
   - `ConfounderAnalyzer`: Confounder analysis and visualization
   - `GlycoworkAnalyzer`: Glycowork library integration for glycan analysis
   - `ClusterAnalyzer`, `ModelTrainer`: Machine learning utilities

2. **`sst_validation/`** - System Suitability Testing for LC-MS

   - `SystemSuitability`: Main validation orchestrator
   - `ValidationThresholds`: Configurable validation parameters
   - Metrics modules: mass accuracy, resolution, sensitivity, retention time, peak shape
   - Comprehensive validation reports and visualizations

3. **`io_utils/`** - Data input/output utilities

   - `MZMineFeatureTable`: MZmine feature table processing
   - `convert_mzmine_feature_table`: Format conversion utilities
   - `save_fig`: Figure saving utilities

4. **`visualization/`** - Plotting and visualization
   - Analysis plots: cluster, confounder, differential analysis
   - SST validation plots: mass accuracy, peak areas, retention time differences
   - Method comparison visualizations
   - **Preprocessing visualizations**: Missing data analysis, CV improvement tracking, feature abundance classification
     - `PreprocessingPlotter`: Visualize missing data patterns and preprocessing pipeline results
     - `FeatureAbundanceClassifier`: Classify and visualize feature abundance distributions
     - `CVAnalysisPlotter`: Track CV improvements through normalization steps

### Key Design Patterns

- **Modular Architecture**: Each module has a single responsibility (MECE principle)
- **Dataclass Configuration**: Multiple configuration dataclasses for type-safe configuration:
  - `DataStructureConfig`: Flexible data structure mapping with QC sample identification
  - `StatisticalConfig`: Statistical thresholds and analysis parameters
  - `VisualizationConfig`: Visual customization and layout settings
  - `TransformationPipelineConfig`: Transformation pipeline tracking
  - `NormalizationConfig`: Normalization method definitions
  - `ValidationThresholds`: SST validation parameters
- **Configuration Factory**: `ConfigFactory` provides centralized configuration management
- **Comprehensive Error Handling**: Custom exceptions for validation errors
- **Statistical Rigor**: Multiple comparison corrections, effect size calculations
- **Visualization Integration**: Each analysis module paired with corresponding visualization functions

### Testing Strategy

- Tests organized by module: `test_analysis/`, `test_sst_validation/`
- High coverage requirements with comprehensive edge case testing
- Integration tests for complex workflows
- Doctest integration for example validation
- Framework: `make test` or `uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml`
- New features require tests, bug fixes require regression tests

### Configuration Files

- `pyproject.toml`: Primary configuration for dependencies, tools, and project metadata
- `Makefile`: Development workflow automation
- `tox.ini`: Multi-version Python testing
- `.cursor/rules/`: Development guidelines and coding standards
- Ruff configuration includes security linting (bandit), complexity checks, and comprehensive style rules

### CLI Interface

The SST validation module provides a command-line interface:

```bash
isospec-validate --acquisition-list data.csv --feature-table features.csv --endogenous-compounds endogenous.csv --exogenous-compounds exogenous.csv --output-dir results/
```

### Data Processing Workflow

1. **Data Ingestion**: MZmine feature tables, acquisition lists, compound libraries
2. **Validation**: System suitability checks across multiple metrics
3. **Analysis**: Statistical analysis with proper multiple comparison corrections
4. **Visualization**: Automated plot generation for all validation results
5. **Reporting**: Markdown and JSON reports with pass/fail indicators

## Development Best Practices

### Environment Setup

```bash
make install  # Creates virtual environment and installs pre-commit hooks
```

### Quality Checks

```bash
make check    # Runs all quality tools in sequence:
              # - Lock file consistency check
              # - Pre-commit hooks (ruff format, ruff check)
              # - MyPy type checking
              # - Deptry dependency analysis
```

### Documentation

```bash
make docs-test  # Test documentation build
make docs      # Build and serve documentation locally
```

### Build and Publish

```bash
make build              # Build wheel file
make publish           # Publish to PyPI
make build-and-publish # Build and publish in one step
```

## Code Quality Tools and Standards

### Ruff (Primary Tool)

- Format: `uv run ruff format .`
- Check: `uv run ruff check .`
- Fix: `uv run ruff check . --fix`
- **Critical requirements**:
  - Line length (120 chars)
  - Import sorting (I001)
  - No unused imports
  - Comprehensive linting rules (see pyproject.toml)

### Type Checking (MyPy)

- Tool: `uv run mypy src/isospec_data_tools`
- **Requirements**:
  - Explicit None checks for Optional types
  - Type narrowing for strings
  - Disallow untyped definitions
  - All source files must have type annotations

### Dependency Management (Deptry)

- Tool: `uv run deptry .`
- Checks for obsolete and missing dependencies
- Ensures clean dependency graph

### Pre-commit Hooks

- Config: `.pre-commit-config.yaml`
- Runs automatically on git commit
- Includes Ruff formatting and linting
- Use `uv run pre-commit run -a` to run manually

## Code Philosophy and Architecture

### Pythonic Development Principles

- **Elegance and Readability**: Write code that is easy to understand and maintain
- **PEP 8 Compliance**: Follow Python style guidelines strictly
- **Explicit over Implicit**: Favor clear, explicit code over overly concise code
- **Zen of Python**: Keep Python principles in mind for design decisions

### Architecture Principles

- **Single Responsibility**: Each module should have one well-defined responsibility
- **Reusable Components**: Develop composable functions and classes
- **Modular Package Structure**: Organize code into logical packages and modules

### Code Quality Requirements

- **Comprehensive Type Annotations**: All functions, methods, and class members
- **Google-style Docstrings**: Detailed documentation for all public APIs
- **Robust Exception Handling**: Use specific exceptions with informative messages
- **Strategic Logging**: Use the logging module for important events and errors

### Exception Handling Best Practices

- **Always use `logger.exception()` instead of `logger.error()` when catching exceptions**
  - Correct: `logger.exception("Failed to process data")`
  - Incorrect: `logger.exception(f"Failed: {e}")`
- **Catch specific exceptions** where possible:
  - File operations: `except (OSError, PermissionError):`
  - JSON parsing: `except json.JSONDecodeError:`
  - Network operations: `except (ConnectionError, TimeoutError):`
- **Only catch `Exception` for**:
  - Top-level handlers that must not crash
  - Cleanup blocks (log at debug level)

## Git Workflow

### Commit Guidelines

- For bug fixes or features based on user reports:
  ```bash
  git commit --trailer "Reported-by:<name>"
  ```
- For commits related to GitHub issues:
  ```bash
  git commit --trailer "Github-Issue:#<number>"
  ```
- **NEVER mention `co-authored-by` or AI tools** in commits or PRs
- **When writing commit messages, never mentioned claude code**

### Pull Requests

- Create detailed descriptions focusing on:
  - High-level problem description
  - Solution approach
  - Avoid code-specific details unless necessary for clarity
- Always add `jerome3o-anthropic` and `jspahrsummers` as reviewers
- **NEVER mention AI tools or co-authoring** in PR descriptions

## Troubleshooting Common Issues

### Line Length Violations

- Break strings with parentheses
- Use multi-line function calls with proper indentation
- Split long imports across multiple lines

### Type Errors

- Add explicit None checks for Optional types
- Use type narrowing for complex types
- Verify function signatures match expectations

### Import Issues

- Remove unused imports
- Follow isort conventions
- Group imports properly (stdlib, third-party, local)

### Development Best Practices

- Run `make check` before committing
- Check git status before commits
- Keep changes minimal and focused
- Follow existing code patterns
- Document all public APIs thoroughly
- Test edge cases and error conditions

## Documentation Standards

### Code Documentation

- **Google-style docstrings** for all public functions, methods, and classes
- Include purpose, parameters, return values, and exceptions
- Provide usage examples where helpful
- Document complex algorithms with inline comments

### Project Documentation

- Keep README.md updated with current setup instructions
- Maintain API documentation using mkdocs
- Document environment setup and dependencies
- Include troubleshooting guides for common issues

### Example Code Requirements

All code must demonstrate:

- Complete type annotations
- Comprehensive Google-style docstrings
- Proper error handling
- Clear inline comments for complex logic
- Usage examples (in tests or `__main__` sections)
- Ruff-compliant formatting

## Code Refactoring Guidelines

### Key Principles for Refactoring

- **Never diverge from the core logic of a function during refactoring**
- Maintain the original function's intent and primary algorithm
- Preserve existing parameter interfaces and return types
- Use type hints, comprehensive docstrings, and clear error handling
- Example refactoring anti-pattern:
  - Do NOT fundamentally change the imputation logic when refactoring a data imputation function
  - Keep the core strategy (e.g., using QC samples, using median/mean) consistent
  - Improve code structure, readability, and error handling without changing the core algorithm

## Critical Function Implementations

### QC-Based Missing Value Imputation

The `impute_missing_values` function in `src/isospec_data_tools/analysis/preprocessing/normalizers.py` implements domain-specific imputation logic:

- **Default method**: `qc_min` - Uses minimum values from QC samples for imputation
- **QC Sample Types**: Defaults to `["QC", "EQC"]` but configurable via `qc_samples` parameter
- **Replacement Processing**: Replaces specified values (default=1) with NaN before imputation
- **Backward Compatibility**: Supports statistical methods (`median`, `mean`, `zero`, `constant`)
- **Error Handling**: Validates QC sample availability and data integrity

**Key Parameters:**

- `sample_type_col`: Column containing sample type information (default: "SampleType")
- `qc_samples`: List of QC sample types for imputation reference
- `replacement_value`: Value to replace with NaN before imputation (default: 1)
- `method`: Imputation strategy - `qc_min` (default), `median`, `mean`, `zero`, `constant`

This implementation preserves the original analytical chemistry domain logic where QC samples provide the most appropriate reference values for missing data imputation.

## Project Configuration System

### Overview

The project configuration system (`analysis.core.project_config`) provides a simplified but flexible configuration management system for analysis workflows. The system has been redesigned from a complex multi-file structure to a single, maintainable module while preserving all user-facing APIs.

### Configuration Classes

1. **`DataStructureConfig`**: Manages data structure mapping and QC sample identification

   - Flexible QC detection methods (contains, equals, callable, list)
   - Configurable sample and feature column names
   - Support for metadata column tracking

2. **`StatisticalConfig`**: Defines statistical analysis parameters

   - CV thresholds and ranges for categorization
   - Percentile thresholds for abundance classification
   - Effect size and p-value thresholds
   - Histogram bin configurations

3. **`VisualizationConfig`**: Controls visual presentation

   - Figure layout dimensions for different plot types
   - Color schemes for sample types, improvements, and abundance levels
   - Style configuration (font sizes, colors, alpha values)

4. **`TransformationPipelineConfig`**: Tracks transformation pipelines

   - Stores transformation results at each stage
   - CV data tracking across pipeline stages
   - Configurable stage names, colors, and descriptions

5. **`NormalizationConfig`**: Defines normalization methods
   - Predefined configs: `tan_config()`, `mqn_config()`
   - Customizable method names and descriptions

### Configuration Management

The `ConfigFactory` class provides centralized configuration management:

```python
from isospec_data_tools.analysis import create_project_config, save_project_config, load_project_config

# Create default configuration
config = create_project_config()

# Create with custom settings
from isospec_data_tools.analysis.core.project_config import DataStructureConfig, StatisticalConfig

custom_data_config = DataStructureConfig(
    sample_column="SampleID",
    qc_identifier=["QC", "POOLED_QC"],
    feature_prefix="Feature_"
)

config = create_project_config(data_config=custom_data_config)

# Save and load configurations
save_project_config(config, "my_project_config.json")
loaded_config = load_project_config("my_project_config.json")

# Special configurations for specific studies
from isospec_data_tools.analysis.core.project_config import ConfigFactory
data_config, stats_config, viz_config = ConfigFactory.colaus_defaults()
```

### Import Changes

The configuration system restructure requires the following import updates:

- **Removed**: `ProjectConfig` class no longer exists
- **Added**: Direct access to configuration dataclasses
- **Factory functions**: `create_project_config`, `load_project_config`, `save_project_config` remain unchanged

```python
# Old (no longer works)
from isospec_data_tools.analysis import ProjectConfig

# New
from isospec_data_tools.analysis import create_project_config
from isospec_data_tools.analysis.core.project_config import (
    ConfigFactory,
    DataStructureConfig,
    StatisticalConfig,
    VisualizationConfig,
    TransformationPipelineConfig,
    NormalizationConfig
)
```

## Code Integration Best Practices

### When Integrating External Code

When integrating external code into isospec-data-tools:

- **Avoid code duplication**: Always check for existing utilities before adding new ones

  - CV calculations → Use existing `CVAnalyzer` from `method_plot.py`
  - Figure saving → Use existing `save_fig` from `io_utils`
  - Statistical utilities → Use existing `StatisticalAnalyzer` from `confounder_plots.py`
  - Plot helpers → Use existing `PlotHelper` for subplot creation

- **Maintain external API compatibility**: When users have existing code:

  - Create wrapper classes with deprecation warnings for legacy APIs
  - Keep original function signatures and class names
  - Only require users to change import paths, not their usage code

- **Example: Preprocessing Visualization Integration**
  - ~60% code reduction achieved by reusing existing utilities
  - Classes available: `PreprocessingPlotter`, `FeatureAbundanceClassifier`, `CVAnalysisPlotter`
  - External users only need to change: `from preprocessing import X` → `from isospec_data_tools.visualization.analysis import X`
