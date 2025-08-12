# Testing Guide for Analysis Module

The analysis module includes comprehensive testing to ensure reliability, correctness, and robustness of statistical methods and data processing functions.

## Testing Architecture

### Test Organization

```
tests/test_analysis/
├── __init__.py
├── integration/              # Integration tests
│   ├── __init__.py
│   └── test_full_workflow.py
├── unit/                     # Unit tests
│   ├── __init__.py
│   ├── test_ancova_validation.py
│   ├── test_confounder_validation.py
│   ├── test_data_quality_robustness.py
│   ├── test_glycowork_integration.py
│   ├── test_model_training_clustering.py
│   └── test_statistical_correctness.py
├── test_classifiers.py       # Legacy classifier tests
├── test_method_plot.py       # Method comparison plots
├── test_normalizer.py        # Normalization tests
└── test_stat_analyzer.py     # Statistical analyzer tests
```

### Test Categories

1. **Unit Tests**: Individual function validation
2. **Integration Tests**: Full workflow testing
3. **Statistical Validation**: Correctness of statistical methods
4. **Edge Case Testing**: Robustness with problematic data
5. **Performance Tests**: Speed and memory usage validation

## Running Tests

### Basic Test Execution

```bash
# Run all analysis tests
make test

# Run specific test module
uv run python -m pytest tests/test_analysis/ -v

# Run with coverage
uv run python -m pytest tests/test_analysis/ --cov=src/isospec_data_tools/analysis --cov-report=html

# Run specific test file
uv run python -m pytest tests/test_analysis/test_stat_analyzer.py -v

# Run specific test method
uv run python -m pytest tests/test_analysis/test_stat_analyzer.py::TestStatisticalAnalyzer::test_perform_t_test -v
```

### Test Configuration

```python
# pytest configuration in pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src/isospec_data_tools",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
    "--cov-fail-under=90"
]
```

## Unit Testing Examples

### Statistical Tests Validation

```python
# tests/test_analysis/unit/test_statistical_correctness.py
import pytest
import numpy as np
from scipy import stats
from isospec_data_tools.analysis.core.statistical_tests import (
    perform_welch_t_test,
    perform_student_t_test
)

class TestStatisticalCorrectness:
    """Test statistical correctness of implemented methods."""

    def test_welch_t_test_against_scipy(self):
        """Test Welch's t-test against scipy implementation."""
        # Generate test data
        np.random.seed(42)
        group1 = np.random.normal(0, 1, 30)
        group2 = np.random.normal(0.5, 1.2, 35)

        # Our implementation
        result = perform_welch_t_test(group1, group2)

        # Scipy implementation
        scipy_statistic, scipy_p_value = stats.ttest_ind(
            group1, group2, equal_var=False
        )

        # Compare results
        assert abs(result['statistic'] - scipy_statistic) < 1e-10
        assert abs(result['p_value'] - scipy_p_value) < 1e-10
        assert result['degrees_of_freedom'] > 0

    def test_student_t_test_assumptions(self):
        """Test Student's t-test assumption validation."""
        # Generate data with equal variances
        np.random.seed(123)
        group1 = np.random.normal(0, 1, 25)
        group2 = np.random.normal(0.3, 1, 25)

        result = perform_student_t_test(group1, group2)

        # Check assumptions
        assert result['equal_variances_assumed'] is True
        assert 'levene_test' in result
        assert result['levene_test']['p_value'] > 0.05  # Equal variances

    def test_t_test_with_identical_groups(self):
        """Test t-test with identical groups."""
        data = np.array([1, 2, 3, 4, 5])

        result = perform_welch_t_test(data, data)

        assert abs(result['statistic']) < 1e-10
        assert result['p_value'] > 0.99  # Should be very close to 1

    def test_t_test_with_missing_values(self):
        """Test t-test handling of missing values."""
        group1 = np.array([1, 2, np.nan, 4, 5])
        group2 = np.array([2, 3, 4, np.nan, 6])

        result = perform_welch_t_test(group1, group2)

        # Should handle missing values appropriately
        assert not np.isnan(result['statistic'])
        assert not np.isnan(result['p_value'])
        assert result['n1'] == 4  # Excluding NaN
        assert result['n2'] == 4  # Excluding NaN
```

