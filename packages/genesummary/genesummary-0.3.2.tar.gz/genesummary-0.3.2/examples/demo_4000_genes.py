#!/usr/bin/env python3
"""
Demonstration script showing how to process 4000 genes (using a smaller sample)
for comprehensive gene information retrieval as requested in the problem statement.
"""

from geneinfo import GeneInfo
import pandas as pd
import time

def main():
    print("=== GeneInfo Package Demonstration ===")
    print("Processing genes similar to what would be done for 4000 genes")
    print("(Using smaller sample due to mock data limitations)\n")
    
    # Initialize GeneInfo
    gene_info = GeneInfo(species="human")
    
    # Sample gene list (in real scenario, this would be 4000 genes)
    sample_genes = [
        "TP53",           # Gene symbol
        "BRCA1",          # Gene symbol  
        "ENSG00000129514", # Ensembl ID (from problem statement)
        "FOXA1",          # Gene symbol that matches the Ensembl ID above
    ]
    
    print(f"Processing {len(sample_genes)} genes:")
    for gene in sample_genes:
        print(f"  - {gene}")
    print()
    
    # Time the processing
    start_time = time.time()
    
    # Get comprehensive information
    print("Fetching comprehensive gene information...")
    df = gene_info.get_batch_info(sample_genes, max_workers=2)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Display results
    print(f"\nProcessing completed in {processing_time:.2f} seconds")
    print(f"Rate: {len(sample_genes)/processing_time:.1f} genes/second")
    print(f"Estimated time for 4000 genes: {4000/len(sample_genes)*processing_time:.1f} seconds")
    print()
    
    print("=== Summary Results ===")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(df.to_string(index=False))
    print()
    
    # Export detailed information for demonstration
    print("=== Exporting Detailed Information ===")
    output_file = "/tmp/comprehensive_gene_info.json"
    gene_info.export_detailed_info(sample_genes, output_file)
    print(f"Detailed gene information exported to: {output_file}")
    
    # Show what kind of detailed information is available
    sample_result = gene_info.get_gene_info("TP53")
    print(f"\n=== Sample Detailed Information for TP53 ===")
    print(f"Basic info: {len(sample_result['basic_info'])} fields")
    print(f"Transcripts: {len(sample_result['transcripts'])} entries")
    if sample_result['transcripts']:
        print(f"  - First transcript: {sample_result['transcripts'][0]['id']}")
        print(f"  - Protein ID: {sample_result['transcripts'][0]['protein_id']}")
    
    print(f"Protein domains: {len(sample_result['protein_domains'])} entries")
    if sample_result['protein_domains']:
        print(f"  - First domain: {sample_result['protein_domains'][0]['description']}")
    
    print(f"Gene Ontology: {len(sample_result['gene_ontology'])} terms")
    if sample_result['gene_ontology']:
        for go_term in sample_result['gene_ontology'][:2]:
            print(f"  - {go_term['go_id']}: {go_term['go_name']}")
    
    print(f"Pathways: {len(sample_result['pathways'])} pathways")
    if sample_result['pathways']:
        for pathway in sample_result['pathways']:
            print(f"  - {pathway['pathway_id']}: {pathway['name']}")
    
    print(f"Orthologs: {len(sample_result['orthologs'])} species")
    print(f"Paralogs: {len(sample_result['paralogs'])} genes")
    
    print("\n=== Integration Ready ===")
    print("The package is ready to integrate:")
    print("- ClinVar clinical variant data")
    print("- COSMIC cancer mutation data")  
    print("- String-db protein-protein interactions")
    print("- Additional species and databases")
    
    print(f"\nFor real-world usage with 4000 genes:")
    print(f"  geneinfo --file your_4000_genes.txt --output comprehensive_results.csv --workers 10")

if __name__ == "__main__":
    main()