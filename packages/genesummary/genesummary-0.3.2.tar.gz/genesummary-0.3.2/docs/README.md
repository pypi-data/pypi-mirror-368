# GeneInfo Documentation

A comprehensive Python package for retrieving detailed gene information from multiple public databases with robust error handling, batch processing capabilities, and modular architecture.

> 🚀 **Version 0.1.0** - Modern bioinformatics tool with rich CLI and Python API

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [API Reference](#api-reference)
- [Data Sources](#data-sources)
- [Performance](#performance)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Package Management](#package-management)

## Overview

GeneInfo bridges the gap between gene identifiers and comprehensive biological annotation by providing a unified interface to query multiple public databases. Whether you're analyzing a single gene or processing thousands of genes from genomics studies, GeneInfo handles the complexity of API interactions, data formatting, and error management.

### Key Capabilities

🧬 **Comprehensive Gene Annotation**
- Basic gene information (symbols, IDs, coordinates, descriptions)
- Transcript variants and alternative splicing information
- Protein domain architecture and functional features

🎯 **Functional Classification**
- Gene Ontology terms (Biological Process, Molecular Function, Cellular Component)
- Biological pathway associations and hierarchies
- Dual-source protein-protein interaction networks:
  - **BioGRID** - Experimental evidence with PubMed references (requires API key)
  - **STRING-db** - Computational predictions + experimental evidence (no API key required)

🏥 **Clinical & Medical Relevance**
- Clinical variant classifications from ClinVar (requires Entrez API key)
- GWAS association data for complex traits
- Disease-gene relationships from OMIM (requires OMIM API key)

⚡ **High-Performance Processing**
- Concurrent batch processing for large gene lists
- Intelligent rate limiting and error recovery
- Graceful degradation when API keys are not available

🔑 **Secure API Management**
- Environment variable support for API keys (ENTREZ, OMIM, BIOGRID)
- CLI argument support for temporary usage
- Graceful fallback when credentials are missing

🎨 **Beautiful Interfaces**
- Rich command-line interface with progress tracking
- Clean Python API with pandas integration
- Multiple export formats (JSON, CSV, directory structures)

## Installation

### Install from PyPI

```bash
pip install genesummary
```

### Using uv (Recommended for Modern Python)

```bash
# Install from GitHub repository
uv add git+https://github.com/chunjie-sam-liu/geneinfo.git

# For development installation
git clone https://github.com/chunjie-sam-liu/geneinfo.git
cd geneinfo
uv add -e .
```

### Using pip (Traditional)

```bash
# Install from GitHub
pip install git+https://github.com/chunjie-sam-liu/geneinfo.git

# Development installation
git clone https://github.com/chunjie-sam-liu/geneinfo.git
cd geneinfo
pip install -e .
```

### System Requirements

- **Python**: 3.11+ (leverages modern Python features)
- **Memory**: 1-4GB recommended for large-scale processing
- **Network**: Internet connection for API access
- **API Keys**: NCBI Entrez and OMIM API keys for full functionality (optional)
- **Email**: Valid email address for NCBI/ClinVar access (required when using API keys)



### API Key Setup (Recommended)

For accessing clinical variants (ClinVar) and phenotype data (OMIM), set up API keys:

```bash
# Create .env file in your project directory
cat > .env << EOF
# API Keys for external services
OMIM_API_KEY="your_omim_api_key_here"
ENTREZ_API_KEY="your_entrez_api_key_here"
ENTREZ_EMAIL="your.email@example.com"
EOF
```

**Getting API Keys:**
- [OMIM API Registration](https://omim.org/api)
- [NCBI Entrez API Registration](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)

### Basic Python Usage

```python
from geneinfo import GeneInfo

# Option 1: Use environment variables (recommended)
gene_info = GeneInfo()

# Option 2: Provide API keys explicitly
gene_info = GeneInfo(
    email="researcher@university.edu",
    entrez_api_key="your_entrez_key",
    omim_api_key="your_omim_key",
    biogrid_api_key="your_biogrid_key"
)

# Option 3: Work without API keys (limited functionality)
gene_info = GeneInfo(
    entrez_api_key=None,
    omim_api_key=None,
    biogrid_api_key=None
)

# Single gene analysis
result = gene_info.get_gene_info("TP53")
print(f"Gene: {result['basic_info']['display_name']}")
print(f"Location: chr{result['basic_info']['seq_region_name']}:{result['basic_info']['start']}-{result['basic_info']['end']}")
print(f"GO terms: {len(result['gene_ontology'])}")
print(f"Protein interactions: {len(result['protein_interactions'])} (BioGRID + STRING-db)")
print(f"Clinical variants: {len(result['clinvar'])} (requires API key)")
```

### Batch Processing

```python
# Process multiple genes efficiently with API keys
gene_list = ["TP53", "BRCA1", "EGFR", "MYC", "KRAS"]
df = gene_info.get_batch_info(gene_list, max_workers=5)

# Quick overview
print(df[['gene_symbol', 'chromosome', 'transcript_count', 'go_term_count']])

# Export detailed results
gene_info.export_detailed_info(gene_list, "comprehensive_results.json")
```

### Command Line Interface

```bash
# Single gene with beautiful output (using .env file for API keys)
geneinfo --gene TP53

# Using API keys via command line
geneinfo --gene TP53 --entrez-api-key YOUR_KEY --omim-api-key YOUR_KEY --email your@email.com

# Batch processing from file
echo -e "TP53\nBRCA1\nEGFR" > genes.txt
geneinfo --file genes.txt --output results.csv

# Detailed export with progress tracking
geneinfo --file genes.txt --detailed --workers 8 --output-dir gene_analysis/

# Working without API keys (limited functionality)
geneinfo --gene TP53 --entrez-api-key=None --omim-api-key=None
```

## API Reference

### Core Classes

#### `GeneInfo(species="human", email=None, entrez_api_key=None, omim_api_key=None)`
Main interface for gene information retrieval.

**Parameters:**
- `species` (str): Target species, default "human"
- `email` (str): Email for NCBI Entrez API access (required when using entrez_api_key)
- `entrez_api_key` (str): NCBI Entrez API key for ClinVar access (optional)
- `omim_api_key` (str): OMIM API key for phenotype data (optional)

**Note:** API keys can also be provided via environment variables:
- `ENTREZ_EMAIL`
- `ENTREZ_API_KEY`
- `OMIM_API_KEY`

**Methods:**

##### `get_gene_info(gene_id: str) -> Dict`
Retrieve comprehensive information for a single gene.

**Parameters:**
- `gene_id` (str): Gene symbol (e.g., "TP53") or Ensembl ID (e.g., "ENSG00000141510")

**Returns:**
```python
{
    "query": str,                    # Input gene identifier
    "basic_info": {...},            # Gene coordinates, description, biotype
    "transcripts": [...],           # Transcript variants
    "protein_domains": [...],       # Protein domain architecture
    "gene_ontology": [...],         # GO term annotations
    "pathways": [...],              # Biological pathways
    "protein_interactions": [...],  # PPI networks
    "paralogs": [...],              # Paralogous genes
    "orthologs": [...],             # Orthologous genes
    "clinvar": [...],               # Clinical variants (requires Entrez API key)
    "gwas": {...},                  # GWAS associations
    "phenotypes": {...},            # OMIM phenotypes (requires OMIM API key)
    "error": str | None             # Error message if any
}
```

##### `get_batch_info(gene_ids: List[str], max_workers=5) -> pd.DataFrame`
Process multiple genes with concurrent workers.

**Parameters:**
- `gene_ids` (List[str]): List of gene symbols or Ensembl IDs
- `max_workers` (int): Maximum concurrent requests (default: 5)

**Returns:**
pandas DataFrame with summary information for all genes.

##### `export_detailed_info(gene_ids: List[str], output_file: str)`
Export comprehensive gene information to JSON file.

##### `export_batch_to_directory(gene_ids: List[str], output_dir: str, max_workers=5)`
Export genes to organized directory structure with individual files and summary.

### Data Fetchers

The modular fetcher architecture allows direct access to specific data sources:

#### Genomic Data
```python
from geneinfo.fetchers.genomic import EnsemblFetcher, MyGeneFetcher

ensembl = EnsemblFetcher(species="human")
gene_data = ensembl.get_gene_info("TP53")
```

#### Protein Data
```python
from geneinfo.fetchers.protein import UniProtFetcher, StringDBFetcher, BioGRIDFetcher

uniprot = UniProtFetcher()
domains = uniprot.get_protein_domains("P04637")  # TP53 UniProt ID

# Protein interaction networks
biogrid = BioGRIDFetcher(api_key="your_biogrid_key")
stringdb = StringDBFetcher()
experimental_ppi = biogrid.get_protein_interactions("TP53")
predicted_ppi = stringdb.get_protein_interactions("TP53")
```

#### Clinical Data
```python
from geneinfo.fetchers.clinical import ClinVarFetcher, GwasFetcher

clinvar = ClinVarFetcher(email="researcher@example.com")
variants = clinvar.get_clinical_variants("TP53")
```

## Data Sources

### Integrated Databases

| Database | Data Type | API Endpoint | Coverage |
|----------|-----------|--------------|----------|
| **Ensembl** | Gene annotation, transcripts, homologs | `rest.ensembl.org` | 🌍 Multi-species |
| **UniProt** | Protein domains, functional sites | `rest.uniprot.org` | 🔬 Protein-focused |
| **Gene Ontology** | Functional classification | `api.geneontology.org` | 🎯 Function terms |
| **Reactome** | Biological pathways | `reactome.org/ContentService` | 🛤️ Pathway networks |
| **ClinVar** | Clinical variants | `eutils.ncbi.nlm.nih.gov` | 🏥 Medical genetics |
| **BioGRID** | Experimental protein interactions | `webservice.thebiogrid.org` | 🔬 Experimental PPI |
| **STRING-db** | Computational protein interactions | `string-db.org/api` | 🕸️ Interaction networks |
| **GWAS Catalog** | Association studies | `ebi.ac.uk/gwas/rest/api` | 📊 Population genetics |
| **OMIM** | Mendelian disorders | `api.omim.org` | 💊 Disease genetics |
| **MyGene** | Aggregated annotations | `mygene.info` | 📚 Meta-database |

### Data Types Retrieved

#### Basic Gene Information
- Gene symbols and synonyms
- Ensembl stable IDs
- Genomic coordinates (chromosome, start, end, strand)
- Gene descriptions and biotypes
- Alternative gene names

#### Transcript Information
- All transcript variants for each gene
- Protein-coding vs non-coding transcripts
- UTR and CDS coordinates
- Translation information
- Alternative splicing patterns

#### Protein Features
- Domain architecture (Pfam, InterPro, SMART)
- Functional sites and motifs
- Signal peptides and transmembrane regions
- Post-translational modification sites
- Protein families and superfamilies

#### Functional Annotation
- Gene Ontology terms (Biological Process, Molecular Function, Cellular Component)
- Evidence codes and references
- GO term hierarchies
- Biological pathway memberships
- Pathway reactions and interactions

#### Evolutionary Information
- Orthologous genes across species
- Paralogous genes within species
- Sequence similarity metrics
- Phylogenetic relationships
- Conservation scores

#### Clinical Relevance
- Pathogenic and benign variants from ClinVar
- Clinical significance classifications
- GWAS associations with complex traits
- P-values and effect sizes
- Disease-gene associations from OMIM
- Phenotypic descriptions

#### Protein Interaction Networks
- **BioGRID interactions** - Experimental evidence with PubMed references (requires API key)
  - Experimental systems (Two-hybrid, Co-IP, Co-crystal, etc.)
  - Throughput classifications (Low/High)
  - Author and publication information
  - Interaction modification details
- **STRING-db interactions** - Computational predictions + experimental evidence (no API key required)
  - Combined confidence scores
  - Individual evidence type scores (experimental, database, textmining, etc.)
  - Functional association networks
  - Co-expression relationships
- **Dual source coverage** - Up to 70+ interactions per gene (e.g., TP53: 21 BioGRID + 50 STRING-db)

## Performance

### Benchmarking Results

| Gene Count | Processing Time | Memory Usage | Success Rate |
|------------|----------------|--------------|--------------|
| 10 genes | ~30 seconds | <100MB | >95% |
| 100 genes | ~5 minutes | ~200MB | >90% |
| 1,000 genes | ~45 minutes | ~500MB | >85% |
| 5,000 genes | ~3.5 hours | ~1.2GB | >80% |

*Results with 5 concurrent workers on standard broadband connection*

### Performance Optimization

#### Concurrent Processing
```python
# Optimal worker configuration for different scenarios
small_list = gene_info.get_batch_info(genes[:50], max_workers=3)      # Conservative
medium_list = gene_info.get_batch_info(genes[:500], max_workers=5)    # Default
large_list = gene_info.get_batch_info(genes[:2000], max_workers=8)    # Aggressive
```

#### Memory Management
```python
# For very large gene lists, process in chunks
def process_large_list(gene_list, chunk_size=1000):
    results = []
    for i in range(0, len(gene_list), chunk_size):
        chunk = gene_list[i:i+chunk_size]
        chunk_results = gene_info.get_batch_info(chunk)
        results.append(chunk_results)
    return pd.concat(results, ignore_index=True)
```

#### Rate Limiting
- Built-in delays respect API usage policies
- Automatic backoff on rate limit errors
- Configurable rate limits per fetcher
- Smart retry logic with exponential backoff

### Error Handling & Resilience

#### Automatic Fallbacks
- Mock data when APIs are unavailable
- Partial results when some APIs fail
- Graceful degradation of service quality
- Comprehensive error logging

#### Network Resilience
- SSL/TLS configuration handling
- Timeout management
- Connection pooling and reuse
- Retry strategies for transient failures

## Examples

### Research Use Cases

#### 1. Cancer Genomics Study
```python
# Analyze a cancer gene panel for clinical variants
cancer_genes = [
    "TP53", "BRCA1", "BRCA2", "PTEN", "ATM", "CHEK2",
    "PALB2", "MLH1", "MSH2", "MSH6", "PMS2"
]

gene_info = GeneInfo(email="oncologist@hospital.edu")
results = gene_info.get_batch_info(cancer_genes)

# Focus on genes with pathogenic variants
pathogenic_genes = results[results['clinvar_count'] > 10]
print(f"High-impact cancer genes: {len(pathogenic_genes)}")

# Export for clinical reporting
gene_info.export_batch_to_directory(
    pathogenic_genes['query'].tolist(),
    "cancer_panel_analysis/"
)
```

#### 2. Pathway Enrichment Analysis
```python
# Prepare gene sets for pathway analysis
immune_genes = ["CD4", "CD8A", "IL2", "IFNG", "TNF", "IL10"]
detailed_results = []

for gene in immune_genes:
    result = gene_info.get_gene_info(gene)
    detailed_results.append(result)

# Extract pathway information
pathway_data = []
for result in detailed_results:
    for pathway in result['pathways']:
        pathway_data.append({
            'gene': result['query'],
            'pathway_id': pathway['pathway_id'],
            'pathway_name': pathway['name'],
            'species': pathway.get('species', 'Homo sapiens')
        })

import pandas as pd
pathway_df = pd.DataFrame(pathway_data)
print(pathway_df.groupby('pathway_name')['gene'].count().sort_values(ascending=False))
```

#### 3. Protein Interaction Network Analysis
```python
# Analyze protein interaction networks for cancer genes
cancer_genes = ["TP53", "BRCA1", "EGFR", "MYC", "KRAS"]

gene_info = GeneInfo(
    email="researcher@university.edu",
    entrez_api_key="your_entrez_key",
    biogrid_api_key="your_biogrid_key"
)

# Build comprehensive interaction network
interaction_network = {}
for gene in cancer_genes:
    result = gene_info.get_gene_info(gene)
    interactions = result['protein_interactions']

    if interactions:
        # Separate experimental vs computational evidence
        experimental = [i for i in interactions if i['source_database'] == 'BioGRID']
        computational = [i for i in interactions if i['source_database'] == 'STRING-db']

        interaction_network[gene] = {
            'experimental_count': len(experimental),
            'computational_count': len(computational),
            'high_confidence_partners': [
                i['partner_symbol'] if 'partner_symbol' in i else i['partner_name']
                for i in experimental  # BioGRID has experimental evidence
            ][:10]  # Top 10
        }

        print(f"{gene}: {len(experimental)} experimental + {len(computational)} predicted interactions")

# Find common interaction partners
all_partners = set()
for gene_data in interaction_network.values():
    all_partners.update(gene_data['high_confidence_partners'])

print(f"Total unique interaction partners: {len(all_partners)}")
```

#### 4. Comparative Genomics
```python
# Compare orthologous genes across species
human_genes = ["TP53", "BRCA1", "MYC"]
orthology_data = []

for gene in human_genes:
    result = gene_info.get_gene_info(gene)

    for ortholog in result['orthologs']:
        orthology_data.append({
            'human_gene': gene,
            'ortholog_species': ortholog['species'],
            'ortholog_id': ortholog['id'],
            'identity_percent': ortholog.get('identity', 0),
            'orthology_type': ortholog.get('type', 'unknown')
        })

ortho_df = pd.DataFrame(orthology_data)
# Analysis of conservation across species
conservation_summary = ortho_df.groupby('human_gene')['identity_percent'].agg(['mean', 'count'])
```

#### 4. Clinical Variant Analysis
```python
# Deep dive into clinical significance
target_gene = "BRCA1"
result = gene_info.get_gene_info(target_gene)

# Categorize variants by clinical significance
variant_categories = {}
for variant in result['clinvar']:
    significance = variant.get('clinical_significance', 'Unknown')
    if significance not in variant_categories:
        variant_categories[significance] = []
    variant_categories[significance].append(variant)

# Report pathogenic variants
pathogenic = variant_categories.get('Pathogenic', [])
print(f"Found {len(pathogenic)} pathogenic variants in {target_gene}")

for variant in pathogenic[:5]:  # Top 5
    print(f"- {variant.get('variation_id')}: {variant.get('name')}")
    print(f"  Condition: {variant.get('disease_name', 'Unknown')}")
```

#### 5. Large-Scale GWAS Follow-up
```python
# Process GWAS hits for functional annotation
gwas_hits_file = "gwas_significant_loci.txt"
with open(gwas_hits_file) as f:
    gwas_genes = [line.strip() for line in f if line.strip()]

print(f"Processing {len(gwas_genes)} GWAS-identified genes...")

# Batch process with progress tracking
gene_info.export_batch_to_directory(
    gwas_genes,
    "gwas_functional_annotation/",
    max_workers=6
)

# Load summary for downstream analysis
summary_df = pd.read_csv("gwas_functional_annotation/summary.csv")
successful = summary_df[summary_df['error'].isna()]

print(f"Successfully annotated {len(successful)}/{len(gwas_genes)} genes")
print(f"Average GO terms per gene: {successful['go_term_count'].mean():.1f}")
print(f"Genes with clinical variants: {(successful['clinvar_count'] > 0).sum()}")
```

### Command Line Workflows

#### Quick Gene Lookup
```bash
# Single gene quick lookup
geneinfo --gene TP53 --verbose

# Multiple genes from command line
geneinfo --gene "TP53,BRCA1,EGFR" --output oncogenes.csv
```

#### Batch Processing Pipeline
```bash
# Step 1: Prepare gene list
echo -e "TP53\nBRCA1\nBRCA2\nPTEN\nEGFR" > cancer_genes.txt

# Step 2: Process with detailed output
geneinfo --file cancer_genes.txt \
         --detailed \
         --workers 5 \
         --email researcher@university.edu \
         --output-dir cancer_analysis/

# Step 3: Quick summary
geneinfo --file cancer_genes.txt --output summary.csv
```

#### Large Dataset Processing
```bash
# Process large gene lists efficiently
geneinfo --file large_gene_list.txt \
         --workers 8 \
         --output-dir comprehensive_analysis/ \
         --email your.email@domain.com

# Monitor progress in separate terminal
tail -f comprehensive_analysis/processing.log
```

## Troubleshooting

### Common Issues and Solutions

#### 1. API Connection Problems

**Problem**: `ConnectionError` or timeout errors
```
ConnectionError: HTTPSConnectionPool(host='rest.ensembl.org', port=443)
```

**Solutions**:
```bash
# Test connectivity with verbose output
geneinfo --gene TP53 --verbose

# Check if specific APIs are accessible
curl -I https://rest.ensembl.org/info/ping
curl -I https://rest.uniprot.org/uniprotkb/search?query=TP53&size=1
```

**Automatic Fallbacks**: The package automatically uses mock data when APIs are unavailable.

#### 2. Rate Limiting Issues

**Problem**: `HTTP 429 Too Many Requests` errors

**Solutions**:
```python
# Reduce concurrent workers
gene_info.get_batch_info(genes, max_workers=2)  # Instead of default 5

# Add delays between requests (advanced usage)
from geneinfo.fetchers.base import BaseFetcher
BaseFetcher.rate_limit = 0.5  # 500ms delay instead of 100ms
```

#### 3. Memory Issues with Large Gene Lists

**Problem**: `MemoryError` or slow performance with thousands of genes

**Solutions**:
```python
# Process in smaller chunks
def process_in_chunks(gene_list, chunk_size=500):
    all_results = []
    for i in range(0, len(gene_list), chunk_size):
        chunk = gene_list[i:i+chunk_size]
        results = gene_info.get_batch_info(chunk)
        all_results.append(results)

        # Save intermediate results
        results.to_csv(f"chunk_{i//chunk_size}.csv", index=False)

    return pd.concat(all_results, ignore_index=True)

# Use directory export for large datasets
gene_info.export_batch_to_directory(large_gene_list, "results/", max_workers=3)
```

#### 4. NCBI/ClinVar Access Issues

**Problem**: ClinVar queries failing or returning empty results

**Solutions**:
```python
# Ensure valid email is provided
gene_info = GeneInfo(email="researcher@institution.edu")  # Use real email

# Test NCBI connectivity
from Bio import Entrez
Entrez.email = "your.email@example.com"
handle = Entrez.esearch(db="clinvar", term="BRCA1[gene]", retmax=1)
record = Entrez.read(handle)
print(f"Found {len(record['IdList'])} ClinVar entries for BRCA1")
```

#### 5. Gene Symbol vs Ensembl ID Issues

**Problem**: Some genes not found or incorrect mappings

**Solutions**:
```python
# Use current gene symbols
# Check HGNC for official symbols: https://www.genenames.org/

# For ambiguous symbols, use Ensembl IDs
ensembl_id = "ENSG00000141510"  # TP53
result = gene_info.get_gene_info(ensembl_id)

# Verify gene identity
print(f"Query: {result['query']}")
print(f"Symbol: {result['basic_info']['display_name']}")
print(f"Ensembl ID: {result['basic_info']['id']}")
```

#### 6. SSL/Certificate Issues

**Problem**: SSL verification errors, especially with STRING-db

**Solutions**:
The package automatically handles SSL issues for known problematic APIs like STRING-db. For other APIs:

```python
# Disable SSL warnings (already handled by the package)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

### Debugging Techniques

#### Verbose Logging
```bash
# Enable detailed logging
geneinfo --gene TP53 --verbose

# Python API verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Testing Individual Fetchers
```python
# Test specific data sources
from geneinfo.fetchers.genomic import EnsemblFetcher
from geneinfo.fetchers.clinical import ClinVarFetcher

# Test Ensembl connectivity
ensembl = EnsemblFetcher()
if ensembl._should_use_mock():
    print("Ensembl API unavailable, using mock data")
else:
    print("Ensembl API accessible")

# Test ClinVar with your email
clinvar = ClinVarFetcher(email="your.email@domain.com")
variants = clinvar.get_clinical_variants("TP53")
print(f"Retrieved {len(variants) if variants else 0} ClinVar variants")
```

#### Performance Monitoring
```python
import time
from rich.progress import Progress

genes = ["TP53", "BRCA1", "EGFR"]  # Your gene list

with Progress() as progress:
    task = progress.add_task("Processing genes...", total=len(genes))

    results = []
    for gene in genes:
        start_time = time.time()
        result = gene_info.get_gene_info(gene)
        end_time = time.time()

        print(f"{gene}: {end_time - start_time:.2f}s")
        results.append(result)
        progress.advance(task)
```

### Getting Help

- 📖 **Documentation**: Check the `examples/` directory for usage patterns
- 🐛 **Issues**: Report bugs on GitHub with verbose output and gene lists
- 💬 **Discussions**: Use GitHub Discussions for usage questions
- 📧 **Contact**: Include `--verbose` output when reporting issues

### Error Codes and Messages

| Error Type | Cause | Solution |
|------------|-------|----------|
| `ConnectionError` | Network/API unavailable | Check internet, will auto-fallback to mock data |
| `ValueError` | Invalid gene identifier | Use valid gene symbols or Ensembl IDs |
| `KeyError` | Missing required data fields | Update package or check API changes |
| `MemoryError` | Large dataset processing | Process in smaller chunks |
| `TimeoutError` | Slow API response | Reduce workers or increase timeout |

---

*This documentation covers GeneInfo v0.1.0. For the latest updates, check the [GitHub repository](https://github.com/chunjie-sam-liu/geneinfo).*


## Package Management

| pnpm Command / Concept  | nvm Command             | uv Equivalent                                             | Description                                                                   |
| ----------------------- | ----------------------- | --------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `pnpm init`             |                         | `uv init`                                                 | Initializes a new Python project, creating a `pyproject.toml`.                |
| `pnpm install`          |                         | `uv sync`                                                 | Installs dependencies from `pyproject.toml` and `uv.lock`.                    |
| `pnpm add <package>`    |                         | `uv add <package>`                                        | Adds a package to your dependencies and installs it.                          |
| `pnpm add -D <package>` |                         | `uv add --dev <package>`                                  | Adds a package to development dependencies.                                   |
| `pnpm add -g <package>` |                         | `uv tool install <package>`                               | Installs a CLI tool globally in an isolated uv-managed environment.           |
| `pnpm remove <package>` |                         | `uv remove <package>`                                     | Removes a dependency from the project.                                        |
| `pnpm run <script>`     |                         | `uv run <script>`                                         | Runs a script defined in `pyproject.toml`.                                    |
| `pnpm list`             |                         | `uv pip list`                                             | Lists installed packages in the virtual environment.                          |
| `pnpm update`           |                         | `uv lock --upgrade`                                       | Upgrades all packages to the latest compatible versions.                      |
| `pnpm update <package>` |                         | `uv lock --upgrade-package <package>`                     | Upgrades a specific package.                                                  |
| `npx <tool>`            |                         | `uvx <tool>` or `uv tool run <tool>`                      | Runs a CLI tool in a temporary environment without installing it permanently. |
|                         | `nvm install <version>` | `uv python install <version>`                             | Installs a specific version of Python.                                        |
|                         | `nvm use <version>`     | `uv venv --python <version>` or `uv python pin <version>` | Uses/pins a specific Python version for the project.                          |
|                         | `nvm list`              | `uv python list`                                          | Lists all Python versions managed or known by `uv`.                           |