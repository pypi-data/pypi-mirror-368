#!/usr/bin/env python3
"""
Test script for protein interactions debugging.

Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-01-08
Description: Debug protein interaction fetchers
Version: 0.1
"""

import logging
import sys

# Set up minimal logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def test_biogrid():
    """Test BioGRID fetcher alone."""
    try:
        from geneinfo.fetchers.protein import BioGRIDFetcher
        print("Testing BioGRID...")

        fetcher = BioGRIDFetcher('43f10f5ba8abbbc691ff047e86545586')
        interactions = fetcher.get_protein_interactions('TP53')

        print(f"BioGRID result: {len(interactions) if interactions else 0} interactions")
        if interactions:
            print(f"First partner: {interactions[0]['partner_symbol']}")
        return True
    except Exception as e:
        print(f"BioGRID error: {e}")
        return False

def test_stringdb():
    """Test STRING-db fetcher alone."""
    try:
        from geneinfo.fetchers.protein import StringDBFetcher
        print("Testing STRING-db...")

        fetcher = StringDBFetcher()
        interactions = fetcher.get_protein_interactions('TP53')

        print(f"STRING-db result: {len(interactions) if interactions else 0} interactions")
        if interactions:
            print(f"First partner: {interactions[0]['partner_name']}")
        return True
    except Exception as e:
        print(f"STRING-db error: {e}")
        return False

if __name__ == "__main__":
    print("Protein interaction debugging script")
    print("-" * 40)

    # Test individual fetchers
    biogrid_ok = test_biogrid()
    stringdb_ok = test_stringdb()

    print("-" * 40)
    print(f"BioGRID: {'✓' if biogrid_ok else '✗'}")
    print(f"STRING-db: {'✓' if stringdb_ok else '✗'}")
