#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Mock API

This module contains tests for the KRS Mock API client.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the path
current_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(current_dir))

# Import the KRS Mock API client
from src.mock.krs_mock_api import KrsMockAPI


class TestKrsMockAPI(unittest.TestCase):
    """Tests for the KRS Mock API client."""
    
    def setUp(self):
        """Set up the test case."""
        self.api = KrsMockAPI()
    
    def test_search_by_krs(self):
        """Test searching by KRS number."""
        # Search for Cyfrowy Polsat by KRS number
        results = self.api.search_entity(krs_number="0000010078")
        
        # Check the results
        self.assertIsNotNone(results)
        self.assertIn("wyniki", results)
        self.assertIn("liczbaWynikow", results)
        self.assertEqual(results["liczbaWynikow"], 1)
        
        # Check the first result
        first_result = results["wyniki"][0]
        self.assertEqual(first_result["krs"], "0000010078")
        self.assertEqual(first_result["nazwa"], "CYFROWY POLSAT SPƒÇ‚ÄúƒπÌ≤ÅKA AKCYJNA")
        self.assertEqual(first_result["nip"], "7961810732")
        self.assertEqual(first_result["regon"], "670925160")
    
    def test_search_by_name(self):
        """Test searching by name."""
        # Search for Cyfrowy Polsat by name
        results = self.api.search_entity(name="Cyfrowy Polsat")
        
        # Check the results
        self.assertIsNotNone(results)
        self.assertIn("wyniki", results)
        self.assertIn("liczbaWynikow", results)
        self.assertEqual(results["liczbaWynikow"], 1)
        
        # Check the first result
        first_result = results["wyniki"][0]
        self.assertEqual(first_result["krs"], "0000010078")
    
    def test_empty_search(self):
        """Test empty search results."""
        # Search with no parameters
        results = self.api.search_entity()
        
        # Check the results
        self.assertIsNotNone(results)
        self.assertIn("wyniki", results)
        self.assertIn("liczbaWynikow", results)
        self.assertEqual(results["liczbaWynikow"], 0)
        self.assertEqual(len(results["wyniki"]), 0)
    
    def test_get_entity_details(self):
        """Test getting entity details."""
        # Get entity details for Cyfrowy Polsat
        details = self.api.get_entity_details("0000010078")
        
        # Check the details
        self.assertIsNotNone(details)
        self.assertEqual(details["krs"], "0000010078")
        self.assertEqual(details["nazwa"], "CYFROWY POLSAT SPƒÇ‚ÄúƒπÌ≤ÅKA AKCYJNA")
        self.assertEqual(details["nip"], "7961810732")
        self.assertEqual(details["regon"], "670925160")
    
    def test_get_representatives(self):
        """Test getting representatives."""
        # Get representatives for Cyfrowy Polsat
        representatives = self.api.get_entity_representatives("0000010078")
        
        # Check the representatives
        self.assertIsNotNone(representatives)
        self.assertIn("reprezentanci", representatives)
        self.assertEqual(len(representatives["reprezentanci"]), 3)
    
    def test_get_shareholders(self):
        """Test getting shareholders."""
        # Get shareholders for Cyfrowy Polsat
        shareholders = self.api.get_entity_shareholders("0000010078")
        
        # Check the shareholders
        self.assertIsNotNone(shareholders)
        self.assertIn("wspolnicy", shareholders)
        self.assertEqual(len(shareholders["wspolnicy"]), 4)
        
        # Check the first shareholder
        first_shareholder = shareholders["wspolnicy"][0]
        self.assertEqual(first_shareholder["nazwa"], "TIVI FOUNDATION")
        self.assertEqual(first_shareholder["typ"], "corporate")
        self.assertEqual(first_shareholder["udzialy"], "57.66%")
    
    def test_custom_responses(self):
        """Test adding custom responses."""
        # Create a mock API instance with custom responses
        custom_api = KrsMockAPI({
            "custom:test": {
                "message": "This is a custom response"
            }
        })
        
        # Add another custom response
        custom_api.add_mock_response("another:test", {
            "message": "This is another custom response"
        })
        
        # Test the custom responses
        self.assertEqual(
            custom_api._make_request("custom:test")["message"],
            "This is a custom response"
        )
        self.assertEqual(
            custom_api._make_request("another:test")["message"],
            "This is another custom response"
        )


if __name__ == "__main__":
    unittest.main()
