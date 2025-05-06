
# KRS API Integration Project

This project provides tools for integrating with the Polish National Court Register (Krajowy Rejestr SÄ…dowy - KRS) API and analyzing company relationships using Neo4j.

## Overview

The Polish Ministry of Justice provides an open API for accessing data from the National Court Register (KRS). This project allows you to:

1. Search for companies and retrieve details from the KRS API
2. Store this data in a Neo4j graph database for relationship analysis
3. Analyze company networks, shareholders, and management relationships
4. Visualize company networks with D3.js and other formats

## Key Features

- **KRS API Integration**: Search for organizations, get details, representatives, shareholders, etc.
- **Neo4j Graph Database**: Store company networks in a graph database for powerful relationship queries
- **Network Analysis**: Find connections between companies, common management, ownership paths
- **Visualization**: Export networks in various formats (D3.js HTML, JSON, GraphML)
- **Command Line Interface**: Access functionality from the command line
- **Mock API Support**: Test functionality without hitting the real API

## Project Structure

```
krs/
â”śâ”€â”€ src/                # Source code
â”‚   â”śâ”€â”€ krs_api.py      # Main API client
â”‚   â”śâ”€â”€ krs_export.py   # Export utilities
â”‚   â”śâ”€â”€ krs_cli.py      # Command line interface
â”‚   â”śâ”€â”€ krs_http.py     # HTTP client utilities
â”‚   â””â”€â”€ graph/          # Neo4j integration
â”‚       â”śâ”€â”€ neo4j_connection.py  # Neo4j connection
â”‚       â”śâ”€â”€ data_model.py        # Graph data model
â”‚       â”śâ”€â”€ krs_graph_service.py # Import service
â”‚       â”śâ”€â”€ network_analyzer.py  # Network analysis
â”‚       â””â”€â”€ network_exporter.py  # Visualization exports
â”‚   â””â”€â”€ mock/           # Mock API for testing
â”śâ”€â”€ examples/           # Example usage
â”śâ”€â”€ output/             # Output files (generated)
â””â”€â”€ tests/              # Tests
```

## Installation

### Prerequisites

- Python 3.8+
- Neo4j Database (local or cloud)
- Required packages:
  ```
  requests
  python-dotenv
  neo4j
  ```

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/krs-api.git
   cd krs-api
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the Neo4j connection parameters:
     ```
     NEO4J_URI=bolt://localhost:7687
     NEO4J_USER=neo4j
     NEO4J_PASSWORD=your_password
     NEO4J_DATABASE=krsgraph
     ```

## Usage

### Basic API Usage

```python
from krs_api import KrsAPI

# Initialize the API client
api = KrsAPI()

# Search for an entity by KRS number
results = api.search_entity(krs_number="0000010078")

# Get detailed data about an entity
entity_data = api.get_entity_details(krs_number="0000010078")

# Get representatives
representatives = api.get_entity_representatives(krs_number="0000010078")
```

### Neo4j Integration

```python
from graph.neo4j_connection import Neo4jConnection
from graph.krs_graph_service import KRSGraphService
from krs_api import KrsAPI

# Initialize connections
neo4j = Neo4jConnection()
krs_api = KrsAPI()

# Create import service
graph_service = KRSGraphService(neo4j, krs_api)

# Import a company and its network
graph_service.import_company("0000010078")
graph_service.import_company_network("0000010078", depth=2)
```

### Network Analysis

```python
from graph.neo4j_connection import Neo4jConnection
from graph.network_analyzer import CompanyNetworkAnalyzer

# Initialize analyzer
neo4j = Neo4jConnection()
analyzer = CompanyNetworkAnalyzer(neo4j)

# Find direct connections
connections = analyzer.find_direct_connections("0000010078")

# Find influential people
influencers = analyzer.find_influential_people(min_companies=2)

# Find ownership paths
paths = analyzer.find_ownership_path("0000010078", "0000429681")
```

### Network Visualization

```python
from graph.neo4j_connection import Neo4jConnection
from graph.network_analyzer import CompanyNetworkAnalyzer
from graph.network_exporter import NetworkExporter

# Initialize exporter
neo4j = Neo4jConnection()
analyzer = CompanyNetworkAnalyzer(neo4j)
exporter = NetworkExporter(analyzer)

# Export in various formats
exporter.export_network_d3js("0000010078", depth=2, output_file="network.html")
exporter.export_network_json("0000010078", depth=2, output_file="network.json")
exporter.export_network_graphml("0000010078", depth=2, output_file="network.graphml")
```

### Command Line Interface

```bash
# Search for a company by name
python src/krs_cli.py search --name "Cyfrowy Polsat"

# Get details about a company by KRS number
python src/krs_cli.py details --krs 0000010078

# Import a company into Neo4j
python src/krs_cli.py import --krs 0000010078

# Export a company network
python src/krs_cli.py network --krs 0000010078 --depth 2 --export html --output network.html
```

### Example Scripts

The `examples` directory contains example scripts demonstrating how to use the API:

```bash
# Run the Cyfrowy Polsat example
python examples/cyfrowy_polsat_example.py

# Run the Neo4j integration example
python examples/cyfrowy_polsat_neo4j.py
```

## Neo4j Data Model

The project uses the following Neo4j data model:

### Nodes
- `Company`: KRS entities with properties (krs, name, nip, regon, status, etc.)
- `Person`: Representatives/managers with properties (first_name, last_name, etc.)
- `Shareholder`: Shareholders with properties (name, type, etc.)

### Relationships
- `MANAGES`: Person to Company (with role property)
- `OWNS_SHARES_IN`: Shareholder to Company (with percentage property)
- `SUBSIDIARY_OF`: Company to Company 
- `AFFILIATED_WITH`: Company to Company

## Sample Cypher Queries

Here are some useful Cypher queries for exploring the data in Neo4j:

```cypher
// View all companies
MATCH (c:Company) RETURN c LIMIT 100

// Find a specific company
MATCH (c:Company {krs: "0000010078"}) RETURN c

// Find company representatives
MATCH (c:Company {krs: "0000010078"})<-[r:MANAGES]-(p:Person) 
RETURN p.first_name, p.last_name, r.role

// Find company shareholders
MATCH (c:Company {krs: "0000010078"})<-[r:OWNS_SHARES_IN]-(s:Shareholder)
RETURN s.name, r.percentage

// Find common management between companies
MATCH (p:Person)-[:MANAGES]->(c1:Company)
MATCH (p)-[:MANAGES]->(c2:Company)
WHERE c1 <> c2
RETURN p.first_name, p.last_name, c1.name, c2.name
```

## Test Data

For testing, you can use the following data for Cyfrowy Polsat S.A.:
- Name: Cyfrowy Polsat SpĂłĹ‚ka Akcyjna
- KRS: 0000010078
- NIP: 7961810732
- REGON: 670925160
- Address: ul. Ĺ�UBINOWA 4A, WARSZAWA

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This is an unofficial client for the KRS API. It is not affiliated with or endorsed by the Polish Ministry of Justice.
