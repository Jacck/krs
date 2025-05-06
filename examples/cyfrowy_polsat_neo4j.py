#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cyfrowy Polsat Neo4j Example

This example demonstrates how to import Cyfrowy Polsat data into Neo4j.
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to the path
current_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(current_dir))

# Import required modules
from src.krs_api import KrsAPI
from src.graph.neo4j_connection import Neo4jConnection
from src.graph.data_model import DatabaseSchema, NodeLabels, RelationshipTypes, NodeProperties


def create_company_node(tx, krs, name, nip=None, regon=None, address=None, status=None):
    """Create a company node in Neo4j."""
    query = f"""
    MERGE (c:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: $krs}})
    ON CREATE SET 
        c.{NodeProperties.NAME} = $name,
        c.{NodeProperties.NIP} = $nip,
        c.{NodeProperties.REGON} = $regon,
        c.{NodeProperties.ADDRESS} = $address,
        c.{NodeProperties.STATUS} = $status,
        c.created_at = datetime()
    ON MATCH SET
        c.{NodeProperties.NAME} = $name,
        c.{NodeProperties.NIP} = $nip,
        c.{NodeProperties.REGON} = $regon,
        c.{NodeProperties.ADDRESS} = $address,
        c.{NodeProperties.STATUS} = $status,
        c.updated_at = datetime()
    RETURN c
    """
    
    result = tx.run(
        query,
        krs=krs,
        name=name,
        nip=nip,
        regon=regon,
        address=address,
        status=status
    )
    
    return result.single()["c"]


def create_person_node(tx, first_name, last_name):
    """Create a person node in Neo4j."""
    # Generate a unique ID for the person
    person_id = f"{first_name.lower()}_{last_name.lower()}"
    
    query = f"""
    MERGE (p:{NodeLabels.PERSON} {{{NodeProperties.ID}: $id}})
    ON CREATE SET 
        p.{NodeProperties.FIRST_NAME} = $first_name,
        p.{NodeProperties.LAST_NAME} = $last_name,
        p.created_at = datetime()
    ON MATCH SET
        p.{NodeProperties.FIRST_NAME} = $first_name,
        p.{NodeProperties.LAST_NAME} = $last_name,
        p.updated_at = datetime()
    RETURN p
    """
    
    result = tx.run(
        query,
        id=person_id,
        first_name=first_name,
        last_name=last_name
    )
    
    return result.single()["p"]


def create_management_relationship(tx, person_id, company_krs, role):
    """Create a management relationship between a person and a company."""
    query = f"""
    MATCH (p:{NodeLabels.PERSON} {{{NodeProperties.ID}: $person_id}})
    MATCH (c:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: $company_krs}})
    MERGE (p)-[r:{RelationshipTypes.MANAGES}]->(c)
    ON CREATE SET 
        r.{NodeProperties.ROLE} = $role,
        r.created_at = datetime()
    ON MATCH SET
        r.{NodeProperties.ROLE} = $role,
        r.updated_at = datetime()
    RETURN r
    """
    
    result = tx.run(
        query,
        person_id=person_id,
        company_krs=company_krs,
        role=role
    )
    
    return result.single()["r"]


def create_shareholder_node(tx, name, shareholder_type):
    """Create a shareholder node in Neo4j."""
    # Generate a unique ID for the shareholder
    shareholder_id = f"shareholder_{name.lower().replace(' ', '_')}"
    
    query = f"""
    MERGE (s:{NodeLabels.SHAREHOLDER} {{id: $id}})
    ON CREATE SET 
        s.{NodeProperties.NAME} = $name,
        s.{NodeProperties.SHAREHOLDER_TYPE} = $type,
        s.created_at = datetime()
    ON MATCH SET
        s.{NodeProperties.NAME} = $name,
        s.{NodeProperties.SHAREHOLDER_TYPE} = $type,
        s.updated_at = datetime()
    RETURN s
    """
    
    result = tx.run(
        query,
        id=shareholder_id,
        name=name,
        type=shareholder_type
    )
    
    return result.single()["s"]


def create_ownership_relationship(tx, shareholder_id, company_krs, percentage):
    """Create an ownership relationship between a shareholder and a company."""
    query = f"""
    MATCH (s:{NodeLabels.SHAREHOLDER} {{id: $shareholder_id}})
    MATCH (c:{NodeLabels.COMPANY} {{{NodeProperties.KRS}: $company_krs}})
    MERGE (s)-[r:{RelationshipTypes.OWNS_SHARES_IN}]->(c)
    ON CREATE SET 
        r.{NodeProperties.PERCENTAGE} = $percentage,
        r.created_at = datetime()
    ON MATCH SET
        r.{NodeProperties.PERCENTAGE} = $percentage,
        r.updated_at = datetime()
    RETURN r
    """
    
    # Convert percentage string to float (e.g., "57.66%" -> 57.66)
    if isinstance(percentage, str) and "%" in percentage:
        percentage = float(percentage.replace("%", ""))
    
    result = tx.run(
        query,
        shareholder_id=shareholder_id,
        company_krs=company_krs,
        percentage=percentage
    )
    
    return result.single()["r"]


