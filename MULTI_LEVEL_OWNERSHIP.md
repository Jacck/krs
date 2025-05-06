# Multi-Level Ownership Analysis

This document describes the methodology for analyzing multi-level ownership structures using the KRS API and Neo4j graph database.

## Overview

Multi-level ownership refers to the ownership structures where companies own other companies, which in turn own other companies, creating complex ownership networks. Analyzing these structures is important for:

- Identifying ultimate beneficial owners
- Understanding corporate control
- Detecting circular ownership structures
- Mapping business groups
- Regulatory compliance

## Methodology

This project implements a multi-level ownership analysis methodology with the following steps:

1. **Data Collection**: Import company data from the KRS API, including shareholders and ownership percentages.
2. **Graph Construction**: Build a graph representation of ownership relationships in Neo4j.
3. **Direct Relationship Analysis**: Analyze direct ownership relationships between entities.
4. **Indirect Relationship Discovery**: Discover and create indirect ownership relationships by traversing the graph.
5. **Ownership Chain Analysis**: Calculate effective ownership percentages through ownership chains.
6. **Visualization**: Visualize the ownership network using Neo4j Browser or export formats.

## Indirect Ownership Discovery

The indirect ownership discovery process involves:

1. **Upstream Analysis**: Find owners of owners (parent companies/shareholders).
2. **Downstream Analysis**: Find subsidiaries of subsidiaries (child companies).
3. **Path Traversal**: Follow ownership relationships to a specified depth (usually 2-5 levels).
4. **Percentage Calculation**: Calculate effective ownership percentages by multiplying percentages along the path.

## Effective Ownership Calculation

Effective ownership is calculated using the following formula:

```
Effective Ownership = Product of all ownership percentages along the path
```

For example, if Company A owns 70% of Company B, and Company B owns 60% of Company C, then Company A's effective ownership of Company C is:

```
70% Ă— 60% = 42%
```

This calculation is implemented in Cypher queries using the `reduce()` function to multiply percentages along ownership paths.

## Relationship Types

The following relationship types are used to represent ownership relationships:

- `OWNS_SHARES_IN`: Direct ownership relationship with a percentage property.
- `INDIRECT_OWNER_OF`: Derived indirect upstream ownership relationship.
- `CONTROLS_INDIRECTLY`: Derived indirect downstream control relationship.

## Implementation

The implementation uses the following components:

- `IndirectOwnershipDiscovery` class: Discovers and creates indirect ownership relationships.
- Cypher queries: Traverse the graph and calculate effective ownership percentages.
- Neo4j database: Stores and queries the ownership graph.

## Usage

To analyze multi-level ownership structures:

1. Populate the Neo4j database with company and shareholder data.
2. Run the `populate_indirect_ownership.py` script to discover indirect relationships.
3. Use the `run_multi_level_analysis.py` script to analyze specific companies.
4. Visualize the results using Neo4j Browser or the visualization scripts.

Example command:

```bash
python run_multi_level_analysis.py --krs 0000010078 --depth 3
```

## Example Cypher Queries

Here are some useful Cypher queries for analyzing multi-level ownership:

```cypher
// Find all indirect owners of a company
MATCH (owner)-[r:INDIRECT_OWNER_OF]->(company:Company {krs: "0000010078"})
RETURN owner.name AS Owner, company.name AS Company, r.percentage AS Percentage
ORDER BY r.percentage DESC

// Find all companies indirectly controlled by a company
MATCH (company:Company {krs: "0000010078"})-[r:CONTROLS_INDIRECTLY]->(subsidiary)
RETURN company.name AS Controller, subsidiary.name AS Subsidiary, r.percentage AS Percentage
ORDER BY r.percentage DESC

// Find ownership paths of any length
MATCH path = (owner)-[:OWNS_SHARES_IN*1..5]->(company:Company {krs: "0000010078"})
WITH owner, company, [rel in relationships(path) | rel.percentage] AS percentages
RETURN 
    owner.name AS Owner, 
    company.name AS Company, 
    percentages AS Path, 
    reduce(s = 1.0, p IN percentages | s * p / 100) * 100 AS EffectivePercentage
ORDER BY EffectivePercentage DESC
```

## Visualization

The ownership network can be visualized using:

1. Neo4j Browser: Interactive graph visualization and exploration.
2. D3.js: HTML-based interactive network visualization.
3. Network export formats: GraphML, JSON, etc.

## Limitations

- Ownership data quality depends on KRS API data accuracy.
- Circular ownership structures may cause issues with percentage calculations.
- Cross-border ownership may not be captured if foreign entities are not in KRS.
- The analysis is limited to the specified depth and may not capture very deep ownership chains.
