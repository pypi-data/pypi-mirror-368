"""
Clustering analysis utilities for data exploration and pattern discovery.

This module provides comprehensive clustering algorithms including K-means, DBSCAN,
and Agglomerative clustering with automatic parameter selection and evaluation.

Note: This is a compatibility wrapper. The actual implementation has been moved to
analysis.modeling.clustering for better organization.
"""

# Import from new location and re-export for backward compatibility
from .modeling.clustering import ClusterAnalyzer

# Re-export all public symbols
__all__ = ["ClusterAnalyzer"]
