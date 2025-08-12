"""
Confounder analysis and statistical testing utilities.

This module provides utilities for analyzing confounders in glycan data,
including statistical tests and effect size calculations.

Note: This is a compatibility wrapper. The actual implementation has been moved to
analysis.specialized.confounder_analysis for better organization.
"""

# Import from new location and re-export for backward compatibility
from .specialized.confounder_analysis import ConfounderAnalyzer

# Re-export all public symbols
__all__ = ["ConfounderAnalyzer"]
