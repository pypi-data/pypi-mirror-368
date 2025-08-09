#!/usr/bin/env python3
"""
Example script demonstrating geneinfo package usage.
"""

import logging
from geneinfo import GeneInfo

# Setup logging
logging.basicConfig(level=logging.INFO)

def main():
    """Example usage of geneinfo package."""
    
    # Initialize GeneInfo
    gene_info = GeneInfo(species="human")
    
    # Example 1: Get information for a single gene
    print("=== Example 1: Single Gene Information ===")
    gene_id = "TP53"  # or use Ensembl ID like "ENSG00000141510"
    result = gene_info.get_gene_info(gene_id)
    
    print(f"Gene: {result['query']}")
    print(f"Ensembl ID: {result['basic_info'].get('id', 'N/A')}")
    print(f"Description: {result['basic_info'].get('description', 'N/A')}")
    print(f"Chromosome: {result['basic_info'].get('seq_region_name', 'N/A')}")
    print(f"Transcripts: {len(result['transcripts'])}")
    print(f"Protein domains: {len(result['protein_domains'])}")
    print(f"GO terms: {len(result['gene_ontology'])}")
    print(f"Pathways: {len(result['pathways'])}")
    print(f"Orthologs: {len(result['orthologs'])}")
    print(f"Paralogs: {len(result['paralogs'])}")
    
    if result['error']:
        print(f"Error: {result['error']}")
    
    print("\n")
    
    # Example 2: Batch processing multiple genes
    print("=== Example 2: Batch Processing ===")
    gene_list = ["TP53", "BRCA1", "EGFR", "MYC", "KRAS"]
    
    # Get summary information as DataFrame
    df = gene_info.get_batch_info(gene_list, max_workers=3)
    print("Summary DataFrame:")
    print(df[['query', 'gene_symbol', 'chromosome', 'transcript_count', 'go_term_count']].head())
    
    print("\n")
    
    # Example 3: Export detailed information
    print("=== Example 3: Export Detailed Information ===")
    output_file = "/tmp/detailed_gene_info.json"
    gene_info.export_detailed_info(["TP53", "BRCA1"], output_file)
    print(f"Detailed information exported to: {output_file}")
    
    print("\n")
    
    # Example 4: Working with Ensembl IDs
    print("=== Example 4: Using Ensembl IDs ===")
    ensembl_id = "ENSG00000129514"  # Example from the problem statement
    result = gene_info.get_gene_info(ensembl_id)
    print(f"Gene symbol: {result['basic_info'].get('display_name', 'N/A')}")
    print(f"Biotype: {result['basic_info'].get('biotype', 'N/A')}")
    
    # Show some transcript details
    if result['transcripts']:
        print(f"\nFirst transcript:")
        transcript = result['transcripts'][0]
        print(f"  ID: {transcript.get('id')}")
        print(f"  Biotype: {transcript.get('biotype')}")
        print(f"  Length: {transcript.get('length')}")
        print(f"  Protein ID: {transcript.get('protein_id', 'N/A')}")
    
    # Show some GO terms
    if result['gene_ontology']:
        print(f"\nFirst few GO terms:")
        for go_term in result['gene_ontology'][:3]:
            print(f"  {go_term.get('go_id')}: {go_term.get('go_name')}")
    
    # Show pathways
    if result['pathways']:
        print(f"\nFirst few pathways:")
        for pathway in result['pathways'][:3]:
            print(f"  {pathway.get('pathway_id')}: {pathway.get('name')}")


if __name__ == "__main__":
    main()