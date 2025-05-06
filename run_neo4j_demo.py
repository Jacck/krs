#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Neo4j Demo Script

This script demonstrates the Neo4j integration capabilities of the KRS API project.
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
from src.graph.neo4j_connection import Neo4jConnection
from src.graph.data_model import DatabaseSchema

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('neo4j_demo.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to execute the Neo4j demo."""
    # Load environment variables
    load_dotenv()
    
    # Create Neo4j connection
    neo4j = Neo4jConnection()
    
    try:
        # Test connection
        if neo4j.verify_connectivity():
            print(f"\nSuccessfully connected to Neo4j database at {neo4j.uri}")
        else:
            print("\nFailed to connect to Neo4j database. Please check your connection settings.")
            return
            
        # Create schema (constraints and indexes)
        print("\nCreating database schema (constraints and indexes)...")
        DatabaseSchema.create_constraints_and_indexes(neo4j)
        print("Schema created successfully!")
        
        # Run a simple query to demonstrate functionality
        print("\nRunning a test query...")
        result = neo4j.query("MATCH (n) RETURN count(n) AS node_count")
        node_count = result[0]["node_count"] if result else 0
        print(f"Node count in database: {node_count}")
        
        # Show available node labels
        print("\nAvailable node labels:")
        labels_result = neo4j.query("CALL db.labels() YIELD label RETURN label ORDER BY label")
        if labels_result:
            for item in labels_result:
                print(f"- {item['label']}")
        else:
            print("No labels found")
            
        # Show available relationship types
        print("\nAvailable relationship types:")
        rel_result = neo4j.query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType ORDER BY relationshipType")
        if rel_result:
            for item in rel_result:
                print(f"- {item['relationshipType']}")
        else:
            print("No relationship types found")
        
        print("\nDemo completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in Neo4j demo: {e}")
        print(f"\nError: {e}")
    finally:
        # Close the Neo4j connection
        neo4j.close()

if __name__ == "__main__":
    main()