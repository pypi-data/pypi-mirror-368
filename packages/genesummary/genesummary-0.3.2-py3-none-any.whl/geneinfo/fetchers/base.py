"""
Base fetcher class with common functionality.

Author: Chunjie Liu
Contact: chunjie.sam.liu.at.gmail.com
Date: 2025-08-06
Description: Base class for API fetchers with rate limiting and error handling
Version: 0.1
"""

import logging
import time
from typing import Any, Dict, Optional

import requests
import urllib3

# Suppress SSL warnings for STRING-db
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class BaseFetcher:
    """Base class for API fetchers with rate limiting and error handling."""

    def __init__(
        self, base_url: str, rate_limit: float = 0.1, use_mock: bool = False
    ):
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.use_mock = use_mock
        self.session = requests.Session()

        # Disable SSL verification to handle certificate issues in corporate networks
        self.session.verify = False

        self.session.headers.update(
            {
                "User-Agent": "GeneInfo/0.1.0 (https://github.com/chunjie-sam-liu/geneinfo)"
            }
        )

    def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request with rate limiting and error handling."""
        # Return None immediately if using mock mode
        if self.use_mock:
            return None

        try:
            time.sleep(self.rate_limit)  # Rate limiting
            response = self.session.get(
                url, params=params, timeout=10
            )  # Reduced timeout
            response.raise_for_status()

            # Handle different content types
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                return response.json()
            else:
                return {"text": response.text}

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            return None
