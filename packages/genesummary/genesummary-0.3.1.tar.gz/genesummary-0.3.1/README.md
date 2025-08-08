# GeneInfo

A comprehensive Python package for retrieving detailed gene information from multiple public databases with robust error handling, batch processing capabilities, and modular architecture.

## Features

GeneInfo provides access to comprehensive gene annotation data through a unified interface:

### Core Gene Information
- **Basic gene data** - Gene symbols, Ensembl IDs, descriptions, genomic coordinates, biotypes
- **Transcripts** - All transcript variants with protein coding information and alternative splicing
- **Genomic location** - Chromosome coordinates, strand information, gene boundaries

### Functional Annotation
- **Protein domains** - Domain architecture from UniProt with evidence codes
- **Gene Ontology** - GO terms and annotations (Biological Process, Molecular Function, Cellular Component)
- **Pathways** - Reactome pathway associations and pathway hierarchies
- **Protein interactions** - Dual-source protein-protein interaction networks:
  - **BioGRID** - Experimental evidence with PubMed references (requires API key)
  - **STRING-db** - Computational predictions + experimental evidence (no API key required)

### Evolutionary Information
- **Homologs** - Paralogs and orthologs across species with similarity metrics
- **Cross-species mapping** - Gene orthology relationships and conservation scores

### Clinical & Disease Data
- **Clinical variants** - ClinVar pathogenic and benign variants with clinical significance
- **GWAS associations** - Genome-wide association study data from EBI GWAS Catalog
- **Disease phenotypes** - OMIM disease associations and phenotypic descriptions

### Advanced Features
- **Batch processing** - Concurrent processing of large gene lists (1000+ genes)
- **API key management** - Secure handling of NCBI Entrez and OMIM API keys via environment variables or CLI
- **Graceful degradation** - Works without API keys with limited functionality (no clinical/phenotype data)
- **Rate limiting** - Built-in API courtesy delays and error handling
- **Rich CLI** - Beautiful command-line interface with progress bars and tables
- **Export formats** - JSON, CSV output with detailed and summary views
- **Real data only** - No mock data fallbacks, returns null when data is inaccessible

## Installation

### Using uv (Recommended)
```bash
# Install from source
uv add git+https://github.com/chunjie-sam-liu/geneinfo.git

# Or clone and install locally
git clone https://github.com/chunjie-sam-liu/geneinfo.git
cd geneinfo
uv add -e .
```

### Using pip
```bash
# Install from source
pip install git+https://github.com/chunjie-sam-liu/geneinfo.git

# Or clone and install locally
git clone https://github.com/chunjie-sam-liu/geneinfo.git
cd geneinfo
pip install -e .
```

### Requirements
- Python 3.11+
- Internet connection for API access (offline mode available)

## Quick Start


### API Key Configuration

For accessing ClinVar (clinical variants), OMIM (phenotype data), and BioGRID (protein interactions), you'll need API keys:

1. **Create a `.env` file** in your project directory:
```bash
# API Keys for external services
OMIM_API_KEY="your_omim_api_key_here"
ENTREZ_API_KEY="your_entrez_api_key_here"
ENTREZ_EMAIL="your.email@example.com"
BIOGRID_API_KEY="your_biogrid_api_key_here"
```

