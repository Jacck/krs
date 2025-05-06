#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run Multi-level Visualization Demo

This script runs the multi-level ownership visualization demo with sample data.
"""

import os
import sys
import logging
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

# Import required modules
from graph.neo4j_connection import Neo4jConnection
from graph.indirect_ownership import IndirectOwnershipDiscovery
from visualize_multi_level_ownership import discover_indirect_relationships, analyze_ownership_structure, generate_ownership_network_visualization


def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('multi_level_demo.log')
        ]
    )


def prepare_test_data():
    """
    Prepare test data by ensuring synthetic test relationships exist.
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("\n" + "=" * 80)
    print(" Preparing Test Data ".center(80, "="))
    print("=" * 80)
    
    neo4j = Neo4jConnection()
    
    try:
        # Check if we have synthetic test data
        discovery_service = IndirectOwnershipDiscovery(neo4j)
        
        # Create synthetic test data
        print("\nCreating synthetic test data to demonstrate multi-level relationships...")
        stats = discovery_service.create_synthetic_test_data()
        
        print(f"Created test data: {stats['companies_created']} companies, "
              f"{stats['shareholders_created']} shareholders, "
              f"{stats['relationships_created']} direct relationships")
        
        return True
    except Exception as e:
        print(f"Error preparing test data: {e}")
        return False
    finally:
        neo4j.close()


def run_cyfrowy_polsat_demo():
    """
    Run a demo using Cyfrowy Polsat data.
    """
    print("\n" + "=" * 80)
    print(" Demo: Cyfrowy Polsat Multi-level Relationships ".center(80, "="))
    print("=" * 80)
    
    krs_number = "0000010078"  # Cyfrowy Polsat KRS
    max_depth = 3
    
    # Discover relationships
    discover_indirect_relationships(krs_number, max_depth)
    
    # Analyze ownership
    analyze_ownership_structure(krs_number, max_depth)
    
    # Generate visualization
    html_file = generate_ownership_network_visualization(krs_number, max_depth)
    
    # Show results
    if html_file:
        print(f"\nVisualization generated: {html_file}")
        print("Open this file in your browser to view the multi-level ownership network.")
        
        # Open the visualization in the default browser
        try:
            print("Opening visualization in default browser...")
            webbrowser.open(f"file://{os.path.abspath(html_file)}")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")


def run_test_data_demo():
    """
    Run a demo using synthetic test data.
    """
    print("\n" + "=" * 80)
    print(" Demo: Synthetic Test Data Multi-level Relationships ".center(80, "="))
    print("=" * 80)
    
    krs_number = "TEST001"  # Test company
    max_depth = 3
    
    # Discover relationships
    discover_indirect_relationships(krs_number, max_depth)
    
    # Analyze ownership
    analyze_ownership_structure(krs_number, max_depth)
    
    # Generate visualization
    html_file = generate_ownership_network_visualization(krs_number, max_depth)
    
    # Show results
    if html_file:
        print(f"\nVisualization generated: {html_file}")
        print("Open this file in your browser to view the multi-level ownership network.")
        
        # Open the visualization in the default browser
        try:
            print("Opening visualization in default browser...")
            webbrowser.open(f"file://{os.path.abspath(html_file)}")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")


def compare_different_depths():
    """
    Generate visualizations at different depths to compare.
    """
    print("\n" + "=" * 80)
    print(" Comparing Different Depth Levels ".center(80, "="))
    print("=" * 80)
    
    krs_number = "0000010078"  # Cyfrowy Polsat KRS
    
    # Generate visualizations at different depths
    html_files = []
    
    for depth in [1, 2, 3]:
        print(f"\nGenerating visualization at depth {depth}...")
        html_file = generate_ownership_network_visualization(krs_number, depth)
        if html_file:
            html_files.append((depth, html_file))
    
    # Show results
    if html_files:
        print("\nGenerations complete!")
        print("\nVisualization files generated:")
        for depth, file in html_files:
            print(f"  - Depth {depth}: {file}")
        
        print("\nOpen these files in your browser to compare the different depth visualizations.")


def main():
    """Main function to run the demo."""
    # Set up logging
    setup_logging()
    
    # Load environment variables
    load_dotenv()
    
    # Prepare test data
    if not prepare_test_data():
        print("Failed to prepare test data. Exiting.")
        return
    
    # Run demos
    print("\nChoose a demo to run:")
    print("1. Cyfrowy Polsat Demo (Real company data)")
    print("2. Synthetic Test Data Demo")
    print("3. Compare Different Depth Levels")
    print("4. Run All Demos")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == "1":
        run_cyfrowy_polsat_demo()
    elif choice == "2":
        run_test_data_demo()
    elif choice == "3":
        compare_different_depths()
    elif choice == "4":
        run_cyfrowy_polsat_demo()
        run_test_data_demo()
        compare_different_depths()
    else:
        print("Invalid choice. Exiting.")
        return
    
    print("\n" + "=" * 80)
    print(" Demo Completed ".center(80, "="))
    print("=" * 80)
    print("\nYou can view the generated HTML files in the 'output' directory.")


if __name__ == "__main__":
    main()