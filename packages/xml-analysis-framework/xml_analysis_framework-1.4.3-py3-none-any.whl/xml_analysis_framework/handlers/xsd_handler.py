#!/usr/bin/env python3
"""
XSD (XML Schema Definition) Handler

Analyzes XML Schema files to extract type definitions, validation rules,
and structural constraints for data quality and validation purposes.
"""

import sys
import os
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class XSDSchemaHandler(XMLHandler):
    """Handler for XML Schema Definition files"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for schema elements
        if root.tag.endswith("schema") or root.tag == "schema":
            # Check for XSD namespace
            if any("XMLSchema" in uri for uri in namespaces.values()):
                return True, 1.0
            return True, 0.7

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        target_namespace = root.get("targetNamespace", "none")
        version = root.get("version", "1.0")

        # Check if it's a specific schema type
        schema_type = "Generic XSD"
        if "w3.org" in target_namespace:
            schema_type = "W3C Standard Schema"
        elif "maven" in target_namespace.lower():
            schema_type = "Maven XSD"
        elif "spring" in target_namespace.lower():
            schema_type = "Spring Framework XSD"

        return DocumentTypeInfo(
            type_name="XML Schema Definition",
            confidence=1.0,
            version=version,
            schema_uri=target_namespace,
            metadata={
                "standard": "W3C XSD",
                "category": "schema_definition",
                "target_namespace": target_namespace,
                "schema_type": schema_type,
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "types": self._analyze_types(root),
            "elements": self._analyze_elements(root),
            "attributes": self._analyze_attributes(root),
            "validation_rules": self._extract_validation_rules(root),
            "namespaces": self._analyze_namespaces(root),
            "imports": self._find_imports(root),
            "complexity_metrics": self._calculate_complexity(root),
        }

        recommendations = [
            "Generate sample valid/invalid XML for testing",
            "Extract validation rules for data quality checks",
            "Create documentation from annotations",
            "Identify reusable type definitions",
            "Check for overly restrictive constraints",
            "Monitor schema evolution over time",
        ]

        ai_use_cases = [
            "Automated test data generation",
            "Schema evolution tracking",
            "Data quality rule extraction",
            "Documentation generation",
            "Schema compatibility checking",
            "Type system analysis",
            "Validation rule optimization",
            "Schema migration assistance",
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
                "complex_types": len(findings["types"]["complex"]),
                "simple_types": len(findings["types"]["simple"]),
                "global_elements": len(findings["elements"]["global"]),
                "global_attributes": len(findings["attributes"]["global"]),
                "validation_rules": len(findings["validation_rules"]),
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_schema_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "type_definitions": self._extract_type_definitions(root),
            "element_definitions": self._extract_element_definitions(root),
            "validation_constraints": self._extract_constraints(root),
            "documentation": self._extract_documentation(root),
            "schema_metadata": {
                "target_namespace": root.get("targetNamespace"),
                "element_form_default": root.get("elementFormDefault", "unqualified"),
                "attribute_form_default": root.get(
                    "attributeFormDefault", "unqualified"
                ),
                "version": root.get("version"),
            },
        }

    def _analyze_types(self, root: Element) -> Dict[str, List[Dict[str, Any]]]:
        complex_types = []
        simple_types = []

        # Extract complex types
        for ct in root.findall(".//{http://www.w3.org/2001/XMLSchema}complexType"):
            complex_types.append(
                {
                    "name": ct.get("name", "anonymous"),
                    "abstract": ct.get("abstract", "false") == "true",
                    "mixed": ct.get("mixed", "false") == "true",
                    "base": self._find_base_type(ct),
                    "elements": len(
                        ct.findall(".//{http://www.w3.org/2001/XMLSchema}element")
                    ),
                    "attributes": len(
                        ct.findall(".//{http://www.w3.org/2001/XMLSchema}attribute")
                    ),
                }
            )

        # Extract simple types
        for st in root.findall(".//{http://www.w3.org/2001/XMLSchema}simpleType"):
            simple_types.append(
                {
                    "name": st.get("name", "anonymous"),
                    "base": self._find_restriction_base(st),
                    "constraints": self._extract_simple_constraints(st),
                }
            )

        return {"complex": complex_types, "simple": simple_types}

    def _analyze_elements(self, root: Element) -> Dict[str, Any]:
        global_elements = []
        _ = []  # Local elements for potential future analysis

        # Global elements (direct children of schema)
        for elem in root.findall("./{http://www.w3.org/2001/XMLSchema}element"):
            global_elements.append(
                {
                    "name": elem.get("name"),
                    "type": elem.get("type"),
                    "nillable": elem.get("nillable", "false") == "true",
                    "abstract": elem.get("abstract", "false") == "true",
                    "substitution_group": elem.get("substitutionGroup"),
                }
            )

        # Count local elements
        all_elements = root.findall(".//{http://www.w3.org/2001/XMLSchema}element")
        local_count = len(all_elements) - len(global_elements)

        return {
            "global": global_elements,
            "local_count": local_count,
            "total": len(all_elements),
        }

    def _analyze_attributes(self, root: Element) -> Dict[str, Any]:
        global_attrs = []

        # Global attributes
        for attr in root.findall("./{http://www.w3.org/2001/XMLSchema}attribute"):
            global_attrs.append(
                {
                    "name": attr.get("name"),
                    "type": attr.get("type"),
                    "use": attr.get("use", "optional"),
                    "default": attr.get("default"),
                }
            )

        # Attribute groups
        attr_groups = root.findall(
            ".//{http://www.w3.org/2001/XMLSchema}attributeGroup[@name]"
        )

        return {
            "global": global_attrs,
            "groups": [{"name": ag.get("name")} for ag in attr_groups],
            "total": len(
                root.findall(".//{http://www.w3.org/2001/XMLSchema}attribute")
            ),
        }

    def _extract_validation_rules(self, root: Element) -> List[Dict[str, Any]]:
        rules = []

        # Extract all restrictions
        for restriction in root.findall(
            ".//{http://www.w3.org/2001/XMLSchema}restriction"
        ):
            base = restriction.get("base", "unknown")
            constraints = {}

            # Common facets
            facets = [
                "minLength",
                "maxLength",
                "pattern",
                "enumeration",
                "minInclusive",
                "maxInclusive",
                "minExclusive",
                "maxExclusive",
                "totalDigits",
                "fractionDigits",
                "whiteSpace",
            ]

            for facet in facets:
                elements = restriction.findall(
                    f".//{{http://www.w3.org/2001/XMLSchema}}{facet}"
                )
                if elements:
                    if facet == "enumeration":
                        constraints[facet] = [e.get("value") for e in elements]
                    elif len(elements) == 1:
                        constraints[facet] = elements[0].get("value")
                    else:
                        constraints[facet] = [e.get("value") for e in elements]

            if constraints:
                rules.append({"base_type": base, "constraints": constraints})

        # Extract key/keyref constraints
        for key in root.findall(".//{http://www.w3.org/2001/XMLSchema}key"):
            rules.append(
                {
                    "type": "key",
                    "name": key.get("name"),
                    "selector": key.find(
                        ".//{http://www.w3.org/2001/XMLSchema}selector"
                    ).get("xpath", ""),
                    "fields": [
                        f.get("xpath", "")
                        for f in key.findall(
                            ".//{http://www.w3.org/2001/XMLSchema}field"
                        )
                    ],
                }
            )

        return rules

    def _analyze_namespaces(self, root: Element) -> Dict[str, Any]:
        imports = []
        includes = []

        for imp in root.findall("./{http://www.w3.org/2001/XMLSchema}import"):
            imports.append(
                {
                    "namespace": imp.get("namespace"),
                    "location": imp.get("schemaLocation"),
                }
            )

        for inc in root.findall("./{http://www.w3.org/2001/XMLSchema}include"):
            includes.append({"location": inc.get("schemaLocation")})

        return {
            "target": root.get("targetNamespace"),
            "imports": imports,
            "includes": includes,
        }

    def _find_imports(self, root: Element) -> List[Dict[str, str]]:
        imports = []

        for imp in root.findall(".//{http://www.w3.org/2001/XMLSchema}import"):
            imports.append(
                {
                    "namespace": imp.get("namespace", ""),
                    "location": imp.get("schemaLocation", ""),
                }
            )

        return imports

    def _calculate_complexity(self, root: Element) -> Dict[str, Any]:
        # Count various elements to assess complexity
        metrics = {
            "total_types": len(
                root.findall(".//{http://www.w3.org/2001/XMLSchema}complexType")
            )
            + len(root.findall(".//{http://www.w3.org/2001/XMLSchema}simpleType")),
            "total_elements": len(
                root.findall(".//{http://www.w3.org/2001/XMLSchema}element")
            ),
            "total_attributes": len(
                root.findall(".//{http://www.w3.org/2001/XMLSchema}attribute")
            ),
            "max_nesting": self._calculate_max_nesting(root),
            "has_recursion": self._check_recursion(root),
            "uses_substitution_groups": len(root.findall(".//*[@substitutionGroup]"))
            > 0,
            "uses_abstract_types": len(root.findall('.//*[@abstract="true"]')) > 0,
        }

        # Calculate complexity score
        complexity_score = (
            min(metrics["total_types"] / 50, 1.0) * 0.3
            + min(metrics["total_elements"] / 100, 1.0) * 0.3
            + min(metrics["max_nesting"] / 10, 1.0) * 0.2
            + (0.2 if metrics["has_recursion"] else 0.0)
        )

        metrics["complexity_score"] = round(complexity_score, 2)

        return metrics

    def _find_base_type(self, complex_type: Element) -> Optional[str]:
        # Check for extension
        extension = complex_type.find(".//{http://www.w3.org/2001/XMLSchema}extension")
        if extension is not None:
            return extension.get("base")

        # Check for restriction
        restriction = complex_type.find(
            ".//{http://www.w3.org/2001/XMLSchema}restriction"
        )
        if restriction is not None:
            return restriction.get("base")

        return None

    def _find_restriction_base(self, simple_type: Element) -> Optional[str]:
        restriction = simple_type.find(
            "./{http://www.w3.org/2001/XMLSchema}restriction"
        )
        if restriction is not None:
            return restriction.get("base")

        # Check for list
        list_elem = simple_type.find("./{http://www.w3.org/2001/XMLSchema}list")
        if list_elem is not None:
            return f"list of {list_elem.get('itemType', 'unknown')}"

        # Check for union
        union_elem = simple_type.find("./{http://www.w3.org/2001/XMLSchema}union")
        if union_elem is not None:
            return f"union of {union_elem.get('memberTypes', 'multiple types')}"

        return None

    def _extract_simple_constraints(self, simple_type: Element) -> Dict[str, Any]:
        constraints = {}
        restriction = simple_type.find(
            "./{http://www.w3.org/2001/XMLSchema}restriction"
        )

        if restriction is not None:
            # Extract enumeration values
            enums = restriction.findall(
                "./{http://www.w3.org/2001/XMLSchema}enumeration"
            )
            if enums:
                constraints["enumeration"] = [e.get("value") for e in enums]

            # Extract pattern
            pattern = restriction.find("./{http://www.w3.org/2001/XMLSchema}pattern")
            if pattern is not None:
                constraints["pattern"] = pattern.get("value")

            # Extract length constraints
            for constraint in ["minLength", "maxLength", "length"]:
                elem = restriction.find(
                    f".//{{http://www.w3.org/2001/XMLSchema}}{constraint}"
                )
                if elem is not None:
                    constraints[constraint] = elem.get("value")

        return constraints

    def _extract_type_definitions(self, root: Element) -> List[Dict[str, Any]]:
        # Return first 20 type definitions with details
        types = []

        for ct in root.findall(
            ".//{http://www.w3.org/2001/XMLSchema}complexType[@name]"
        )[:10]:
            types.append(
                {
                    "name": ct.get("name"),
                    "kind": "complex",
                    "abstract": ct.get("abstract", "false") == "true",
                    "documentation": self._get_documentation(ct),
                }
            )

        for st in root.findall(
            ".//{http://www.w3.org/2001/XMLSchema}simpleType[@name]"
        )[:10]:
            types.append(
                {
                    "name": st.get("name"),
                    "kind": "simple",
                    "base": self._find_restriction_base(st),
                    "documentation": self._get_documentation(st),
                }
            )

        return types

    def _extract_element_definitions(self, root: Element) -> List[Dict[str, Any]]:
        # Return global element definitions
        elements = []

        for elem in root.findall("./{http://www.w3.org/2001/XMLSchema}element")[:20]:
            elements.append(
                {
                    "name": elem.get("name"),
                    "type": elem.get("type"),
                    "min_occurs": elem.get("minOccurs", "1"),
                    "max_occurs": elem.get("maxOccurs", "1"),
                    "documentation": self._get_documentation(elem),
                }
            )

        return elements

    def _extract_constraints(self, root: Element) -> List[Dict[str, Any]]:
        # Extract unique/key/keyref constraints
        constraints = []

        for constraint_type in ["unique", "key", "keyref"]:
            for elem in root.findall(
                f".//{{http://www.w3.org/2001/XMLSchema}}{constraint_type}"
            ):
                constraints.append(
                    {
                        "type": constraint_type,
                        "name": elem.get("name"),
                        "refer": elem.get("refer"),  # for keyref
                    }
                )

        return constraints

    def _extract_documentation(self, root: Element) -> Dict[str, List[str]]:
        docs = {}

        for elem in root.findall(".//*[@name]"):
            doc = self._get_documentation(elem)
            if doc:
                elem_name = elem.get("name")
                elem_type = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                key = f"{elem_type}:{elem_name}"
                docs[key] = doc

        return docs

    def _get_documentation(self, element: Element) -> Optional[str]:
        annotation = element.find("./{http://www.w3.org/2001/XMLSchema}annotation")
        if annotation is not None:
            doc = annotation.find("./{http://www.w3.org/2001/XMLSchema}documentation")
            if doc is not None and doc.text:
                return doc.text.strip()
        return None

    def _calculate_max_nesting(self, root: Element) -> int:
        # Simplified calculation of nesting depth
        max_depth = 0

        def check_depth(elem, depth=0):
            nonlocal max_depth
            max_depth = max(max_depth, depth)

            # Check sequences and choices
            for container in elem.findall(
                ".//{http://www.w3.org/2001/XMLSchema}sequence"
            ) + elem.findall(".//{http://www.w3.org/2001/XMLSchema}choice"):
                check_depth(container, depth + 1)

        for ct in root.findall(".//{http://www.w3.org/2001/XMLSchema}complexType"):
            check_depth(ct)

        return max_depth

    def _check_recursion(self, root: Element) -> bool:
        # Simplified check for recursive type definitions
        type_refs = {}

        # Build reference map
        for elem in root.findall(".//{http://www.w3.org/2001/XMLSchema}element[@type]"):
            elem_type = elem.get("type")
            parent = elem
            while parent is not None:
                parent = parent.find("..")
                if parent is not None and parent.get("name"):
                    parent_name = parent.get("name")
                    if parent_name not in type_refs:
                        type_refs[parent_name] = set()
                    type_refs[parent_name].add(elem_type)
                    break

        # Check for cycles (simplified)
        for type_name, refs in type_refs.items():
            if type_name in refs:
                return True

        return False

    def _assess_schema_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        # Assess various quality aspects
        metrics = findings["complexity_metrics"]

        # Documentation coverage
        doc_count = len(findings.get("documentation", {}))
        total_named = (
            len(findings["types"]["complex"])
            + len(findings["types"]["simple"])
            + len(findings["elements"]["global"])
        )
        doc_coverage = doc_count / max(total_named, 1)

        # Reusability (global vs local definitions)
        global_count = len(findings["types"]["complex"]) + len(
            findings["types"]["simple"]
        )
        reusability = min(global_count / 20, 1.0)  # Assume 20+ global types is good

        # Constraint usage
        constraint_score = min(len(findings["validation_rules"]) / 10, 1.0)

        return {
            "documentation": doc_coverage,
            "reusability": reusability,
            "validation_completeness": constraint_score,
            "complexity": 1.0
            - metrics["complexity_score"],  # Lower complexity is better
            "maintainability": (
                doc_coverage + reusability + (1.0 - metrics["complexity_score"])
            )
            / 3,
        }
