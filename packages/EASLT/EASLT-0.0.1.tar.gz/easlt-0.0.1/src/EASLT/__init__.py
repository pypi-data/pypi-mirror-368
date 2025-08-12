"""
Enhanced Automatic Shifted Log Transformer Package

A sophisticated data transformation library that automatically applies optimized
log transformations with Monte Carlo weight optimization for improving data normality.

Feng et al 2016

Features:
- Adaptive transformation strategies based on data complexity
- Monte Carlo optimization for quality score weights
- Numba-accelerated computations for performance
- Robust outlier handling with adaptive winsorizing
- Comprehensive transformation quality evaluation

Classes:
    AutomaticShiftedLogTransformer: Main transformer class with Monte Carlo optimization

Example:
    >>> from EASLT import AutomaticShiftedLogTransformer
    >>> import pandas as pd
    >>> 
    >>> # Create transformer
    >>> transformer = AutomaticShiftedLogTransformer(
    ...     mc_iterations=1000,
    ...     random_state=42
    ... )
    >>> 
    >>> # Fit and transform data
    >>> transformer.fit(data)
    >>> transformed_data = transformer.transform(data)
    >>> 
    >>> # Get transformation summary
    >>> summary = transformer.get_transformation_summary()
"""

from .EASLT import (
    AutomaticShiftedLogTransformer,
    # Import key Numba-optimized functions if needed externally
    _apply_transform,
    _compute_shift_robust,
    _calculate_skewness,
    _calculate_kurtosis,
    _quality_score_core,
    _stability_score,
    _hybrid_quality_score,
    _monte_carlo_optimization,
    _optimize_params
)

# Package metadata
__version__ = "0.1.0"
__author__ = "Muhammad Akmal Husain"
__email__ = "akmalhusain2003@gmail.com"
__description__ = "Enhanced Automatic Shifted Log Transformer with Monte Carlo optimization"
__url__ = "https://github.com/AkmalHusain2003/enhanced-automatic-shifted-log"
__license__ = "MIT"

# Main exports - what users will typically import
__all__ = [
    "AutomaticShiftedLogTransformer",
    # Optionally expose utility functions
    "_apply_transform",
    "_compute_shift_robust",
    "_calculate_skewness", 
    "_calculate_kurtosis",
    "_quality_score_core",
    "_stability_score",
    "_hybrid_quality_score",
    "_monte_carlo_optimization",
    "_optimize_params"
]

# Package-level constants that users might want to access
DEFAULT_BETA_RANGE = (-8, 8, 0.01)
DEFAULT_MC_ITERATIONS = 1000
DEFAULT_EPSILON = 1e-12
DEFAULT_EARLY_STOP_THRESHOLD = 0.85


def create_balanced_transformer(random_state=None):
    """
    Create a balanced transformer with default settings.
    
    Parameters:
        random_state (int, optional): Random seed for reproducibility
    
    Returns:
        AutomaticShiftedLogTransformer: Configured transformer instance
    """
    return AutomaticShiftedLogTransformer(random_state=random_state)

# Version check function
def check_dependencies():
    """
    Check if all required dependencies are available and properly configured.
    
    Returns:
        dict: Status of each dependency
    """
    dependencies = {}
    
    try:
        import numpy as np
        dependencies['numpy'] = {'status': 'OK', 'version': np.__version__}
    except ImportError:
        dependencies['numpy'] = {'status': 'MISSING', 'version': None}
    
    try:
        import pandas as pd
        dependencies['pandas'] = {'status': 'OK', 'version': pd.__version__}
    except ImportError:
        dependencies['pandas'] = {'status': 'MISSING', 'version': None}
    
    try:
        import sklearn
        dependencies['sklearn'] = {'status': 'OK', 'version': sklearn.__version__}
    except ImportError:
        dependencies['sklearn'] = {'status': 'MISSING', 'version': None}
    
    try:
        import scipy
        dependencies['scipy'] = {'status': 'OK', 'version': scipy.__version__}
    except ImportError:
        dependencies['scipy'] = {'status': 'MISSING', 'version': None}
    
    try:
        import numba
        dependencies['numba'] = {'status': 'OK', 'version': numba.__version__}
    except ImportError:
        dependencies['numba'] = {'status': 'MISSING', 'version': None}
    
    return dependencies

# Package initialization message (optional - can be removed for production)
def _show_startup_info():
    """Show package information on import."""
    print(f"Enhanced Automatic Shifted Log Transformer v{__version__}")
    print("Ready for Monte Carlo optimized transformations!")

# Uncomment the line below if you want startup info (not recommended for production)
# _show_startup_info()