### Preprocessing Tests

```python
# tests/test_analysis/test_normalizer.py
import pytest
import pandas as pd
import numpy as np
from isospec_data_tools.analysis.preprocessing.normalizers import (
    total_abundance_normalization,
    impute_missing_values
)

class TestNormalization:
    """Test normalization functions."""

    @pytest.fixture
    def sample_data(self):
        """Create sample metabolomics data."""
        np.random.seed(42)
        data = pd.DataFrame({
            'sample_id': [f'S{i:03d}' for i in range(1, 21)],
            'SampleType': ['Sample'] * 15 + ['QC'] * 5,
            'metabolite_1': np.random.lognormal(0, 1, 20),
            'metabolite_2': np.random.lognormal(1, 0.5, 20),
            'metabolite_3': np.random.lognormal(0.5, 0.8, 20),
            'group': ['Control'] * 10 + ['Treatment'] * 10
        })
        return data

    def test_total_abundance_normalization(self, sample_data):
        """Test total abundance normalization."""
        feature_cols = ['metabolite_1', 'metabolite_2', 'metabolite_3']

        normalized = total_abundance_normalization(
            data=sample_data,
            feature_cols=feature_cols
        )

        # Check that normalization preserves sample count
        assert len(normalized) == len(sample_data)

        # Check that normalized values are different from original
        for col in feature_cols:
            assert not np.allclose(normalized[col], sample_data[col])

        # Check that total abundance is similar across samples
        total_abundances = normalized[feature_cols].sum(axis=1)
        cv = total_abundances.std() / total_abundances.mean()
        assert cv < 0.1  # CV should be low after normalization

    def test_impute_missing_values_qc_method(self, sample_data):
        """Test QC-based imputation method."""
        feature_cols = ['metabolite_1', 'metabolite_2', 'metabolite_3']

        # Introduce missing values
        data_with_missing = sample_data.copy()
        data_with_missing.loc[0, 'metabolite_1'] = np.nan
        data_with_missing.loc[1, 'metabolite_2'] = np.nan

        # Impute using QC method
        imputed = impute_missing_values(
            data=data_with_missing,
            method="qc_min",
            sample_type_col="SampleType",
            qc_samples=["QC"]
        )

        # Check that missing values are filled
        assert not imputed[feature_cols].isnull().any().any()

        # Check that imputed values are reasonable
        qc_data = sample_data[sample_data['SampleType'] == 'QC']
        qc_min_metabolite_1 = qc_data['metabolite_1'].min()

        assert imputed.loc[0, 'metabolite_1'] == qc_min_metabolite_1

    def test_impute_missing_values_statistical_methods(self, sample_data):
        """Test statistical imputation methods."""
        feature_cols = ['metabolite_1', 'metabolite_2', 'metabolite_3']

        # Introduce missing values
        data_with_missing = sample_data.copy()
        data_with_missing.loc[0, 'metabolite_1'] = np.nan
        data_with_missing.loc[1, 'metabolite_2'] = np.nan

        # Test different imputation methods
        methods = ['median', 'mean', 'zero']

        for method in methods:
            imputed = impute_missing_values(
                data=data_with_missing,
                method=method
            )

            # Check that missing values are filled
            assert not imputed[feature_cols].isnull().any().any()

            # Check specific imputation values
            if method == 'median':
                expected_value = sample_data['metabolite_1'].median()
                assert imputed.loc[0, 'metabolite_1'] == expected_value
            elif method == 'mean':
                expected_value = sample_data['metabolite_1'].mean()
                assert imputed.loc[0, 'metabolite_1'] == expected_value
            elif method == 'zero':
                assert imputed.loc[0, 'metabolite_1'] == 0
```

