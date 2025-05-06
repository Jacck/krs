#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cyfrowy Polsat Example

This example demonstrates how to use the KRS API to retrieve data about Cyfrowy Polsat.
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to the path
current_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(current_dir))

# Import the KRS API client
from src.krs_api import KrsAPI
from src.krs_export import KrsExporter


def main():
    """Main function to run the example."""
    # Create the KRS API client
    api = KrsAPI()
    
    try:
        # Search for Cyfrowy Polsat by KRS number
        print("\nSearching for Cyfrowy Polsat by KRS number...")
        search_results = api.search_entity(krs_number="0000010078")
        print(f"Found {search_results.get('liczbaWynikow', 0)} results")
        
        # Get entity details
        print("\nGetting entity details...")
        entity_data = api.get_entity_details("0000010078")
        print(f"Entity name: {entity_data.get('nazwa')}")
        print(f"NIP: {entity_data.get('nip')}")
        print(f"REGON: {entity_data.get('regon')}")
        print(f"Address: {entity_data.get('adres')}")
        
        # Get representatives
        print("\nGetting representatives...")
        representatives = api.get_entity_representatives("0000010078")
        reps_list = representatives.get("reprezentanci", [])
        print(f"Found {len(reps_list)} representatives:")
        for rep in reps_list:
            print(f"- {rep.get('imie')} {rep.get('nazwisko')}, {rep.get('funkcja')}")
        
        # Get shareholders
        print("\nGetting shareholders...")
        shareholders = api.get_entity_shareholders("0000010078")
        shareholders_list = shareholders.get("wspolnicy", [])
        print(f"Found {len(shareholders_list)} shareholders:")
        for shareholder in shareholders_list:
            print(f"- {shareholder.get('nazwa')}, {shareholder.get('udzialy')}")
        
        # Export the data to files
        output_dir = os.path.join(current_dir, "output")
        print("\nExporting data to files...")
        
        # Export entity summary
        summary_files = KrsExporter.export_entity_summary(entity_data, output_dir, "0000010078")
        print(f"Entity summary exported to {', '.join(summary_files.values())}")
        
        # Export representatives
        rep_files = KrsExporter.export_representatives(representatives, output_dir, "0000010078")
        print(f"Representatives exported to {', '.join(rep_files.values())}")
        
        # Export shareholders
        shareholder_files = KrsExporter.export_shareholders(shareholders, output_dir, "0000010078")
        print(f"Shareholders exported to {', '.join(shareholder_files.values())}")
        
        print("\nExample completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
