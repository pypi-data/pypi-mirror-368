#!/usr/bin/env python3
"""
# Author: Chunjie Liu
# Contact: chunjie.sam.liu.at.gmail.com
# Date: 2025-08-06
# Description: Test script for enhanced geneinfo features (MyGene and OMIM)
# Version: 0.1

Test script for the enhanced geneinfo features including MyGene basic information
and OMIM phenotype data.
"""

import json
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from geneinfo import GeneInfo


def test_enhanced_basic_info():
    """Test the enhanced basic information from MyGene."""
    print("🧬 Testing Enhanced Basic Information (MyGene)")
    print("=" * 60)

    try:
        # Initialize GeneInfo
        gi = GeneInfo(species="human")

        # Test with TP53
        print("Testing with TP53...")
        result = gi.get_gene_info("TP53")

        if result and "basic_info" in result:
            basic_info = result["basic_info"]

            print(f"✅ Ensembl ID: {basic_info.get('id', 'N/A')}")
            print(f"✅ Gene Symbol: {basic_info.get('display_name', 'N/A')}")
            print(f"✅ Entrez ID: {basic_info.get('entrez_id', 'N/A')}")
            print(f"✅ HGNC ID: {basic_info.get('hgnc_id', 'N/A')}")
            print(f"✅ UniProt ID: {basic_info.get('uniprot_id', 'N/A')}")
            print(f"✅ Aliases: {basic_info.get('aliases', [])}")
            print(f"✅ Gene Type: {basic_info.get('type_of_gene', 'N/A')}")
            print(f"✅ Map Location: {basic_info.get('map_location', 'N/A')}")

            # Check if summary is available
            summary = basic_info.get("summary", "")
            if summary:
                print(f"✅ Summary: {summary[:100]}...")
            else:
                print("⚠️  Summary: Not available")

            print("\n📍 Genomic Position (MyGene):")
            genomic_pos = basic_info.get("genomic_pos_mygene", {})
            if genomic_pos:
                print(f"   Chr: {genomic_pos.get('chr', 'N/A')}")
                print(f"   Start: {genomic_pos.get('start', 'N/A')}")
                print(f"   End: {genomic_pos.get('end', 'N/A')}")
                print(f"   Strand: {genomic_pos.get('strand', 'N/A')}")
            else:
                print("   No genomic position data from MyGene")

        else:
            print("❌ Failed to retrieve enhanced basic information")

    except Exception as e:
        print(f"❌ Error testing enhanced basic info: {e}")

    print("\n")


def test_omim_phenotypes():
    """Test the OMIM phenotype data."""
    print("🏥 Testing OMIM Phenotype Data")
    print("=" * 60)

    try:
        # Initialize GeneInfo
        gi = GeneInfo(species="human")

        # Test with TP53
        print("Testing OMIM phenotypes for TP53...")
        result = gi.get_gene_info("TP53")

        if result and "phenotypes" in result:
            phenotype_data = result["phenotypes"]

            print(
                f"✅ Total Phenotypes: {phenotype_data.get('total_phenotypes', 0)}"
            )

            # Show gene entries
            gene_entries = phenotype_data.get("gene_entries", [])
            print(f"✅ OMIM Gene Entries: {len(gene_entries)}")
            for i, entry in enumerate(gene_entries[:3]):  # Show first 3
                print(
                    f"   {i + 1}. MIM #{entry.get('mim_number')}: {entry.get('title', 'N/A')[:60]}..."
                )

            # Show phenotypes
            phenotypes = phenotype_data.get("phenotypes", [])
            print(f"✅ Disease Associations: {len(phenotypes)}")
            for i, pheno in enumerate(phenotypes[:5]):  # Show first 5
                print(f"   {i + 1}. {pheno.get('phenotype', 'N/A')[:80]}...")
                if pheno.get("inheritance"):
                    print(f"      Inheritance: {pheno.get('inheritance')}")
                if pheno.get("phenotype_mim_number"):
                    print(f"      MIM: {pheno.get('phenotype_mim_number')}")

        else:
            print("❌ Failed to retrieve OMIM phenotype data")

    except Exception as e:
        print(f"❌ Error testing OMIM phenotypes: {e}")

    print("\n")


def test_complete_gene_info():
    """Test the complete gene information retrieval."""
    print("🔬 Testing Complete Gene Information")
    print("=" * 60)

    try:
        # Initialize GeneInfo
        gi = GeneInfo(species="human")

        # Test with BRCA1 (smaller gene for faster testing)
        print("Testing complete information for BRCA1...")
        result = gi.get_gene_info("BRCA1")

        if result:
            print("✅ Data Categories Available:")
            categories = [
                ("basic_info", "Basic Information"),
                ("transcripts", "Transcripts"),
                ("protein_domains", "Protein Domains"),
                ("gene_ontology", "Gene Ontology"),
                ("pathways", "Pathways"),
                ("protein_interactions", "Protein Interactions"),
                ("paralogs", "Paralogs"),
                ("orthologs", "Orthologs"),
                ("clinvar", "ClinVar Variants"),
                ("gwas", "GWAS Associations"),
                ("phenotypes", "OMIM Phenotypes"),
            ]

            for key, name in categories:
                data = result.get(key, {})
                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict):
                    if key == "gwas":
                        count = len(data.get("associations", []))
                    elif key == "phenotypes":
                        count = len(data.get("phenotypes", []))
                    else:
                        count = 1 if data else 0
                else:
                    count = 1 if data else 0

                status = "✅" if count > 0 else "⚠️"
                print(f"   {status} {name}: {count} items")

            # Show enhanced basic info highlights
            basic_info = result.get("basic_info", {})
            print("\n🎯 Enhanced Basic Information Highlights:")
            print(f"   Entrez ID: {basic_info.get('entrez_id', 'N/A')}")
            print(f"   HGNC ID: {basic_info.get('hgnc_id', 'N/A')}")
            print(f"   UniProt ID: {basic_info.get('uniprot_id', 'N/A')}")
            print(f"   Aliases: {len(basic_info.get('aliases', []))} aliases")

            # Show phenotype highlights
            phenotype_data = result.get("phenotypes", {})
            print("\n🏥 OMIM Phenotype Highlights:")
            print(
                f"   Total Phenotypes: {phenotype_data.get('total_phenotypes', 0)}"
            )
            print(
                f"   Gene Entries: {len(phenotype_data.get('gene_entries', []))}"
            )

        else:
            print("❌ Failed to retrieve complete gene information")

    except Exception as e:
        print(f"❌ Error testing complete gene info: {e}")


def main():
    """Main test function."""
    print("🧪 Testing Enhanced GeneInfo Features")
    print("=" * 80)
    print("Testing MyGene enhanced basic information and OMIM phenotype data")
    print("=" * 80)
    print()

    # Test individual components
    test_enhanced_basic_info()
    test_omim_phenotypes()
    test_complete_gene_info()

    print("🎉 Testing Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