### ANCOVA Tests

```python
# tests/test_analysis/unit/test_ancova_validation.py
import pytest
import pandas as pd
import numpy as np
from isospec_data_tools.analysis.specialized.ancova_analysis import ANCOVAAnalyzer

class TestANCOVAValidation:
    """Test ANCOVA implementation and validation."""

    @pytest.fixture
    def ancova_data(self):
        """Create sample data for ANCOVA testing."""
        np.random.seed(42)
        n_samples = 100

        # Generate covariates
        age = np.random.normal(45, 10, n_samples)
        bmi = np.random.normal(25, 3, n_samples)

        # Generate treatment groups
        treatment = np.random.choice(['Control', 'Treatment'], n_samples)

        # Generate dependent variables with realistic relationships
        metabolite_1 = (
            2 * (treatment == 'Treatment') +
            0.1 * age +
            0.05 * bmi +
            np.random.normal(0, 1, n_samples)
        )

        metabolite_2 = (
            1.5 * (treatment == 'Treatment') +
            0.08 * age +
            0.02 * bmi +
            np.random.normal(0, 0.8, n_samples)
        )

        data = pd.DataFrame({
            'age': age,
            'bmi': bmi,
            'treatment': treatment,
            'metabolite_1': metabolite_1,
            'metabolite_2': metabolite_2
        })

        return data

    def test_ancova_initialization(self, ancova_data):
        """Test ANCOVA analyzer initialization."""
        analyzer = ANCOVAAnalyzer(
            data=ancova_data,
            dependent_vars=['metabolite_1', 'metabolite_2'],
            factor_col='treatment',
            covariate_cols=['age', 'bmi']
        )

        assert analyzer.data is not None
        assert analyzer.dependent_vars == ['metabolite_1', 'metabolite_2']
        assert analyzer.factor_col == 'treatment'
        assert analyzer.covariate_cols == ['age', 'bmi']

    def test_ancova_assumptions_checking(self, ancova_data):
        """Test ANCOVA assumptions checking."""
        analyzer = ANCOVAAnalyzer(
            data=ancova_data,
            dependent_vars=['metabolite_1'],
            factor_col='treatment',
            covariate_cols=['age', 'bmi']
        )

        assumptions = analyzer.check_assumptions(
            features=['metabolite_1'],
            significance_level=0.05
        )

        assert 'metabolite_1' in assumptions
        assert 'normality' in assumptions['metabolite_1']
        assert 'homoscedasticity' in assumptions['metabolite_1']
        assert 'linearity' in assumptions['metabolite_1']

        # Each assumption should have 'passed' and 'p_value' keys
        for assumption in assumptions['metabolite_1'].values():
            assert 'passed' in assumption
            assert 'p_value' in assumption
            assert isinstance(assumption['passed'], bool)
            assert 0 <= assumption['p_value'] <= 1

    def test_ancova_analysis_execution(self, ancova_data):
        """Test ANCOVA analysis execution."""
        analyzer = ANCOVAAnalyzer(
            data=ancova_data,
            dependent_vars=['metabolite_1', 'metabolite_2'],
            factor_col='treatment',
            covariate_cols=['age', 'bmi']
        )

        results = analyzer.perform_ancova_analysis()

        assert 'factor_effects' in results
        assert 'covariate_effects' in results
        assert 'model_summary' in results

        # Check factor effects
        factor_effects = results['factor_effects']
        assert len(factor_effects) == 2  # Two metabolites

        for metabolite in ['metabolite_1', 'metabolite_2']:
            assert metabolite in factor_effects
            assert 'f_statistic' in factor_effects[metabolite]
            assert 'p_value' in factor_effects[metabolite]
            assert 'degrees_of_freedom' in factor_effects[metabolite]

        # Check covariate effects
        covariate_effects = results['covariate_effects']
        for metabolite in ['metabolite_1', 'metabolite_2']:
            assert metabolite in covariate_effects
            for covariate in ['age', 'bmi']:
                assert covariate in covariate_effects[metabolite]
                assert 'coefficient' in covariate_effects[metabolite][covariate]
                assert 'p_value' in covariate_effects[metabolite][covariate]
```

