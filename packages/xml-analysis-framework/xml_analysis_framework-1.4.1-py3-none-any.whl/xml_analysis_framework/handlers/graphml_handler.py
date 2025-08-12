#!/usr/bin/env python3
"""
GraphML Handler

Analyzes GraphML (Graph Markup Language) files which describe graphs, networks,
and their associated data. Extracts nodes, edges, graph structure, attributes,
and performs network analysis for visualization and graph algorithms.
"""

import re
import sys
import os
import math
from typing import Dict, List, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class GraphMLHandler(XMLHandler):
    """Handler for GraphML (Graph Markup Language) files"""

    GRAPHML_NAMESPACE = "http://graphml.graphdrawing.org/xmlns"
    GRAPHML_NAMESPACES = ["graphml.graphdrawing.org", "graphdrawing.org/xmlns"]

    def _get_namespace(self, root: Element) -> str:
        """Extract namespace prefix from root element"""
        if "}" in root.tag:
            return root.tag.split("}")[0] + "}"
        return ""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for GraphML namespace
        for uri in namespaces.values():
            if any(ns in uri for ns in self.GRAPHML_NAMESPACES):
                return True, 1.0

        # Check root element
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if root_tag.lower() == "graphml":
            return True, 0.95

        # Check for GraphML-specific elements
        ns = self._get_namespace(root)
        graphml_elements = ["graph", "node", "edge", "key", "data"]
        found_elements = sum(
            1 for elem in graphml_elements if root.find(f".//{ns}{elem}") is not None
        )

        if found_elements >= 3:
            return True, min(found_elements * 0.2, 0.9)

        # Check for graph with nodes and edges
        graph = root.find(".//graph")
        if graph is not None:
            nodes = len(graph.findall(".//node"))
            edges = len(graph.findall(".//edge"))
            if nodes > 0 and edges > 0:
                return True, 0.8
            elif nodes > 0:
                return True, 0.6

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Detect GraphML version
        version = "1.0"  # Default
        if "version" in root.attrib:
            version = root.get("version", "1.0")

        # Detect graph characteristics
        ns = self._get_namespace(root)
        graph_type = "generic"

        # Analyze graph structure
        graphs = root.findall(f".//{ns}graph")
        if graphs:
            graph = graphs[0]  # Analyze first graph

            # Check if directed
            is_directed = graph.get("edgedefault", "undirected") == "directed"

            # Count nodes and edges
            node_count = len(graph.findall(f"{ns}node"))
            edge_count = len(graph.findall(f"{ns}edge"))

            # Determine graph type based on structure
            if node_count > 0 and edge_count > 0:
                edge_node_ratio = edge_count / node_count

                if edge_node_ratio > 3:
                    graph_type = "dense_network"
                elif edge_node_ratio < 0.5:
                    graph_type = "sparse_network"
                elif is_directed:
                    graph_type = "directed_graph"
                else:
                    graph_type = "undirected_graph"
            elif node_count > 0:
                graph_type = "node_only"

            # Check for specific patterns
            if any(
                "tree" in str(data.text).lower()
                for data in root.findall(".//data")
                if data.text
            ):
                graph_type = "tree_structure"
            elif any(
                "social" in str(data.text).lower()
                for data in root.findall(".//data")
                if data.text
            ):
                graph_type = "social_network"
            elif any(
                "neural" in str(data.text).lower()
                for data in root.findall(".//data")
                if data.text
            ):
                graph_type = "neural_network"

        # Determine complexity
        total_elements = len(root.findall(".//node")) + len(root.findall(".//edge"))
        complexity = (
            "simple"
            if total_elements < 50
            else "medium" if total_elements < 500 else "complex"
        )

        return DocumentTypeInfo(
            type_name="GraphML Network",
            confidence=0.95,
            version=version,
            metadata={
                "standard": "GraphML",
                "category": "network_data",
                "graph_type": graph_type,
                "complexity": complexity,
                "node_count": len(root.findall(".//node")),
                "edge_count": len(root.findall(".//edge")),
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "file_info": self._analyze_file_info(root),
            "graph_structure": self._analyze_graph_structure(root),
            "nodes": self._analyze_nodes(root),
            "edges": self._analyze_edges(root),
            "attributes": self._analyze_attributes(root),
            "network_metrics": self._calculate_network_metrics(root),
            "data_properties": self._analyze_data_properties(root),
            "layout_info": self._analyze_layout_information(root),
            "connectivity": self._analyze_connectivity(root),
        }

        recommendations = [
            "Perform network analysis and centrality calculations",
            "Visualize graph structure with layout algorithms",
            "Detect communities and clustering patterns",
            "Analyze shortest paths and connectivity",
            "Extract subgraphs and components",
            "Calculate graph metrics (diameter, density, clustering)",
            "Apply graph algorithms (PageRank, betweenness centrality)",
            "Generate graph statistics and reports",
            "Export to analysis tools (NetworkX, Gephi, Cytoscape)",
            "Validate graph integrity and detect anomalies",
        ]

        ai_use_cases = [
            "Social network analysis and community detection",
            "Neural network architecture analysis",
            "Knowledge graph construction and reasoning",
            "Dependency graph analysis for software systems",
            "Biological network analysis (protein interactions)",
            "Transportation network optimization",
            "Citation network analysis and ranking",
            "Graph-based recommendation systems",
            "Fraud detection through network patterns",
            "Supply chain network analysis and optimization",
        ]

        # Get document type info  
        doc_type = self.detect_type(file_path, root=root, namespaces={})
        
        return SpecializedAnalysis(
            # From DocumentTypeInfo
            type_name=doc_type.type_name,
            confidence=doc_type.confidence,
            version=doc_type.version,
            schema_uri=doc_type.schema_uri,
            metadata=doc_type.metadata,
            # Analysis fields
            key_findings=findings,
            recommendations=recommendations,
            data_inventory={
                "total_graphs": findings["graph_structure"]["graph_count"],
                "total_nodes": findings["nodes"]["node_count"],
                "total_edges": findings["edges"]["edge_count"],
                "attribute_keys": findings["attributes"]["key_count"],
                "data_elements": findings["data_properties"]["data_count"],
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_graph_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "graph_metadata": self._extract_graph_metadata(root),
            "node_catalog": self._extract_node_catalog(root),
            "edge_catalog": self._extract_edge_catalog(root),
            "attribute_schema": self._extract_attribute_schema(root),
            "network_statistics": self._extract_network_statistics(root),
        }

    def _analyze_file_info(self, root: Element) -> Dict[str, Any]:
        """Analyze GraphML file information"""
        file_info = {
            "root_element": root.tag,
            "version": root.get("version"),
            "xmlns": root.get("xmlns"),
            "namespaces": {},
            "schema_location": None,
        }

        # Extract namespaces
        if "}" in root.tag:
            namespace = root.tag.split("}")[0] + "}"
            file_info["namespaces"]["graphml"] = namespace.strip("{}")

        # Check for schema location
        schema_attrs = [
            "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
            "schemaLocation",
        ]
        for attr in schema_attrs:
            if attr in root.attrib:
                file_info["schema_location"] = root.get(attr)
                break

        return file_info

    def _analyze_graph_structure(self, root: Element) -> Dict[str, Any]:
        """Analyze graph structure and properties"""
        ns = self._get_namespace(root)
        structure_info = {
            "graph_count": 0,
            "graphs": [],
            "directed_graphs": 0,
            "undirected_graphs": 0,
            "mixed_graphs": 0,
        }

        graphs = root.findall(f"{ns}graph")
        structure_info["graph_count"] = len(graphs)

        for graph in graphs:
            graph_data = {
                "id": graph.get("id"),
                "edgedefault": graph.get("edgedefault", "undirected"),
                "node_count": len(graph.findall(f"{ns}node")),
                "edge_count": len(graph.findall(f"{ns}edge")),
                "hyperedge_count": len(graph.findall(f"{ns}hyperedge")),
                "subgraph_count": len(graph.findall(f"{ns}graph")),
            }

            # Count graph types
            edge_default = graph_data["edgedefault"]
            if edge_default == "directed":
                structure_info["directed_graphs"] += 1
            elif edge_default == "undirected":
                structure_info["undirected_graphs"] += 1
            else:
                structure_info["mixed_graphs"] += 1

            structure_info["graphs"].append(graph_data)

        return structure_info

    def _analyze_nodes(self, root: Element) -> Dict[str, Any]:
        """Analyze node information"""
        ns = self._get_namespace(root)
        node_info = {
            "node_count": 0,
            "nodes": [],
            "node_attributes": {},
            "isolated_nodes": 0,
            "max_degree": 0,
        }

        nodes = root.findall(f".//{ns}node")
        node_info["node_count"] = len(nodes)

        # Build edge reference map for degree calculation
        edge_map = {}
        edges = root.findall(f".//{ns}edge")
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source:
                edge_map[source] = edge_map.get(source, 0) + 1
            if target and target != source:  # Avoid double counting self-loops
                edge_map[target] = edge_map.get(target, 0) + 1

        for node in nodes[:100]:  # Limit for performance
            node_data = {
                "id": node.get("id"),
                "data_elements": len(node.findall(f"{ns}data")),
                "ports": len(node.findall(f"{ns}port")),
                "degree": edge_map.get(node.get("id"), 0),
            }

            # Track max degree
            node_info["max_degree"] = max(node_info["max_degree"], node_data["degree"])

            # Count isolated nodes
            if node_data["degree"] == 0:
                node_info["isolated_nodes"] += 1

            # Extract node attributes from data elements
            for data in node.findall(f"{ns}data"):
                key = data.get("key")
                if key:
                    if key not in node_info["node_attributes"]:
                        node_info["node_attributes"][key] = 0
                    node_info["node_attributes"][key] += 1

            node_info["nodes"].append(node_data)

        return node_info

    def _analyze_edges(self, root: Element) -> Dict[str, Any]:
        """Analyze edge information"""
        ns = self._get_namespace(root)
        edge_info = {
            "edge_count": 0,
            "edges": [],
            "edge_attributes": {},
            "directed_edges": 0,
            "undirected_edges": 0,
            "self_loops": 0,
            "parallel_edges": 0,
        }

        edges = root.findall(f".//{ns}edge")
        edge_info["edge_count"] = len(edges)

        # Track parallel edges
        edge_pairs = {}

        for edge in edges[:100]:  # Limit for performance
            edge_data = {
                "id": edge.get("id"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "directed": edge.get("directed"),
                "data_elements": len(edge.findall(f"{ns}data")),
            }

            # Count self-loops
            if edge_data["source"] == edge_data["target"]:
                edge_info["self_loops"] += 1

            # Track parallel edges
            if edge_data["source"] and edge_data["target"]:
                pair = tuple(sorted([edge_data["source"], edge_data["target"]]))
                edge_pairs[pair] = edge_pairs.get(pair, 0) + 1

            # Count directed vs undirected
            if edge_data["directed"] == "true":
                edge_info["directed_edges"] += 1
            elif edge_data["directed"] == "false":
                edge_info["undirected_edges"] += 1

            # Extract edge attributes from data elements
            for data in edge.findall(f"{ns}data"):
                key = data.get("key")
                if key:
                    if key not in edge_info["edge_attributes"]:
                        edge_info["edge_attributes"][key] = 0
                    edge_info["edge_attributes"][key] += 1

            edge_info["edges"].append(edge_data)

        # Count parallel edges
        edge_info["parallel_edges"] = sum(
            1 for count in edge_pairs.values() if count > 1
        )

        return edge_info

    def _analyze_attributes(self, root: Element) -> Dict[str, Any]:
        """Analyze attribute key definitions"""
        ns = self._get_namespace(root)
        attr_info = {
            "key_count": 0,
            "keys": [],
            "attribute_domains": {},
            "attribute_types": {},
            "for_types": {},
        }

        keys = root.findall(f"{ns}key")
        attr_info["key_count"] = len(keys)

        for key in keys:
            key_data = {
                "id": key.get("id"),
                "for": key.get("for"),
                "attr_name": key.get("attr.name"),
                "attr_type": key.get("attr.type", "string"),
                "default_value": None,
                "description": None,
            }

            # Extract default value
            default = key.find(f"{ns}default")
            if default is not None and default.text:
                key_data["default_value"] = default.text

            # Extract description
            desc = key.find(f"{ns}desc")
            if desc is not None and desc.text:
                key_data["description"] = desc.text

            # Track attribute domains and types
            if key_data["for"]:
                attr_info["for_types"][key_data["for"]] = (
                    attr_info["for_types"].get(key_data["for"], 0) + 1
                )

            if key_data["attr_type"]:
                attr_info["attribute_types"][key_data["attr_type"]] = (
                    attr_info["attribute_types"].get(key_data["attr_type"], 0) + 1
                )

            attr_info["keys"].append(key_data)

        return attr_info

    def _analyze_data_properties(self, root: Element) -> Dict[str, Any]:
        """Analyze data elements and their properties"""
        ns = self._get_namespace(root)
        data_info = {
            "data_count": 0,
            "data_elements": [],
            "key_usage": {},
            "value_types": {},
            "empty_data": 0,
        }

        data_elements = root.findall(f".//{ns}data")
        data_info["data_count"] = len(data_elements)

        # Build parent mapping for data elements
        parent_map = {}
        for elem in root.iter():
            for child in elem:
                parent_map[child] = elem

        for data in data_elements[:200]:  # Limit for performance
            parent = parent_map.get(data)
            parent_type = parent.tag.split("}")[-1] if parent is not None else None

            data_data = {
                "key": data.get("key"),
                "value": data.text,
                "has_content": bool(data.text and data.text.strip()),
                "parent_type": parent_type,
            }

            # Track key usage
            if data_data["key"]:
                data_info["key_usage"][data_data["key"]] = (
                    data_info["key_usage"].get(data_data["key"], 0) + 1
                )

            # Count empty data
            if not data_data["has_content"]:
                data_info["empty_data"] += 1

            # Analyze value types
            if data_data["value"]:
                value_type = self._detect_value_type(data_data["value"])
                data_info["value_types"][value_type] = (
                    data_info["value_types"].get(value_type, 0) + 1
                )

            data_info["data_elements"].append(data_data)

        return data_info

    def _analyze_layout_information(self, root: Element) -> Dict[str, Any]:
        """Analyze layout and visual information"""
        layout_info = {
            "has_coordinates": False,
            "coordinate_keys": [],
            "visual_attributes": [],
            "geometric_data": False,
        }

        # Look for common layout attribute keys
        coordinate_indicators = ["x", "y", "z", "pos", "position", "coord", "layout"]
        visual_indicators = [
            "color",
            "size",
            "width",
            "height",
            "shape",
            "style",
            "label",
        ]

        for key in root.findall(".//key"):
            attr_name = key.get("attr.name", "").lower()
            key_id = key.get("id", "").lower()

            # Check for coordinate attributes
            if any(
                coord in attr_name or coord in key_id for coord in coordinate_indicators
            ):
                layout_info["has_coordinates"] = True
                layout_info["coordinate_keys"].append(key.get("id"))

            # Check for visual attributes
            if any(
                visual in attr_name or visual in key_id for visual in visual_indicators
            ):
                layout_info["visual_attributes"].append(key.get("id"))

        # Check for geometric data in values
        for data in root.findall(".//data"):
            if data.text:
                # Look for numeric coordinates or geometric data
                if re.search(r"-?\d+\.?\d*,-?\d+\.?\d*", data.text):
                    layout_info["geometric_data"] = True
                    break

        return layout_info

    def _analyze_connectivity(self, root: Element) -> Dict[str, Any]:
        """Analyze graph connectivity patterns"""
        ns = self._get_namespace(root)
        connectivity_info = {
            "total_components": 0,
            "largest_component_size": 0,
            "connectivity_ratio": 0.0,
            "average_degree": 0.0,
            "degree_distribution": {},
        }

        # Build adjacency information
        nodes = set()
        edges = []

        for node in root.findall(f".//{ns}node"):
            node_id = node.get("id")
            if node_id:
                nodes.add(node_id)

        for edge in root.findall(f".//{ns}edge"):
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                edges.append((source, target))

        if nodes:
            # Calculate degree distribution
            degree_count = {}
            for node in nodes:
                degree = sum(1 for s, t in edges if s == node or t == node)
                degree_count[node] = degree

                degree_bin = f"{degree//10*10}-{degree//10*10+9}"
                connectivity_info["degree_distribution"][degree_bin] = (
                    connectivity_info["degree_distribution"].get(degree_bin, 0) + 1
                )

            # Calculate average degree
            total_degree = sum(degree_count.values())
            connectivity_info["average_degree"] = (
                total_degree / len(nodes) if nodes else 0
            )

            # Estimate connectivity (simplified)
            max_possible_edges = len(nodes) * (len(nodes) - 1) // 2
            actual_edges = len(edges)
            connectivity_info["connectivity_ratio"] = (
                actual_edges / max_possible_edges if max_possible_edges > 0 else 0
            )

        return connectivity_info

    def _calculate_network_metrics(self, root: Element) -> Dict[str, Any]:
        """Calculate basic network metrics"""
        metrics = {
            "density": 0.0,
            "avg_clustering": 0.0,
            "diameter_estimate": 0,
            "assortativity_estimate": 0.0,
            "modularity_estimate": 0.0,
        }

        node_count = len(root.findall(".//node"))
        edge_count = len(root.findall(".//edge"))

        # Calculate density
        if node_count > 1:
            max_possible_edges = node_count * (node_count - 1) // 2
            metrics["density"] = (
                edge_count / max_possible_edges if max_possible_edges > 0 else 0
            )

        # Estimate diameter (rough approximation)
        if node_count > 0 and edge_count > 0:
            avg_degree = (2 * edge_count) / node_count
            if avg_degree > 1:
                metrics["diameter_estimate"] = max(
                    2, int(math.log(node_count) / math.log(avg_degree))
                )

        # Simple clustering estimate
        if metrics["density"] > 0:
            metrics["avg_clustering"] = min(metrics["density"] * 2, 1.0)

        return metrics

    def _detect_value_type(self, value: str) -> str:
        """Detect the type of a data value"""
        value = value.strip()

        # Check for numeric types
        try:
            if "." in value:
                float(value)
                return "float"
            else:
                int(value)
                return "integer"
        except ValueError:
            pass

        # Check for boolean
        if value.lower() in ["true", "false", "yes", "no", "1", "0"]:
            return "boolean"

        # Check for URL
        if value.startswith(("http://", "https://", "ftp://")):
            return "url"

        # Check for coordinates
        if re.match(r"-?\d+\.?\d*,-?\d+\.?\d*", value):
            return "coordinates"

        # Check for date-like
        if re.match(r"\d{4}-\d{2}-\d{2}", value):
            return "date"

        return "string"

    def _extract_graph_metadata(self, root: Element) -> Dict[str, Any]:
        """Extract high-level graph metadata"""
        metadata = {
            "file_version": root.get("version"),
            "namespace": root.get("xmlns"),
            "graph_count": len(root.findall(".//graph")),
            "total_nodes": len(root.findall(".//node")),
            "total_edges": len(root.findall(".//edge")),
            "attribute_keys": len(root.findall(".//key")),
            "has_hierarchy": len(root.findall(".//graph//graph")) > 0,
        }

        return metadata

    def _extract_node_catalog(self, root: Element) -> List[Dict[str, Any]]:
        """Extract node catalog with attributes"""
        nodes = []

        for node in root.findall(".//node")[:50]:  # Limit for performance
            node_data = {
                "id": node.get("id"),
                "attributes": {},
                "port_count": len(node.findall(".//port")),
            }

            # Extract node attributes
            for data in node.findall(".//data"):
                key = data.get("key")
                value = data.text
                if key and value:
                    node_data["attributes"][key] = value

            nodes.append(node_data)

        return nodes

    def _extract_edge_catalog(self, root: Element) -> List[Dict[str, Any]]:
        """Extract edge catalog with attributes"""
        edges = []

        for edge in root.findall(".//edge")[:50]:  # Limit for performance
            edge_data = {
                "id": edge.get("id"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "directed": edge.get("directed"),
                "attributes": {},
            }

            # Extract edge attributes
            for data in edge.findall(".//data"):
                key = data.get("key")
                value = data.text
                if key and value:
                    edge_data["attributes"][key] = value

            edges.append(edge_data)

        return edges

    def _extract_attribute_schema(self, root: Element) -> Dict[str, Any]:
        """Extract attribute schema information"""
        schema = {
            "node_attributes": {},
            "edge_attributes": {},
            "graph_attributes": {},
            "all_attributes": {},
        }

        for key in root.findall(".//key"):
            key_info = {
                "id": key.get("id"),
                "name": key.get("attr.name"),
                "type": key.get("attr.type", "string"),
                "domain": key.get("for", "all"),
                "default": None,
                "description": None,
            }

            # Extract default value
            default = key.find(".//default")
            if default is not None and default.text:
                key_info["default"] = default.text

            # Extract description
            desc = key.find(".//desc")
            if desc is not None and desc.text:
                key_info["description"] = desc.text

            # Categorize by domain
            domain = key_info["domain"]
            if domain == "node":
                schema["node_attributes"][key_info["id"]] = key_info
            elif domain == "edge":
                schema["edge_attributes"][key_info["id"]] = key_info
            elif domain == "graph":
                schema["graph_attributes"][key_info["id"]] = key_info

            schema["all_attributes"][key_info["id"]] = key_info

        return schema

    def _extract_network_statistics(self, root: Element) -> Dict[str, Any]:
        """Extract network statistics"""
        stats = {
            "node_count": len(root.findall(".//node")),
            "edge_count": len(root.findall(".//edge")),
            "graph_count": len(root.findall(".//graph")),
            "data_elements": len(root.findall(".//data")),
            "attribute_keys": len(root.findall(".//key")),
            "hyperedge_count": len(root.findall(".//hyperedge")),
            "port_count": len(root.findall(".//port")),
        }

        # Calculate derived statistics
        if stats["node_count"] > 0:
            stats["edges_per_node"] = stats["edge_count"] / stats["node_count"]
            stats["data_per_node"] = stats["data_elements"] / stats["node_count"]
        else:
            stats["edges_per_node"] = 0
            stats["data_per_node"] = 0

        return stats

    def _assess_graph_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess graph data quality metrics"""
        metrics = {
            "completeness": 0.0,
            "consistency": 0.0,
            "connectivity": 0.0,
            "attribute_coverage": 0.0,
            "overall": 0.0,
        }

        # Completeness (presence of essential elements)
        structure = findings["graph_structure"]
        nodes = findings["nodes"]
        edges = findings["edges"]

        completeness_factors = []
        if structure["graph_count"] > 0:
            completeness_factors.append(0.3)
        if nodes["node_count"] > 0:
            completeness_factors.append(0.3)
        if edges["edge_count"] > 0:
            completeness_factors.append(0.2)
        if findings["attributes"]["key_count"] > 0:
            completeness_factors.append(0.2)

        metrics["completeness"] = sum(completeness_factors)

        # Consistency (data integrity)
        data_props = findings["data_properties"]
        consistency_score = 1.0

        if data_props["data_count"] > 0:
            empty_ratio = data_props["empty_data"] / data_props["data_count"]
            consistency_score -= empty_ratio * 0.5

        metrics["consistency"] = max(0.0, consistency_score)

        # Connectivity (network structure quality)
        connectivity = findings["connectivity"]
        metrics["connectivity"] = min(connectivity["connectivity_ratio"] * 2, 1.0)

        # Attribute coverage
        if nodes["node_count"] > 0:
            attr_coverage = len(nodes["node_attributes"]) / max(nodes["node_count"], 1)
            metrics["attribute_coverage"] = min(attr_coverage, 1.0)

        # Overall quality
        metrics["overall"] = (
            metrics["completeness"] * 0.3
            + metrics["consistency"] * 0.25
            + metrics["connectivity"] * 0.25
            + metrics["attribute_coverage"] * 0.2
        )

        return metrics
