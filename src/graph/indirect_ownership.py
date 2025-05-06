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