### Model Training Tests

```python
# tests/test_analysis/unit/test_model_training_clustering.py
import pytest
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from isospec_data_tools.analysis.modeling.clustering import ClusterAnalyzer
from isospec_data_tools.analysis.modeling.model_evaluation import ModelTrainer

class TestModelTrainingClustering:
    """Test machine learning utilities."""

    @pytest.fixture
    def classification_data(self):
        """Create sample classification data."""
        X, y = make_classification(
            n_samples=200,
            n_features=20,
            n_informative=10,
            n_redundant=5,
            n_clusters_per_class=1,
            random_state=42
        )

        feature_cols = [f'feature_{i}' for i in range(X.shape[1])]
        data = pd.DataFrame(X, columns=feature_cols)
        data['target'] = y

        return data, feature_cols

    def test_cluster_analyzer_initialization(self, classification_data):
        """Test cluster analyzer initialization."""
        data, feature_cols = classification_data

        analyzer = ClusterAnalyzer(
            data=data,
            feature_cols=feature_cols
        )

        assert analyzer.data is not None
        assert analyzer.feature_cols == feature_cols
        assert len(analyzer.feature_cols) == 20

    def test_kmeans_clustering(self, classification_data):
        """Test K-means clustering."""
        data, feature_cols = classification_data

        analyzer = ClusterAnalyzer(
            data=data,
            feature_cols=feature_cols
        )

        results = analyzer.perform_kmeans_clustering(
            n_clusters_range=(2, 5),
            random_state=42
        )

        assert 'cluster_results' in results
        assert 'evaluation_metrics' in results
        assert 'optimal_k' in results

        # Check cluster results for different k values
        for k in range(2, 5):
            assert k in results['cluster_results']
            assert 'labels' in results['cluster_results'][k]
            assert 'inertia' in results['cluster_results'][k]
            assert len(results['cluster_results'][k]['labels']) == len(data)

    def test_model_trainer_initialization(self, classification_data):
        """Test model trainer initialization."""
        data, feature_cols = classification_data

        trainer = ModelTrainer(
            data=data,
            target_col='target',
            feature_cols=feature_cols
        )

        assert trainer.data is not None
        assert trainer.target_col == 'target'
        assert trainer.feature_cols == feature_cols

    def test_feature_selection(self, classification_data):
        """Test feature selection methods."""
        data, feature_cols = classification_data

        trainer = ModelTrainer(
            data=data,
            target_col='target',
            feature_cols=feature_cols
        )

        # Test univariate feature selection
        selected_features = trainer.select_features(
            method='univariate',
            k_features=10,
            scoring='f_classif'
        )

        assert len(selected_features) == 10
        assert all(feature in feature_cols for feature in selected_features)

    def test_model_training(self, classification_data):
        """Test model training."""
        data, feature_cols = classification_data

        trainer = ModelTrainer(
            data=data,
            target_col='target',
            feature_cols=feature_cols
        )

        # Train a simple model
        models = trainer.train_classification_models(
            algorithms=['random_forest', 'logistic_regression'],
            cv_folds=3,
            hyperparameter_tuning=False,
            random_state=42
        )

        assert 'random_forest' in models
        assert 'logistic_regression' in models

        # Check model attributes
        rf_model = models['random_forest']
        assert hasattr(rf_model, 'predict')
        assert hasattr(rf_model, 'predict_proba')

        # Test predictions
        predictions = rf_model.predict(data[feature_cols])
        assert len(predictions) == len(data)
        assert all(pred in [0, 1] for pred in predictions)
```

## Integration Testing

### Full Workflow Tests

