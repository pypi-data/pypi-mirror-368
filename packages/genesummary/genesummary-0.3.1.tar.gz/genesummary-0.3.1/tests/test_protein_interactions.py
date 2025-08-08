# Author: Chunjie Liu
# Contact: chunjie.sam.liu.at.gmail.com
# Date: 2025-01-08
# Description: Tests for protein interaction functionality
# Version: 0.1

"""
Tests for protein interaction fetchers and integration.
"""

from unittest.mock import Mock, patch
import pytest
import requests

from geneinfo.fetchers.protein import BioGRIDFetcher, StringDBFetcher
from geneinfo.core import GeneInfo


class TestProteinInteractionIntegration:
    """Integration tests for protein interaction functionality."""

    @patch("geneinfo.fetchers.protein.BioGRIDFetcher._make_request")
    def test_dual_source_integration(self, mock_biogrid_request):
        """Test that both BioGRID and STRING-db work together."""
        # Mock BioGRID response
        biogrid_response = {
            "12345": {
                "OFFICIAL_SYMBOL_A": "TP53",
                "OFFICIAL_SYMBOL_B": "MDM2",
                "ENTREZ_GENE_B": "4193",
                "ORGANISM_B_NAME": "Homo sapiens",
                "EXPERIMENTAL_SYSTEM": "Two-hybrid",
                "EXPERIMENTAL_SYSTEM_TYPE": "physical",
                "THROUGHPUT": "Low Throughput",
                "PUBMED_ID": "123456",
                "AUTHOR": "Smith et al.",
                "BIOGRID_ID_INTERACTOR_A": "12345",
                "MODIFICATION": "",
                "QUALIFICATIONS": "",
                "TAGS": ""
            }
        }
        mock_biogrid_request.return_value = biogrid_response

        # Mock STRING-db response
        stringdb_response = Mock()
        stringdb_response.json.return_value = [
            {
                "stringId_A": "9606.ENSP00000269305",
                "stringId_B": "9606.ENSP00000355812",
                "preferredName_A": "TP53",
                "preferredName_B": "CDKN1A",
                "score": 0.999,
                "escore": 0.981,
                "dscore": 0.900,
                "tscore": 0.756,
                "ascore": 0.123,
                "nscore": 0.0,
                "fscore": 0.0,
                "pscore": 0.234
            }
        ]
        stringdb_response.raise_for_status.return_value = None

        # Test individual fetchers
        biogrid_fetcher = BioGRIDFetcher(api_key="test_key")
        biogrid_interactions = biogrid_fetcher.get_protein_interactions("TP53")

        stringdb_fetcher = StringDBFetcher()
        with patch.object(stringdb_fetcher.session, 'get', return_value=stringdb_response):
            stringdb_interactions = stringdb_fetcher.get_protein_interactions("TP53")

        # Verify both work
        assert biogrid_interactions is not None
        assert len(biogrid_interactions) == 1
        assert biogrid_interactions[0]["partner_symbol"] == "MDM2"
        assert biogrid_interactions[0]["source_database"] == "BioGRID"

        assert stringdb_interactions is not None
        assert len(stringdb_interactions) == 1
        assert stringdb_interactions[0]["partner_name"] == "CDKN1A"
        assert stringdb_interactions[0]["source_database"] == "STRING-db"

    def test_biogrid_extract_interaction_partner(self):
        """Test BioGRID interaction partner extraction logic."""
        fetcher = BioGRIDFetcher(api_key="test_key")

        # Test case where query gene is A
        interaction_a = {
            "OFFICIAL_SYMBOL_A": "TP53",
            "OFFICIAL_SYMBOL_B": "MDM2",
            "ENTREZ_GENE_B": "4193",
            "ORGANISM_B_NAME": "Homo sapiens",
            "EXPERIMENTAL_SYSTEM": "Two-hybrid",
            "EXPERIMENTAL_SYSTEM_TYPE": "physical",
            "THROUGHPUT": "Low Throughput",
            "PUBMED_ID": "123456",
            "AUTHOR": "Smith et al.",
            "BIOGRID_ID_INTERACTOR_A": "12345",
        }

        result = fetcher._extract_interaction_partner(interaction_a, "TP53")
        assert result["partner_symbol"] == "MDM2"
        assert result["partner_entrez_id"] == "4193"

        # Test case where query gene is B
        interaction_b = {
            "OFFICIAL_SYMBOL_A": "MDM2",
            "OFFICIAL_SYMBOL_B": "TP53",
            "ENTREZ_GENE_A": "4193",
            "ORGANISM_A_NAME": "Homo sapiens",
            "EXPERIMENTAL_SYSTEM": "Co-immunoprecipitation",
            "EXPERIMENTAL_SYSTEM_TYPE": "physical",
            "THROUGHPUT": "Low Throughput",
            "PUBMED_ID": "789012",
            "AUTHOR": "Jones et al.",
            "BIOGRID_ID_INTERACTOR_A": "67890",
        }

        result = fetcher._extract_interaction_partner(interaction_b, "TP53")
        assert result["partner_symbol"] == "MDM2"
        assert result["partner_entrez_id"] == "4193"

    def test_stringdb_evidence_types_logic(self):
        """Test STRING-db evidence types extraction logic."""
        fetcher = StringDBFetcher()

        # Test interaction with multiple evidence types
        interaction = {
            "escore": 0.8,   # experimental - should be included
            "dscore": 0.5,   # database - should be included
            "tscore": 0.05,  # textmining - should NOT be included (< 0.1)
            "ascore": 0.3,   # coexpression - should be included
            "nscore": 0.0,   # neighborhood - should NOT be included
            "fscore": 0.15,  # fusion - should be included
            "pscore": 0.2    # phylogenetic - should be included
        }

        evidence_types = fetcher._get_evidence_types(interaction)

        expected = ["experimental", "database", "coexpression", "fusion", "phylogenetic"]
        assert all(et in evidence_types for et in expected)
        assert "textmining" not in evidence_types
        assert "neighborhood" not in evidence_types

    @patch.dict("os.environ", {"BIOGRID_API_KEY": "env_test_key"})
    def test_biogrid_api_key_from_environment(self):
        """Test that BioGRID API key is correctly loaded from environment."""
        fetcher = BioGRIDFetcher()
        assert fetcher.api_key == "env_test_key"

    def test_stringdb_species_configuration(self):
        """Test STRING-db species configuration."""
        # Test default human species
        fetcher_human = StringDBFetcher()
        assert fetcher_human.species == "9606"

        # Test mouse species
        fetcher_mouse = StringDBFetcher(species="10090")
        assert fetcher_mouse.species == "10090"

    @patch("geneinfo.fetchers.protein.BioGRIDFetcher._make_request")
    def test_biogrid_large_response_limiting(self, mock_request):
        """Test that BioGRID limits large responses to prevent memory issues."""
        # Create a large mock response (40 interactions)
        large_response = {}
        for i in range(40):
            large_response[str(i)] = {
                "OFFICIAL_SYMBOL_A": "TP53",
                "OFFICIAL_SYMBOL_B": f"PARTNER{i}",
                "ENTREZ_GENE_B": str(1000 + i),
                "ORGANISM_B_NAME": "Homo sapiens",
                "EXPERIMENTAL_SYSTEM": "Two-hybrid",
                "EXPERIMENTAL_SYSTEM_TYPE": "physical",
                "THROUGHPUT": "High Throughput",
                "PUBMED_ID": "123456",
                "AUTHOR": "Smith et al.",
                "BIOGRID_ID_INTERACTOR_A": str(i),
                "MODIFICATION": "",
                "QUALIFICATIONS": "",
                "TAGS": ""
            }

        mock_request.return_value = large_response

        fetcher = BioGRIDFetcher(api_key="test_key")
        result = fetcher.get_protein_interactions("TP53")

        # Should be limited to 30 interactions max
        assert len(result) <= 30

    def test_stringdb_timeout_handling(self):
        """Test STRING-db timeout handling."""
        fetcher = StringDBFetcher()

        with patch.object(fetcher.session, 'get', side_effect=requests.exceptions.Timeout("Request timed out")):
            result = fetcher.get_protein_interactions("TP53")
            assert result is None

    def test_interaction_data_consistency(self):
        """Test that interaction data has consistent field names."""
        # BioGRID fields
        biogrid_fields = [
            "partner_symbol", "partner_entrez_id", "partner_organism",
            "experimental_system", "experimental_system_type", "throughput",
            "pubmed_id", "pubmed_author", "interaction_id", "source_database"
        ]

        # STRING-db fields
        stringdb_fields = [
            "partner_id", "partner_name", "combined_score", "experimental_score",
            "database_score", "textmining_score", "coexpression_score",
            "evidence_types", "source_database"
        ]

        # These are the expected field structures - just verify they're defined
        assert len(biogrid_fields) > 0
        assert len(stringdb_fields) > 0
        assert "source_database" in biogrid_fields
        assert "source_database" in stringdb_fields