2. **Get API keys**:
   - **OMIM API Key**: Register at [OMIM API](https://omim.org/api)
   - **Entrez API Key**: Register at [NCBI API](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)
   - **BioGRID API Key**: Register at [BioGRID API](https://wiki.thebiogrid.org/doku.php/biogridrest)

3. **API key priority**:
   - CLI arguments (highest priority)
   - Environment variables from `.env` file
   - None (graceful degradation - returns null data)

### Python API

```python
from geneinfo import GeneInfo

# Option 1: Use environment variables (recommended)
# Create .env file with API keys (see above)
gene_info = GeneInfo()

# Option 2: Provide API keys explicitly
gene_info = GeneInfo(
    email="your.email@example.com",
    entrez_api_key="your_entrez_key",
    omim_api_key="your_omim_key",
    biogrid_api_key="your_biogrid_key"
)

# Option 3: Work without API keys (limited functionality)
gene_info = GeneInfo(
    email=None,
    entrez_api_key=None,
    omim_api_key=None,
    biogrid_api_key=None
)

# Get comprehensive information for a single gene
result = gene_info.get_gene_info("TP53")
print(f"Gene: {result['basic_info']['display_name']}")
print(f"Description: {result['basic_info']['description']}")
print(f"Chromosome: {result['basic_info']['seq_region_name']}")
print(f"Transcripts: {len(result['transcripts'])}")
print(f"GO terms: {len(result['gene_ontology'])}")
print(f"Pathways: {len(result['pathways'])}")
print(f"Protein interactions: {len(result['protein_interactions'])} (BioGRID + STRING-db)")
print(f"Clinical variants: {len(result['clinvar'])} (requires API key)")

# Batch process multiple genes with concurrent workers
genes = ["TP53", "BRCA1", "EGFR", "MYC", "KRAS"]
df = gene_info.get_batch_info(genes, max_workers=5)
print(df[['gene_symbol', 'chromosome', 'transcript_count', 'go_term_count']].head())

# Export detailed information to JSON
gene_info.export_detailed_info(genes, "detailed_results.json")

# Export to organized directory structure
gene_info.export_batch_to_directory(genes, "gene_data/", max_workers=5)
```

### Advanced Usage

```python
# Process large gene lists efficiently
with open("large_gene_list.txt") as f:
    gene_list = [line.strip() for line in f if line.strip()]

# Initialize with API keys for full functionality
gene_info = GeneInfo(
    email="researcher@university.edu",
    entrez_api_key="your_entrez_key",
    omim_api_key="your_omim_key",
    biogrid_api_key="your_biogrid_key"
)

# Batch processing with progress tracking
df = gene_info.get_batch_info(gene_list, max_workers=10)

# Filter successful results
successful = df[df['error'].isna()]
print(f"Successfully processed {len(successful)}/{len(gene_list)} genes")

# Access specific data types
for _, gene in successful.iterrows():
    detailed = gene_info.get_gene_info(gene['query'])

    # Protein domains
    if detailed['protein_domains']:
        print(f"\n{gene['gene_symbol']} protein domains:")
        for domain in detailed['protein_domains'][:3]:
            print(f"  - {domain['name']}: {domain['start']}-{domain['end']}")

    # Protein interactions (dual sources)
    if detailed['protein_interactions']:
        biogrid_interactions = [i for i in detailed['protein_interactions']
                              if i.get('source_database') == 'BioGRID']
        stringdb_interactions = [i for i in detailed['protein_interactions']
                               if i.get('source_database') == 'STRING-db']
        print(f"  - {len(biogrid_interactions)} BioGRID interactions (experimental)")
        print(f"  - {len(stringdb_interactions)} STRING-db interactions (computational)")

    # Clinical variants (requires Entrez API key)
    if detailed['clinvar']:
        pathogenic = [v for v in detailed['clinvar']
                     if 'pathogenic' in v.get('clinical_significance', '').lower()]
        print(f"  - {len(pathogenic)} pathogenic variants found")

# Working without API keys (limited functionality)
gene_info_limited = GeneInfo(
    entrez_api_key=None,
    omim_api_key=None,
    biogrid_api_key=None
)

# This will still work but return empty for clinical/phenotype data
result = gene_info_limited.get_gene_info("TP53")
print(f"Basic info available: {bool(result['basic_info'])}")
print(f"Protein interactions: {len(result['protein_interactions'])} (STRING-db only)")
print(f"Clinical variants: {len(result['clinvar'])} (empty without API key)")
print(f"OMIM phenotypes: {bool(result['phenotypes'])} (empty without API key)")
```

### Command Line Interface

```bash
# Single gene information with rich output
geneinfo --gene TP53 --output tp53_info.json

# Using API keys via CLI arguments
geneinfo --gene TP53 --entrez-api-key YOUR_ENTREZ_KEY --omim-api-key YOUR_OMIM_KEY --biogrid-api-key YOUR_BIOGRID_KEY --output tp53_info.json

# Using environment variables (recommended - create .env file)
geneinfo --gene TP53 --output tp53_info.json

# Process multiple genes from file
geneinfo --file genes.txt --output results.csv

# Detailed information in JSON format
geneinfo --gene BRCA1 --detailed --output brca1_detailed.json

# Batch processing with custom workers and API keys
geneinfo --file large_gene_list.txt --workers 10 \
  --entrez-api-key YOUR_ENTREZ_KEY \
  --omim-api-key YOUR_OMIM_KEY \
  --biogrid-api-key YOUR_BIOGRID_KEY \
  --email your.email@example.com \
  --output batch_results.csv

# Export to organized directory structure
geneinfo --file genes.txt --output-dir gene_analysis/ --workers 8

# Verbose output for debugging
geneinfo --gene TP53 --verbose --detailed --output tp53_debug.json

# Process Ensembl IDs
geneinfo --gene ENSG00000141510 --output tp53_ensembl.json

# Species-specific queries (when supported)
geneinfo --gene TP53 --species human --output tp53_human.json

# Check CLI help for all options
geneinfo --help
```

### CLI Output Examples

The CLI provides beautiful, formatted output with:
- 📊 Progress bars for batch processing
- 🎨 Colored tables for gene information display
- ⚡ Real-time processing statistics
- 📝 Summary reports with success/failure counts
- 🔍 Verbose logging for troubleshooting

## Input Formats & Output

### Supported Input Formats
The package accepts multiple gene identifier formats:
- **Gene symbols**: `TP53`, `BRCA1`, `EGFR` (case-insensitive)
- **Ensembl Gene IDs**: `ENSG00000141510`, `ENSG00000012048`
- **Mixed lists**: Can process files containing both symbols and IDs

### Output Formats

#### Summary CSV Output
```csv
query,gene_symbol,ensembl_id,chromosome,start_pos,end_pos,strand,transcript_count,go_term_count,pathway_count,interaction_count,clinvar_count,error
TP53,TP53,ENSG00000141510,17,7668421,7687490,-1,12,87,23,71,1043,
BRCA1,BRCA1,ENSG00000012048,17,43044295,43170245,-1,27,34,15,45,892,
```

#### Detailed JSON Output
```json
{
  "query": "TP53",
  "basic_info": {
    "id": "ENSG00000141510",
    "display_name": "TP53",
    "description": "tumor protein p53",
    "seq_region_name": "17",
    "start": 7668421,
    "end": 7687490,
    "strand": -1,
    "biotype": "protein_coding"
  },
  "transcripts": [...],
  "protein_domains": [...],
  "gene_ontology": [...],
  "pathways": [...],
  "protein_interactions": [...],
  "paralogs": [...],
  "orthologs": [...],
  "clinvar": [...],
  "gwas": {...}
}
```

#### Directory Export Structure
```
gene_data/
├── summary.csv              # Overview of all processed genes
├── TP53_ENSG00000141510.json
├── BRCA1_ENSG00000012048.json
└── EGFR_ENSG00000073756.json
```

## Data Sources & Architecture

### Primary Data Sources
- **🧬 Ensembl** - Gene annotation, transcripts, genomic coordinates, homologs
- **🔬 UniProt** - Protein domains, functional annotations, protein features
- **🎯 Gene Ontology** - GO term annotations and functional classifications
- **🛤️ Reactome** - Biological pathways and pathway hierarchies
- **🏥 ClinVar** - Clinical variant classifications and disease associations
- **🧪 EBI GWAS Catalog** - Genome-wide association study results
- **💊 OMIM** - Mendelian disorders and phenotype-genotype relationships
- **📚 MyGene.info** - Enhanced gene annotation aggregation
- **🔗 BioGRID** - Experimental protein-protein interactions with evidence
- **🌐 STRING-db** - Computational + experimental protein interaction networks

### Modular Fetcher Architecture

The package uses a modular design with specialized fetchers:

```python
# Genomic data fetchers
from geneinfo.fetchers.genomic import EnsemblFetcher, MyGeneFetcher

# Protein data fetchers
from geneinfo.fetchers.protein import UniProtFetcher, StringDBFetcher, BioGRIDFetcher

# Functional annotation fetchers
from geneinfo.fetchers.functional import GOFetcher, ReactomeFetcher

# Clinical data fetchers
from geneinfo.fetchers.clinical import ClinVarFetcher, GwasFetcher, OMIMFetcher
```

### Robust Error Handling
- 🔄 **Graceful degradation** - Returns null data when APIs are unavailable or API keys missing
- ⏱️ **Rate limiting** with respectful API usage
- 🛡️ **SSL/TLS handling** for various certificate configurations
- 📝 **Comprehensive logging** with different verbosity levels
- 🔍 **Input validation** for gene symbols and Ensembl IDs
- 🔑 **API key management** - Secure environment variable handling

## Performance & Usage Examples

### Performance Characteristics
- **Throughput**: ~100-500 genes/minute (network dependent)
- **Concurrency**: Configurable worker threads (default: 5, max recommended: 10)
- **Memory**: Efficient streaming processing for large gene lists
- **Rate limiting**: Built-in delays to respect API usage policies

### Real-world Usage Examples

#### Cancer Gene Panel Analysis
```python
# Process a cancer gene panel with API keys for clinical data
cancer_genes = ["TP53", "BRCA1", "BRCA2", "EGFR", "KRAS", "PIK3CA", "AKT1"]
gene_info = GeneInfo(
    email="researcher@university.edu",
    entrez_api_key="your_entrez_key",
    omim_api_key="your_omim_key",
    biogrid_api_key="your_biogrid_key"
)

results = gene_info.get_batch_info(cancer_genes)
# Filter for genes with clinical variants (requires Entrez API key)
cancer_variants = results[results['clinvar_count'] > 0]
print(f"Found clinical variants in {len(cancer_variants)} cancer genes")

# Analyze protein interaction networks
for gene in cancer_genes:
    detailed = gene_info.get_gene_info(gene)
    interactions = detailed['protein_interactions']
    if interactions:
        biogrid_count = len([i for i in interactions if i['source_database'] == 'BioGRID'])
        stringdb_count = len([i for i in interactions if i['source_database'] == 'STRING-db'])
        print(f"{gene}: {biogrid_count} experimental + {stringdb_count} predicted interactions")
```

#### Pathway Enrichment Preprocessing
```python
# Prepare data for pathway analysis
gene_list = ["TP53", "MDM2", "CDKN1A", "BAX", "BBC3"]  # p53 pathway genes
detailed_results = [gene_info.get_gene_info(gene) for gene in gene_list]

# Extract GO terms for enrichment analysis
all_go_terms = []
for result in detailed_results:
    for go_term in result['gene_ontology']:
        all_go_terms.append({
            'gene': result['query'],
            'go_id': go_term['go_id'],
            'go_name': go_term['go_name'],
            'namespace': go_term['namespace']
        })
```

#### Large-scale Genomics Project
```python
# Process GWAS significant genes (thousands of genes)
with open("gwas_significant_genes.txt") as f:
    gwas_genes = [line.strip() for line in f]  # 5000+ genes

# Process in batches with progress tracking
gene_info.export_batch_to_directory(
    gwas_genes,
    "gwas_gene_annotation/",
    max_workers=8
)
# Creates organized directory with individual files + summary
```

## Development & Testing

### Running Tests
```bash
# Install development dependencies
uv add --dev pytest pytest-cov pytest-asyncio

# Run test suite
uv run pytest

# Run with coverage
uv run pytest --cov=geneinfo --cov-report=html
```

### Project Structure
```
geneinfo/
├── geneinfo/
│   ├── __init__.py          # Main package exports
│   ├── core.py              # GeneInfo main class
│   ├── cli.py               # Command-line interface
│   ├── mock_data.py         # Fallback data for offline mode
│   └── fetchers/            # Modular data fetchers
│       ├── base.py          # Base fetcher with common functionality
│       ├── genomic.py       # Ensembl, MyGene fetchers
│       ├── protein.py       # UniProt, STRING-db fetchers
│       ├── functional.py    # GO, Reactome fetchers
│       └── clinical.py      # ClinVar, GWAS, OMIM fetchers
├── tests/                   # Comprehensive test suite
├── examples/                # Usage examples and demos
├── docs/                    # Documentation (you are here!)
└── pyproject.toml          # Modern Python packaging
```

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Follow the coding standards in `.github/copilot-instructions.md`
4. Add tests for new functionality
5. Run the test suite: `uv run pytest`
6. Submit a pull request

## Dependencies & Requirements

### Core Dependencies
- **Python 3.11+** - Modern Python features and type hints
- **requests** - HTTP client for API calls
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computing
- **typer** - CLI framework with rich features
- **rich** - Beautiful terminal output and progress bars
- **biopython** - Bioinformatics tools (for Entrez/ClinVar)
- **mygene** - Enhanced gene annotation client
- **python-dotenv** - Environment variable management for API keys

### System Requirements
- Internet connection for API access
- API keys for full functionality (NCBI Entrez, OMIM, BioGRID)
- Sufficient memory for large gene lists (typically <1GB for 10,000 genes)
- Email address for ClinVar/NCBI Entrez access (required when using API keys)

## Troubleshooting

### Common Issues

#### API Access Problems
```bash
# Test API connectivity
geneinfo --gene TP53 --verbose

# Working without API keys (limited functionality)
geneinfo --gene TP53 --entrez-api-key=None --omim-api-key=None --output results.json
```

#### API Key Configuration
```bash
# Check if API keys are being loaded correctly
geneinfo --gene TP53 --verbose

# Set API keys via environment variables (recommended)
echo 'ENTREZ_API_KEY="your_key_here"' > .env
echo 'OMIM_API_KEY="your_key_here"' >> .env
echo 'BIOGRID_API_KEY="your_key_here"' >> .env
echo 'ENTREZ_EMAIL="your.email@example.com"' >> .env

# Or pass via CLI
geneinfo --gene TP53 --entrez-api-key YOUR_ENTREZ_KEY --omim-api-key YOUR_OMIM_KEY --biogrid-api-key YOUR_BIOGRID_KEY --email your@email.com
```

#### Large Gene List Processing
```bash
# For very large lists, reduce concurrent workers
geneinfo --file huge_gene_list.txt --workers 3 --output results.csv

# Process in smaller batches if memory is limited
split -l 1000 huge_gene_list.txt batch_
```

### Getting Help
- 📖 Check the `examples/` directory for usage patterns
- 🐛 Report issues on GitHub with verbose output logs
- 💬 Include gene lists and error messages in bug reports
- 📧 Use `--verbose` flag for detailed debugging information

## License & Citation

### License
MIT License - see LICENSE file for details.

### Citation
If you use GeneInfo in your research, please cite:

```bibtex
@software{geneinfo2025,
  author = {Liu, Chunjie},
  title = {GeneInfo: Comprehensive Gene Information Retrieval},
  url = {https://github.com/chunjie-sam-liu/geneinfo},
  version = {0.1.0},
  year = {2025}
}
```

### Acknowledgments
This package aggregates data from multiple public biological databases. Please also cite the original data sources in your publications:

- **Ensembl**: Cunningham et al. (2022) Nucleic Acids Research
- **UniProt**: The UniProt Consortium (2023) Nucleic Acids Research
- **Gene Ontology**: Aleksander et al. (2023) Genetics
- **Reactome**: Gillespie et al. (2022) Nucleic Acids Research
- **ClinVar**: Landrum et al. (2020) Nucleic Acids Research
- **BioGRID**: Oughtred et al. (2021) Nucleic Acids Research
- **STRING**: Szklarczyk et al. (2023) Nucleic Acids Research
- **GWAS Catalog**: Sollis et al. (2023) Nucleic Acids Research

---

**Author**: Chunjie Liu
**Contact**: chunjie.sam.liu.at.gmail.com
**Version**: 0.1.0
**Date**: 2025-08-06