def create_cyfrowy_polsat_graph(neo4j_connection):
    """Create a graph representation of Cyfrowy Polsat data in Neo4j."""
    # Get Cyfrowy Polsat data from the KRS API
    api = KrsAPI()
    
    # Get entity details
    entity_data = api.get_entity_details("0000010078")
    
    # Get representatives
    representatives = api.get_entity_representatives("0000010078")
    reps_list = representatives.get("reprezentanci", [])
    
    # Get shareholders
    shareholders = api.get_entity_shareholders("0000010078")
    shareholders_list = shareholders.get("wspolnicy", [])
    
    # Create the company node
    def create_company(tx):
        return create_company_node(
            tx,
            krs=entity_data.get("krs"),
            name=entity_data.get("nazwa"),
            nip=entity_data.get("nip"),
            regon=entity_data.get("regon"),
            address=entity_data.get("adres"),
            status=entity_data.get("status")
        )
    
    company = neo4j_connection.execute_write_transaction(create_company)
    print(f"Created company node: {company}")
    
    # Create representatives and relationships
    for rep in reps_list:
        def create_rep_and_relationship(tx):
            person = create_person_node(
                tx,
                first_name=rep.get("imie"),
                last_name=rep.get("nazwisko")
            )
            
            person_id = f"{rep.get('imie').lower()}_{rep.get('nazwisko').lower()}"
            
            relationship = create_management_relationship(
                tx,
                person_id=person_id,
                company_krs=entity_data.get("krs"),
                role=rep.get("funkcja")
            )
            
            return {"person": person, "relationship": relationship}
        
        result = neo4j_connection.execute_write_transaction(create_rep_and_relationship)
        print(f"Created person node: {result['person']} with relationship: {result['relationship']}")
    
    # Create shareholders and relationships
    for shareholder in shareholders_list:
        def create_shareholder_and_relationship(tx):
            shareholder_node = create_shareholder_node(
                tx,
                name=shareholder.get("nazwa"),
                shareholder_type=shareholder.get("typ", "unknown")
            )
            
            shareholder_id = f"shareholder_{shareholder.get('nazwa').lower().replace(' ', '_')}"
            
            relationship = create_ownership_relationship(
                tx,
                shareholder_id=shareholder_id,
                company_krs=entity_data.get("krs"),
                percentage=shareholder.get("udzialy")
            )
            
            return {"shareholder": shareholder_node, "relationship": relationship}
        
        result = neo4j_connection.execute_write_transaction(create_shareholder_and_relationship)
        print(f"Created shareholder node: {result['shareholder']} with relationship: {result['relationship']}")
    
    # Generate Neo4j Cypher queries for later use
    output_dir = os.path.join(current_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "neo4j_queries_0000010078_depth3.cypher"), "w", encoding="utf-8") as f:
        f.write("""
// View company details
MATCH (c:Company {krs: "0000010078"})
RETURN c

// View representatives
MATCH (p:Person)-[r:MANAGES]->(c:Company {krs: "0000010078"})
RETURN p.first_name, p.last_name, r.role

// View shareholders
MATCH (s:Shareholder)-[r:OWNS_SHARES_IN]->(c:Company {krs: "0000010078"})
RETURN s.name, r.percentage
ORDER BY r.percentage DESC

// View ownership network up to 3 levels deep
MATCH path = (n)-[r*1..3]-(c:Company {krs: "0000010078"})
RETURN path
        """)
    
    print(f"\nNeo4j Cypher queries saved to {os.path.join(output_dir, 'neo4j_queries_0000010078_depth3.cypher')}")


def main():
    """Main function to run the example."""
    try:
        # Create Neo4j connection
        neo4j = Neo4jConnection()
        
        # Test the connection
        if neo4j.verify_connectivity():
            print("\nConnected to Neo4j database!")
        else:
            print("\nFailed to connect to Neo4j database.")
            return
        
        # Create the database schema (constraints and indexes)
        print("\nCreating database schema...")
        DatabaseSchema.create_constraints_and_indexes(neo4j)
        
        # Create the Cyfrowy Polsat graph
        print("\nCreating Cyfrowy Polsat graph...")
        create_cyfrowy_polsat_graph(neo4j)
        
        print("\nExample completed successfully!")
        print("""\nYou can now explore the graph in Neo4j Browser using the Cypher query:
        MATCH path = (n)-[r*1..2]-(c:Company {krs: "0000010078"})
        RETURN path""")
        
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Close the Neo4j connection
        if 'neo4j' in locals():
            neo4j.close()


if __name__ == "__main__":
    main()
