# Author: Chunjie Liu
# Contact: chunjie.sam.liu.at.gmail.com
# Date: 2025-08-06
# Description: Tests for core GeneInfo class
# Version: 0.1

"""
Tests for core GeneInfo functionality.
"""

import json
from unittest.mock import Mock, patch

import pytest

from geneinfo.core import GeneInfo
from geneinfo.mock_data import MOCK_GENE_DATA


class TestGeneInfo:
    """Test cases for GeneInfo class."""

    def test_init(self):
        """Test GeneInfo initialization."""
        gene_info = GeneInfo(species="human")
        assert gene_info.species == "human"
        assert hasattr(gene_info, "ensembl_fetcher")
        assert hasattr(gene_info, "uniprot_fetcher")
        assert hasattr(gene_info, "go_fetcher")
        assert hasattr(gene_info, "reactome_fetcher")

    def test_init_different_species(self):
        """Test GeneInfo initialization with different species."""
        gene_info = GeneInfo(species="mouse")
        assert gene_info.species == "mouse"

    @patch("geneinfo.core.MyGeneFetcher")
    @patch("geneinfo.core.EnsemblFetcher")
    @patch("geneinfo.core.UniProtFetcher")
    @patch("geneinfo.core.GOFetcher")
    @patch("geneinfo.core.ReactomeFetcher")
    @patch("geneinfo.core.BioGRIDFetcher")
    @patch("geneinfo.core.StringDBFetcher")
    def test_get_gene_info_structure(
        self, mock_stringdb, mock_biogrid, mock_reactome, mock_go, mock_uniprot, mock_ensembl, mock_mygene
    ):
        """Test that get_gene_info returns proper structure."""
        # Mock the fetchers
        mock_ensembl_instance = Mock()
        mock_ensembl_instance.get_gene_info.return_value = MOCK_GENE_DATA[
            "TP53"
        ]["basic_info"]
        mock_ensembl_instance.get_transcripts.return_value = MOCK_GENE_DATA[
            "TP53"
        ]["transcripts"]
        mock_ensembl_instance.get_homologs.return_value = {
            "orthologs": MOCK_GENE_DATA["TP53"].get("orthologs", []),
            "paralogs": MOCK_GENE_DATA["TP53"].get("paralogs", []),
        }
        mock_ensembl.return_value = mock_ensembl_instance

        # Mock MyGene fetcher
        mock_mygene_instance = Mock()
        mock_mygene_instance.get_gene_info.return_value = MOCK_GENE_DATA["TP53"]["basic_info"]
        mock_mygene.return_value = mock_mygene_instance

        mock_uniprot_instance = Mock()
        mock_uniprot_instance.get_protein_domains.return_value = MOCK_GENE_DATA[
            "TP53"
        ].get("protein_domains", [])
        mock_uniprot.return_value = mock_uniprot_instance

        # Mock BioGRID fetcher
        mock_biogrid_instance = Mock()
        mock_biogrid_instance.get_protein_interactions.return_value = [
            {"partner_symbol": "MDM2", "source_database": "BioGRID"}
        ]
        mock_biogrid.return_value = mock_biogrid_instance

        # Mock STRING-db fetcher
        mock_stringdb_instance = Mock()
        mock_stringdb_instance.get_protein_interactions.return_value = [
            {"partner_name": "CDKN1A", "source_database": "STRING-db"}
        ]
        mock_stringdb.return_value = mock_stringdb_instance

        mock_go_instance = Mock()
        mock_go_instance.get_go_terms.return_value = MOCK_GENE_DATA["TP53"].get(
            "gene_ontology", []
        )
        mock_go.return_value = mock_go_instance

        mock_reactome_instance = Mock()
        mock_reactome_instance.get_pathways.return_value = MOCK_GENE_DATA[
            "TP53"
        ].get("pathways", [])
        mock_reactome.return_value = mock_reactome_instance

        gene_info = GeneInfo(biogrid_api_key="test_key")
        result = gene_info.get_gene_info("TP53")

        # Check structure
        expected_keys = [
            "query",
            "basic_info",
            "transcripts",
            "protein_domains",
            "gene_ontology",
            "pathways",
            "protein_interactions",
            "paralogs",
            "orthologs",
        ]
        for key in expected_keys:
            assert key in result

        assert result["query"] == "TP53"

        # Check that protein interactions include both sources
        interactions = result["protein_interactions"]
        assert len(interactions) == 2
        assert any(i.get("source_database") == "BioGRID" for i in interactions)
        assert any(i.get("source_database") == "STRING-db" for i in interactions)

    def test_get_gene_info_empty_input(self):
        """Test get_gene_info with empty input."""
        gene_info = GeneInfo()

        with pytest.raises((ValueError, TypeError)):
            gene_info.get_gene_info("")

    def test_get_gene_info_none_input(self):
        """Test get_gene_info with None input."""
        gene_info = GeneInfo()

        with pytest.raises((ValueError, TypeError)):
            gene_info.get_gene_info(None)

    def test_init_with_biogrid_api_key(self):
        """Test GeneInfo initialization with BioGRID API key."""
        gene_info = GeneInfo(biogrid_api_key="test_key")
        assert gene_info.biogrid_api_key == "test_key"
        assert gene_info.biogrid_fetcher is not None

    @patch("geneinfo.utils.load_environment")
    def test_init_without_biogrid_api_key(self, mock_load_env):
        """Test GeneInfo initialization without BioGRID API key."""
        # Mock load_environment to return empty environment
        mock_load_env.return_value = {}

        gene_info = GeneInfo()
        assert gene_info.biogrid_api_key is None
        # BioGRID fetcher should still be None without API key

    @patch("geneinfo.core.BioGRIDFetcher")
    @patch("geneinfo.core.StringDBFetcher")
    def test_protein_interactions_biogrid_only(self, mock_stringdb, mock_biogrid):
        """Test protein interactions with only BioGRID available."""
        # Mock BioGRID success
        mock_biogrid_instance = Mock()
        mock_biogrid_instance.get_protein_interactions.return_value = [
            {"partner_symbol": "MDM2", "source_database": "BioGRID"}
        ]
        mock_biogrid.return_value = mock_biogrid_instance

        # Mock STRING-db failure
        mock_stringdb_instance = Mock()
        mock_stringdb_instance.get_protein_interactions.side_effect = Exception("Network error")
        mock_stringdb.return_value = mock_stringdb_instance

        gene_info = GeneInfo(biogrid_api_key="test_key")

        # Mock other fetchers to avoid network calls
        with patch.object(gene_info, 'ensembl_fetcher') as mock_ensembl, \
             patch.object(gene_info, 'uniprot_fetcher') as mock_uniprot, \
             patch.object(gene_info, 'go_fetcher') as mock_go, \
             patch.object(gene_info, 'reactome_fetcher') as mock_reactome, \
             patch.object(gene_info, 'gwas_fetcher') as mock_gwas, \
             patch.object(gene_info, 'mygene_fetcher') as mock_mygene:

            # Mock basic responses
            mock_ensembl.get_gene_info.return_value = {"gene_symbol": "TP53"}
            mock_ensembl.get_transcripts.return_value = []
            mock_ensembl.get_homologs.return_value = {"orthologs": [], "paralogs": []}
            mock_uniprot.get_protein_domains.return_value = []
            mock_go.get_go_terms.return_value = []
            mock_reactome.get_pathways.return_value = []
            mock_gwas.get_gwas_studies.return_value = []
            mock_mygene.get_basic_info.return_value = {}

            result = gene_info.get_gene_info("TP53")

            # Should have only BioGRID interactions
            interactions = result["protein_interactions"]
            assert len(interactions) == 1
            assert interactions[0]["source_database"] == "BioGRID"

    @patch("geneinfo.core.BioGRIDFetcher")
    @patch("geneinfo.core.StringDBFetcher")
    def test_protein_interactions_stringdb_only(self, mock_stringdb, mock_biogrid):
        """Test protein interactions with only STRING-db available."""
        # Mock STRING-db success
        mock_stringdb_instance = Mock()
        mock_stringdb_instance.get_protein_interactions.return_value = [
            {"partner_name": "CDKN1A", "source_database": "STRING-db"}
        ]
        mock_stringdb.return_value = mock_stringdb_instance

        # Mock BioGRID not available (no API key)
        mock_biogrid.return_value = None

        gene_info = GeneInfo()  # No BioGRID API key
        gene_info.biogrid_fetcher = None  # Ensure it's None

        # Mock other fetchers to avoid network calls
        with patch.object(gene_info, 'ensembl_fetcher') as mock_ensembl, \
             patch.object(gene_info, 'uniprot_fetcher') as mock_uniprot, \
             patch.object(gene_info, 'go_fetcher') as mock_go, \
             patch.object(gene_info, 'reactome_fetcher') as mock_reactome, \
             patch.object(gene_info, 'gwas_fetcher') as mock_gwas, \
             patch.object(gene_info, 'mygene_fetcher') as mock_mygene:

            # Mock basic responses
            mock_ensembl.get_gene_info.return_value = {"gene_symbol": "TP53"}
            mock_ensembl.get_transcripts.return_value = []
            mock_ensembl.get_homologs.return_value = {"orthologs": [], "paralogs": []}
            mock_uniprot.get_protein_domains.return_value = []
            mock_go.get_go_terms.return_value = []
            mock_reactome.get_pathways.return_value = []
            mock_gwas.get_gwas_studies.return_value = []
            mock_mygene.get_basic_info.return_value = {}

            result = gene_info.get_gene_info("TP53")

            # Should have only STRING-db interactions
            interactions = result["protein_interactions"]
            assert len(interactions) == 1
            assert interactions[0]["source_database"] == "STRING-db"
