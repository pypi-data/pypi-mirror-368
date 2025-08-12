"""Memory-efficient preprocessing pipeline for large datasets.

This module provides a pipeline class that chains preprocessing operations
while minimizing memory usage through in-place operations and smart
intermediate result management.
"""

import logging
from collections.abc import Callable
from typing import Any, Optional, Union

import pandas as pd

from isospec_data_tools.analysis.core.project_config import DataStructureConfig

from ..utils.exceptions import DataValidationError
from .normalizers import impute_missing_values, total_abundance_normalization
from .transformers import log2_transform_numeric

# Configure logging
logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """
    Memory-efficient preprocessing pipeline for large omics datasets.

    This class chains preprocessing operations while minimizing memory usage
    through in-place operations and intermediate result management.

    Example:
        >>> config = DataStructureConfig(feature_prefix="FT-")
        >>> pipeline = PreprocessingPipeline(data_config=config)
        >>>
        >>> # Chain operations with automatic memory management
        >>> result = (pipeline
        ...     .impute_missing_values(method='qc_min')
        ...     .normalize_total_abundance()
        ...     .log2_transform()
        ...     .execute(data))

        # Memory-efficient version for large datasets
        >>> pipeline = PreprocessingPipeline(data_config=config, memory_efficient=True)
        >>> pipeline.execute_inplace(data)  # Modifies data in place
    """

    def __init__(
        self,
        data_config: DataStructureConfig,
        memory_efficient: bool = False,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ):
        """
        Initialize preprocessing pipeline.

        Args:
            data_config: Configuration for data structure mapping
            memory_efficient: If True, use in-place operations to minimize memory usage
            progress_callback: Optional callback function for progress updates
        """
        self.data_config = data_config
        self.memory_efficient = memory_efficient
        self.progress_callback = progress_callback
        self._operations: list[dict[str, Any]] = []
        self._current_step = 0

    def impute_missing_values(
        self, method: str = "qc_min", fill_value: Optional[float] = None
    ) -> "PreprocessingPipeline":
        """
        Add missing value imputation to the pipeline.

        Args:
            method: Imputation method ('qc_min', 'median', 'mean', 'zero', 'constant')
            fill_value: Value for constant imputation

        Returns:
            Self for method chaining
        """
        self._operations.append({
            "function": impute_missing_values,
            "kwargs": {
                "data_config": self.data_config,
                "method": method,
                "fill_value": fill_value,
                "inplace": self.memory_efficient,
            },
            "name": f"Impute missing values ({method})",
        })
        return self

    def normalize_total_abundance(self, prefix: Optional[str] = None) -> "PreprocessingPipeline":
        """
        Add total abundance normalization to the pipeline.

        Args:
            prefix: Feature column prefix

        Returns:
            Self for method chaining
        """
        feature_prefix = prefix or self.data_config.feature_prefix
        self._operations.append({
            "function": total_abundance_normalization,
            "kwargs": {"prefix": feature_prefix, "inplace": self.memory_efficient},
            "name": "Total abundance normalization",
        })
        return self

    def log2_transform(self, prefix: Optional[str] = None) -> "PreprocessingPipeline":
        """
        Add log2 transformation to the pipeline.

        Args:
            prefix: Feature column prefix

        Returns:
            Self for method chaining
        """
        feature_prefix = prefix or self.data_config.feature_prefix
        self._operations.append({
            "function": log2_transform_numeric,
            "kwargs": {"prefix": feature_prefix, "inplace": self.memory_efficient},
            "name": "Log2 transformation",
        })
        return self

    def add_custom_operation(self, function: Callable[..., Any], name: str, **kwargs: Any) -> "PreprocessingPipeline":
        """
        Add a custom preprocessing operation to the pipeline.

        Args:
            function: Function to call (must accept DataFrame as first argument)
            name: Human-readable name for the operation
            **kwargs: Additional arguments to pass to the function

        Returns:
            Self for method chaining
        """
        if self.memory_efficient:
            kwargs["inplace"] = True

        self._operations.append({"function": function, "kwargs": kwargs, "name": name})
        return self

    def execute(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Execute the preprocessing pipeline.

        Args:
            data: Input DataFrame

        Returns:
            Processed DataFrame (or input DataFrame if memory_efficient=True)

        Raises:
            DataValidationError: If any preprocessing step fails
        """
        if not self._operations:
            logger.warning("No operations defined in pipeline")
            return data

        logger.info(f"Executing preprocessing pipeline with {len(self._operations)} operations")

        if self.memory_efficient:
            logger.info("Using memory-efficient mode (in-place operations)")

        current_data = data
        total_steps = len(self._operations)

        try:
            for i, operation in enumerate(self._operations):
                self._current_step = i + 1
                op_name = operation["name"]

                if self.progress_callback:
                    self.progress_callback(op_name, self._current_step, total_steps)

                logger.info(f"Step {self._current_step}/{total_steps}: {op_name}")

                # Execute operation
                result = operation["function"](current_data, **operation["kwargs"])

                # Handle result based on memory mode
                if self.memory_efficient:
                    # In memory-efficient mode, functions return None and modify in-place
                    if result is not None:
                        logger.warning(f"Operation {op_name} returned data despite inplace=True")
                else:
                    # In normal mode, functions return modified data
                    if result is None:
                        raise DataValidationError(f"Operation {op_name} returned None unexpectedly")
                    current_data = result

            logger.info("Preprocessing pipeline completed successfully")
            return current_data

        except Exception as e:
            logger.exception(f"Pipeline failed at step {self._current_step}: {operation['name']}")
            raise DataValidationError(f"Preprocessing pipeline failed: {e}") from e

    def execute_inplace(self, data: pd.DataFrame) -> None:
        """
        Execute the pipeline with in-place modifications (memory efficient).

        Args:
            data: DataFrame to modify in place

        Raises:
            DataValidationError: If any preprocessing step fails
        """
        # Temporarily set memory efficient mode
        original_mode = self.memory_efficient
        self.memory_efficient = True

        try:
            self.execute(data)
        finally:
            # Restore original mode
            self.memory_efficient = original_mode

    def get_memory_estimate(self, data_shape: tuple[int, int]) -> dict[str, Union[int, float, str]]:
        """
        Estimate memory usage for the pipeline.

        Args:
            data_shape: Shape tuple (rows, cols) of input data

        Returns:
            Dictionary with memory estimates
        """
        rows, cols = data_shape
        # Assume 8 bytes per float64 value
        base_memory_mb = (rows * cols * 8) / (1024 * 1024)

        if self.memory_efficient:
            # In-place operations use minimal additional memory
            estimated_peak_mb = base_memory_mb * 1.1  # 10% overhead
            mode = "Memory-efficient (in-place)"
        else:
            # Each operation creates a copy
            estimated_peak_mb = base_memory_mb * (len(self._operations) + 1)
            mode = "Standard (creates copies)"

        return {
            "base_memory_mb": round(base_memory_mb, 2),
            "estimated_peak_mb": round(estimated_peak_mb, 2),
            "operations_count": len(self._operations),
            "mode": mode,
            "recommendation": "Use memory_efficient=True for datasets > 100MB"
            if base_memory_mb > 100
            else "Current mode is suitable",
        }

    def clear(self) -> "PreprocessingPipeline":
        """
        Clear all operations from the pipeline.

        Returns:
            Self for method chaining
        """
        self._operations.clear()
        self._current_step = 0
        logger.info("Pipeline operations cleared")
        return self

    def __repr__(self) -> str:
        """String representation of the pipeline."""
        mode = "memory-efficient" if self.memory_efficient else "standard"
        operations = [op["name"] for op in self._operations]
        return f"PreprocessingPipeline(mode={mode}, operations={operations})"
