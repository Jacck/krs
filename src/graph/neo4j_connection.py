#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Neo4j Connection Module

This module provides connection functionality to the Neo4j graph database.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from neo4j import GraphDatabase
from dotenv import load_dotenv


class Neo4jConnection:
    """
    Connection handler for Neo4j database.
    
    This class manages the connection to the Neo4j database and provides
    methods for executing queries and transactions.
    """

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, 
                 password: Optional[str] = None, database: Optional[str] = None):
        """
        Initialize the Neo4j connection.
        
        If connection parameters are not provided, they will be loaded from environment variables.
        
        Args:
            uri: The Neo4j server URI (e.g., bolt://localhost:7687)
            user: The Neo4j username
            password: The Neo4j password
            database: The Neo4j database name
        """
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Use provided parameters or load from environment
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "")
        self.database = database or os.getenv("NEO4J_DATABASE", "krsgraph")
        
        # Additional connection settings
        self.max_connection_lifetime = int(os.getenv("NEO4J_MAX_CONNECTION_LIFETIME", 3600))
        self.max_connection_pool_size = int(os.getenv("NEO4J_MAX_CONNECTION_POOL_SIZE", 50))
        self.connection_timeout = int(os.getenv("NEO4J_CONNECTION_TIMEOUT", 30))
        
        # Set up logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize connection
        self.driver = None
        self.connect()

    def connect(self) -> None:
        """
        Establish a connection to the Neo4j database.
        """
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=self.max_connection_lifetime,
                max_connection_pool_size=self.max_connection_pool_size,
                connection_timeout=self.connection_timeout
            )
            self.logger.info(f"Connected to Neo4j database: {self.database} at {self.uri}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self) -> None:
        """
        Close the Neo4j database connection.
        """
        if self.driver:
            self.driver.close()
            self.driver = None
            self.logger.info("Neo4j connection closed")

    def verify_connectivity(self) -> bool:
        """
        Verify the connection to the Neo4j database.
        
        Returns:
            True if the connection is established, False otherwise.
        """
        try:
            # Always use the specified database for this check
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 AS test")
                return result.single()["test"] == 1
        except Exception as e:
            self.logger.error(f"Connection verification failed: {e}")
            return False

    def query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a Cypher query and return the results.
        
        Args:
            query: The Cypher query to execute
            parameters: Query parameters
            
        Returns:
            A list of records as dictionaries
        """
        if not self.driver:
            self.connect()
            
        try:
            # Always use the specified database for queries
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters)
                return [record.data() for record in result]
        except Exception as e:
            self.logger.error(f"Query execution failed: {query}, error: {e}")
            raise

    def execute_write_transaction(self, tx_function, *args, **kwargs):
        """
        Execute a write transaction.
        
        Args:
            tx_function: A function that takes a transaction as its first argument
            *args: Additional arguments to pass to the transaction function
            **kwargs: Additional keyword arguments to pass to the transaction function
            
        Returns:
            The result of the transaction function
        """
        if not self.driver:
            self.connect()
            
        # Always use the specified database for transactions
        with self.driver.session(database=self.database) as session:
            return session.write_transaction(tx_function, *args, **kwargs)

    def execute_read_transaction(self, tx_function, *args, **kwargs):
        """
        Execute a read transaction.
        
        Args:
            tx_function: A function that takes a transaction as its first argument
            *args: Additional arguments to pass to the transaction function
            **kwargs: Additional keyword arguments to pass to the transaction function
            
        Returns:
            The result of the transaction function
        """
        if not self.driver:
            self.connect()
            
        # Always use the specified database for transactions
        with self.driver.session(database=self.database) as session:
            return session.read_transaction(tx_function, *args, **kwargs)


# Create a singleton instance for global use
_neo4j_instance = None

def get_neo4j_connection() -> Neo4jConnection:
    """
    Get a singleton instance of the Neo4j connection.
    
    Returns:
        A Neo4jConnection instance
    """
    global _neo4j_instance
    if _neo4j_instance is None:
        _neo4j_instance = Neo4jConnection()
    return _neo4j_instance