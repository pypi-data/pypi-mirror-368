# Author: Chunjie Liu
# Contact: chunjie.sam.liu.at.gmail.com
# Date: 2025-08-06
# Description: Tests for data fetchers
# Version: 0.1

"""
Tests for data fetchers.
"""

from unittest.mock import Mock, patch
import os

import pytest
import requests

from geneinfo.fetchers import (
    BaseFetcher,
    EnsemblFetcher,
    GOFetcher,
    ReactomeFetcher,
    UniProtFetcher,
    BioGRIDFetcher,
    StringDBFetcher,
)


class TestBaseFetcher:
    """Test cases for BaseFetcher class."""

    @patch("geneinfo.fetchers.base.requests.Session.get")
    @patch("time.sleep")
    def test_make_request_success(self, mock_sleep, mock_get):
        """Test successful API request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        fetcher = BaseFetcher("http://example.com")
        result = fetcher._make_request("http://example.com/test")

        assert result == {"test": "data"}
        mock_sleep.assert_called_once_with(0.1)
        mock_get.assert_called_once()

    @patch("geneinfo.fetchers.base.requests.Session.get")
    @patch("time.sleep")
    def test_make_request_http_error(self, mock_sleep, mock_get):
        """Test API request with HTTP error."""
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP Error")

        fetcher = BaseFetcher("http://example.com")
        result = fetcher._make_request("http://example.com/test")

        assert result is None


class TestEnsemblFetcher:
    """Test cases for EnsemblFetcher class."""

    def test_init(self):
        """Test EnsemblFetcher initialization."""
        fetcher = EnsemblFetcher("human")
        assert (
            fetcher.species == "homo_sapiens"
        )  # "human" maps to "homo_sapiens"
        assert "ensembl" in fetcher.base_url

    def test_init_mouse(self):
        """Test EnsemblFetcher initialization with mouse."""
        fetcher = EnsemblFetcher("mouse")
        assert fetcher.species == "mouse"


class TestUniProtFetcher:
    """Test cases for UniProtFetcher class."""

    def test_init(self):
        """Test UniProtFetcher initialization."""
        fetcher = UniProtFetcher()
        assert "uniprot" in fetcher.base_url


class TestGOFetcher:
    """Test cases for GOFetcher class."""

    def test_init(self):
        """Test GOFetcher initialization."""
        fetcher = GOFetcher()
        assert (
            "ebi.ac.uk" in fetcher.base_url
            or "ontology" in fetcher.base_url.lower()
        )


class TestReactomeFetcher:
    """Test cases for ReactomeFetcher class."""

    def test_init(self):
        """Test ReactomeFetcher initialization."""
        fetcher = ReactomeFetcher()
        assert "reactome" in fetcher.base_url


class TestBioGRIDFetcher:
    """Test cases for BioGRIDFetcher class."""

    def test_init_with_api_key(self):
        """Test BioGRIDFetcher initialization with API key."""
        fetcher = BioGRIDFetcher(api_key="test_key")
        assert fetcher.api_key == "test_key"
        assert "thebiogrid.org" in fetcher.base_url

    @patch.dict("os.environ", {}, clear=True)
    @patch("geneinfo.utils.load_environment")
    def test_init_without_api_key(self, mock_load_env):
        """Test BioGRIDFetcher initialization without API key."""
        mock_load_env.return_value = None
        fetcher = BioGRIDFetcher()
        assert fetcher.api_key is None

    @patch("geneinfo.fetchers.protein.BioGRIDFetcher._make_request")
    def test_get_protein_interactions_success(self, mock_request):
        """Test successful protein interactions retrieval."""
        # Mock BioGRID API response
        mock_response = {
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
        mock_request.return_value = mock_response

        fetcher = BioGRIDFetcher(api_key="test_key")
        result = fetcher.get_protein_interactions("TP53")

        assert result is not None
        assert len(result) == 1
        assert result[0]["partner_symbol"] == "MDM2"
        assert result[0]["experimental_system"] == "Two-hybrid"
        assert result[0]["source_database"] == "BioGRID"

    @patch.dict("os.environ", {}, clear=True)
    @patch("geneinfo.utils.load_environment")
    @patch("geneinfo.fetchers.protein.BioGRIDFetcher._make_request")
    def test_get_protein_interactions_no_api_key(self, mock_request, mock_load_env):
        """Test protein interactions without API key."""
        mock_load_env.return_value = None
        fetcher = BioGRIDFetcher()
        result = fetcher.get_protein_interactions("TP53")
        assert result is None
        mock_request.assert_not_called()

    @patch("geneinfo.fetchers.protein.BioGRIDFetcher._make_request")
    def test_get_protein_interactions_empty_response(self, mock_request):
        """Test protein interactions with empty response."""
        mock_request.return_value = {}

        fetcher = BioGRIDFetcher(api_key="test_key")
        result = fetcher.get_protein_interactions("NONEXISTENT")

        assert result is None


class TestStringDBFetcher:
    """Test cases for StringDBFetcher class."""

    def test_init(self):
        """Test StringDBFetcher initialization."""
        fetcher = StringDBFetcher()
        assert fetcher.species == "9606"  # Human NCBI taxon ID
        assert "string-db.org" in fetcher.base_url

    def test_init_different_species(self):
        """Test StringDBFetcher initialization with different species."""
        fetcher = StringDBFetcher(species="10090")  # Mouse
        assert fetcher.species == "10090"

    def test_get_protein_interactions_success(self):
        """Test successful protein interactions retrieval from STRING-db."""
        # Mock STRING-db API response
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "stringId_A": "9606.ENSP00000269305",
                "stringId_B": "9606.ENSP00000355812",
                "preferredName_A": "TP53",
                "preferredName_B": "MDM2",
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
        mock_response.raise_for_status.return_value = None

        fetcher = StringDBFetcher()

        with patch.object(fetcher.session, 'get', return_value=mock_response):
            result = fetcher.get_protein_interactions("TP53")

            assert result is not None
            assert len(result) == 1
            assert result[0]["partner_name"] == "MDM2"
            assert result[0]["combined_score"] == 0.999
            assert result[0]["source_database"] == "STRING-db"
            assert "experimental" in result[0]["evidence_types"]

    def test_get_protein_interactions_empty_response(self):
        """Test protein interactions with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None

        fetcher = StringDBFetcher()

        with patch.object(fetcher.session, 'get', return_value=mock_response):
            result = fetcher.get_protein_interactions("NONEXISTENT")
            assert result is None

    def test_get_protein_interactions_network_error(self):
        """Test protein interactions with network error."""
        fetcher = StringDBFetcher()

        with patch.object(fetcher.session, 'get', side_effect=requests.exceptions.RequestException("Network error")):
            result = fetcher.get_protein_interactions("TP53")
            assert result is None

    def test_get_evidence_types(self):
        """Test evidence types extraction."""
        fetcher = StringDBFetcher()

        # Mock interaction with various scores
        interaction = {
            "escore": 0.5,
            "dscore": 0.3,
            "tscore": 0.0,
            "ascore": 0.2,
            "nscore": 0.0,
            "fscore": 0.0,
            "pscore": 0.15  # Changed from 0.1 to 0.15 to be > 0.1
        }

        evidence_types = fetcher._get_evidence_types(interaction)

        # Should include evidence types with score > 0.1
        expected_types = ["experimental", "database", "coexpression", "phylogenetic"]
        assert all(et in evidence_types for et in expected_types)
        assert "textmining" not in evidence_types  # score is 0.0
