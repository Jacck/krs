#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Search Company Example

This example demonstrates how to search for companies using the KRS API.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add the src directory to the path
current_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(current_dir))

# Import the KRS API client
from src.krs_api import KrsAPI


def main():
    """Main function to run the example."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Search for companies using the KRS API"
    )
    parser.add_argument(
        "--krs", 
        type=str, 
        help="KRS number"
    )
    parser.add_argument(
        "--nip", 
        type=str, 
        help="NIP number"
    )
    parser.add_argument(
        "--regon", 
        type=str, 
        help="REGON number"
    )
    parser.add_argument(
        "--name", 
        type=str, 
        help="Company name"
    )
    args = parser.parse_args()
    
    # Check if at least one search parameter was provided
    if not any([args.krs, args.nip, args.regon, args.name]):
        print("Error: At least one search parameter (--krs, --nip, --regon, --name) must be provided")
        parser.print_help()
        return
    
    # Create the KRS API client
    api = KrsAPI()
    
    try:
        # Search for the company
        print("\nSearching for company...")
        search_results = api.search_entity(
            krs_number=args.krs,
            nip=args.nip,
            regon=args.regon,
            name=args.name
        )
        
        # Print the results
        result_count = search_results.get("liczbaWynikow", 0)
        print(f"Found {result_count} results")
        
        if result_count > 0:
            for i, result in enumerate(search_results.get("wyniki", [])):
                print(f"\nResult {i+1}:")
                print(f"KRS: {result.get('krs')}")
                print(f"Name: {result.get('nazwa')}")
                print(f"NIP: {result.get('nip')}")
                print(f"REGON: {result.get('regon')}")
                print(f"Status: {result.get('status')}")
                print(f"Address: {result.get('adres')}")
                
                # If the first result has a KRS number, get more details
                if i == 0 and result.get("krs"):
                    choice = input("\nDo you want to get more details about this company? (y/n): ")
                    if choice.lower() == "y":
                        print("\nGetting more details...")
                        krs = result.get("krs")
                        
                        # Get entity details
                        details = api.get_entity_details(krs)
                        print(f"\nDetails for {details.get('nazwa')}:")
                        print(json.dumps(details, indent=2, ensure_ascii=False))
                        
                        # Get representatives
                        choice = input("\nDo you want to get representatives? (y/n): ")
                        if choice.lower() == "y":
                            representatives = api.get_entity_representatives(krs)
                            reps_list = representatives.get("reprezentanci", [])
                            print(f"\nRepresentatives ({len(reps_list)}):")
                            for rep in reps_list:
                                print(f"- {rep.get('imie')} {rep.get('nazwisko')}, {rep.get('funkcja')}")
                        
                        # Get shareholders
                        choice = input("\nDo you want to get shareholders? (y/n): ")
                        if choice.lower() == "y":
                            shareholders = api.get_entity_shareholders(krs)
                            shareholders_list = shareholders.get("wspolnicy", [])
                            print(f"\nShareholders ({len(shareholders_list)}):")
                            for shareholder in shareholders_list:
                                print(f"- {shareholder.get('nazwa')}, {shareholder.get('udzialy')}")
        
        print("\nExample completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
