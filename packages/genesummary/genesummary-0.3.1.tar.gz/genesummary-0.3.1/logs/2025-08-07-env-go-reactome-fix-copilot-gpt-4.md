Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-08-07
Description: Ensure .env API keys are used; fix GO and Reactome fetchers to reduce 400/404s; normalize UniProt ID.
Version: 0.1

# Context
- User provided .env with OMIM and Entrez API keys and email.
- CLI run showed warnings that keys were not picked up and several 400/404 responses (GO, Reactome, Ensembl homology).

# Changes
1) Environment handling
   - utils.get_api_key now falls back to .env when CLI option is None/empty.
   - get_email reuses the same logic.

2) MyGene normalization
   - Extract a single UniProt accession (Swiss-Prot preferred) from MyGene's uniprot field.

3) GO fetcher
   - Accepts Entrez/Ensembl/UniProt/gene symbol and builds proper GO bioentity path (e.g., NCBIGene:7157).
   - Core now passes Entrez ID (or Ensembl/symbol) to GO fetcher.

4) Reactome fetcher
   - Prefer mapping via UniProt accession: /ContentService/mapping/UniProt/{ACC}/pathways
   - Fallback to previous query endpoint.
   - Core now passes UniProt ID when available.

# Expected outcome
- CLI should auto-detect OMIM and Entrez API keys from .env without flags.
- GO and Reactome sections should populate for common genes like TP53 (Entrez 7157, UniProt P04637).
- ClinVar should run using ENTREZ_EMAIL and ENTREZ_API_KEY.

# Verification
- Static checks: no syntax errors reported.
- Manual: run `uv run geneinfo --gene TP53 -v` to observe improved counts for GO terms, pathways, and ClinVar.

# Notes / Future
- Ensembl homology/genetree 400/404 still handled with graceful fallback; add robust parsing later.
- Consider caching/memoization to reduce repeated API calls in batch mode.
