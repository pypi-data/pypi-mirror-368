"""
NetVizCorpy - Visualisation tool for Corporate group(s) Network as available on WikiData in Python
Copyright (c) 2025 Zsofia Baruwa

Documentation: https://
Examples: https://
Source: https://github.com/zb15/NetVizCorpy
"""
# Load version info
try:
    from .version import __version__
except ImportError:
    __version__ = "unknown"

# Import key classes for top-level access
from .query import Querier
from .identifyQIDs import Searcher
from .deriveNetwork import NetworkBuilder
from .postProcess import Cleaner
from .visualiseNetwork import Visualiser

# Define public API
__all__ = [
    "Querier",
    "Searcher",
    "NetworkBuilder",
    "Cleaner",
    "Visualiser",
]
