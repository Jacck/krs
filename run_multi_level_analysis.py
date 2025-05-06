#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-level Ownership Analysis Script

This script analyzes multi-level ownership structures by discovering and analyzing
indirect ownership relationships using the Neo4j graph database.
"""

import os
import sys
import time
import logging
import argparse
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
        logging.FileHandler('multi_level_demo.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to execute the multi-level ownership analysis."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Analyze multi-level ownership structures"
    )
    parser.add_argument(
        "--krs", 
        type=str, 
        default="0000010078",
        help="KRS number of the company to analyze (default: 0000010078 - Cyfrowy Polsat)"
    )
    parser.add_argument(
        "--depth", 
        type=int, 
        default=3,
        help="Maximum depth for ownership analysis (default: 3)"
    )
    parser.add_argument(
        "--synthetic", 
        action="store_true",
        help="Create synthetic test data before analysis"
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()
    
    # Create Neo4j connection
    neo4j = Neo4jConnection()
    
    try:
        # Verify Neo4j connectivity
        if not neo4j.verify_connectivity():
            print("\nError: Could not connect to Neo4j database. Please check your connection settings.")
            return
            
        print(f"\nConnected to Neo4j database at {neo4j.uri}")
        
        # Create the discovery service
        discovery_service = IndirectOwnershipDiscovery(neo4j)
        
        # Create synthetic test data if requested
        if args.synthetic:
            print("\nCreating synthetic test data for demonstration...")
            stats = discovery_service.create_synthetic_test_data()
            print(f"Created {stats['companies_created']} companies, {stats['shareholders_created']} shareholders, "
                  f"and {stats['relationships_created']} relationships")
        
        # Discover indirect relationships
        print(f"\nAnalyzing multi-level ownership for company with KRS: {args.krs} (depth: {args.depth})")
        start_time = time.time()
        
        # Execute discovery
        stats = discovery_service.discover_indirect_relationships(args.krs, args.depth)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Print results
        print(f"\nAnalysis completed in {execution_time:.2f} seconds!")
        print(f"\nResults:")
        print(f"* Created {stats['upstream_relationships']} upstream indirect ownership relationships")
        print(f"* Created {stats['downstream_relationships']} downstream indirect ownership relationships")
        print(f"* Total: {stats['total_relationships']} indirect ownership relationships")
        print(f"* Linked {stats['companies_linked']} companies and {stats['shareholders_linked']} shareholders")
        
        # Print example Cypher queries
        print("\nYou can now explore the multi-level ownership network in Neo4j Browser.")
        print("\nExample Cypher queries:")
        print("""
        // View all indirect ownership relationships for the company
        MATCH (entity)-[r:INDIRECT_OWNER_OF]->(company:Company {krs: "%s"})
        RETURN entity.name AS Owner, company.name AS Company, r.percentage AS Percentage
        ORDER BY r.percentage DESC
        
        // View multi-level ownership paths
        MATCH path = (entity)-[:OWNS_SHARES_IN|INDIRECT_OWNER_OF*1..%d]-(company:Company {krs: "%s"})
        RETURN path
        
        // Find ultimate beneficial owners (individuals who indirectly control the company)
        MATCH (person:Shareholder {shareholder_type: 'individual'})-[r:INDIRECT_OWNER_OF]->(company:Company {krs: "%s"})
        RETURN person.name AS UltimateOwner, r.percentage AS EffectiveControl
        ORDER BY r.percentage DESC
        """ % (args.krs, args.depth, args.krs, args.krs))
        
    except Exception as e:
        logger.error(f"Error in multi-level ownership analysis: {e}")
        print(f"\nError: {e}")
    finally:
        # Close the Neo4j connection
        neo4j.close()

if __name__ == "__main__":
    main()