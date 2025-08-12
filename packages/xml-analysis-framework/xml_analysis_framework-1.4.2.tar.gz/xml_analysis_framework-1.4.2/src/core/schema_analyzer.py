#!/usr/bin/env python3
"""
Fixed XML Schema Analyzer for Large Files

Handles very large XML files efficiently using iterative parsing
instead of recursive analysis to avoid stack overflow.
"""

import defusedxml.ElementTree as ET
from collections import defaultdict
import json
import sys
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ElementInfo:
    """Information about an XML element"""

    tag: str
    count: int
    depth_levels: Set[int]
    attributes: Dict[str, Set[str]]
    text_patterns: List[str]
    parent_elements: Set[str]
    child_elements: Set[str]


@dataclass
class XMLSchema:
    """Complete XML schema information"""

    root_element: str
    namespaces: Dict[str, str]
    elements: Dict[str, ElementInfo]
    max_depth: int
    total_elements: int
    structure_tree: Dict[str, Any]
    sample_paths: List[str]


class XMLSchemaAnalyzer:
    def __init__(self, max_samples=3, max_text_length=100, max_analysis_depth=15):
        self.max_samples = max_samples
        self.max_text_length = max_text_length
        self.max_analysis_depth = max_analysis_depth  # Prevent infinite analysis

        self.elements = defaultdict(
            lambda: ElementInfo(
                tag="",
                count=0,
                depth_levels=set(),
                attributes=defaultdict(set),
                text_patterns=[],
                parent_elements=set(),
                child_elements=set(),
            )
        )
        self.namespaces = {}
        self.structure_tree = {}
        self.sample_paths = []
        self.max_depth = 0

        # Set a reasonable recursion limit
        sys.setrecursionlimit(3000)

    def clean_tag(self, tag: str) -> str:
        """Remove namespace prefix from tag for cleaner analysis"""
        return tag.split("}")[-1] if "}" in tag else tag

    def get_namespace(self, tag: str) -> Optional[str]:
        """Extract namespace from tag"""
        if "}" in tag:
            return tag.split("}")[0][1:]  # Remove leading {
        return None

    def analyze_file_iterative(self, file_path: str) -> XMLSchema:
        """Analyze XML file using iterative parsing for large files"""
        print(f"Using iterative parsing for large file: {file_path}")

        # Use iterparse for memory-efficient parsing
        context = ET.iterparse(file_path, events=("start", "end", "start-ns"))

        element_stack: List[Any] = []
        path_stack: List[str] = []
        elements_processed = 0
        max_elements = 50000  # Limit analysis to prevent excessive processing

        root_element = None

        try:
            for event, elem in context:
                if elements_processed > max_elements:
                    print(f"Reached analysis limit of {max_elements} elements")
                    break

                if event == "start-ns":
                    # Handle namespace declarations
                    prefix, uri = elem
                    self.namespaces[prefix or "default"] = uri

                elif event == "start":
                    if root_element is None:
                        root_element = self.clean_tag(elem.tag)

                    clean_tag = self.clean_tag(elem.tag)
                    depth = len(element_stack)

                    # Limit depth analysis
                    if depth > self.max_analysis_depth:
                        continue

                    self.max_depth = max(self.max_depth, depth)

                    # Update element info
                    element_info = self.elements[clean_tag]
                    element_info.tag = clean_tag
                    element_info.count += 1
                    element_info.depth_levels.add(depth)

                    # Parent-child relationships
                    if element_stack:
                        parent_tag = element_stack[-1]
                        element_info.parent_elements.add(parent_tag)
                        self.elements[parent_tag].child_elements.add(clean_tag)

                    # Analyze attributes (limit to avoid memory issues)
                    for attr_name, attr_value in list(elem.attrib.items())[:10]:
                        clean_attr = self.clean_tag(attr_name)
                        # Limit attribute value length and count
                        if len(element_info.attributes[clean_attr]) < 5:
                            element_info.attributes[clean_attr].add(attr_value[:50])

                    # Store sample paths
                    if depth <= 3 and len(self.sample_paths) < 20:
                        current_path = "/".join(path_stack + [clean_tag])
                        self.sample_paths.append(current_path)

                    element_stack.append(clean_tag)
                    path_stack.append(clean_tag)
                    elements_processed += 1

                elif event == "end":
                    clean_tag = self.clean_tag(elem.tag)

                    # Store text content if present and not too deep
                    if (
                        elem.text
                        and elem.text.strip()
                        and len(element_stack) <= self.max_analysis_depth
                    ):
                        if clean_tag in self.elements:
                            element_info = self.elements[clean_tag]
                            if len(element_info.text_patterns) < self.max_samples:
                                text = elem.text.strip()[: self.max_text_length]
                                if text:  # Only store non-empty text
                                    element_info.text_patterns.append(text)

                    # Pop from stacks
                    if element_stack and element_stack[-1] == clean_tag:
                        element_stack.pop()
                    if path_stack and path_stack[-1] == clean_tag:
                        path_stack.pop()

                    # Clear element to save memory
                    elem.clear()

                # Progress indicator for very large files
                if elements_processed % 10000 == 0 and elements_processed > 0:
                    print(f"Processed {elements_processed:,} elements...")

        except Exception as e:
            print(f"Warning: Parsing stopped early due to: {e}")
            print(f"Analyzed {elements_processed:,} elements before stopping")

        # Build structure tree (limited depth to avoid recursion issues)
        self.structure_tree = self._build_structure_tree_iterative()

        # Create schema
        total_elements = sum(info.count for info in self.elements.values())

        return XMLSchema(
            root_element=root_element or "unknown",
            namespaces=self.namespaces,
            elements=dict(self.elements),  # Convert defaultdict
            max_depth=self.max_depth,
            total_elements=total_elements,
            structure_tree=self.structure_tree,
            sample_paths=self.sample_paths,
        )

    def _build_structure_tree_iterative(self) -> Dict[str, Any]:
        """Build structure tree without recursion"""
        tree = {}

        # Find root elements (no parents)
        root_elements = []
        for tag, info in self.elements.items():
            if not info.parent_elements:
                root_elements.append(tag)

        # Build tree for each root (limit depth)
        for root_tag in root_elements:
            tree[root_tag] = self._build_subtree_limited(root_tag, max_depth=5)

        return tree

    def _build_subtree_limited(
        self, tag: str, current_depth=0, max_depth=5
    ) -> Dict[str, Any]:
        """Build subtree with depth limit to avoid recursion issues"""
        if current_depth >= max_depth or tag not in self.elements:
            return {"truncated": True}

        info = self.elements[tag]
        node = {
            "count": info.count,
            "attributes": list(info.attributes.keys())[:5],  # Limit attributes shown
            "has_text": len(info.text_patterns) > 0,
            "children": {},
        }

        # Add children (limited)
        for child_tag in list(info.child_elements)[:10]:  # Limit children
            if child_tag in self.elements:
                node["children"][child_tag] = self._build_subtree_limited(
                    child_tag, current_depth + 1, max_depth
                )

        return node

    def analyze_file(self, file_path: str) -> XMLSchema:
        """Main analysis method - chooses appropriate strategy"""
        import os

        file_size = os.path.getsize(file_path)
        size_mb = file_size / (1024 * 1024)

        print(f"File size: {size_mb:.1f} MB")

        # Use iterative parsing for files larger than 5MB
        if size_mb > 5:
            return self.analyze_file_iterative(file_path)
        else:
            # For smaller files, use the original method but with safety limits
            return self.analyze_file_iterative(file_path)

    def generate_llm_description(self, schema: XMLSchema) -> str:
        """Generate a concise description suitable for LLM consumption"""
        description = f"""XML Document Schema Analysis

Document Type: {schema.root_element}
Total Elements: {schema.total_elements:,}
Maximum Depth: {schema.max_depth}
Unique Element Types: {len(schema.elements)}

NAMESPACES:
{json.dumps(schema.namespaces, indent=2)}

DOCUMENT STRUCTURE:
Root: {schema.root_element}
Sample Paths: {', '.join(schema.sample_paths[:10])}

KEY ELEMENTS (Top 10 by frequency):
"""

        # Sort elements by count
        sorted_elements = sorted(
            schema.elements.items(), key=lambda x: x[1].count, reverse=True
        )[:10]

        for tag, info in sorted_elements:
            attrs_summary = (
                f"[{len(info.attributes)} attrs]" if info.attributes else "[no attrs]"
            )
            text_summary = "[has text]" if info.text_patterns else "[no text]"
            children_summary = (
                f"[{len(info.child_elements)} children]"
                if info.child_elements
                else "[leaf]"
            )

            description += (
                f"\n- {tag}: {info.count:,} occurrences, "
                f"depths {sorted(info.depth_levels)[:5]} {attrs_summary} "
                f"{text_summary} {children_summary}"
            )

            # Show key attributes
            if info.attributes:
                key_attrs = list(info.attributes.keys())[:3]
                description += f"\n  Key attributes: {', '.join(key_attrs)}"

            # Show sample text
            if info.text_patterns:
                sample_text = info.text_patterns[0][:50]
                description += f'\n  Sample text: "{sample_text}..."'

        # Simplified structure tree (avoid deep nesting in output)
        description += "\n\nSTRUCTURE SUMMARY:\n"
        for root_elem, tree_info in list(schema.structure_tree.items())[:3]:
            description += f"- {root_elem}: {tree_info.get('count', 0)} occurrences\n"
            if "children" in tree_info:
                child_count = len(tree_info["children"])
                if child_count > 0:
                    child_names = list(tree_info["children"].keys())[:5]
                    description += (
                        f"  Children ({child_count}): {', '.join(child_names)}\n"
                    )

        return description


