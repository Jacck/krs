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