# System Suitability Testing (SST) Validation

The SST validation module provides comprehensive system suitability validation for LC-MS data, ensuring that the mass spectrometer was well calibrated and conditioned for subsequent acquisitions.

## Overview

The module performs several critical validation checks:

1. **Mass Accuracy**: Evaluates mass error (ppm) for known compounds
2. **Mass Resolution**: Measures Full Width at Half Maximum (FWHM)
3. **Sensitivity and Signal Intensity**: Evaluates Signal-to-Noise ratio (S/N) and peak areas
4. **Retention Time Stability**: Measures RT deviation and reproducibility
5. **Peak Shape**: Evaluates peak asymmetry and tailing factors

## Installation

```bash
pip install isospec-data-tools
```

## Usage

### Basic Usage

```python
from isospec_data_tools.sst_validation import SystemSuitability, ValidationThresholds

# Initialize validator with default thresholds
validator = SystemSuitability(
    acquisition_list="path/to/acquisition_list.csv",
    feature_table="path/to/mzmine_features.csv",
    endogenous_compounds="path/to/endogenous_compounds.csv",
    exogenous_compounds="path/to/exogenous_compounds.csv"
)

# Run validation
results = validator.run_all_validations()

# Generate report
validator.generate_report("validation_report.md")

# Generate plots
validator.generate_plots("plots_directory")
```

### Custom Thresholds

```python
# Configure custom validation thresholds
thresholds = ValidationThresholds(
    mass_accuracy_ppm=5.0,  # Stricter mass accuracy requirement
    resolution_threshold=40000,  # Higher resolution requirement
    sn_ratio_high=200,  # Higher S/N requirement for standards
    sn_ratio_low=20,  # Higher S/N requirement for endogenous compounds
    rt_deviation_minutes=0.05,  # Stricter RT stability requirement
    peak_asymmetry_range=(0.95, 1.25)  # Tighter peak shape
)

# Initialize validator with custom thresholds
validator = SystemSuitability(
    acquisition_list="path/to/acquisition_list.csv",
    feature_table="path/to/mzmine_features.csv",
    endogenous_compounds="path/to/endogenous_compounds.csv",
    exogenous_compounds="path/to/exogenous_compounds.csv",
    thresholds=thresholds
)
```

### Command Line Interface

```bash
# Run validation from command line
isospec-validate \
    --acquisition-list path/to/acquisition_list.csv \
    --feature-table path/to/mzmine_features.csv \
    --endogenous-compounds path/to/endogenous_compounds.csv \
    --exogenous-compounds path/to/exogenous_compounds.csv \
    --output-dir validation_results
```

## Input Files

### Acquisition List (CSV)

Contains batch acquisition information with the following required columns:

- `filename`: Raw data file name
- `class`: Sample class/type
- `replicate_group`: Group identifier for replicates
- `acquisition_order`: Order of acquisition
- `batch`: Batch identifier

Example:

```csv
filename,class,replicate_group,acquisition_order,batch
sample1.raw,standard,group1,1,batch1
sample2.raw,standard,group1,2,batch1
sample3.raw,endogenous,group2,3,batch1
```

### Feature Table (CSV)

Tidy feature table from MZmine with the following required columns:

- `mz`: Mass-to-charge ratio
- `rt`: Retention time
- `area`: Peak area
- `height`: Peak height
- `fwhm`: Full width at half maximum
- `asymmetry`: Peak asymmetry factor
- `tailing`: Peak tailing factor
- One column per sample file containing intensity values

### Target Compounds Lists (CSV)

Two separate files for endogenous and exogenous compounds with the following required columns:

- `name`: Compound name
- `mz`: Theoretical m/z
- `rt`: Expected retention time (optional)
- `abundance_level`: 'high' or 'low' (for S/N thresholds)

Example:

```csv
name,mz,rt,abundance_level
Caffeine,195.0877,5.2,high
Glucose,180.0634,3.8,low
```

## Output

The validation process generates several outputs:

1. **Validation Report** (`validation_report.md`)

   - Detailed markdown report with validation results
   - Includes summary statistics and detailed findings
   - Color-coded pass/fail indicators

2. **Visualization Plots**

   - Peak area distribution
   - Mass accuracy distribution
   - Peak asymmetry histogram
   - Retention time differences pyramid plot

3. **JSON Results** (`system_suitability_report_TIMESTAMP.json`)
   - Machine-readable format for further processing
   - Contains all raw validation results and metrics

## Exit Codes

- `0`: All validation checks passed
- `1`: One or more validation checks failed or an error occurred

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
