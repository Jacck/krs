#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KRS API Client

This module provides a client for the Polish National Court Register (KRS) API.
"""

import json
import requests
from typing import Dict, List, Any, Optional, Union


class KrsAPI:
    """
    Client for the Polish National Court Register (KRS) API.
    """

    def __init__(self, base_url: str = "https://prs.ms.gov.pl/krs/openApi"):
        """
        Initialize the KRS API client.

        Args:
            base_url: The base URL for the KRS API.
        """
        self.base_url = base_url
        self.session = requests.Session()
        # Add appropriate headers for API requests
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def _make_request(self, endpoint: str, method: str = "GET", params: Optional[Dict] = None, 
                      data: Optional[Dict] = None) -> Dict:
        """
        Make a request to the KRS API.

        Args:
            endpoint: The API endpoint to request.
            method: The HTTP method to use.
            params: Query parameters to include in the request.
            data: JSON data to include in the request body.

        Returns:
            The response data as a dictionary.

        Raises:
            requests.exceptions.RequestException: If the request fails.
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params)
            elif method == "POST":
                response = self.session.post(url, params=params, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def search_entity(self, 
                     krs_number: Optional[str] = None,
                     nip: Optional[str] = None,
                     regon: Optional[str] = None,
                     name: Optional[str] = None) -> Dict:
        """
        Search for entities in the KRS.

        Args:
            krs_number: KRS number of the entity.
            nip: NIP (tax identification number) of the entity.
            regon: REGON (statistical number) of the entity.
            name: Name of the entity.

        Returns:
            Search results as a dictionary.
        """
        params = {}
        if krs_number:
            params["krs"] = krs_number
        if nip:
            params["nip"] = nip
        if regon:
            params["regon"] = regon
        if name:
            params["nazwa"] = name
            
        return self._make_request("podmiot/szukaj", params=params)

    def get_entity_details(self, krs_number: str) -> Dict:
        """
        Get detailed information about an entity.

        Args:
            krs_number: KRS number of the entity.

        Returns:
            Entity details as a dictionary.
        """
        return self._make_request(f"podmiot/{krs_number}")

    def get_entity_section(self, krs_number: str, section_number: int) -> Dict:
        """
        Get information from a specific section of an entity's extract.

        Args:
            krs_number: KRS number of the entity.
            section_number: Section number (1-6).

        Returns:
            Section data as a dictionary.
        """
        if section_number not in range(1, 7):
            raise ValueError("Section number must be between 1 and 6")
            
        return self._make_request(f"podmiot/{krs_number}/dzial/{section_number}")

    def get_entity_representatives(self, krs_number: str) -> Dict:
        """
        Get information about representatives of an entity.

        Args:
            krs_number: KRS number of the entity.

        Returns:
            Representatives data as a dictionary.
        """
        return self._make_request(f"podmiot/{krs_number}/reprezentanci")

    def get_entity_shareholders(self, krs_number: str) -> Dict:
        """
        Get information about shareholders of an entity.

        Args:
            krs_number: KRS number of the entity.

        Returns:
            Shareholders data as a dictionary.
        """
        return self._make_request(f"podmiot/{krs_number}/wspolnicy")

    def get_beneficial_owners(self, krs_number: str) -> Dict:
        """
        Get information about beneficial owners of an entity.

        Args:
            krs_number: KRS number of the entity.

        Returns:
            Beneficial owners data as a dictionary.
        """
        return self._make_request(f"podmiot/{krs_number}/beneficjenci")


if __name__ == "__main__":
    # Example usage
    api = KrsAPI()
    
    try:
        # Search for an entity
        search_results = api.search_entity(name="Example Company")
        print(f"Search results: {json.dumps(search_results, indent=2, ensure_ascii=False)}")
        
        # If results found, get details for the first one
        if search_results.get("wyniki") and len(search_results["wyniki"]) > 0:
            first_result = search_results["wyniki"][0]
            krs_number = first_result.get("krs")
            
            if krs_number:
                # Get detailed information
                details = api.get_entity_details(krs_number)
                print(f"Entity details: {json.dumps(details, indent=2, ensure_ascii=False)}")
                
                # Get representatives
                representatives = api.get_entity_representatives(krs_number)
                print(f"Representatives: {json.dumps(representatives, indent=2, ensure_ascii=False)}")
    
    except Exception as e:
        print(f"An error occurred: {e}")