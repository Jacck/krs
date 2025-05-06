#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Visualize Multi-level Ownership Relationships

This script creates interactive visualizations of multi-level ownership relationships
using the existing Neo4j database. It builds on the indirect ownership discovery 
functionality to provide a comprehensive view of the ownership network.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

# Import required modules
from graph.neo4j_connection import Neo4jConnection
from graph.indirect_ownership import IndirectOwnershipDiscovery
from graph.network_analyzer import CompanyNetworkAnalyzer
from graph.ownership_analyzer import OwnershipAnalyzer


def setup_logging(level=logging.INFO):
    """
    Configure logging.
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('multi_level_ownership.log')
        ]
    )


def print_header():
    """
    Print a header for the script.
    """
    print("\n" + "=" * 80)
    print(" Multi-level Ownership Relationship Visualization ".center(80, "="))
    print("=" * 80)
    print("\nThis tool visualizes direct and indirect ownership relationships")
    print("between companies and their shareholders at multiple levels.")
    print("\n" + "-" * 80)


def print_section(title):
    """
    Print a section header.
    """
    print("\n" + "-" * 80)
    print(f" {title} ".center(80, "-"))
    print("-" * 80)


def discover_indirect_relationships(krs_number, max_depth):
    """
    Discover and import indirect ownership relationships for visualization.
    
    Args:
        krs_number: The KRS number of the company
        max_depth: Maximum depth for relationship discovery
        
    Returns:
        Statistics about the discovered relationships
    """
    print_section(f"Discovering Indirect Relationships (Depth: {max_depth})")
    neo4j = Neo4jConnection()
    
    try:
        print(f"Analyzing indirect relationships for company with KRS: {krs_number}")
        discovery_service = IndirectOwnershipDiscovery(neo4j)
        stats = discovery_service.discover_indirect_relationships(krs_number, max_depth=max_depth)
        
        print("\nIndirect Relationship Discovery Results:")
        print(f"  - Upstream relationships discovered: {stats['upstream_relationships']}")
        print(f"  - Downstream relationships discovered: {stats['downstream_relationships']}")
        print(f"  - Total indirect relationships: {stats['total_relationships']}")
        print(f"  - Companies linked: {stats['companies_linked']}")
        print(f"  - Shareholders linked: {stats['shareholders_linked']}")
        
        return stats
    except Exception as e:
        print(f"Error discovering indirect relationships: {e}")
        return None
    finally:
        neo4j.close()


def analyze_ownership_structure(krs_number, max_depth):
    """
    Analyze the ownership structure and display effective ownership percentages.
    
    Args:
        krs_number: The KRS number of the company
        max_depth: Maximum depth for analysis
    """
    print_section(f"Analyzing Ownership Structure (Depth: {max_depth})")
    neo4j = Neo4jConnection()
    
    try:
        print(f"Analyzing ownership structure for company with KRS: {krs_number}")
        
        # Get company name
        query = "MATCH (c:Company {krs: $krs}) RETURN c.name AS name"
        result = neo4j.query(query, {"krs": krs_number})
        company_name = result[0]["name"] if result else krs_number
        
        print(f"\nCompany: {company_name}")
        
        # Query direct owners
        direct_query = """
        MATCH (shareholder)-[r:OWNS_SHARES_IN]->(c:Company {krs: $krs})
        RETURN shareholder.name AS name, 
               r.percentage AS percentage
        ORDER BY percentage DESC
        """
        direct_owners = neo4j.query(direct_query, {"krs": krs_number})
        
        print("\nDirect Shareholders:")
        for owner in direct_owners:
            print(f"  - {owner['name']}: {owner['percentage']}%")
        
        # Query indirect owners using the INDIRECT_OWNER_OF relationship
        indirect_query = """
        MATCH (shareholder)-[r:INDIRECT_OWNER_OF]->(c:Company {krs: $krs})
        RETURN shareholder.name AS name, 
               r.percentage AS effective_percentage
        ORDER BY effective_percentage DESC
        """
        indirect_owners = neo4j.query(indirect_query, {"krs": krs_number})
        
        if indirect_owners:
            print("\nIndirect Shareholders (Ultimate Beneficial Owners):")
            for owner in indirect_owners:
                print(f"  - {owner['name']}: {owner['effective_percentage']:.2f}% (effective ownership)")
        else:
            print("\nNo indirect shareholders found.")
        
        # Find ownership chains
        chain_query = f"""
        MATCH path = (owner)-[r:OWNS_SHARES_IN*1..{max_depth}]->(c:Company {{krs: $krs}})
        WHERE NOT (owner)<-[:OWNS_SHARES_IN]-()
        WITH owner, path, relationships(path) AS rels,
             reduce(s = 1.0, rel IN relationships(path) | 
                s * CASE WHEN rel.percentage IS NOT NULL 
                        THEN rel.percentage / 100 
                        ELSE 1 
                   END
             ) * 100 AS effective_percentage
        WHERE effective_percentage >= 0.1
        RETURN owner.name AS ultimate_owner,
               [node IN nodes(path) | node.name] AS ownership_chain,
               [rel IN rels | rel.percentage] AS percentages,
               effective_percentage
        ORDER BY effective_percentage DESC
        """
        
        chains = neo4j.query(chain_query, {"krs": krs_number})
        
        if chains:
            print("\nOwnership Chains:")
            for i, chain in enumerate(chains, 1):
                owner = chain["ultimate_owner"]
                path = chain["ownership_chain"]
                percentages = chain["percentages"]
                effective = chain["effective_percentage"]
                
                print(f"\nChain {i}: {owner} -> {' -> '.join(path[1:-1])} -> {company_name}")
                print(f"  Percentages: {' -> '.join([f'{p}%' for p in percentages])}")
                print(f"  Effective Ownership: {effective:.2f}%")
        
        return True
    except Exception as e:
        print(f"Error analyzing ownership structure: {e}")
        return False
    finally:
        neo4j.close()


def generate_ownership_network_visualization(krs_number, max_depth):
    """
    Generate a D3.js visualization of the ownership network.
    
    Args:
        krs_number: The KRS number of the company
        max_depth: Maximum depth for the network
        
    Returns:
        Path to the generated HTML file
    """
    print_section(f"Generating Ownership Network Visualization (Depth: {max_depth})")
    neo4j = Neo4jConnection()
    
    try:
        # Create output directory
        output_dir = Path(__file__).resolve().parent / "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Create HTML file
        html_file = output_dir / f"ownership_network_{krs_number}_depth{max_depth}.html"
        print(f"Creating visualization at {html_file}...")
        
        # Get company name
        query = "MATCH (c:Company {krs: $krs}) RETURN c.name AS name"
        result = neo4j.query(query, {"krs": krs_number})
        company_name = result[0]["name"] if result else krs_number
        
        # First, get the central company
        central_query = """
        MATCH (c:Company {krs: $krs})
        RETURN {
            id: id(c),
            name: c.name,
            krs: c.krs,
            type: 'central'
        } AS central
        """
        central_result = neo4j.query(central_query, {"krs": krs_number})
        if not central_result:
            print(f"Company with KRS {krs_number} not found.")
            return None
        central = central_result[0]["central"]
        
        # Get direct shareholders
        direct_query = """
        MATCH (shareholder)-[r:OWNS_SHARES_IN]->(c:Company {krs: $krs})
        RETURN {
            id: id(shareholder),
            name: shareholder.name,
            krs: CASE WHEN shareholder:Company THEN shareholder.krs ELSE null END,
            type: CASE
                WHEN shareholder:Company THEN 'company'
                WHEN shareholder:Shareholder AND shareholder.shareholder_type = 'individual' THEN 'individual'
                WHEN shareholder:Shareholder THEN 'corporate'
                ELSE 'unknown'
            END
        } AS node,
        {
            source: id(shareholder),
            target: id(c),
            type: 'OWNS_SHARES_IN',
            percentage: r.percentage,
            is_indirect: false
        } AS link
        """
        direct_result = neo4j.query(direct_query, {"krs": krs_number})
        
        # Get indirect shareholders
        indirect_query = """
        MATCH (shareholder)-[r:INDIRECT_OWNER_OF]->(c:Company {krs: $krs})
        RETURN {
            id: id(shareholder),
            name: shareholder.name,
            krs: CASE WHEN shareholder:Company THEN shareholder.krs ELSE null END,
            type: CASE
                WHEN shareholder:Company THEN 'company'
                WHEN shareholder:Shareholder AND shareholder.shareholder_type = 'individual' THEN 'individual'
                WHEN shareholder:Shareholder THEN 'corporate'
                ELSE 'unknown'
            END
        } AS node,
        {
            source: id(shareholder),
            target: id(c),
            type: 'INDIRECT_OWNER_OF',
            percentage: r.percentage,
            is_indirect: true
        } AS link
        """
        indirect_result = neo4j.query(indirect_query, {"krs": krs_number})
        
        # Combine results
        nodes = [central]
        links = []
        node_ids = {central["id"]}
        
        for record in direct_result:
            node = record["node"]
            link = record["link"]
            if node["id"] not in node_ids:
                nodes.append(node)
                node_ids.add(node["id"])
            links.append(link)
        
        for record in indirect_result:
            node = record["node"]
            link = record["link"]
            if node["id"] not in node_ids:
                nodes.append(node)
                node_ids.add(node["id"])
            links.append(link)
        
        # Handle higher depth levels if needed
        if max_depth > 1:
            # Get additional nodes and links for higher depth
            higher_depth_query = f"""
            MATCH path = (c:Company {{krs: $krs}})-[:OWNS_SHARES_IN*1..{max_depth-1}]->(related)
            WHERE related <> c
            WITH c, related, [rel in relationships(path) | rel] as rels
            RETURN {{
                id: id(related),
                name: related.name,
                krs: CASE WHEN related:Company THEN related.krs ELSE null END,
                type: CASE
                    WHEN related:Company THEN 'company'
                    WHEN related:Shareholder AND related.shareholder_type = 'individual' THEN 'individual'
                    WHEN related:Shareholder THEN 'corporate'
                    ELSE 'unknown'
                END
            }} AS node
            """
            higher_nodes_result = neo4j.query(higher_depth_query, {"krs": krs_number})
            
            for record in higher_nodes_result:
                node = record["node"]
                if node["id"] not in node_ids:
                    nodes.append(node)
                    node_ids.add(node["id"])
            
            # Get additional links
            higher_links_query = f"""
            MATCH (a)-[r:OWNS_SHARES_IN]->(b)
            WHERE id(a) IN $node_ids AND id(b) IN $node_ids
            RETURN {{
                source: id(a),
                target: id(b),
                type: type(r),
                percentage: r.percentage,
                is_indirect: false
            }} AS link
            """
            higher_links_result = neo4j.query(higher_links_query, {"node_ids": list(node_ids)})
            
            for record in higher_links_result:
                link = record["link"]
                # Check if link is not already added
                if not any(l["source"] == link["source"] and l["target"] == link["target"] for l in links):
                    links.append(link)
        
        # Create visualization data
        visualization_data = {
            "nodes": nodes,
            "links": links
        }
        
        # Create D3.js visualization
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Ownership Network - {company_name}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            overflow: hidden;
        }}
        
        #visualization {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}
        
        .controls {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: white;
            border: 1px solid #ccc;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 100;
        }}
        
        .legend {{
            margin-top: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        
        .legend-color {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .toggle {{
            margin-bottom: 10px;
        }}
        
        .node {{
            stroke: #fff;
            stroke-width: 1.5px;
            cursor: pointer;
        }}
        
        .link {{
            stroke-opacity: 0.6;
        }}
        
        .indirect-link {{
            stroke-dasharray: 5, 5;
        }}
        
        .tooltip {{
            position: absolute;
            background: white;
            border: 1px solid #ccc;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            z-index: 101;
            pointer-events: none;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div id="visualization"></div>
    
    <div class="controls">
        <h3>Ownership Network</h3>
        <div>Company: {company_name}</div>
        <div>KRS: {krs_number}</div>
        <div>Depth: {max_depth}</div>
        
        <div class="toggle">
            <input type="checkbox" id="show-indirect" checked>
            <label for="show-indirect">Show Indirect Relationships</label>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #1f77b4;"></div>
                <div>Central Company</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #ff7f0e;"></div>
                <div>Company</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #2ca02c;"></div>
                <div>Individual Shareholder</div>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #d62728;"></div>
                <div>Corporate Shareholder</div>
            </div>
            <div class="legend-item">
                <div style="width: 20px; height: 2px; background: #000; margin-right: 8px;"></div>
                <div>Direct Ownership</div>
            </div>
            <div class="legend-item">
                <div style="width: 20px; height: 2px; background: #000; margin-right: 8px; stroke-dasharray: 5, 5; border-top: 1px dashed #000;"></div>
                <div>Indirect Ownership</div>
            </div>
        </div>
    </div>
    
    <script>
        // Network data
        const networkData = {json.dumps(visualization_data)};
        
        // Prepare data for D3
        const nodes = networkData.nodes;
        const links = networkData.links;
        
        // Create a map for node lookup
        const nodeMap = new Map();
        nodes.forEach(node => nodeMap.set(node.id, node));
        
        // Process links to use node references
        links.forEach(link => {{
            link.source = nodeMap.get(link.source);
            link.target = nodeMap.get(link.target);
        }});
        
        // Set up the visualization
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        // Color scale
        const nodeColors = {{
            "central": "#1f77b4",
            "company": "#ff7f0e",
            "individual": "#2ca02c",
            "corporate": "#d62728",
            "unknown": "#9467bd"
        }};
        
        // Create SVG
        const svg = d3.select("#visualization")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        // Set up zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 5])
            .on("zoom", zoomed);
        
        svg.call(zoom);
        
        // Create a container for the zoom transform
        const container = svg.append("g");
        
        // Create tooltip
        const tooltip = d3.select("#visualization")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
        
        // Create links
        const link = container.append("g")
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("class", d => `link ${{d.is_indirect ? "indirect-link" : ""}}`)
            .attr("stroke", "#999")
            .attr("stroke-width", d => {{
                if (d.percentage) {{
                    return Math.max(1, Math.sqrt(d.percentage) / 2);
                }}
                return 1;
            }});
        
        // Create nodes
        const node = container.append("g")
            .selectAll("circle")
            .data(nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", d => d.type === "central" ? 12 : 8)
            .attr("fill", d => nodeColors[d.type] || nodeColors.unknown)
            .call(d3.drag()
                .on("start", dragStarted)
                .on("drag", dragged)
                .on("end", dragEnded));
        
        // Add labels
        const label = container.append("g")
            .selectAll("text")
            .data(nodes)
            .enter().append("text")
            .attr("dx", 12)
            .attr("dy", ".35em")
            .text(d => d.name);
        
        // Node tooltips
        node.on("mouseover", function(event, d) {{
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            
            let tooltipContent = `<strong>${{d.name}}</strong>`;
            if (d.krs) {{
                tooltipContent += `<br>KRS: ${{d.krs}}`;
            }}
            tooltipContent += `<br>Type: ${{d.type.charAt(0).toUpperCase() + d.type.slice(1)}}`;
            
            // Find connected links
            const outgoingLinks = links.filter(l => l.source.id === d.id);
            const incomingLinks = links.filter(l => l.target.id === d.id);
            
            if (outgoingLinks.length > 0) {{
                tooltipContent += `<br><br><strong>Owns:</strong>`;
                outgoingLinks.forEach(l => {{
                    tooltipContent += `<br>${{l.target.name}}`;
                    if (l.percentage) {{
                        tooltipContent += ` (${{l.percentage}}%)`;
                    }}
                    if (l.is_indirect) {{
                        tooltipContent += ` (indirect)`;
                    }}
                }});
            }}
            
            if (incomingLinks.length > 0) {{
                tooltipContent += `<br><br><strong>Owned by:</strong>`;
                incomingLinks.forEach(l => {{
                    tooltipContent += `<br>${{l.source.name}}`;
                    if (l.percentage) {{
                        tooltipContent += ` (${{l.percentage}}%)`;
                    }}
                    if (l.is_indirect) {{
                        tooltipContent += ` (indirect)`;
                    }}
                }});
            }}
            
            tooltip.html(tooltipContent)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        }})
        .on("mouseout", function() {{
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        }});
        
        // Force simulation
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(150))
            .force("charge", d3.forceManyBody().strength(-500))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .on("tick", ticked);
        
        // Update positions on each tick
        function ticked() {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }}
        
        // Zooming function
        function zoomed(event) {{
            container.attr("transform", event.transform);
        }}
        
        // Drag functions
        function dragStarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragEnded(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            //d.fx = null;
            //d.fy = null;
        }}
        
        // Toggle indirect relationships
        d3.select("#show-indirect").on("change", function() {{
            const showIndirect = this.checked;
            
            link.filter(d => d.is_indirect)
                .style("visibility", showIndirect ? "visible" : "hidden");
            
            // If hiding indirect links, also hide nodes that would be disconnected
            if (!showIndirect) {{
                // Find nodes only connected by indirect links
                const visibleLinks = links.filter(d => !d.is_indirect);
                const connectedNodeIds = new Set();
                
                visibleLinks.forEach(l => {{
                    connectedNodeIds.add(l.source.id);
                    connectedNodeIds.add(l.target.id);
                }});
                
                node.style("visibility", d => {{
                    // Always show the central node
                    if (d.type === "central") return "visible";
                    return connectedNodeIds.has(d.id) ? "visible" : "hidden";
                }});
                
                label.style("visibility", d => {{
                    if (d.type === "central") return "visible";
                    return connectedNodeIds.has(d.id) ? "visible" : "hidden";
                }});
            }} else {{
                // Show all nodes
                node.style("visibility", "visible");
                label.style("visibility", "visible");
            }}
            
            // Restart simulation
            simulation.alpha(0.1).restart();
        }});
    </script>
</body>
</html>
        """
        
        # Write the HTML file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Visualization generated successfully: {html_file}")
        return str(html_file)
        
    except Exception as e:
        print(f"Error generating ownership network visualization: {e}")
        return None
    finally:
        neo4j.close()


