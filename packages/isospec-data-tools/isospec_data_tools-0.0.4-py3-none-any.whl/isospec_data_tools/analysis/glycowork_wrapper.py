"""
Integration utilities for the Glycowork library.

This module provides wrapper functions and utilities for integrating
with the Glycowork library for specialized glycan analysis.

Note: This is a compatibility wrapper. The actual implementation has been moved to
analysis.specialized.glycowork_integration for better organization.
"""

# Import from new location and re-export for backward compatibility
from .specialized.glycowork_integration import GlycoworkAnalyzer

# Re-export all public symbols
__all__ = ["GlycoworkAnalyzer"]
