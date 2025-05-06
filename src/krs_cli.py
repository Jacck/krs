#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KRS Command Line Interface

This module provides a command-line interface for the KRS API client.
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to the path
current_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(current_dir))

# Import other modules
from src.krs_api import KrsAPI


def main():
    """Main function to run the command-line interface."""
    # Load environment variables
    load_dotenv()
    
    # Create the argument parser
    parser = argparse.ArgumentParser(
        description="KRS API Client - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for an entity")
    search_parser.add_argument("--krs", type=str, help="KRS number")
    search_parser.add_argument("--nip", type=str, help="NIP number")
    search_parser.add_argument("--regon", type=str, help="REGON number")
    search_parser.add_argument("--name", type=str, help="Entity name")
    search_parser.add_argument("--output", type=str, help="Output file path (JSON)")
    
    # Details command
    details_parser = subparsers.add_parser("details", help="Get entity details")
    details_parser.add_argument("--krs", type=str, required=True, help="KRS number")
    details_parser.add_argument("--output", type=str, help="Output file path (JSON)")
    
    # Representatives command
    reps_parser = subparsers.add_parser("representatives", help="Get entity representatives")
    reps_parser.add_argument("--krs", type=str, required=True, help="KRS number")
    reps_parser.add_argument("--output", type=str, help="Output file path (JSON)")
    
    # Shareholders command
    shareholders_parser = subparsers.add_parser("shareholders", help="Get entity shareholders")
    shareholders_parser.add_argument("--krs", type=str, required=True, help="KRS number")
    shareholders_parser.add_argument("--output", type=str, help="Output file path (JSON)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if a command was specified
    if args.command is None:
        parser.print_help()
        return
    
    # Initialize the KRS API client
    api = KrsAPI()
    
    try:
        # Execute the appropriate command
        if args.command == "search":
            handle_search_command(api, args)
        elif args.command == "details":
            handle_details_command(api, args)
        elif args.command == "representatives":
            handle_representatives_command(api, args)
        elif args.command == "shareholders":
            handle_shareholders_command(api, args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def handle_search_command(api: KrsAPI, args) -> None:
    """Handle the search command."""
    # Validate that at least one search parameter was provided
    if not any([args.krs, args.nip, args.regon, args.name]):
        print("Error: At least one search parameter (--krs, --nip, --regon, --name) must be provided")
        sys.exit(1)
    
    # Execute the search
    results = api.search_entity(
        krs_number=args.krs,
        nip=args.nip,
        regon=args.regon,
        name=args.name
    )
    
    # Output the results
    handle_output(results, args.output)


def handle_details_command(api: KrsAPI, args) -> None:
    """Handle the details command."""
    # Get entity details
    details = api.get_entity_details(args.krs)
    
    # Output the results
    handle_output(details, args.output)


def handle_representatives_command(api: KrsAPI, args) -> None:
    """Handle the representatives command."""
    # Get entity representatives
    representatives = api.get_entity_representatives(args.krs)
    
    # Output the results
    handle_output(representatives, args.output)


def handle_shareholders_command(api: KrsAPI, args) -> None:
    """Handle the shareholders command."""
    # Get entity shareholders
    shareholders = api.get_entity_shareholders(args.krs)
    
    # Output the results
    handle_output(shareholders, args.output)


def handle_output(data: Dict, output_path: Optional[str] = None) -> None:
    """Handle the output of data."""
    # Format the data as JSON
    formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
    
    # Output to file if specified, otherwise print to console
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_data)
        print(f"Output written to {output_path}")
    else:
        print(formatted_data)


if __name__ == "__main__":
    main()
