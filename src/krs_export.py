#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KRS Export Utilities

This module provides utilities for exporting KRS data to various formats.
"""

import os
import json
import csv
import xml.dom.minidom
import xmltodict
from typing import Dict, List, Any, Optional, Union
from pathlib import Path


class KrsExporter:
    """Utilities for exporting KRS data to various formats."""
    
    @staticmethod
    def export_json(data: Dict, output_path: str) -> None:
        """Export data to a JSON file.
        
        Args:
            data: Data to export
            output_path: Path to the output file
            
        Raises:
            IOError: If there is an error writing to the file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Write the data to the file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def export_csv(data: List[Dict], output_path: str, fieldnames: Optional[List[str]] = None) -> None:
        """Export data to a CSV file.
        
        Args:
            data: List of dictionaries to export
            output_path: Path to the output file
            fieldnames: List of field names to include (default: all fields)
            
        Raises:
            IOError: If there is an error writing to the file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # If fieldnames are not provided, use all keys from the first item
        if fieldnames is None and data and len(data) > 0:
            fieldnames = list(data[0].keys())
        
        # Write the data to the file
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    
    @staticmethod
    def export_xml(data: Dict, output_path: str, root_element: str = "root") -> None:
        """Export data to an XML file.
        
        Args:
            data: Data to export
            output_path: Path to the output file
            root_element: Name of the root XML element (default: "root")
            
        Raises:
            IOError: If there is an error writing to the file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Convert the data to XML
        xml_data = xmltodict.unparse({root_element: data}, pretty=True)
        
        # Format the XML with proper indentation
        dom = xml.dom.minidom.parseString(xml_data)
        formatted_xml = dom.toprettyxml(indent="  ")
        
        # Write the formatted XML to the file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(formatted_xml)
    
    @staticmethod
    def export_representatives(representatives: Dict, output_dir: str, entity_krs: str) -> Dict[str, str]:
        """Export representatives data to multiple formats.
        
        Args:
            representatives: Representatives data
            output_dir: Directory for output files
            entity_krs: KRS number of the entity
            
        Returns:
            Dictionary of output file paths
            
        Raises:
            IOError: If there is an error writing to the files
        """
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define output file paths
        output_files = {
            "json": os.path.join(output_dir, f"{entity_krs}_representatives.json"),
            "csv": os.path.join(output_dir, f"{entity_krs}_representatives.csv"),
            "xml": os.path.join(output_dir, f"{entity_krs}_representatives.xml")
        }
        
        # Extract the list of representatives
        reps_list = representatives.get("reprezentanci", [])
        
        # Export to different formats
        KrsExporter.export_json(representatives, output_files["json"])
        KrsExporter.export_csv(reps_list, output_files["csv"])
        KrsExporter.export_xml(representatives, output_files["xml"], "representatives")
        
        return output_files
    
    @staticmethod
    def export_shareholders(shareholders: Dict, output_dir: str, entity_krs: str) -> Dict[str, str]:
        """Export shareholders data to multiple formats.
        
        Args:
            shareholders: Shareholders data
            output_dir: Directory for output files
            entity_krs: KRS number of the entity
            
        Returns:
            Dictionary of output file paths
            
        Raises:
            IOError: If there is an error writing to the files
        """
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define output file paths
        output_files = {
            "json": os.path.join(output_dir, f"{entity_krs}_shareholders.json"),
            "csv": os.path.join(output_dir, f"{entity_krs}_shareholders.csv"),
            "xml": os.path.join(output_dir, f"{entity_krs}_shareholders.xml")
        }
        
        # Extract the list of shareholders
        shareholder_list = shareholders.get("wspolnicy", [])
        
        # Export to different formats
        KrsExporter.export_json(shareholders, output_files["json"])
        KrsExporter.export_csv(shareholder_list, output_files["csv"])
        KrsExporter.export_xml(shareholders, output_files["xml"], "shareholders")
        
        return output_files
    
    @staticmethod
    def export_entity_summary(entity_data: Dict, output_dir: str, entity_krs: str) -> Dict[str, str]:
        """Export entity summary data to multiple formats.
        
        Args:
            entity_data: Entity data
            output_dir: Directory for output files
            entity_krs: KRS number of the entity
            
        Returns:
            Dictionary of output file paths
            
        Raises:
            IOError: If there is an error writing to the files
        """
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Define output file paths
        output_files = {
            "json": os.path.join(output_dir, f"{entity_krs}_summary.json"),
            "xml": os.path.join(output_dir, f"{entity_krs}_summary.xml")
        }
        
        # Create a summary from the entity data
        summary = {
            "krs": entity_data.get("krs"),
            "name": entity_data.get("nazwa"),
            "nip": entity_data.get("nip"),
            "regon": entity_data.get("regon"),
            "address": entity_data.get("adres"),
            "registration_date": entity_data.get("dataRejestracji"),
            "legal_form": entity_data.get("formaFrawna"),
            "status": entity_data.get("status"),
        }
        
        # Export to different formats
        KrsExporter.export_json(summary, output_files["json"])
        KrsExporter.export_xml(summary, output_files["xml"], "entity_summary")
        
        return output_files
