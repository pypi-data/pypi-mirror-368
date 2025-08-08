"""
Protein data fetchers for UniProt, STRING-db, and BioGRID APIs.

Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-08-07
Description: Fetchers for protein domain and interaction data
Version: 0.2
"""

import logging
import time
from typing import Dict, List, Optional

from .base import BaseFetcher
from ..utils import get_api_key

logger = logging.getLogger(__name__)


class UniProtFetcher(BaseFetcher):
    """Fetcher for UniProt API."""

    def __init__(self):
        super().__init__("https://rest.uniprot.org")

    def get_protein_domains(self, protein_id: str) -> Optional[List[Dict]]:
        """Get protein domain information from UniProt."""
        # Convert Ensembl protein ID to UniProt if needed
        uniprot_id = self._get_uniprot_id(protein_id)
        if not uniprot_id:
            return None

        url = f"{self.base_url}/uniprotkb/{uniprot_id}.json"
        result = self._make_request(url)

        if result and "features" in result:
            domains = []
            for feature in result["features"]:
                if feature.get("type") in ["DOMAIN", "REGION", "MOTIF"]:
                    domain_info = {
                        "type": feature.get("type"),
                        "description": feature.get("description"),
                        "start": feature.get("location", {})
                        .get("start", {})
                        .get("value"),
                        "end": feature.get("location", {})
                        .get("end", {})
                        .get("value"),
                        "evidence": feature.get("evidences", []),
                    }
                    domains.append(domain_info)
            return domains

        return None

    def get_protein_interactions(self, protein_id: str) -> Optional[List[Dict]]:
        """Get protein-protein interactions."""
        # This is a simplified implementation
        # In a real scenario, you'd use STRING-db or IntAct APIs
        return []

    def _get_uniprot_id(self, protein_id: str) -> Optional[str]:
        """Convert Ensembl protein ID to UniProt ID."""
        if not protein_id.startswith("ENSP"):
            return protein_id  # Assume it's already UniProt

        url = f"{self.base_url}/idmapping/run"
        data = {"from": "Ensembl_Protein", "to": "UniProtKB", "ids": protein_id}

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            job_id = response.json().get("jobId")

            if job_id:
                # Poll for results
                status_url = f"{self.base_url}/idmapping/status/{job_id}"
                for _ in range(10):  # Max 10 attempts
                    time.sleep(1)
                    status_response = self.session.get(status_url)
                    if status_response.status_code == 200:
                        results_url = (
                            f"{self.base_url}/idmapping/results/{job_id}"
                        )
                        results_response = self.session.get(results_url)
                        if results_response.status_code == 200:
                            results = results_response.json()
                            if (
                                "results" in results
                                and len(results["results"]) > 0
                            ):
                                return results["results"][0]["to"]
                        break

        except Exception as e:
            logger.error(f"Error converting protein ID {protein_id}: {str(e)}")

        return None


class StringDBFetcher(BaseFetcher):
    """Fetcher for STRING-db protein-protein interactions."""

    def __init__(self, species: str = "9606"):
        # STRING-db API works fine with normal SSL verification
        super().__init__("https://string-db.org/api")
        self.species = species  # NCBI taxon ID (9606 for human)

    def get_protein_interactions(
        self, gene_symbol: str
    ) -> Optional[List[Dict]]:
        """Get protein-protein interactions from STRING-db."""
        try:
            # STRING-db can work directly with gene symbols for common genes
            # Try direct query first, fall back to ID mapping if needed
            url = f"{self.base_url}/json/interaction_partners"
            params = {
                "identifiers": gene_symbol,
                "species": self.species,
                "limit": 50,  # Limit to top 50 interactions
                "required_score": 400,  # Medium confidence threshold
                "caller_identity": "geneinfo_v0.1",
            }

            # Use GET method as it works reliably
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()

            if result and isinstance(result, list):
                interactions = []
                for interaction in result:
                    interaction_info = {
                        "partner_id": interaction.get("stringId_B"),
                        "partner_name": interaction.get("preferredName_B"),
                        "combined_score": interaction.get("score"),
                        "experimental_score": interaction.get("escore"),
                        "database_score": interaction.get("dscore"),
                        "textmining_score": interaction.get("tscore"),
                        "coexpression_score": interaction.get("ascore"),
                        "evidence_types": self._get_evidence_types(interaction),
                        "source_database": "STRING-db"
                    }
                    interactions.append(interaction_info)

                return interactions if interactions else None

            return None

        except Exception as e:
            logger.error(
                f"Error fetching STRING-db interactions for {gene_symbol}: {str(e)}"
            )
            return None

    def _get_string_id(self, gene_symbol: str) -> Optional[str]:
        """Map gene symbol to STRING identifier."""
        try:
            url = f"{self.base_url}/json/get_string_ids"
            params = {
                "identifiers": gene_symbol,
                "species": self.species,
                "echo_query": 1,
                "caller_identity": "geneinfo_v0.1",
            }

            response = self.session.post(url, data=params, timeout=30)
            response.raise_for_status()

            # Wait 1 second as requested by STRING API
            time.sleep(1)

            result = response.json()

            if result and isinstance(result, list) and len(result) > 0:
                # Return the first (best) match
                return result[0].get("stringId")

            return None

        except Exception as e:
            logger.error(f"Error mapping {gene_symbol} to STRING ID: {str(e)}")
            return None

    def _get_evidence_types(self, interaction: Dict) -> List[str]:
        """Extract evidence types based on scores."""
        evidence_types = []
        scores = {
            "experimental": interaction.get("escore", 0),
            "database": interaction.get("dscore", 0),
            "textmining": interaction.get("tscore", 0),
            "coexpression": interaction.get("ascore", 0),
            "neighborhood": interaction.get("nscore", 0),
            "fusion": interaction.get("fscore", 0),
            "phylogenetic": interaction.get("pscore", 0),
        }

        for evidence_type, score in scores.items():
            if score and float(score) > 0.1:  # Only include if score > 0.1
                evidence_types.append(evidence_type)

        return evidence_types