```python
# tests/test_analysis/integration/test_full_workflow.py
import pytest
import pandas as pd
import numpy as np
from isospec_data_tools.analysis import (
    DataWrangler,
    StatisticalAnalyzer,
    ConfounderAnalyzer,
    ClusterAnalyzer,
    create_project_config
)

class TestFullWorkflow:
    """Test complete analysis workflows."""

    @pytest.fixture
    def metabolomics_study_data(self):
        """Create comprehensive metabolomics study data."""
        np.random.seed(42)
        n_samples = 100
        n_metabolites = 50

        # Create sample metadata
        sample_ids = [f'S{i:03d}' for i in range(1, n_samples + 1)]
        sample_types = ['Sample'] * 80 + ['QC'] * 20
        groups = ['Control'] * 40 + ['Treatment'] * 40 + ['QC'] * 20
        ages = np.random.normal(45, 10, n_samples)
        bmis = np.random.normal(25, 3, n_samples)

        # Create metabolite data
        metabolite_data = {}
        for i in range(n_metabolites):
            metabolite_name = f'metabolite_{i:03d}'

            # Generate realistic metabolite concentrations
            base_concentration = np.random.lognormal(0, 1, n_samples)

            # Add group effects for some metabolites
            if i < 10:  # First 10 metabolites show group differences
                group_effect = np.where(np.array(groups) == 'Treatment', 1.5, 1.0)
                base_concentration *= group_effect

            # Add age effects for some metabolites
            if i < 5:  # First 5 metabolites show age effects
                age_effect = 1 + 0.01 * (ages - 45)
                base_concentration *= age_effect

            metabolite_data[metabolite_name] = base_concentration

        # Combine into DataFrame
        data = pd.DataFrame({
            'sample_id': sample_ids,
            'SampleType': sample_types,
            'group': groups,
            'age': ages,
            'bmi': bmis,
            **metabolite_data
        })

        return data

    def test_complete_analysis_workflow(self, metabolomics_study_data):
        """Test complete analysis workflow."""
        data = metabolomics_study_data
        feature_cols = [col for col in data.columns if col.startswith('metabolite_')]

        # Step 1: Data preprocessing
        wrangler = DataWrangler()

        # Normalization
        normalized_data = wrangler.total_abundance_normalization(
            data=data,
            feature_cols=feature_cols
        )

        # Imputation
        imputed_data = wrangler.impute_missing_values(
            data=normalized_data,
            method='median'
        )

        assert not imputed_data[feature_cols].isnull().any().any()

        # Step 2: Statistical analysis
        analyzer = StatisticalAnalyzer()

        # Filter to samples only (exclude QC)
        sample_data = imputed_data[imputed_data['SampleType'] == 'Sample']

        # Perform t-test
        t_results = analyzer.perform_t_test(
            data=sample_data,
            group_col='group',
            feature_cols=feature_cols,
            test_type='welch'
        )

        assert len(t_results) == len(feature_cols)
        assert 'p_value' in t_results.columns
        assert 'statistic' in t_results.columns

        # Step 3: Confounder analysis
        confounder = ConfounderAnalyzer(
            data=sample_data,
            target_col='group',
            feature_cols=feature_cols
        )

        confounders = confounder.identify_confounders(
            potential_confounders=['age', 'bmi'],
            significance_threshold=0.05
        )

        assert isinstance(confounders, list)

        # Step 4: Clustering analysis
        cluster = ClusterAnalyzer(
            data=sample_data,
            feature_cols=feature_cols
        )

        cluster_results = cluster.perform_clustering(
            methods=['kmeans'],
            n_clusters_range=(2, 5),
            scaling_method='standard'
        )

        assert 'kmeans' in cluster_results
        assert 'cluster_results' in cluster_results['kmeans']

        # Verify workflow integration
        assert len(sample_data) == len(cluster_results['kmeans']['cluster_results'][2]['labels'])

    def test_configuration_driven_workflow(self, metabolomics_study_data):
        """Test configuration-driven analysis workflow."""
        data = metabolomics_study_data
        feature_cols = [col for col in data.columns if col.startswith('metabolite_')]

        # Create configuration
        config = create_project_config()

        # Initialize analyzers with configuration
        wrangler = DataWrangler(config=config)
        analyzer = StatisticalAnalyzer(config=config)

        # Run configured analysis
        sample_data = data[data['SampleType'] == 'Sample']

        processed_data = wrangler.preprocess_data(
            data=sample_data,
            feature_cols=feature_cols
        )

        results = analyzer.run_full_analysis(
            data=processed_data,
            feature_cols=feature_cols,
            group_col='group'
        )

        assert 'preprocessing' in results
        assert 'statistical_tests' in results
        assert 'significant_features' in results

        # Verify configuration was applied
        assert results['preprocessing']['normalization_method'] == 'total_abundance'
        assert results['statistical_tests']['test_type'] == 'welch'
        assert results['statistical_tests']['correction_method'] == 'bonferroni'
```