def analyze_xml_file(file_path: str, output_json: bool = False) -> str:
    """Main function to analyze XML file"""
    analyzer = XMLSchemaAnalyzer(max_samples=3, max_analysis_depth=15)
    schema = analyzer.analyze_file(file_path)

    if output_json:
        # Convert to dict for JSON serialization
        schema_dict = asdict(schema)
        # Convert sets to lists for JSON
        for element_info in schema_dict["elements"].values():
            if "depth_levels" in element_info:
                element_info["depth_levels"] = list(element_info["depth_levels"])
            if "parent_elements" in element_info:
                element_info["parent_elements"] = list(element_info["parent_elements"])
            if "child_elements" in element_info:
                element_info["child_elements"] = list(element_info["child_elements"])
            if "attributes" in element_info:
                for attr_name in element_info["attributes"]:
                    element_info["attributes"][attr_name] = list(
                        element_info["attributes"][attr_name]
                    )

        return json.dumps(schema_dict, indent=2)
    else:
        return analyzer.generate_llm_description(schema)


if __name__ == "__main__":
    import sys  # noqa: F811

    if len(sys.argv) < 2:
        print("Usage: python xml_analyzer.py <xml_file> [--json]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_json = "--json" in sys.argv

    try:
        result = analyze_xml_file(file_path, output_json)
        print(result)
    except Exception as e:
        print(f"Error analyzing XML file: {e}")
        sys.exit(1)
