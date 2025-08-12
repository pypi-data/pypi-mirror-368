# System Suitability Testing (SST) Validation

The SST validation module provides comprehensive system suitability validation for LC-MS data, ensuring that the mass spectrometer was well calibrated and conditioned for subsequent acquisitions.

## Overview

The module performs several critical validation checks:

1. **Mass Accuracy**: Evaluates mass error (ppm) for known compounds
2. **Mass Resolution**: Measures Full Width at Half Maximum (FWHM)
3. **Sensitivity and Signal Intensity**: Evaluates Signal-to-Noise ratio (S/N) and peak areas
4. **Retention Time Stability**: Measures RT deviation and reproducibility
5. **Peak Shape**: Evaluates peak asymmetry and tailing factors

## Usage

```python
from isospec_data_tools.sst_validation import SystemSuitability, ValidationThresholds

# Configure validation thresholds
thresholds = ValidationThresholds(
    mass_accuracy_ppm=5.0,
    resolution_min=30000,
    sn_ratio_high=100,
    sn_ratio_low=10,
    rt_deviation_max=0.1,
    peak_asymmetry_range=(0.9, 1.2)
)

# Initialize validator
validator = SystemSuitability(
    acquisition_list="path/to/acquisition_list.csv",
    feature_table="path/to/mzmine_features.csv",
    endogenous_compounds="path/to/endogenous_compounds.csv",
    exogenous_compounds="path/to/exogenous_compounds.csv",
    thresholds=thresholds
)

# Run validation
results = validator.validate()

# Generate report
validator.generate_report("validation_reports")
```

## Input Files

### Acquisition List (CSV)

Contains batch acquisition information with the following required columns:

- `filename`: Raw data file name
- `class`: Sample class/type
- `replicate_group`: Group identifier for replicates
- `acquisition_order`: Order of acquisition
- `batch`: Batch identifier

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

## API Reference

::: isospec_data_tools.sst_validation.SystemSuitability
handler: python
options:
show_root_heading: true
show_source: false

::: isospec_data_tools.sst_validation.ValidationThresholds
handler: python
options:
show_root_heading: true
show_source: false
