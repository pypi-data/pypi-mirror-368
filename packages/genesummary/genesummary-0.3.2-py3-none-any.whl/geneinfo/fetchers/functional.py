"""
Functional data fetchers for Gene Ontology and Reactome APIs.

Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-08-06
Description: Fetchers for functional annotation and pathway data
Version: 0.1
"""

import logging
from typing import Dict, List, Optional

from .base import BaseFetcher

logger = logging.getLogger(__name__)


class GOFetcher(BaseFetcher):
    """Fetcher for Gene Ontology annotations using QuickGO API."""

    def __init__(self):
        super().__init__("https://www.ebi.ac.uk/QuickGO/services")

    def get_go_terms(self, identifier: str) -> Optional[List[Dict]]:
        """Get GO terms for a gene using QuickGO API.

        Accepts: UniProt ID (preferred), gene symbol, or other identifiers.
        """
        try:
            # Try to get GO terms via QuickGO API
            if self._looks_like_uniprot(identifier):
                return self._get_go_from_quickgo(identifier)
            else:
                # For gene symbols, try to use them directly
                return self._get_go_from_quickgo(identifier, by_symbol=True)

        except Exception as e:
            logger.error(f"Error fetching GO terms for {identifier}: {str(e)}")
        return None

    def _looks_like_uniprot(self, identifier: str) -> bool:
        """Check if identifier looks like a UniProt accession."""
        if not identifier or len(identifier) < 6:
            return False
        # UniProt pattern: [OPQ][0-9][A-Z0-9]{3}[0-9] or [A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}
        return identifier[0].isalpha() and any(c.isdigit() for c in identifier)

    def _get_go_from_quickgo(self, identifier: str, by_symbol: bool = False) -> Optional[List[Dict]]:
        """Get GO terms from QuickGO API."""
        try:
            url = f"{self.base_url}/annotation/search"

            if by_symbol:
                params = {
                    'geneProductSymbol': identifier,
                    'limit': 50,
                    'taxonId': 9606  # Human
                }
            else:
                params = {
                    'geneProductId': identifier,
                    'limit': 50
                }

            response = self._make_request(url, params)

            if response and "results" in response:
                go_terms = []
                for annotation in response["results"]:
                    go_info = {
                        "go_id": annotation.get("goId"),
                        "term": annotation.get("goName", ""),
                        "category": self._map_go_aspect(annotation.get("goAspect")),
                        "evidence": annotation.get("goEvidence"),
                        "qualifier": annotation.get("qualifier"),
                        "reference": annotation.get("reference"),
                        "assigned_by": annotation.get("assignedBy"),
                    }
                    go_terms.append(go_info)

                return go_terms[:50]  # Limit to 50 most relevant

        except Exception as e:
            logger.error(f"Error fetching GO from QuickGO for {identifier}: {str(e)}")
        return None

    def _map_go_aspect(self, aspect: str) -> str:
        """Map GO aspect to standard category names."""
        if not aspect:
            return "unknown"
        aspect_map = {
            "biological_process": "biological_process",
            "molecular_function": "molecular_function",
            "cellular_component": "cellular_component"
        }
        return aspect_map.get(aspect.lower(), aspect)
        return None

    def _build_go_bioentity_path(self, identifier: str) -> Optional[str]:
        """Build GO API bioentity path from mixed identifiers.

        GO API expects bioentity CURIEs or namespaces like NCBIGene:7157 or UniProtKB:P04637.
        Fallback to gene/TP53 if a symbol is provided.
        """
        if not identifier:
            return None

        s = identifier.strip()
        # Entrez numeric
        if s.isdigit():
            return f"NCBIGene:{s}"
        # Ensembl gene
        if s.upper().startswith("ENSG"):
            return f"ENSEMBL:{s}"
        # UniProt accession (simple heuristic: starts with [OPQ][0-9] or [A-NR-Z][0-9]...)
        if len(s) >= 6 and any(s[0].upper().startswith(p) for p in list("OPQ")):
            return f"UniProtKB:{s}"
        # If looks like UniProt (alphanumeric with pattern), still try UniProtKB
        if len(s) >= 6 and s[0].isalnum():
            # Keep symbol fallback too
            pass
        # Default treat as gene symbol
        return f"gene/{s}"


class ReactomeFetcher(BaseFetcher):
    """Fetcher for Reactome pathway data."""

    def __init__(self):
        super().__init__("https://reactome.org/ContentService")

    def get_pathways(self, identifier: str) -> Optional[List[Dict]]:
        """Get Reactome pathways using preferred mapping endpoints.

        Accepts UniProt accession, Ensembl ID, or gene symbol. Prefer UniProt if available.
        """
        try:
            # Try direct mapping via UniProt accession
            if identifier and self._looks_like_uniprot(identifier):
                acc = identifier
                url = f"{self.base_url}/data/mapping/UniProt/{acc}/pathways"
                response = self._make_request(url)
                if response and isinstance(response, list):
                    return [
                        {
                            "pathway_id": item.get("stId"),
                            "name": item.get("displayName"),
                            "species": item.get("speciesName"),
                            "url": f"https://reactome.org/content/detail/{item.get('stId')}",
                        }
                        for item in response[:10]
                        if item.get("stId")
                    ]

            # Fallback: generic query by symbol/identifier
            url = f"{self.base_url}/data/query/{identifier}"
            response = self._make_request(url)
            if response and isinstance(response, list) and len(response) > 0:
                pathways = []
                for item in response[:10]:
                    if item.get("className") == "Pathway":
                        pathways.append(
                            {
                                "pathway_id": item.get("stId"),
                                "name": item.get("displayName"),
                                "species": item.get("speciesName"),
                                "url": f"https://reactome.org/content/detail/{item.get('stId')}",
                            }
                        )
                return pathways or None
        except Exception as e:
            logger.error(f"Error fetching pathways for {identifier}: {str(e)}")
        return None

    def _looks_like_uniprot(self, s: str) -> bool:
        if not s:
            return False
        s = s.strip()
        # Simple UniProt pattern check (doesn't cover all cases): one letter + 5 digits or 2 letters + 4 digits, optional -#
        # We'll be permissive here
        return len(s) >= 6 and s[0].isalnum()
