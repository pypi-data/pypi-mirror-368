"""
Machine learning classification utilities.

This module provides comprehensive tools for model training with cross-validation,
hyperparameter tuning, and performance evaluation for classification tasks.

Note: This is a compatibility wrapper. The actual implementation has been moved to
analysis.modeling.model_evaluation for better organization.
"""

# Import from new location and re-export for backward compatibility
from .modeling.model_evaluation import ModelTrainer

# Re-export all public symbols
__all__ = ["ModelTrainer"]