def main():
    """
    Main function.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Visualize multi-level ownership relationships")
    parser.add_argument("krs", help="KRS number of the company")
    parser.add_argument("--depth", "-d", type=int, default=3, help="Maximum relationship depth (default: 3)")
    parser.add_argument("--discover", action="store_true", help="Discover and import indirect relationships")
    parser.add_argument("--analyze", action="store_true", help="Analyze ownership structure")
    parser.add_argument("--visualize", action="store_true", help="Generate visualization")
    parser.add_argument("--all", action="store_true", help="Perform all operations")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(level=logging.DEBUG if args.debug else logging.INFO)
    
    # Load environment variables
    load_dotenv()
    
    # Print header
    print_header()
    
    # Check if at least one operation is specified
    if not (args.discover or args.analyze or args.visualize or args.all):
        print("No operation specified. Use --discover, --analyze, --visualize, or --all.")
        parser.print_help()
        return
    
    # Perform operations
    if args.discover or args.all:
        discover_indirect_relationships(args.krs, args.depth)
    
    if args.analyze or args.all:
        analyze_ownership_structure(args.krs, args.depth)
    
    if args.visualize or args.all:
        html_file = generate_ownership_network_visualization(args.krs, args.depth)
        if html_file:
            print(f"\nOpen {html_file} in your browser to view the visualization.")
    
    print("\n" + "=" * 80)
    print(" Operation Completed ".center(80, "="))
    print("=" * 80)


if __name__ == "__main__":
    main()