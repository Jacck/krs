#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KRS HTTP Client

This module provides HTTP client functionality for the KRS API.
"""

import requests
import logging
import time
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin


class KrsHttpClient:
    """HTTP client for the KRS API with rate limiting and error handling."""
    
    def __init__(self, base_url: str, rate_limit: int = 5):
        """Initialize the HTTP client.
        
        Args:
            base_url: Base URL for the KRS API
            rate_limit: Maximum number of requests per second (default: 5)
        """
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        self.last_request_time = 0
        self.logger = logging.getLogger(__name__)
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a GET request to the API endpoint.
        
        Args:
            endpoint: API endpoint to request
            params: Query parameters
            
        Returns:
            Response data as a dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Make a POST request to the API endpoint.
        
        Args:
            endpoint: API endpoint to request
            params: Query parameters
            data: JSON data for the request body
            
        Returns:
            Response data as a dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        return self._request("POST", endpoint, params=params, data=data)
    
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                data: Optional[Dict] = None) -> Dict:
        """Make a request to the API with rate limiting and error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint to request
            params: Query parameters
            data: JSON data for the request body
            
        Returns:
            Response data as a dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Build the full URL
        url = urljoin(self.base_url, endpoint)
        
        # Log the request
        self.logger.debug(f"Making {method} request to {url}")
        if params:
            self.logger.debug(f"Parameters: {params}")
        if data:
            self.logger.debug(f"Data: {data}")
        
        try:
            # Make the request
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                response = self.session.post(url, params=params, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Update the last request time
            self.last_request_time = time.time()
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse the response as JSON
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            # Handle specific API errors
            if e.response.status_code == 429:
                self.logger.warning("Rate limit exceeded. Retrying after delay.")
                time.sleep(5)  # Wait 5 seconds before retrying
                return self._request(method, endpoint, params, data)
            raise
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
    
    def _apply_rate_limit(self) -> None:
        """Apply rate limiting to respect the API's limits."""
        if self.rate_limit <= 0:
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit
        
        if elapsed_time < min_interval:
            sleep_time = min_interval - elapsed_time
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