class BioGRIDFetcher(BaseFetcher):
    """Fetcher for BioGRID protein-protein interactions."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__("https://webservice.thebiogrid.org")
        # Get API key from parameter or environment
        self.api_key = get_api_key("BIOGRID_API_KEY", api_key)

        if not self.api_key:
            logger.warning("BioGRID API key not found. Protein interactions will be limited.")

    def get_protein_interactions(self, gene_symbol: str) -> Optional[List[Dict]]:
        """Get protein-protein interactions from BioGRID.

        Uses the BioGRID REST API to fetch interactions for the given gene symbol.
        Returns first-order interactors with evidence information.
        """
        if not self.api_key:
            logger.warning("BioGRID API key required for protein interactions")
            return None

        try:
            # BioGRID REST API endpoint for interactions
            url = f"{self.base_url}/interactions/"

            params = {
                'accessKey': self.api_key,
                'searchNames': 'true',  # Search by gene symbol
                'geneList': gene_symbol,
                'includeInteractors': 'true',  # Include first-order interactors
                'includeInteractorInteractions': 'false',  # Don't include interactor-interactor
                'taxId': '9606',  # Human taxonomy ID
                'format': 'json',  # JSON format
                'max': '50',  # Limit to 50 most relevant interactions
                'includeHeader': 'false'
            }

            response = self._make_request(url, params)

            if response and isinstance(response, dict):
                interactions = []
                unique_partners = set()

                # BioGRID returns a dict with interaction IDs as keys
                for interaction_id, interaction in response.items():
                    # Extract interaction partner information
                    partner_info = self._extract_interaction_partner(interaction, gene_symbol)
                    if partner_info and partner_info['partner_symbol'] not in unique_partners:
                        unique_partners.add(partner_info['partner_symbol'])
                        interactions.append(partner_info)

                        # Limit to prevent too many results
                        if len(interactions) >= 30:
                            break

                logger.info(f"Found {len(interactions)} BioGRID interactions for {gene_symbol}")
                return interactions if interactions else None

            return None

        except Exception as e:
            logger.error(f"Error fetching BioGRID interactions for {gene_symbol}: {str(e)}")
            return None

    def _extract_interaction_partner(self, interaction: Dict, query_gene: str) -> Optional[Dict]:
        """Extract interaction partner information from BioGRID interaction data."""
        try:
            # BioGRID returns interactions with OFFICIAL_SYMBOL_A and OFFICIAL_SYMBOL_B
            symbol_a = interaction.get('OFFICIAL_SYMBOL_A', '')
            symbol_b = interaction.get('OFFICIAL_SYMBOL_B', '')

            # Determine which is the partner (not the query gene)
            if symbol_a.upper() == query_gene.upper():
                partner_symbol = symbol_b
                partner_id = interaction.get('ENTREZ_GENE_B', '')
                partner_organism = interaction.get('ORGANISM_B_NAME', '')
            elif symbol_b.upper() == query_gene.upper():
                partner_symbol = symbol_a
                partner_id = interaction.get('ENTREZ_GENE_A', '')
                partner_organism = interaction.get('ORGANISM_A_NAME', '')
            else:
                # This shouldn't happen with proper query, but handle gracefully
                partner_symbol = symbol_b  # Default to B as partner
                partner_id = interaction.get('ENTREZ_GENE_B', '')
                partner_organism = interaction.get('ORGANISM_B_NAME', '')

            if not partner_symbol:
                return None

            # Extract interaction details
            interaction_info = {
                'partner_symbol': partner_symbol,
                'partner_entrez_id': partner_id,
                'partner_organism': partner_organism,
                'experimental_system': interaction.get('EXPERIMENTAL_SYSTEM', 'Unknown'),
                'experimental_system_type': interaction.get('EXPERIMENTAL_SYSTEM_TYPE', 'Unknown'),
                'throughput': interaction.get('THROUGHPUT', 'Unknown'),
                'pubmed_id': interaction.get('PUBMED_ID', ''),
                'pubmed_author': interaction.get('AUTHOR', ''),
                'interaction_id': interaction.get('BIOGRID_ID_INTERACTOR_A', ''),
                'modification': interaction.get('MODIFICATION', ''),
                'qualifications': interaction.get('QUALIFICATIONS', ''),
                'tags': interaction.get('TAGS', ''),
                'source_database': 'BioGRID'
            }

            return interaction_info

        except Exception as e:
            logger.error(f"Error extracting BioGRID interaction partner: {str(e)}")
            return None