## Test Data and Fixtures

### Common Test Fixtures

```python
# tests/test_analysis/conftest.py
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_metabolomics_data():
    """Standard metabolomics test data."""
    np.random.seed(42)
    n_samples = 60
    n_metabolites = 20

    # Create sample metadata
    sample_data = {
        'sample_id': [f'S{i:03d}' for i in range(1, n_samples + 1)],
        'SampleType': ['Sample'] * 50 + ['QC'] * 10,
        'group': ['Control'] * 25 + ['Treatment'] * 25 + ['QC'] * 10,
        'age': np.random.normal(45, 10, n_samples),
        'bmi': np.random.normal(25, 3, n_samples),
        'batch': np.random.choice(['B1', 'B2', 'B3'], n_samples)
    }

    # Create metabolite data
    for i in range(n_metabolites):
        metabolite_name = f'metabolite_{i:03d}'
        concentrations = np.random.lognormal(0, 1, n_samples)

        # Add some group effects
        if i < 5:
            group_effect = np.where(np.array(sample_data['group']) == 'Treatment', 1.5, 1.0)
            concentrations *= group_effect

        sample_data[metabolite_name] = concentrations

    return pd.DataFrame(sample_data)

@pytest.fixture
def feature_columns():
    """Standard feature column names."""
    return [f'metabolite_{i:03d}' for i in range(20)]

@pytest.fixture
def statistical_test_data():
    """Data specifically for statistical test validation."""
    np.random.seed(123)

    # Create groups with known differences
    control_group = np.random.normal(0, 1, 30)
    treatment_group = np.random.normal(0.5, 1, 30)

    return {
        'control': control_group,
        'treatment': treatment_group,
        'identical': control_group,
        'different_variance': np.random.normal(0.5, 2, 30)
    }
```

## Test Utilities

### Custom Test Helpers

```python
# tests/test_analysis/test_utils.py
import numpy as np
import pandas as pd
from scipy import stats

def assert_statistical_equivalence(result1, result2, tolerance=1e-10):
    """Assert that two statistical results are equivalent within tolerance."""
    assert abs(result1['statistic'] - result2['statistic']) < tolerance
    assert abs(result1['p_value'] - result2['p_value']) < tolerance

def assert_dataframe_normalized(data, feature_cols, normalization_type='total_abundance'):
    """Assert that a dataframe has been properly normalized."""
    if normalization_type == 'total_abundance':
        # Check that total abundances are similar
        total_abundances = data[feature_cols].sum(axis=1)
        cv = total_abundances.std() / total_abundances.mean()
        assert cv < 0.1, f"CV of total abundances too high: {cv}"

    elif normalization_type == 'median_quotient':
        # Check that median quotients are close to 1
        median_values = data[feature_cols].median()
        quotients = data[feature_cols] / median_values
        median_quotients = quotients.median(axis=1)
        assert abs(median_quotients.median() - 1.0) < 0.01

def assert_no_missing_values(data, feature_cols):
    """Assert that there are no missing values in specified columns."""
    assert not data[feature_cols].isnull().any().any()

def assert_valid_p_values(p_values):
    """Assert that p-values are valid."""
    assert all(0 <= p <= 1 for p in p_values)
    assert not any(np.isnan(p) for p in p_values)

def create_test_data_with_known_effects(n_samples=100, n_features=20, effect_size=0.5):
    """Create test data with known statistical effects."""
    np.random.seed(42)

    # Create features with known group differences
    control_data = np.random.normal(0, 1, (n_samples // 2, n_features))
    treatment_data = np.random.normal(effect_size, 1, (n_samples // 2, n_features))

    # Combine data
    all_data = np.vstack([control_data, treatment_data])
    groups = ['Control'] * (n_samples // 2) + ['Treatment'] * (n_samples // 2)

    feature_cols = [f'feature_{i}' for i in range(n_features)]
    data = pd.DataFrame(all_data, columns=feature_cols)
    data['group'] = groups

    return data, feature_cols
```

