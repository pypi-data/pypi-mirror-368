"""
GeneInfo: A Python package for comprehensive gene information retrieval.

This package provides functionality to fetch detailed gene information including:
- Basic gene information and transcripts
- Protein domains
- Gene ontology terms
- Pathways
- Protein-protein interactions
- Paralogs and orthologs
- Clinical variants (ClinVar)
- Cancer mutations (COSMIC)
"""

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version  # Python < 3.8

try:
    __version__ = version("geneinfo")
except Exception:
    # Fallback for development or when package is not installed
    __version__ = "0.1.0.dev0"
__author__ = "Chunjie Liu"

from .core import GeneInfo
from .fetchers import EnsemblFetcher, GOFetcher, ReactomeFetcher, UniProtFetcher
from .utils import get_api_key, get_email, load_environment

__all__ = [
    "GeneInfo",
    "EnsemblFetcher",
    "UniProtFetcher",
    "GOFetcher",
    "ReactomeFetcher",
    "__version__",
    "__author__",
]
