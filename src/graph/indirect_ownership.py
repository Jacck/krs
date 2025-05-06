#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Indirect Ownership Discovery

This module provides functionality for discovering and importing indirect ownership
relationships into Neo4j.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Set
from .neo4j_connection import Neo4jConnection
from .data_model import (
    NodeLabels, RelationshipTypes, 
    NodeProperties, RelationshipProperties
)


class IndirectOwnershipDiscovery:
    """
    Service for discovering and importing indirect ownership relationships.
    """

    def __init__(self, neo4j_connection: Neo4jConnection):
        """
        Initialize the Indirect Ownership Discovery service.
        
        Args:
            neo4j_connection: A Neo4jConnection instance
        """
        self.neo4j = neo4j_connection
        self.logger = logging.getLogger(__name__)
        
    def discover_indirect_relationships(self, seed_krs: str, max_depth: int = 3) -> Dict:
        """
        Discover indirect ownership relationships starting from a seed company.
        
        This function analyzes the graph to find extended ownership relationships up to
        a specified depth. It can identify both upstream (owners of owners) and 
        downstream (subsidiaries of subsidiaries) relationships.
        
        Args:
            seed_krs: The KRS number of the seed company
            max_depth: Maximum depth for relationship discovery (default: 3)
            
        Returns:
            Statistics about the discovered relationships
        """
        stats = {
            "upstream_relationships": 0,
            "downstream_relationships": 0,
            "total_relationships": 0,
            "companies_linked": 0,
            "shareholders_linked": 0
        }
        
        # Discover upstream relationships (owners of owners)
        self.logger.info(f"Discovering upstream ownership relationships for KRS: {seed_krs}")
        upstream_stats = self._discover_upstream_relationships(seed_krs, max_depth)
        
        # Discover downstream relationships (subsidiaries of subsidiaries)
        self.logger.info(f"Discovering downstream ownership relationships for KRS: {seed_krs}")
        downstream_stats = self._discover_downstream_relationships(seed_krs, max_depth)
        
        # Combine statistics
        stats["upstream_relationships"] = upstream_stats["relationships_created"]
        stats["downstream_relationships"] = downstream_stats["relationships_created"]
        stats["total_relationships"] = upstream_stats["relationships_created"] + downstream_stats["relationships_created"]
        stats["companies_linked"] = upstream_stats["companies_linked"] + downstream_stats["companies_linked"]
        stats["shareholders_linked"] = upstream_stats["shareholders_linked"] + downstream_stats["shareholders_linked"]
        
        return stats
    
    def _discover_upstream_relationships(self, krs_number: str, max_depth: int) -> Dict:
        """
        Discover upstream ownership relationships (owners of owners).
        
        Args:
            krs_number: The KRS number of the company
            max_depth: Maximum depth for relationship discovery
            
        Returns:
            Statistics about the discovered relationships
        """
        stats = {
            "relationships_created": 0,
            "companies_linked": 0,
            "shareholders_linked": 0
        }
        
        # Query to find all ownership paths up to max_depth
        query = f"""
        // Find all ownership paths leading to the company up to depth {max_depth}
        MATCH path = (owner)-[r:{RelationshipTypes.OWNS_SHARES_IN}*2..{max_depth}]->(target:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: $krs}})
        
        // Extract nodes and relationships along the path
        WITH path, nodes(path) AS nodes, relationships(path) AS rels
        
        // Calculate the effective ownership percentage
        WITH 
            nodes[0] AS indirect_owner, 
            nodes[size(nodes)-1] AS company,
            reduce(s = 1.0, rel IN rels | 
                s * CASE WHEN rel.{NodeProperties.PERCENTAGE} IS NOT NULL 
                        THEN rel.{NodeProperties.PERCENTAGE} / 100 
                        ELSE 1 
                   END
            ) * 100 AS effective_percentage
        
        // Create indirect relationship (if it doesn't exist)
        MERGE (indirect_owner)-[r:INDIRECT_OWNER_OF]->(company)
        ON CREATE SET 
            r.{NodeProperties.PERCENTAGE} = effective_percentage,
            r.{NodeProperties.SOURCE} = 'derived',
            r.created_at = datetime()
        ON MATCH SET 
            r.{NodeProperties.PERCENTAGE} = effective_percentage,
            r.updated_at = datetime()
        
        // Return statistics
        RETURN 
            count(r) AS relationships_created,
            sum(CASE WHEN indirect_owner:{NodeLabels.COMPANY} THEN 1 ELSE 0 END) AS companies_linked,
            sum(CASE WHEN indirect_owner:{NodeLabels.SHAREHOLDER} THEN 1 ELSE 0 END) AS shareholders_linked
        """
        
        parameters = {"krs": krs_number}
        
        try:
            # Execute the query to create indirect relationships
            results = self.neo4j.query(query, parameters)
            
            if results and len(results) > 0:
                stats["relationships_created"] = results[0].get("relationships_created", 0)
                stats["companies_linked"] = results[0].get("companies_linked", 0)
                stats["shareholders_linked"] = results[0].get("shareholders_linked", 0)
                
                self.logger.info(f"Created {stats['relationships_created']} indirect upstream ownership relationships")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error discovering upstream relationships: {e}")
            return stats
    
    def _discover_downstream_relationships(self, krs_number: str, max_depth: int) -> Dict:
        """
        Discover downstream ownership relationships (subsidiaries of subsidiaries).
        
        Args:
            krs_number: The KRS number of the company
            max_depth: Maximum depth for relationship discovery
            
        Returns:
            Statistics about the discovered relationships
        """
        stats = {
            "relationships_created": 0,
            "companies_linked": 0,
            "shareholders_linked": 0
        }
        
        # Query to find all ownership paths up to max_depth in the downstream direction
        query = f"""
        // Find all ownership paths starting from the company up to depth {max_depth}
        MATCH path = (source:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: $krs}})-[r:{RelationshipTypes.OWNS_SHARES_IN}*2..{max_depth}]->(target)
        
        // Extract the nodes and relationships
        WITH path, nodes(path) AS nodes, relationships(path) AS rels
        
        // Calculate the effective ownership percentage
        WITH 
            nodes[0] AS company, 
            nodes[size(nodes)-1] AS indirect_subsidiary,
            reduce(s = 1.0, rel IN rels | 
                s * CASE WHEN rel.{NodeProperties.PERCENTAGE} IS NOT NULL 
                        THEN rel.{NodeProperties.PERCENTAGE} / 100 
                        ELSE 1 
                   END
            ) * 100 AS effective_percentage
        
        // Skip if there's already a direct relationship
        WHERE NOT (company)-[:{RelationshipTypes.OWNS_SHARES_IN}]->(indirect_subsidiary)
        
        // Create indirect relationship (if it doesn't exist)
        MERGE (company)-[r:CONTROLS_INDIRECTLY]->(indirect_subsidiary)
        ON CREATE SET 
            r.{NodeProperties.PERCENTAGE} = effective_percentage,
            r.{NodeProperties.SOURCE} = 'derived',
            r.created_at = datetime()
        ON MATCH SET 
            r.{NodeProperties.PERCENTAGE} = effective_percentage,
            r.updated_at = datetime()
        
        // Return statistics
        RETURN 
            count(r) AS relationships_created,
            sum(CASE WHEN indirect_subsidiary:{NodeLabels.COMPANY} THEN 1 ELSE 0 END) AS companies_linked,
            sum(CASE WHEN indirect_subsidiary:{NodeLabels.SHAREHOLDER} THEN 1 ELSE 0 END) AS shareholders_linked
        """
        
        parameters = {"krs": krs_number}
        
        try:
            # Execute the query to create indirect relationships
            results = self.neo4j.query(query, parameters)
            
            if results and len(results) > 0:
                stats["relationships_created"] = results[0].get("relationships_created", 0)
                stats["companies_linked"] = results[0].get("companies_linked", 0)
                stats["shareholders_linked"] = results[0].get("shareholders_linked", 0)
                
                self.logger.info(f"Created {stats['relationships_created']} indirect downstream ownership relationships")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error discovering downstream relationships: {e}")
            return stats

    def create_synthetic_test_data(self) -> Dict:
        """
        Create synthetic test data to demonstrate multi-level ownership relationships.
        
        This function creates a chain of companies and shareholders with ownership relationships
        to demonstrate the indirect ownership discovery functionality.
        
        Returns:
            Statistics about the created test data
        """
        stats = {
            "companies_created": 0,
            "shareholders_created": 0,
            "relationships_created": 0
        }
        
        # First cleanup any existing test data
        cleanup_query = """
        MATCH (n) 
        WHERE n.krs IN ["TEST001", "TEST002", "TEST003", "TEST004", "TEST005"] 
            OR n.id IN ["shareholder_test1", "shareholder_test2", "shareholder_test3"]
        DETACH DELETE n
        """
        
        try:
            self.neo4j.query(cleanup_query)
            self.logger.info("Cleaned up existing test data (if any)")
        except Exception as e:
            self.logger.warning(f"Cleanup step had an issue: {e}")
        
        # Create companies query
        companies_query = f"""
        CREATE (c1:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST001", {NodeProperties.NAME}: "Test Company 1", {NodeProperties.STATUS}: "Active"}})
        CREATE (c2:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST002", {NodeProperties.NAME}: "Test Company 2", {NodeProperties.STATUS}: "Active"}})
        CREATE (c3:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST003", {NodeProperties.NAME}: "Test Company 3", {NodeProperties.STATUS}: "Active"}})
        CREATE (c4:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST004", {NodeProperties.NAME}: "Test Company 4", {NodeProperties.STATUS}: "Active"}})
        CREATE (c5:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST005", {NodeProperties.NAME}: "Test Company 5", {NodeProperties.STATUS}: "Active"}})
        RETURN count(*) as companies_created
        """
        
        # Create shareholders query
        shareholders_query = f"""
        CREATE (s1:{NodeLabels.SHAREHOLDER} {{id: "shareholder_test1", {NodeProperties.NAME}: "Test Shareholder 1", {NodeProperties.SHAREHOLDER_TYPE}: "company"}})
        CREATE (s2:{NodeLabels.SHAREHOLDER} {{id: "shareholder_test2", {NodeProperties.NAME}: "Test Shareholder 2", {NodeProperties.SHAREHOLDER_TYPE}: "company"}})
        CREATE (s3:{NodeLabels.SHAREHOLDER} {{id: "shareholder_test3", {NodeProperties.NAME}: "Test Shareholder 3", {NodeProperties.SHAREHOLDER_TYPE}: "individual"}})
        RETURN count(*) as shareholders_created
        """
        
        # Create relationships query
        relationships_query = f"""
        MATCH (s1:{NodeLabels.SHAREHOLDER} {{id: "shareholder_test1"}})
        MATCH (s2:{NodeLabels.SHAREHOLDER} {{id: "shareholder_test2"}})
        MATCH (s3:{NodeLabels.SHAREHOLDER} {{id: "shareholder_test3"}})
        MATCH (c1:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST001"}})
        MATCH (c2:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST002"}})
        MATCH (c3:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST003"}})
        MATCH (c4:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST004"}})
        MATCH (c5:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST005"}})
        
        CREATE (s1)-[:{RelationshipTypes.OWNS_SHARES_IN} {{{NodeProperties.PERCENTAGE}: 75.0}}]->(c1)
        CREATE (s2)-[:{RelationshipTypes.OWNS_SHARES_IN} {{{NodeProperties.PERCENTAGE}: 60.0}}]->(s1)
        CREATE (s3)-[:{RelationshipTypes.OWNS_SHARES_IN} {{{NodeProperties.PERCENTAGE}: 80.0}}]->(s2)
        CREATE (c1)-[:{RelationshipTypes.OWNS_SHARES_IN} {{{NodeProperties.PERCENTAGE}: 51.0}}]->(c2)
        CREATE (c2)-[:{RelationshipTypes.OWNS_SHARES_IN} {{{NodeProperties.PERCENTAGE}: 70.0}}]->(c3)
        CREATE (c1)-[:{RelationshipTypes.OWNS_SHARES_IN} {{{NodeProperties.PERCENTAGE}: 30.0}}]->(c4)
        CREATE (c4)-[:{RelationshipTypes.OWNS_SHARES_IN} {{{NodeProperties.PERCENTAGE}: 25.0}}]->(c5)
        
        RETURN 7 as relationships_created
        """
        
        # Connect to Cyfrowy Polsat if it exists
        connect_query = f"""
        MATCH (c1:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "TEST001"}})
        MATCH (cp:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: "0000010078"}})
        CREATE (c1)-[:{RelationshipTypes.OWNS_SHARES_IN} {{{NodeProperties.PERCENTAGE}: 15.0}}]->(cp)
        RETURN count(*) as additional_relationships
        """
        
        try:
            # Execute the queries
            companies_result = self.neo4j.query(companies_query)
            if companies_result and len(companies_result) > 0:
                stats["companies_created"] = companies_result[0].get("companies_created", 0)
            
            shareholders_result = self.neo4j.query(shareholders_query)
            if shareholders_result and len(shareholders_result) > 0:
                stats["shareholders_created"] = shareholders_result[0].get("shareholders_created", 0)
            
            relationships_result = self.neo4j.query(relationships_query)
            if relationships_result and len(relationships_result) > 0:
                stats["relationships_created"] = relationships_result[0].get("relationships_created", 0)
            
            # Try to connect to Cyfrowy Polsat (ignore errors if it doesn't exist)
            try:
                connect_result = self.neo4j.query(connect_query)
                if connect_result and len(connect_result) > 0:
                    stats["relationships_created"] += connect_result[0].get("additional_relationships", 0)
            except Exception:
                pass
            
            self.logger.info(f"Created synthetic test data: {stats['companies_created']} companies, "
                             f"{stats['shareholders_created']} shareholders, "
                             f"{stats['relationships_created']} relationships")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error creating synthetic test data: {e}")
            return stats
