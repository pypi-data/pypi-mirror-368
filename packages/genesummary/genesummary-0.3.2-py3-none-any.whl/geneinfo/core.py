"""
# Author: Chunjie Liu
# Contact: chunjie.sam.liu.at.gmail.com
# Date: 2025-08-06
# Description: Core GeneInfo class for comprehensive gene information retrieval
# Version: 0.1

Core GeneInfo class for comprehensive gene information retrieval.
"""

import json
import logging
from typing import Dict, List, Optional, Union

import pandas as pd
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .fetchers import (
    EnsemblFetcher,
    MyGeneFetcher,
    UniProtFetcher,
    BioGRIDFetcher,
    StringDBFetcher,
    GOFetcher,
    ReactomeFetcher,
    OMIMFetcher,
    GWASFetcher,
    ClinVarFetcher,
)
from .utils import _NOT_PROVIDED, get_api_key, get_email

logger = logging.getLogger(__name__)
console = Console()


class GeneInfo:
    """
    Main class for fetching comprehensive gene information.

    This class coordinates multiple data sources to provide comprehensive
    gene information including basic gene data, transcripts, protein domains,
    gene ontology, pathways, protein interactions, paralogs, orthologs,
    and clinical/cancer variant data.
    """

    def __init__(
        self,
        species: str = "human",
        email: Optional[str] = _NOT_PROVIDED,
        entrez_api_key: Optional[str] = _NOT_PROVIDED,
        omim_api_key: Optional[str] = _NOT_PROVIDED,
        biogrid_api_key: Optional[str] = _NOT_PROVIDED,
    ):
        """
        Initialize GeneInfo instance.

        Args:
            species: Target species for gene queries (default: "human")
            email: Email address for NCBI Entrez API (required for ClinVar)
            entrez_api_key: API key for NCBI Entrez (optional, can be in .env)
            omim_api_key: API key for OMIM (optional, can be in .env)
            biogrid_api_key: API key for BioGRID (optional, can be in .env)
        """
        self.species = species

        # Get email and API keys from CLI args or environment
        self.email = get_email(email)
        self.entrez_api_key = get_api_key("ENTREZ_API_KEY", entrez_api_key)
        self.omim_api_key = get_api_key("OMIM_API_KEY", omim_api_key)
        self.biogrid_api_key = get_api_key("BIOGRID_API_KEY", biogrid_api_key)

        # Initialize fetchers that don't require API keys
        self.ensembl_fetcher = EnsemblFetcher(species)
        self.uniprot_fetcher = UniProtFetcher()
        self.go_fetcher = GOFetcher()
        self.reactome_fetcher = ReactomeFetcher()
        self.gwas_fetcher = GWASFetcher()
        self.mygene_fetcher = MyGeneFetcher(species)

        # Initialize STRING-db fetcher (no API key required)
        self.stringdb_fetcher = StringDBFetcher()

        # Initialize BioGRID fetcher for protein interactions
        self.biogrid_fetcher = None
        if self.biogrid_api_key:
            try:
                self.biogrid_fetcher = BioGRIDFetcher(self.biogrid_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize BioGRID fetcher: {e}")

        # Initialize fetchers that require API keys (will be None if keys not available)
        self.clinvar_fetcher = None
        if self.email and self.entrez_api_key:
            try:
                self.clinvar_fetcher = ClinVarFetcher(
                    self.email, self.entrez_api_key
                )
            except Exception as e:
                logger.warning(f"Failed to initialize ClinVar fetcher: {e}")

        self.omim_fetcher = None
        if self.omim_api_key:
            try:
                self.omim_fetcher = OMIMFetcher(self.omim_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OMIM fetcher: {e}")

    def get_gene_info(self, gene_id: str) -> Dict:
        """
        Get comprehensive gene information for a single gene.

        Args:
            gene_id: Gene symbol or Ensembl ID (e.g., "TP53" or "ENSG00000141510")

        Returns:
            Dictionary containing comprehensive gene information

        Raises:
            ValueError: If gene_id is empty or None
            TypeError: If gene_id is not a string
        """
        # Input validation
        if gene_id is None:
            raise ValueError("gene_id cannot be None")
        if not isinstance(gene_id, str):
            raise TypeError("gene_id must be a string")
        if not gene_id.strip():
            raise ValueError("gene_id cannot be empty")

        # Clean the gene_id
        gene_id = gene_id.strip()

        result = {
            "query": gene_id,
            "basic_info": {},
            "transcripts": [],
            "protein_domains": [],
            "gene_ontology": [],
            "pathways": [],
            "protein_interactions": [],
            "paralogs": [],
            "orthologs": [],
            "clinvar": [],
            "gwas": {},
            "phenotypes": {},
            "cosmic": [],
            "error": None,
        }

        try:
            # Get basic gene information from Ensembl
            logger.info(f"Fetching basic info for {gene_id}")
            basic_info = self.ensembl_fetcher.get_gene_info(gene_id)
            if basic_info:
                result["basic_info"] = basic_info

                # Use Ensembl ID for subsequent queries
                ensembl_id = basic_info.get("id", gene_id)

                # Get gene symbol for subsequent queries
                gene_symbol = (
                    basic_info.get("display_name")
                    or basic_info.get("external_name")
                    or gene_id
                )

                # Enhance basic information with MyGene data
                logger.info(f"Fetching enhanced basic info for {gene_symbol}")
                enhanced_info = self.mygene_fetcher.get_enhanced_gene_info(
                    gene_symbol
                )
                if enhanced_info:
                    # Merge enhanced info into basic_info
                    result["basic_info"].update(
                        {
                            "entrez_id": enhanced_info.get("entrez_id"),
                            "aliases": enhanced_info.get("aliases", []),
                            "hgnc_id": enhanced_info.get("hgnc_id"),
                            "uniprot_id": enhanced_info.get("uniprot_id"),
                            "type_of_gene": enhanced_info.get("type_of_gene"),
                            "map_location": enhanced_info.get("map_location"),
                            "summary": enhanced_info.get("summary"),
                            "genomic_pos_mygene": enhanced_info.get(
                                "genomic_pos", {}
                            ),
                        }
                    )

                # Get OMIM phenotype data
                logger.info(f"Fetching OMIM phenotypes for {gene_symbol}")
                if self.omim_fetcher:
                    phenotype_data = self.omim_fetcher.get_phenotype_data(
                        gene_symbol
                    )
                    result["phenotypes"] = phenotype_data
                else:
                    logger.warning(
                        "OMIM API key not provided, skipping phenotype data"
                    )
                    result["phenotypes"] = {}

                # Get transcripts
                logger.info(f"Fetching transcripts for {ensembl_id}")
                transcripts = self.ensembl_fetcher.get_transcripts(ensembl_id)
                result["transcripts"] = transcripts or []

                # Get orthologs and paralogs
                logger.info(f"Fetching homologs for {ensembl_id}")
                homologs = self.ensembl_fetcher.get_homologs(ensembl_id)
                if homologs:
                    result["orthologs"] = homologs.get("orthologs", [])
                    result["paralogs"] = homologs.get("paralogs", [])

                # Get protein information if available
                if transcripts:
                    protein_ids = [
                        t.get("protein_id")
                        for t in transcripts
                        if t.get("protein_id")
                    ]
                    if protein_ids:
                        # Get protein domains from Ensembl (InterPro features)
                        logger.info(
                            f"Fetching protein domains for {protein_ids[0]}"
                        )
                        domains = self.ensembl_fetcher.get_protein_domains(
                            protein_ids[0]
                        )
                        result["protein_domains"] = domains or []

                # Get protein interactions from BioGRID and STRING-db
                logger.info(f"Fetching protein interactions for {gene_symbol}")
                all_interactions = []

                # Try BioGRID first (experimental evidence)
                if self.biogrid_fetcher:
                    biogrid_interactions = self.biogrid_fetcher.get_protein_interactions(gene_symbol)
                    if biogrid_interactions:
                        all_interactions.extend(biogrid_interactions)
                        logger.info(f"Found {len(biogrid_interactions)} BioGRID interactions")
                else:
                    logger.info(f"BioGRID API key not found - skipping BioGRID interactions")

                # Try STRING-db (computational predictions + experimental)
                try:
                    stringdb_interactions = self.stringdb_fetcher.get_protein_interactions(gene_symbol)
                    if stringdb_interactions:
                        all_interactions.extend(stringdb_interactions)
                        logger.info(f"Found {len(stringdb_interactions)} STRING-db interactions")
                except Exception as e:
                    logger.warning(f"STRING-db interactions failed: {e}")

                result["protein_interactions"] = all_interactions

                # Get Gene Ontology information (use UniProt ID if available, fallback to gene symbol)
                logger.info(f"Fetching GO terms for {gene_symbol}")
                uniprot_id = result["basic_info"].get("uniprot_id")
                if uniprot_id and len(uniprot_id) >= 6:
                    go_terms = self.go_fetcher.get_go_terms(uniprot_id)
                else:
                    go_terms = self.go_fetcher.get_go_terms(gene_symbol)
                result["gene_ontology"] = go_terms or []

                # Get pathway information (prefer UniProt accession if available, fallback to gene symbol)
                logger.info(f"Fetching pathways for {gene_symbol}")
                uniprot_id = result["basic_info"].get("uniprot_id")
                if uniprot_id and len(uniprot_id) >= 6 and uniprot_id[0].isalpha():
                    # Use UniProt ID if it looks valid
                    pathway_identifier = uniprot_id
                else:
                    # Fallback to gene symbol
                    pathway_identifier = gene_symbol
                pathways = self.reactome_fetcher.get_pathways(pathway_identifier)
                result["pathways"] = pathways or []

                # Get ClinVar clinical variants
                logger.info(f"Fetching ClinVar variants for {gene_symbol}")
                if self.clinvar_fetcher:
                    clinvar_variants = (
                        self.clinvar_fetcher.get_clinical_variants(gene_symbol)
                    )
                    result["clinvar"] = clinvar_variants or []
                else:
                    logger.warning(
                        "Entrez API key not provided, skipping ClinVar data"
                    )
                    result["clinvar"] = []

                # Get GWAS associations
                logger.info(f"Fetching GWAS associations for {gene_symbol}")
                gwas_data = self.gwas_fetcher.get_gwas_data(gene_symbol)
                result["gwas"] = gwas_data

        except Exception as e:
            logger.error(f"Error fetching information for {gene_id}: {str(e)}")
            result["error"] = str(e)

        return result

    def get_batch_info(
        self, gene_ids: List[str], max_workers: int = 5
    ) -> pd.DataFrame:
        """
        Get comprehensive gene information for multiple genes.

        Args:
            gene_ids: List of gene symbols or Ensembl IDs
            max_workers: Maximum number of concurrent requests

        Returns:
            pandas DataFrame containing gene information
        """
        import concurrent.futures

        results = []

        # Process genes in batches to avoid overwhelming APIs
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers
        ) as executor:
            future_to_gene = {
                executor.submit(self.get_gene_info, gene_id): gene_id
                for gene_id in gene_ids
            }

            for future in concurrent.futures.as_completed(future_to_gene):
                gene_id = future_to_gene[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing {gene_id}: {str(e)}")
                    results.append({"query": gene_id, "error": str(e)})

        # Convert to DataFrame
        df_data = []
        for result in results:
            row = {
                "query": result.get("query"),
                "ensembl_id": result.get("basic_info", {}).get("id"),
                "gene_symbol": result.get("basic_info", {}).get("display_name"),
                "description": result.get("basic_info", {}).get("description"),
                "chromosome": result.get("basic_info", {}).get(
                    "seq_region_name"
                ),
                "start": result.get("basic_info", {}).get("start"),
                "end": result.get("basic_info", {}).get("end"),
                "strand": result.get("basic_info", {}).get("strand"),
                "biotype": result.get("basic_info", {}).get("biotype"),
                "transcript_count": len(result.get("transcripts", [])),
                "domain_count": len(result.get("protein_domains", [])),
                "go_term_count": len(result.get("gene_ontology", [])),
                "pathway_count": len(result.get("pathways", [])),
                "interaction_count": len(
                    result.get("protein_interactions", [])
                ),
                "ortholog_count": len(result.get("orthologs", [])),
                "paralog_count": len(result.get("paralogs", [])),
                "error": result.get("error"),
            }
            df_data.append(row)

        return pd.DataFrame(df_data)

    def export_detailed_info(self, gene_ids: List[str], output_file: str):
        """
        Export detailed gene information to JSON file.

        Args:
            gene_ids: List of gene symbols or Ensembl IDs
            output_file: Output JSON file path
        """
        results = []
        for gene_id in gene_ids:
            result = self.get_gene_info(gene_id)
            results.append(result)

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Detailed gene information exported to {output_file}")

    def export_batch_to_directory(
        self, gene_ids: List[str], output_dir: str, max_workers: int = 5
    ) -> None:
        """
        Export gene information to individual files in a directory with summary statistics.

        Args:
            gene_ids: List of gene symbols or Ensembl IDs
            output_dir: Output directory path
            max_workers: Maximum number of concurrent requests

        Creates:
            - Individual JSON files for each gene in the output directory
            - summary.csv with request statistics and gene information overview
        """
        import concurrent.futures
        import os
        from pathlib import Path

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = []
        successful_requests = 0
        failed_requests = 0

        # Process genes in batches to avoid overwhelming APIs
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers
        ) as executor:
            future_to_gene = {
                executor.submit(self.get_gene_info, gene_id): gene_id
                for gene_id in gene_ids
            }

            for future in concurrent.futures.as_completed(future_to_gene):
                gene_id = future_to_gene[future]
                try:
                    result = future.result()
                    results.append(result)

                    # Save individual gene file
                    gene_filename = f"{gene_id.replace('/', '_')}.json"
                    gene_file_path = output_path / gene_filename

                    with open(gene_file_path, "w") as f:
                        json.dump(result, f, indent=2, default=str)

                    successful_requests += 1
                    logger.info(f"Exported {gene_id} to {gene_filename}")

                except Exception as e:
                    logger.error(f"Error processing {gene_id}: {str(e)}")
                    error_result = {"query": gene_id, "error": str(e)}
                    results.append(error_result)

                    # Save error file
                    error_filename = f"{gene_id.replace('/', '_')}_error.json"
                    error_file_path = output_path / error_filename

                    with open(error_file_path, "w") as f:
                        json.dump(error_result, f, indent=2, default=str)

                    failed_requests += 1

        # Create summary DataFrame
        df_data = []
        for result in results:
            row = {
                "query": result.get("query"),
                "status": "success" if "error" not in result else "error",
                "ensembl_id": result.get("basic_info", {}).get("id"),
                "gene_symbol": result.get("basic_info", {}).get("display_name"),
                "description": result.get("basic_info", {}).get("description"),
                "chromosome": result.get("basic_info", {}).get(
                    "seq_region_name"
                ),
                "start": result.get("basic_info", {}).get("start"),
                "end": result.get("basic_info", {}).get("end"),
                "strand": result.get("basic_info", {}).get("strand"),
                "biotype": result.get("basic_info", {}).get("biotype"),
                "transcript_count": len(result.get("transcripts", [])),
                "domain_count": len(result.get("protein_domains", [])),
                "go_term_count": len(result.get("gene_ontology", [])),
                "pathway_count": len(result.get("pathways", [])),
                "interaction_count": len(
                    result.get("protein_interactions", [])
                ),
                "ortholog_count": len(result.get("orthologs", [])),
                "paralog_count": len(result.get("paralogs", [])),
                "error_message": result.get("error", ""),
            }
            df_data.append(row)

        # Save summary CSV
        df = pd.DataFrame(df_data)
        summary_file_path = output_path / "summary.csv"
        df.to_csv(summary_file_path, index=False)

        # Log summary statistics
        total_requests = len(gene_ids)
        logger.info("Batch processing completed:")
        logger.info(f"  - Total genes processed: {total_requests}")
        logger.info(f"  - Successful requests: {successful_requests}")
        logger.info(f"  - Failed requests: {failed_requests}")
        logger.info(
            f"  - Success rate: {successful_requests / total_requests * 100:.1f}%"
        )
        logger.info(f"  - Results saved to: {output_dir}")
        logger.info(f"  - Summary saved to: {summary_file_path}")

        console.print("[green]✅ Batch export completed[/green]")
        console.print(f"[blue]📁 Output directory: {output_dir}[/blue]")
        console.print(
            f"[blue]📊 Summary: {successful_requests}/{total_requests} successful[/blue]"
        )
