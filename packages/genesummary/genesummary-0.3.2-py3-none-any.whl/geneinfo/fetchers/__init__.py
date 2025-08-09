"""
Fetchers package for biological database APIs.

Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-08-06
Description: Modular fetchers for different biological databases
Version: 0.1
"""

from .base import BaseFetcher
from .clinical import ClinVarFetcher, GWASFetcher, OMIMFetcher
from .functional import GOFetcher, ReactomeFetcher
from .genomic import EnsemblFetcher, MyGeneFetcher
from .protein import StringDBFetcher, UniProtFetcher, BioGRIDFetcher

__all__ = [
    "BaseFetcher",
    "EnsemblFetcher",
    "MyGeneFetcher",
    "UniProtFetcher",
    "StringDBFetcher",
    "BioGRIDFetcher",
    "GOFetcher",
    "ReactomeFetcher",
    "ClinVarFetcher",
    "GWASFetcher",
    "OMIMFetcher",
]
