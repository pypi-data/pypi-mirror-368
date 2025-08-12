#!/usr/bin/env python3
"""
SVG Handler

Analyzes SVG (Scalable Vector Graphics) documents for design pattern recognition,
accessibility analysis, style extraction, and vector graphic optimization.
"""

import re
import sys
import os
from typing import Dict, List, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class SVGHandler(XMLHandler):
    """Handler for SVG (Scalable Vector Graphics) documents"""

    SVG_NAMESPACE = "http://www.w3.org/2000/svg"

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for SVG root element
        if root.tag == f"{{{self.SVG_NAMESPACE}}}svg" or root.tag == "svg":
            return True, 1.0

        # Check for SVG namespace in declared namespaces
        for uri in namespaces.values():
            if self.SVG_NAMESPACE in uri:
                return True, 0.9

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Determine SVG version
        version = root.get("version", "1.1")

        # Detect SVG type/purpose
        svg_type = self._detect_svg_type(root)

        metadata = {
            "standard": "W3C SVG",
            "category": "graphics",
            "svg_type": svg_type,
            "has_animations": self._check_animations(root),
            "has_scripts": self._has_scripts(root),
            "element_count": len(list(root.iter())),
            "has_accessibility": self._check_accessibility(root),
        }

        return DocumentTypeInfo(
            type_name="SVG Graphics", confidence=1.0, version=version, metadata=metadata
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "svg_info": {
                "version": root.get("version", "1.1"),
                "svg_type": self._detect_svg_type(root),
                "namespace": self._extract_namespace_info(root),
            },
            "dimensions": self._analyze_dimensions(root),
            "elements": self._analyze_elements(root),
            "graphics": self._analyze_graphics_content(root),
            "styles": self._analyze_styles(root),
            "accessibility": self._analyze_accessibility(root),
            "animations": self._analyze_animations(root),
            "scripts": self._analyze_scripts(root),
            "optimization": self._analyze_optimization_opportunities(root),
            "security": self._analyze_security_aspects(root),
        }

        recommendations = [
            "Extract for design system documentation",
            "Analyze for accessibility improvements (title, desc, ARIA labels)",
            "Optimize path data and remove unnecessary elements",
            "Convert to other formats for broader compatibility",
            "Review script usage for security implications",
            "Implement responsive design with viewBox",
            "Add semantic structure with groups and labels",
            "Optimize colors and gradients for performance",
        ]

        ai_use_cases = [
            "Automatic icon and graphic classification",
            "Design pattern recognition and extraction",
            "Accessibility compliance analysis and enhancement",
            "Style guide generation for design systems",
            "Vector graphic optimization and compression",
            "Automated color palette extraction",
            "Logo and brand asset management",
            "SVG animation analysis and optimization",
            "Cross-platform compatibility assessment",
        ]

        data_inventory = {
            "total_elements": len(findings["elements"]["element_details"]),
            "graphic_elements": len(findings["graphics"]["graphic_elements"]),
            "text_elements": len(findings["graphics"]["text_elements"]),
            "style_definitions": len(findings["styles"]["style_definitions"]),
            "animations": len(findings["animations"]["animation_elements"]),
        }

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
            data_inventory=data_inventory,
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_svg_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "svg_metadata": {
                "version": root.get("version", "1.1"),
                "type": self._detect_svg_type(root),
                "dimensions": self._extract_dimension_summary(root),
            },
            "design_summary": self._extract_design_summary(root),
            "accessibility_summary": self._extract_accessibility_summary(root),
            "technical_summary": self._extract_technical_summary(root),
        }

    def _detect_svg_type(self, root: Element) -> str:
        """Detect the type/purpose of the SVG"""
        # Count different types of elements to infer purpose
        element_counts = self._count_svg_elements(root)

        # Check for common icon patterns
        if element_counts.get("path", 0) > 0 and len(list(root.iter())) < 20:
            return "Icon"

        # Check for logo patterns
        if element_counts.get("text", 0) > 0 and (
            element_counts.get("path", 0) > 0 or element_counts.get("g", 0) > 0
        ):
            return "Logo"

        # Check for illustration patterns
        if element_counts.get("g", 0) > 3 and len(list(root.iter())) > 50:
            return "Illustration"

        # Check for chart/diagram patterns
        if element_counts.get("line", 0) > 0 or element_counts.get("rect", 0) > 5:
            return "Chart/Diagram"

        # Check for animation
        if self._check_animations(root):
            return "Animation"

        return "Graphic"

    def _extract_namespace_info(self, root: Element) -> Dict[str, Any]:
        """Extract namespace information"""
        namespaces = {}
        for key, value in root.attrib.items():
            if key.startswith("xmlns"):
                prefix = key.split(":", 1)[1] if ":" in key else "default"
                namespaces[prefix] = value

        return {
            "declared_namespaces": namespaces,
            "svg_namespace": self.SVG_NAMESPACE in str(namespaces.values()),
            "xlink_namespace": "xlink" in namespaces,
        }

    def _analyze_dimensions(self, root: Element) -> Dict[str, Any]:
        """Analyze SVG dimensions and viewport"""
        return {
            "width": root.get("width"),
            "height": root.get("height"),
            "viewBox": root.get("viewBox"),
            "preserveAspectRatio": root.get("preserveAspectRatio"),
            "has_responsive_design": root.get("viewBox") is not None,
            "has_fixed_dimensions": root.get("width") is not None
            and root.get("height") is not None,
            "viewport_info": self._parse_viewport(root),
        }

    def _analyze_elements(self, root: Element) -> Dict[str, Any]:
        """Analyze SVG elements structure"""
        element_info = {
            "total_elements": 0,
            "element_details": [],
            "element_counts": {},
            "max_depth": 0,
            "group_structure": [],
        }

        # Count all elements
        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            element_info["element_counts"][tag] = (
                element_info["element_counts"].get(tag, 0) + 1
            )
            element_info["total_elements"] += 1

            # Analyze individual elements
            element_detail = {
                "tag": tag,
                "id": elem.get("id"),
                "class": elem.get("class"),
                "has_style": elem.get("style") is not None,
                "has_transform": elem.get("transform") is not None,
            }
            element_info["element_details"].append(element_detail)

        # Calculate structure metrics
        element_info["max_depth"] = self._calculate_max_depth(root)
        element_info["group_structure"] = self._analyze_group_structure(root)

        return element_info

    def _analyze_graphics_content(self, root: Element) -> Dict[str, Any]:
        """Analyze graphics content types"""
        graphics_info = {
            "graphic_elements": [],
            "text_elements": [],
            "shapes": [],
            "paths": [],
            "images": [],
            "use_elements": [],
        }

        graphic_tags = [
            "rect",
            "circle",
            "ellipse",
            "line",
            "polyline",
            "polygon",
            "path",
        ]

        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if tag in graphic_tags:
                graphics_info["graphic_elements"].append(
                    {
                        "type": tag,
                        "id": elem.get("id"),
                        "style": elem.get("style"),
                        "fill": elem.get("fill"),
                        "stroke": elem.get("stroke"),
                    }
                )

                if tag == "path":
                    graphics_info["paths"].append(
                        {
                            "id": elem.get("id"),
                            "data": elem.get("d"),
                            "length": len(elem.get("d", "")),
                        }
                    )
                else:
                    graphics_info["shapes"].append({"type": tag, "id": elem.get("id")})

            elif tag == "text":
                graphics_info["text_elements"].append(
                    {
                        "content": elem.text,
                        "x": elem.get("x"),
                        "y": elem.get("y"),
                        "font_family": elem.get("font-family"),
                        "font_size": elem.get("font-size"),
                    }
                )

            elif tag == "image":
                graphics_info["images"].append(
                    {
                        "href": elem.get("href")
                        or elem.get("{http://www.w3.org/1999/xlink}href"),
                        "width": elem.get("width"),
                        "height": elem.get("height"),
                    }
                )

            elif tag == "use":
                graphics_info["use_elements"].append(
                    {
                        "href": elem.get("href")
                        or elem.get("{http://www.w3.org/1999/xlink}href"),
                        "x": elem.get("x"),
                        "y": elem.get("y"),
                    }
                )

        return graphics_info

    def _analyze_styles(self, root: Element) -> Dict[str, Any]:
        """Analyze styling approaches"""
        style_info = {
            "style_definitions": [],
            "inline_styles": 0,
            "class_usage": 0,
            "colors": [],
            "fonts": [],
            "css_rules": [],
        }

        # Find style elements
        for style_elem in root.findall(".//style"):
            if style_elem.text:
                style_info["style_definitions"].append(
                    {
                        "content": style_elem.text,
                        "type": style_elem.get("type", "text/css"),
                    }
                )

                # Extract CSS rules
                css_content = style_elem.text
                rules = re.findall(r"([^{]+)\s*\{([^}]+)\}", css_content)
                for selector, properties in rules:
                    style_info["css_rules"].append(
                        {"selector": selector.strip(), "properties": properties.strip()}
                    )

        # Count inline styles and classes
        for elem in root.iter():
            if elem.get("style"):
                style_info["inline_styles"] += 1

                # Extract colors from inline styles
                style_text = elem.get("style", "")
                colors = re.findall(r"(?:fill|stroke|color):\s*([^;]+)", style_text)
                style_info["colors"].extend(colors)

            if elem.get("class"):
                style_info["class_usage"] += 1

            # Extract colors from attributes
            for attr in ["fill", "stroke", "color"]:
                if elem.get(attr):
                    style_info["colors"].append(elem.get(attr))

            # Extract fonts
            for attr in ["font-family", "font-face"]:
                if elem.get(attr):
                    style_info["fonts"].append(elem.get(attr))

        # Remove duplicates and filter colors
        style_info["colors"] = list(
            set([c for c in style_info["colors"] if c not in ["none", "transparent"]])
        )
        style_info["fonts"] = list(set(style_info["fonts"]))

        return style_info

    def _analyze_accessibility(self, root: Element) -> Dict[str, Any]:
        """Analyze accessibility features"""
        accessibility_info = {
            "has_title": False,
            "has_description": False,
            "aria_labels": 0,
            "role_attributes": 0,
            "alt_text_coverage": 0,
            "accessibility_score": 0.0,
            "recommendations": [],
        }

        # Check for title
        if root.find(".//title") is not None:
            accessibility_info["has_title"] = True
        else:
            accessibility_info["recommendations"].append(
                "Add title element for screen readers"
            )

        # Check for description
        if root.find(".//desc") is not None:
            accessibility_info["has_description"] = True
        else:
            accessibility_info["recommendations"].append(
                "Add description element for context"
            )

        # Count ARIA attributes
        for elem in root.iter():
            if elem.get("aria-label") or elem.get("aria-labelledby"):
                accessibility_info["aria_labels"] += 1
            if elem.get("role"):
                accessibility_info["role_attributes"] += 1

        # Calculate accessibility score
        score = 0
        if accessibility_info["has_title"]:
            score += 0.4
        if accessibility_info["has_description"]:
            score += 0.3
        if accessibility_info["aria_labels"] > 0:
            score += 0.2
        if accessibility_info["role_attributes"] > 0:
            score += 0.1

        accessibility_info["accessibility_score"] = score

        return accessibility_info

    def _analyze_animations(self, root: Element) -> Dict[str, Any]:
        """Analyze SVG animations"""
        animation_info = {
            "has_animations": False,
            "animation_elements": [],
            "animation_types": {},
            "css_animations": 0,
        }

        animation_tags = [
            "animate",
            "animateTransform",
            "animateMotion",
            "set",
            "animateColor",
        ]

        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if tag in animation_tags:
                animation_info["has_animations"] = True
                animation_detail = {
                    "type": tag,
                    "attributeName": elem.get("attributeName"),
                    "dur": elem.get("dur"),
                    "repeatCount": elem.get("repeatCount"),
                    "values": elem.get("values"),
                }
                animation_info["animation_elements"].append(animation_detail)
                animation_info["animation_types"][tag] = (
                    animation_info["animation_types"].get(tag, 0) + 1
                )

        # Check for CSS animations in style elements
        for style_elem in root.findall(".//style"):
            if style_elem.text and (
                "animation" in style_elem.text or "keyframes" in style_elem.text
            ):
                animation_info["css_animations"] += 1

        return animation_info

    def _analyze_scripts(self, root: Element) -> Dict[str, Any]:
        """Analyze embedded scripts"""
        script_info = {
            "has_scripts": False,
            "script_count": 0,
            "script_types": [],
            "external_scripts": [],
            "inline_scripts": [],
        }

        for script_elem in root.findall(".//script"):
            script_info["has_scripts"] = True
            script_info["script_count"] += 1

            script_type = script_elem.get("type", "application/javascript")
            script_info["script_types"].append(script_type)

            href = script_elem.get("href") or script_elem.get(
                "{http://www.w3.org/1999/xlink}href"
            )
            if href:
                script_info["external_scripts"].append(href)
            elif script_elem.text:
                script_info["inline_scripts"].append(
                    {
                        "content": script_elem.text[:100],  # First 100 chars
                        "length": len(script_elem.text),
                    }
                )

        return script_info

    def _analyze_optimization_opportunities(self, root: Element) -> Dict[str, Any]:
        """Analyze optimization opportunities"""
        optimization_info = {
            "unused_definitions": 0,
            "redundant_groups": 0,
            "long_paths": 0,
            "optimization_score": 0.0,
            "recommendations": [],
        }

        # Check for unused definitions
        defs = root.find(".//defs")
        if defs is not None:
            defined_ids = set(elem.get("id") for elem in defs.iter() if elem.get("id"))
            used_ids = set()

            for elem in root.iter():
                href = elem.get("href") or elem.get(
                    "{http://www.w3.org/1999/xlink}href"
                )
                if href and href.startswith("#"):
                    used_ids.add(href[1:])

            optimization_info["unused_definitions"] = len(defined_ids - used_ids)

        # Check for long path data
        for path_elem in root.findall(".//path"):
            path_data = path_elem.get("d", "")
            if len(path_data) > 1000:  # Arbitrary threshold
                optimization_info["long_paths"] += 1

        # Check for redundant groups
        groups = root.findall(".//g")
        single_child_groups = sum(1 for g in groups if len(list(g)) == 1)
        optimization_info["redundant_groups"] = single_child_groups

        # Generate recommendations
        if optimization_info["unused_definitions"] > 0:
            optimization_info["recommendations"].append("Remove unused definitions")
        if optimization_info["long_paths"] > 0:
            optimization_info["recommendations"].append(
                "Optimize path data for smaller file size"
            )
        if optimization_info["redundant_groups"] > 0:
            optimization_info["recommendations"].append(
                "Remove unnecessary group elements"
            )

        return optimization_info

    def _analyze_security_aspects(self, root: Element) -> Dict[str, Any]:
        """Analyze security considerations"""
        security_info = {
            "security_risks": [],
            "external_references": [],
            "script_usage": self._has_scripts(root),
            "foreign_objects": 0,
        }

        # Check for script usage
        if security_info["script_usage"]:
            security_info["security_risks"].append(
                "Contains JavaScript - review for XSS risks"
            )

        # Check for external references
        for elem in root.iter():
            href = elem.get("href") or elem.get("{http://www.w3.org/1999/xlink}href")
            if href and href.startswith("http"):
                security_info["external_references"].append(href)
                security_info["security_risks"].append("Contains external references")

        # Check for foreign objects
        foreign_objects = root.findall(".//foreignObject")
        security_info["foreign_objects"] = len(foreign_objects)
        if foreign_objects:
            security_info["security_risks"].append(
                "Contains foreign objects - review content"
            )

        return security_info

    def _check_animations(self, root: Element) -> bool:
        """Check if SVG contains animations"""
        animation_tags = [
            "animate",
            "animateTransform",
            "animateMotion",
            "set",
            "animateColor",
        ]
        namespace = root.tag.split("}")[0][1:] if "}" in root.tag else ""

        for tag in animation_tags:
            search_path = f".//{{{namespace}}}{tag}" if namespace else f".//{tag}"
            if root.find(search_path) is not None:
                return True

        # Check for CSS animations
        for style_elem in root.findall(".//style"):
            if style_elem.text and (
                "animation" in style_elem.text or "keyframes" in style_elem.text
            ):
                return True

        return False

    def _has_scripts(self, root: Element) -> bool:
        """Check if SVG contains scripts"""
        return len(root.findall(".//script")) > 0

    def _check_accessibility(self, root: Element) -> bool:
        """Check if SVG has basic accessibility features"""
        return (
            root.find(".//title") is not None
            or root.find(".//desc") is not None
            or any(elem.get("aria-label") for elem in root.iter())
        )

    def _count_svg_elements(self, root: Element) -> Dict[str, int]:
        """Count SVG elements by type"""
        elements = {}
        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            elements[tag] = elements.get(tag, 0) + 1
        return elements

    def _parse_viewport(self, root: Element) -> Dict[str, Any]:
        """Parse viewport information"""
        viewbox = root.get("viewBox")
        if viewbox:
            parts = viewbox.split()
            if len(parts) == 4:
                return {
                    "x": float(parts[0]),
                    "y": float(parts[1]),
                    "width": float(parts[2]),
                    "height": float(parts[3]),
                }
        return {}

    def _analyze_group_structure(self, root: Element) -> List[Dict[str, Any]]:
        """Analyze group structure for organization"""
        groups = []
        for group in root.findall(".//g"):
            group_info = {
                "id": group.get("id"),
                "class": group.get("class"),
                "child_count": len(list(group)),
                "has_transform": group.get("transform") is not None,
            }
            groups.append(group_info)
        return groups

    def _calculate_max_depth(self, elem: Element, depth: int = 0) -> int:
        """Calculate maximum depth of element tree"""
        if not list(elem):
            return depth
        return max(self._calculate_max_depth(child, depth + 1) for child in elem)

    def _extract_dimension_summary(self, root: Element) -> Dict[str, Any]:
        """Extract dimension summary"""
        return {
            "width": root.get("width"),
            "height": root.get("height"),
            "has_viewbox": root.get("viewBox") is not None,
            "responsive": root.get("viewBox") is not None and root.get("width") is None,
        }

    def _extract_design_summary(self, root: Element) -> Dict[str, Any]:
        """Extract design summary"""
        elements = self._count_svg_elements(root)
        return {
            "element_count": sum(elements.values()),
            "primary_elements": {k: v for k, v in elements.items() if v > 1},
            "has_text": elements.get("text", 0) > 0,
            "has_images": elements.get("image", 0) > 0,
        }

    def _extract_accessibility_summary(self, root: Element) -> Dict[str, Any]:
        """Extract accessibility summary"""
        return {
            "has_title": root.find(".//title") is not None,
            "has_description": root.find(".//desc") is not None,
            "aria_attributes": sum(1 for elem in root.iter() if elem.get("aria-label")),
        }

    def _extract_technical_summary(self, root: Element) -> Dict[str, Any]:
        """Extract technical summary"""
        return {
            "version": root.get("version", "1.1"),
            "has_scripts": self._has_scripts(root),
            "has_animations": self._check_animations(root),
            "namespace_count": len(
                [k for k in root.attrib.keys() if k.startswith("xmlns")]
            ),
        }

    def _assess_svg_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess SVG quality across multiple dimensions"""

        # Accessibility quality
        accessibility_score = findings["accessibility"]["accessibility_score"]

        # Technical quality
        technical_score = 0.0
        if findings["dimensions"]["has_responsive_design"]:
            technical_score += 0.4
        if not findings["scripts"]["has_scripts"]:  # No scripts is better for security
            technical_score += 0.3
        if findings["elements"]["total_elements"] < 100:  # Reasonable complexity
            technical_score += 0.3

        # Optimization quality
        optimization = findings["optimization"]
        optimization_score = 1.0
        if optimization["unused_definitions"] > 0:
            optimization_score -= 0.3
        if optimization["redundant_groups"] > 0:
            optimization_score -= 0.2
        if optimization["long_paths"] > 0:
            optimization_score -= 0.2
        optimization_score = max(0.0, optimization_score)

        # Security quality
        security_score = 1.0
        security_risks = len(findings["security"]["security_risks"])
        if security_risks > 0:
            security_score = max(0.0, 1.0 - (security_risks * 0.25))

        return {
            "accessibility": accessibility_score,
            "technical": technical_score,
            "optimization": optimization_score,
            "security": security_score,
            "overall": (
                accessibility_score
                + technical_score
                + optimization_score
                + security_score
            )
            / 4,
        }
