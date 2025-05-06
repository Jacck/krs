#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Database Connection

This script tests the connection to the Neo4j database.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))

# Import Neo4j connection
from src.graph.neo4j_connection import Neo4jConnection


def main():
    """Test the Neo4j database connection."""
    # Load environment variables
    load_dotenv()
    
    # Print current Neo4j connection settings
    print("\nNeo4j Connection Settings:")
    print(f"URI: {os.getenv('NEO4J_URI', 'bolt://localhost:7687')}")
    print(f"User: {os.getenv('NEO4J_USER', 'neo4j')}")
    print(f"Database: {os.getenv('NEO4J_DATABASE', 'krsgraph')}")
    
    # Ask for confirmation
    print("\nAttempting to connect to Neo4j database...")
    
    try:
        # Create connection
        neo4j = Neo4jConnection()
        
        # Test connection
        if neo4j.verify_connectivity():
            print("\nConnection successful! The Neo4j database is accessible.")
            
            # Run a simple query
            result = neo4j.query("RETURN 1 + 1 AS sum")
            print(f"\nTest query result: {result[0]['sum']}")
            
            # Get database info
            db_info = neo4j.query("CALL dbms.components() YIELD name, versions RETURN name, versions")
            print(f"\nDatabase Info: {db_info[0]['name']} {db_info[0]['versions']}")
        else:
            print("\nConnection failed! Please check your Neo4j connection settings.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Close connection
        if 'neo4j' in locals():
            neo4j.close()
            print("\nNeo4j connection closed.")


if __name__ == "__main__":
    main()