## Performance Testing

### Benchmark Tests

```python
# tests/test_analysis/test_performance.py
import pytest
import time
import numpy as np
import pandas as pd
from memory_profiler import profile

class TestPerformance:
    """Test performance characteristics of analysis functions."""

    def test_normalization_performance(self, benchmark):
        """Benchmark normalization performance."""
        # Create large dataset
        n_samples = 1000
        n_features = 500

        data = pd.DataFrame(
            np.random.lognormal(0, 1, (n_samples, n_features)),
            columns=[f'feature_{i}' for i in range(n_features)]
        )

        feature_cols = data.columns.tolist()

        # Benchmark normalization
        result = benchmark(
            total_abundance_normalization,
            data=data,
            feature_cols=feature_cols
        )

        assert len(result) == n_samples
        assert len(result.columns) == n_features

    def test_statistical_test_performance(self, benchmark):
        """Benchmark statistical test performance."""
        # Create test data
        n_samples = 1000
        group1 = np.random.normal(0, 1, n_samples)
        group2 = np.random.normal(0.2, 1, n_samples)

        # Benchmark t-test
        result = benchmark(
            perform_welch_t_test,
            group1_data=group1,
            group2_data=group2
        )

        assert 'p_value' in result
        assert 'statistic' in result

    @profile
    def test_memory_usage_large_dataset(self):
        """Test memory usage with large datasets."""
        # Create very large dataset
        n_samples = 10000
        n_features = 1000

        data = pd.DataFrame(
            np.random.lognormal(0, 1, (n_samples, n_features)),
            columns=[f'feature_{i}' for i in range(n_features)]
        )

        feature_cols = data.columns.tolist()

        # Test memory-efficient normalization
        result = total_abundance_normalization(
            data=data,
            feature_cols=feature_cols
        )

        # Should not consume excessive memory
        assert len(result) == n_samples
        assert len(result.columns) == n_features
```

## Continuous Integration Testing

### GitHub Actions Configuration

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11, 3.12]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install uv
          uv sync --dev

      - name: Run tests
        run: |
          uv run pytest tests/ --cov=src/isospec_data_tools --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Best Practices

### Test Writing Guidelines

1. **Clear test names**: Use descriptive test method names
2. **Isolated tests**: Each test should be independent
3. **Comprehensive coverage**: Test both success and failure cases
4. **Edge case testing**: Include boundary conditions and error cases
5. **Performance testing**: Include benchmarks for critical functions

### Test Data Management

1. **Reproducible data**: Use fixed random seeds
2. **Realistic data**: Create data that mimics real-world scenarios
3. **Edge cases**: Include problematic data patterns
4. **Data validation**: Verify test data properties

### Assertion Strategies

1. **Specific assertions**: Use precise assertions rather than generic ones
2. **Error messages**: Include helpful error messages
3. **Tolerance levels**: Use appropriate tolerance for numerical comparisons
4. **Multiple assertions**: Test multiple aspects of results

For more information on running and writing tests, see the project's testing documentation and CI configuration.
