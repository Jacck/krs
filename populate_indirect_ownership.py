#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Indirect Ownership Population Script

This script populates indirect ownership relationships in the Neo4j database.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir / "src"))

# Import required modules
from graph.neo4j_connection import Neo4jConnection
from graph.indirect_ownership import IndirectOwnershipDiscovery

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('multi_level_analysis.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to execute the indirect ownership discovery process."""
    # Load environment variables
    load_dotenv()
    
    # Create Neo4j connection
    neo4j = Neo4jConnection()
    
    try:
        # Create the discovery service
        discovery_service = IndirectOwnershipDiscovery(neo4j)
        
        # First, create synthetic test data for demonstration
        logger.info("Creating synthetic test data...")
        test_stats = discovery_service.create_synthetic_test_data()
        
        print(f"\nCreated synthetic test data:")
        print(f"* {test_stats['companies_created']} companies")
        print(f"* {test_stats['shareholders_created']} shareholders")
        print(f"* {test_stats['relationships_created']} ownership relationships")
        
        # Now discover indirect relationships
        print("\nDiscovering indirect ownership relationships...")
        
        # List of companies to analyze (can be extended)
        companies_to_analyze = [
            "TEST001",  # Test company from synthetic data
            "0000010078"  # Cyfrowy Polsat if it exists
        ]
        
        total_relationships = 0
        
        # Process each company
        for krs in companies_to_analyze:
            print(f"\nAnalyzing company with KRS: {krs}")
            
            try:
                # Discover indirect relationships for this company
                stats = discovery_service.discover_indirect_relationships(krs, max_depth=3)
                
                # Print statistics
                print(f"* Created {stats['upstream_relationships']} upstream indirect relationships")
                print(f"* Created {stats['downstream_relationships']} downstream indirect relationships")
                print(f"* Total: {stats['total_relationships']} indirect relationships")
                
                total_relationships += stats['total_relationships']
                
            except Exception as e:
                logger.error(f"Error processing company {krs}: {e}")
        
        print(f"\nProcess completed! Created a total of {total_relationships} indirect ownership relationships.")
        print("\nYou can now visualize the multi-level ownership network in Neo4j Browser.")
        print("\nRecommended visualization query:")
        print("""
        // Multi-level Ownership Network
        MATCH path = (entity)-[:OWNS_SHARES_IN|INDIRECT_OWNER_OF|CONTROLS_INDIRECTLY*1..3]-(company:Company {krs: "0000010078"})
        RETURN path
        """)
        
    except Exception as e:
        logger.error(f"Error in indirect ownership discovery process: {e}")
    finally:
        # Close the Neo4j connection
        neo4j.close()

if __name__ == "__main__":
    main()