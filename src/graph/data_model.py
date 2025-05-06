#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Neo4j Data Model

This module defines the data model for the KRS graph database.
"""

# Node labels
class NodeLabels:
    COMPANY = "Company"
    PERSON = "Person"
    SHAREHOLDER = "Shareholder"

# Relationship types
class RelationshipTypes:
    MANAGES = "MANAGES"
    OWNS_SHARES_IN = "OWNS_SHARES_IN"
    SUBSIDIARY_OF = "SUBSIDIARY_OF"
    AFFILIATED_WITH = "AFFILIATED_WITH"

# Property keys for nodes
class NodeProperties:
    # Common properties
    ID = "id"
    NAME = "name"
    TYPE = "type"
    
    # Company properties
    KRS = "krs"
    NIP = "nip"
    REGON = "regon"
    ADDRESS = "address"
    STATUS = "status"
    REGISTRATION_DATE = "registration_date"
    LEGAL_FORM = "legal_form"
    
    # Person properties
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    ROLE = "role"
    
    # Shareholder properties
    SHAREHOLDER_TYPE = "shareholder_type"  # Individual, Company, Organization

# Property keys for relationships
class RelationshipProperties:
    # MANAGES relationship properties
    ROLE = "role"
    START_DATE = "start_date"
    END_DATE = "end_date"
    
    # OWNS_SHARES_IN relationship properties
    PERCENTAGE = "percentage"
    VALUE = "value"
    
    # SUBSIDIARY_OF relationship properties
    RELATIONSHIP_TYPE = "relationship_type"
    
    # Common properties
    UPDATED_AT = "updated_at"
    SOURCE = "source"

# Entity types
class EntityTypes:
    COMPANY = "company"
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"

# Constraint and index queries
class DatabaseSchema:
    # Node constraints
    CONSTRAINTS = [
        f"CREATE CONSTRAINT company_krs IF NOT EXISTS FOR (c:{NodeLabels.COMPANY}) REQUIRE c.{NodeProperties.KRS} IS UNIQUE",
        f"CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:{NodeLabels.PERSON}) REQUIRE p.{NodeProperties.ID} IS UNIQUE",
        f"CREATE CONSTRAINT shareholder_id IF NOT EXISTS FOR (s:{NodeLabels.SHAREHOLDER}) REQUIRE s.{NodeProperties.ID} IS UNIQUE"
    ]
    
    # Indexes
    INDEXES = [
        f"CREATE INDEX company_nip IF NOT EXISTS FOR (c:{NodeLabels.COMPANY}) ON (c.{NodeProperties.NIP})",
        f"CREATE INDEX company_regon IF NOT EXISTS FOR (c:{NodeLabels.COMPANY}) ON (c.{NodeProperties.REGON})",
        f"CREATE INDEX company_name IF NOT EXISTS FOR (c:{NodeLabels.COMPANY}) ON (c.{NodeProperties.NAME})",
        f"CREATE INDEX person_name IF NOT EXISTS FOR (p:{NodeLabels.PERSON}) ON (p.{NodeProperties.LAST_NAME}, p.{NodeProperties.FIRST_NAME})",
        f"CREATE INDEX shareholder_name IF NOT EXISTS FOR (s:{NodeLabels.SHAREHOLDER}) ON (s.{NodeProperties.NAME})"
    ]
    
    @staticmethod
    def create_constraints_and_indexes(neo4j_connection):
        """
        Create constraints and indexes in the Neo4j database.
        
        Args:
            neo4j_connection: A Neo4jConnection instance
        """
        for constraint in DatabaseSchema.CONSTRAINTS:
            neo4j_connection.query(constraint)
        
        for index in DatabaseSchema.INDEXES:
            neo4j_connection.query(index)