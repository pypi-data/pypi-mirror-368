"""
Disjoint Forest Data Structure

A high-performance C++ implementation of disjoint-set data structure 
with Python bindings using pybind11.

This package provides a unified interface for working with any Python object type
in a disjoint-set data structure, with support for dynamic operations like
expanding capacity, contracting nodes, and clearing the forest.
"""

__version__ = "1.1"
__author__ = "DisjointForest Contributors"
__license__ = "MIT"

# Import the main classes from the compiled module
try:
    from .disjoint_forest import DisjointForest, Node
    __all__ = ['DisjointForest', 'Node']
except ImportError:
    # Fallback for development or if the compiled module isn't available
    __all__ = []
    import warnings
    warnings.warn(
        "Could not import compiled disjoint_forest module. "
        "Please ensure the package is properly built.",
        ImportWarning
    )


def get_version():
    """Get the package version."""
    return __version__


def get_info():
    """Get package information."""
    return {
        'name': 'disjoint-forest',
        'version': __version__,
        'author': __author__,
        'license': __license__,
        'description': 'High-performance disjoint-set data structure with Python bindings'
    } 