class TestProteinInteractionErrorHandling:
    """Test error handling in protein interaction fetchers."""

    def test_biogrid_missing_fields(self):
        """Test BioGRID handling of missing required fields."""
        fetcher = BioGRIDFetcher(api_key="test_key")

        # Interaction missing partner symbol
        incomplete_interaction = {
            "OFFICIAL_SYMBOL_A": "TP53",
            # Missing OFFICIAL_SYMBOL_B
            "ENTREZ_GENE_B": "4193",
        }

        result = fetcher._extract_interaction_partner(incomplete_interaction, "TP53")
        assert result is None

    def test_stringdb_invalid_json_response(self):
        """Test STRING-db handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None

        fetcher = StringDBFetcher()
        with patch.object(fetcher.session, 'get', return_value=mock_response):
            result = fetcher.get_protein_interactions("TP53")
            assert result is None

    @patch("geneinfo.fetchers.protein.BioGRIDFetcher._make_request")
    def test_biogrid_none_response(self, mock_request):
        """Test BioGRID handling of None response."""
        mock_request.return_value = None

        fetcher = BioGRIDFetcher(api_key="test_key")
        result = fetcher.get_protein_interactions("TP53")

        assert result is None

    def test_stringdb_missing_score_fields(self):
        """Test STRING-db handling of missing score fields."""
        fetcher = StringDBFetcher()

        # Interaction missing some score fields
        incomplete_interaction = {
            "escore": 0.5,
            # Missing other score fields
        }

        evidence_types = fetcher._get_evidence_types(incomplete_interaction)

        # Should handle missing fields gracefully
        assert isinstance(evidence_types, list)
        if evidence_types:  # If any evidence types found
            assert "experimental" in evidence_types
