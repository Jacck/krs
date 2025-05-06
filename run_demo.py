#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KRS API Demo

This script provides a demo of the KRS API client functionality.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

# Import required modules
from src.krs_api import KrsAPI
from src.mock.krs_mock_api import KrsMockAPI
from src.krs_export import KrsExporter


def main():
    """Main function to run the demo."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="KRS API Demo"
    )
    parser.add_argument(
        "--mock", 
        action="store_true",
        help="Use mock API instead of real API"
    )
    parser.add_argument(
        "--krs", 
        type=str, 
        default="0000010078",
        help="KRS number to query (default: 0000010078 - Cyfrowy Polsat)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="output",
        help="Directory for output files (default: 'output')"
    )
    args = parser.parse_args()
    
    # Create the KRS API client
    print(f"\nInitializing {'Mock ' if args.mock else ''}KRS API client...")
    api = KrsMockAPI() if args.mock else KrsAPI()
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Search for entity by KRS number
        print(f"\nSearching for entity with KRS number: {args.krs}")
        search_results = api.search_entity(krs_number=args.krs)
        print(f"Found {search_results.get('liczbaWynikow', 0)} results")
        
        # Export search results to JSON
        search_output_path = os.path.join(args.output_dir, f"{args.krs}_search.json")
        KrsExporter.export_json(search_results, search_output_path)
        print(f"Search results exported to {search_output_path}")
        
        # Get entity details
        print(f"\nGetting details for entity with KRS number: {args.krs}")
        entity_data = api.get_entity_details(args.krs)
        print(f"Entity name: {entity_data.get('nazwa')}")
        
        # Export entity details
        output_files = KrsExporter.export_entity_summary(entity_data, args.output_dir, args.krs)
        print(f"Entity details exported to {', '.join(output_files.values())}")
        
        # Get representatives
        print(f"\nGetting representatives for entity with KRS number: {args.krs}")
        representatives = api.get_entity_representatives(args.krs)
        reps_list = representatives.get("reprezentanci", [])
        print(f"Found {len(reps_list)} representatives")
        
        # Export representatives
        rep_files = KrsExporter.export_representatives(representatives, args.output_dir, args.krs)
        print(f"Representatives exported to {', '.join(rep_files.values())}")
        
        # Get shareholders
        print(f"\nGetting shareholders for entity with KRS number: {args.krs}")
        shareholders = api.get_entity_shareholders(args.krs)
        shareholders_list = shareholders.get("wspolnicy", [])
        print(f"Found {len(shareholders_list)} shareholders")
        
        # Export shareholders
        shareholder_files = KrsExporter.export_shareholders(shareholders, args.output_dir, args.krs)
        print(f"Shareholders exported to {', '.join(shareholder_files.values())}")
        
        print("\nDemo completed successfully! Output files are in the '{args.output_dir}' directory.")
        print("\nYou can now examine the exported data or import it into Neo4j for relationship analysis.")
        print("\nTo import the data into Neo4j, use the following commands:")
        print(f"  python run_neo4j_demo.py")
        print(f"  python examples/cyfrowy_polsat_neo4j.py")
        
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
