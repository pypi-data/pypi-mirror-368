#!/usr/bin/env python3
"""
XHTML (Extensible HyperText Markup Language) Handler

Analyzes XHTML documents which are XML-compliant HTML files.
Extracts content structure, semantic elements, accessibility features,
metadata, and web standards compliance information.
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


class XHTMLHandler(XMLHandler):
    """Handler for XHTML documents"""

    XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"

    def _get_namespace(self, root: Element) -> str:
        """Extract namespace prefix from root element"""
        if "}" in root.tag:
            return root.tag.split("}")[0] + "}"
        return ""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for XHTML namespace
        if any("w3.org/1999/xhtml" in uri for uri in namespaces.values()):
            return True, 1.0

        # Check root element
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if root_tag.lower() == "html":
            # Check for XHTML-specific attributes or elements
            ns = self._get_namespace(root)

            # Look for DOCTYPE or XHTML characteristics
            xhtml_indicators = 0

            # Check for common XHTML elements
            xhtml_elements = ["head", "body", "title", "meta", "link"]
            for elem in xhtml_elements:
                if root.find(f".//{ns}{elem}") is not None:
                    xhtml_indicators += 1

            # Check for xml:lang attribute (common in XHTML)
            if root.get("{http://www.w3.org/XML/1998/namespace}lang"):
                xhtml_indicators += 2

            # Check for xmlns attribute
            if root.get("xmlns"):
                xhtml_indicators += 2

            if xhtml_indicators >= 3:
                return True, min(xhtml_indicators * 0.15, 0.9)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Detect XHTML version
        version = "1.0"  # Default

        # Check DOCTYPE or namespace for version hints
        if "xhtml1/DTD/xhtml1-strict.dtd" in str(root):
            version = "1.0 Strict"
        elif "xhtml1/DTD/xhtml1-transitional.dtd" in str(root):
            version = "1.0 Transitional"
        elif "xhtml1/DTD/xhtml1-frameset.dtd" in str(root):
            version = "1.0 Frameset"
        elif "xhtml11.dtd" in str(root):
            version = "1.1"

        # Detect document type based on content
        ns = self._get_namespace(root)
        doc_type = "webpage"

        # Check for specific patterns
        if root.find(f".//{ns}article") is not None:
            doc_type = "article"
        elif root.find(f".//{ns}form") is not None:
            doc_type = "form_page"
        elif len(root.findall(f".//{ns}nav")) > 0:
            doc_type = "navigation_page"
        elif (
            root.find(f".//{ns}main") is not None
            or root.find(f".//{ns}section") is not None
        ):
            doc_type = "content_page"

        return DocumentTypeInfo(
            type_name="XHTML Document",
            confidence=0.90,
            version=version,
            metadata={
                "standard": "W3C XHTML",
                "category": "web_content",
                "document_type": doc_type,
                "compliance": "xml_compliant",
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "document_structure": self._analyze_structure(root),
            "content_analysis": self._analyze_content(root),
            "semantic_elements": self._analyze_semantic_elements(root),
            "metadata": self._analyze_metadata(root),
            "accessibility": self._analyze_accessibility(root),
            "links_and_media": self._analyze_links_and_media(root),
            "forms": self._analyze_forms(root),
            "styling_and_scripts": self._analyze_styling_and_scripts(root),
            "standards_compliance": self._assess_compliance(root),
        }

        recommendations = [
            "Validate XHTML markup against W3C standards",
            "Optimize content structure for search engines",
            "Improve accessibility with ARIA attributes",
            "Analyze semantic markup for better SEO",
            "Extract content for content management systems",
            "Audit links and media references",
            "Review form structure and validation",
            "Check cross-browser compatibility",
        ]

        ai_use_cases = [
            "Content extraction and text mining",
            "Web scraping and data extraction",
            "SEO analysis and optimization",
            "Accessibility compliance checking",
            "Content structure analysis",
            "Link analysis and validation",
            "Form field extraction",
            "Semantic markup analysis",
            "Multi-language content detection",
            "Template and layout analysis",
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
                "total_elements": findings["document_structure"]["total_elements"],
                "content_sections": findings["content_analysis"]["sections"],
                "semantic_elements": findings["semantic_elements"]["total_semantic"],
                "links": findings["links_and_media"]["total_links"],
                "forms": findings["forms"]["form_count"],
                "images": findings["links_and_media"]["images"],
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "page_metadata": self._extract_page_metadata(root),
            "content_hierarchy": self._extract_content_hierarchy(root),
            "navigation_structure": self._extract_navigation(root),
            "form_data": self._extract_form_data(root),
            "media_inventory": self._extract_media_inventory(root),
        }

    def _analyze_structure(self, root: Element) -> Dict[str, Any]:
        """Analyze document structure"""
        ns = self._get_namespace(root)
        structure = {
            "total_elements": 0,
            "max_depth": 0,
            "has_doctype": False,
            "has_head": False,
            "has_body": False,
            "element_counts": {},
        }

        # Count all elements and track types
        for elem in root.iter():
            structure["total_elements"] += 1
            tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            structure["element_counts"][tag_name] = (
                structure["element_counts"].get(tag_name, 0) + 1
            )

        # Calculate max depth
        structure["max_depth"] = self._calculate_max_depth(root)

        # Check for essential structure
        structure["has_head"] = root.find(f"{ns}head") is not None
        structure["has_body"] = root.find(f"{ns}body") is not None

        return structure

    def _analyze_content(self, root: Element) -> Dict[str, Any]:
        """Analyze content elements"""
        ns = self._get_namespace(root)
        content = {
            "headings": {},
            "paragraphs": 0,
            "lists": 0,
            "tables": 0,
            "sections": 0,
            "text_content_length": 0,
            "language": None,
        }

        # Count headings by level
        for level in range(1, 7):
            count = len(root.findall(f".//{ns}h{level}"))
            if count > 0:
                content["headings"][f"h{level}"] = count

        # Count other content elements
        content["paragraphs"] = len(root.findall(f".//{ns}p"))
        content["lists"] = (
            len(root.findall(f".//{ns}ul"))
            + len(root.findall(f".//{ns}ol"))
            + len(root.findall(f".//{ns}dl"))
        )
        content["tables"] = len(root.findall(f".//{ns}table"))
        content["sections"] = (
            len(root.findall(f".//{ns}section"))
            + len(root.findall(f".//{ns}article"))
            + len(root.findall(f".//{ns}div"))
        )

        # Calculate text content
        body = root.find(f"{ns}body")
        if body is not None:
            text_content = self._extract_text_content(body)
            content["text_content_length"] = len(text_content)

        # Detect language
        lang = (
            root.get("lang")
            or root.get("{http://www.w3.org/XML/1998/namespace}lang")
            or self._detect_content_language(root, ns)
        )
        content["language"] = lang

        return content

    def _analyze_semantic_elements(self, root: Element) -> Dict[str, Any]:
        """Analyze HTML5 semantic elements"""
        ns = self._get_namespace(root)
        semantic = {"total_semantic": 0, "elements": {}}

        # HTML5 semantic elements
        semantic_elements = [
            "header",
            "nav",
            "main",
            "section",
            "article",
            "aside",
            "footer",
            "figure",
            "figcaption",
            "details",
            "summary",
            "mark",
            "time",
        ]

        for elem_name in semantic_elements:
            count = len(root.findall(f".//{ns}{elem_name}"))
            if count > 0:
                semantic["elements"][elem_name] = count
                semantic["total_semantic"] += count

        return semantic

    def _analyze_metadata(self, root: Element) -> Dict[str, Any]:
        """Analyze document metadata"""
        ns = self._get_namespace(root)
        metadata = {
            "title": None,
            "description": None,
            "keywords": None,
            "author": None,
            "viewport": None,
            "charset": None,
            "meta_tags": [],
            "link_tags": [],
        }

        # Find head section
        head = root.find(f"{ns}head")
        if head is None:
            return metadata

        # Extract title
        title_elem = head.find(f"{ns}title")
        if title_elem is not None and title_elem.text:
            metadata["title"] = title_elem.text.strip()

        # Extract meta tags
        for meta in head.findall(f"{ns}meta"):
            meta_info = {
                "name": meta.get("name"),
                "content": meta.get("content"),
                "property": meta.get("property"),
                "http_equiv": meta.get("http-equiv"),
                "charset": meta.get("charset"),
            }

            # Extract common meta tags
            if meta.get("name") == "description":
                metadata["description"] = meta.get("content")
            elif meta.get("name") == "keywords":
                metadata["keywords"] = meta.get("content")
            elif meta.get("name") == "author":
                metadata["author"] = meta.get("content")
            elif meta.get("name") == "viewport":
                metadata["viewport"] = meta.get("content")
            elif meta.get("charset"):
                metadata["charset"] = meta.get("charset")

            metadata["meta_tags"].append(meta_info)

        # Extract link tags
        for link in head.findall(f"{ns}link"):
            link_info = {
                "rel": link.get("rel"),
                "href": link.get("href"),
                "type": link.get("type"),
                "media": link.get("media"),
                "sizes": link.get("sizes"),
            }
            metadata["link_tags"].append(link_info)

        return metadata

    def _analyze_accessibility(self, root: Element) -> Dict[str, Any]:
        """Analyze accessibility features"""
        ns = self._get_namespace(root)
        accessibility = {
            "alt_texts": 0,
            "missing_alt_texts": 0,
            "aria_attributes": 0,
            "form_labels": 0,
            "unlabeled_inputs": 0,
            "heading_structure": [],
            "landmark_roles": 0,
            "tab_indexes": 0,
        }

        # Check images for alt text
        for img in root.findall(f".//{ns}img"):
            if img.get("alt") is not None:
                accessibility["alt_texts"] += 1
            else:
                accessibility["missing_alt_texts"] += 1

        # Count ARIA attributes
        for elem in root.iter():
            for attr in elem.attrib:
                if attr.startswith("aria-"):
                    accessibility["aria_attributes"] += 1
                elif attr == "role":
                    accessibility["landmark_roles"] += 1
                elif attr == "tabindex":
                    accessibility["tab_indexes"] += 1

        # Check form labels
        labels = root.findall(f".//{ns}label")
        accessibility["form_labels"] = len(labels)

        # Check unlabeled inputs
        inputs = root.findall(f".//{ns}input")
        labeled_inputs = set()

        for label in labels:
            if label.get("for"):
                labeled_inputs.add(label.get("for"))

        unlabeled = 0
        for input_elem in inputs:
            input_id = input_elem.get("id")
            input_type = input_elem.get("type", "text")
            if (
                input_type not in ["hidden", "submit", "button"]
                and input_id not in labeled_inputs
            ):
                # Check if input is inside a label
                parent = (
                    input_elem.getparent() if hasattr(input_elem, "getparent") else None
                )
                if parent is None or parent.tag.split("}")[-1] != "label":
                    unlabeled += 1

        accessibility["unlabeled_inputs"] = unlabeled

        # Analyze heading structure
        heading_levels = []
        for level in range(1, 7):
            headings = root.findall(f".//{ns}h{level}")
            if headings:
                heading_levels.extend([level] * len(headings))

        accessibility["heading_structure"] = heading_levels

        return accessibility

    def _analyze_links_and_media(self, root: Element) -> Dict[str, Any]:
        """Analyze links and media elements"""
        ns = self._get_namespace(root)
        links_media = {
            "total_links": 0,
            "internal_links": 0,
            "external_links": 0,
            "email_links": 0,
            "broken_link_indicators": 0,
            "images": 0,
            "videos": 0,
            "audio": 0,
            "media_formats": {},
        }

        # Analyze links
        for link in root.findall(f".//{ns}a"):
            href = link.get("href")
            if href:
                links_media["total_links"] += 1

                if href.startswith("mailto:"):
                    links_media["email_links"] += 1
                elif href.startswith(("http://", "https://", "//")):
                    links_media["external_links"] += 1
                elif href.startswith("#") or not href.startswith(
                    ("http", "ftp", "mailto")
                ):
                    links_media["internal_links"] += 1

                # Simple broken link indicators
                if href in ["#", "javascript:void(0)", "javascript:;"]:
                    links_media["broken_link_indicators"] += 1

        # Analyze media
        for img in root.findall(f".//{ns}img"):
            links_media["images"] += 1
            src = img.get("src")
            if src:
                ext = self._get_file_extension(src)
                if ext:
                    links_media["media_formats"][ext] = (
                        links_media["media_formats"].get(ext, 0) + 1
                    )

        for video in root.findall(f".//{ns}video"):
            links_media["videos"] += 1

        for audio in root.findall(f".//{ns}audio"):
            links_media["audio"] += 1

        return links_media

    def _analyze_forms(self, root: Element) -> Dict[str, Any]:
        """Analyze form elements"""
        ns = self._get_namespace(root)
        forms = {
            "form_count": 0,
            "input_types": {},
            "total_inputs": 0,
            "select_elements": 0,
            "textarea_elements": 0,
            "button_elements": 0,
            "form_methods": {},
            "form_actions": [],
        }

        # Analyze forms
        for form in root.findall(f".//{ns}form"):
            forms["form_count"] += 1

            method = form.get("method", "get").lower()
            forms["form_methods"][method] = forms["form_methods"].get(method, 0) + 1

            action = form.get("action")
            if action:
                forms["form_actions"].append(action)

        # Analyze inputs
        for input_elem in root.findall(f".//{ns}input"):
            forms["total_inputs"] += 1
            input_type = input_elem.get("type", "text").lower()
            forms["input_types"][input_type] = (
                forms["input_types"].get(input_type, 0) + 1
            )

        # Count other form elements
        forms["select_elements"] = len(root.findall(f".//{ns}select"))
        forms["textarea_elements"] = len(root.findall(f".//{ns}textarea"))
        forms["button_elements"] = len(root.findall(f".//{ns}button"))

        return forms

    def _analyze_styling_and_scripts(self, root: Element) -> Dict[str, Any]:
        """Analyze styling and script elements"""
        ns = self._get_namespace(root)
        styling_scripts = {
            "inline_styles": 0,
            "external_stylesheets": 0,
            "inline_scripts": 0,
            "external_scripts": 0,
            "style_attributes": 0,
            "script_types": {},
        }

        # Count style elements
        for style in root.findall(f".//{ns}style"):
            styling_scripts["inline_styles"] += 1

        # Count external stylesheets
        head = root.find(f"{ns}head")
        if head is not None:
            for link in head.findall(f"{ns}link"):
                if link.get("rel") == "stylesheet":
                    styling_scripts["external_stylesheets"] += 1

        # Count script elements
        for script in root.findall(f".//{ns}script"):
            if script.get("src"):
                styling_scripts["external_scripts"] += 1
            else:
                styling_scripts["inline_scripts"] += 1

            script_type = script.get("type", "text/javascript")
            styling_scripts["script_types"][script_type] = (
                styling_scripts["script_types"].get(script_type, 0) + 1
            )

        # Count style attributes
        for elem in root.iter():
            if elem.get("style"):
                styling_scripts["style_attributes"] += 1

        return styling_scripts

    def _assess_compliance(self, root: Element) -> Dict[str, Any]:
        """Assess standards compliance"""
        compliance = {
            "has_doctype": False,
            "has_xmlns": False,
            "has_lang": False,
            "well_formed": True,  # Assumption since we parsed it
            "semantic_structure": False,
            "accessibility_score": 0.0,
        }

        # Check for namespace
        compliance["has_xmlns"] = root.get("xmlns") is not None

        # Check for language
        compliance["has_lang"] = (
            root.get("lang") is not None
            or root.get("{http://www.w3.org/XML/1998/namespace}lang") is not None
        )

        # Check for semantic structure
        ns = self._get_namespace(root)
        semantic_elements = ["header", "nav", "main", "section", "article", "footer"]
        semantic_count = sum(
            len(root.findall(f".//{ns}{elem}")) for elem in semantic_elements
        )
        compliance["semantic_structure"] = semantic_count > 0

        return compliance

    def _extract_page_metadata(self, root: Element) -> Dict[str, Any]:
        """Extract comprehensive page metadata"""
        metadata = self._analyze_metadata(root)

        # Add additional metadata
        ns = self._get_namespace(root)
        result = {
            "title": metadata["title"],
            "description": metadata["description"],
            "keywords": metadata["keywords"],
            "author": metadata["author"],
            "language": root.get("lang")
            or root.get("{http://www.w3.org/XML/1998/namespace}lang"),
            "charset": metadata["charset"],
            "viewport": metadata["viewport"],
        }

        # Extract Open Graph data
        head = root.find(f"{ns}head")
        if head is not None:
            og_data = {}
            for meta in head.findall(f"{ns}meta"):
                property_attr = meta.get("property")
                if property_attr and property_attr.startswith("og:"):
                    og_data[property_attr] = meta.get("content")

            if og_data:
                result["open_graph"] = og_data

        return result

    def _extract_content_hierarchy(self, root: Element) -> List[Dict[str, Any]]:
        """Extract content hierarchy based on headings"""
        ns = self._get_namespace(root)
        hierarchy = []

        # Find all headings in document order
        body = root.find(f"{ns}body")
        if body is not None:
            for elem in body.iter():
                tag_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if tag_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    level = int(tag_name[1])
                    text = elem.text.strip() if elem.text else ""

                    hierarchy.append(
                        {
                            "level": level,
                            "text": text,
                            "id": elem.get("id"),
                            "class": elem.get("class"),
                        }
                    )

        return hierarchy[:50]  # Limit for performance

    def _extract_navigation(self, root: Element) -> List[Dict[str, Any]]:
        """Extract navigation structure"""
        ns = self._get_namespace(root)
        navigation = []

        # Find navigation elements
        for nav in root.findall(f".//{ns}nav"):
            nav_info = {"id": nav.get("id"), "class": nav.get("class"), "links": []}

            # Extract links within navigation
            for link in nav.findall(f".//{ns}a"):
                link_info = {
                    "text": link.text.strip() if link.text else "",
                    "href": link.get("href"),
                    "title": link.get("title"),
                }
                nav_info["links"].append(link_info)

            navigation.append(nav_info)

        return navigation[:10]  # Limit

    def _extract_form_data(self, root: Element) -> List[Dict[str, Any]]:
        """Extract form structure data"""
        ns = self._get_namespace(root)
        forms_data = []

        for form in root.findall(f".//{ns}form"):
            form_info = {
                "id": form.get("id"),
                "name": form.get("name"),
                "action": form.get("action"),
                "method": form.get("method", "get"),
                "enctype": form.get("enctype"),
                "fields": [],
            }

            # Extract form fields
            for input_elem in form.findall(f".//{ns}input"):
                field_info = {
                    "type": input_elem.get("type", "text"),
                    "name": input_elem.get("name"),
                    "id": input_elem.get("id"),
                    "required": input_elem.get("required") is not None,
                    "placeholder": input_elem.get("placeholder"),
                }
                form_info["fields"].append(field_info)

            for select in form.findall(f".//{ns}select"):
                field_info = {
                    "type": "select",
                    "name": select.get("name"),
                    "id": select.get("id"),
                    "required": select.get("required") is not None,
                    "multiple": select.get("multiple") is not None,
                    "options": len(select.findall(f"{ns}option")),
                }
                form_info["fields"].append(field_info)

            for textarea in form.findall(f".//{ns}textarea"):
                field_info = {
                    "type": "textarea",
                    "name": textarea.get("name"),
                    "id": textarea.get("id"),
                    "required": textarea.get("required") is not None,
                    "placeholder": textarea.get("placeholder"),
                }
                form_info["fields"].append(field_info)

            forms_data.append(form_info)

        return forms_data[:10]  # Limit

    def _extract_media_inventory(
        self, root: Element
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract media inventory"""
        ns = self._get_namespace(root)
        media = {"images": [], "videos": [], "audio": []}

        # Extract images
        for img in root.findall(f".//{ns}img")[:50]:  # Limit
            img_info = {
                "src": img.get("src"),
                "alt": img.get("alt"),
                "title": img.get("title"),
                "width": img.get("width"),
                "height": img.get("height"),
                "class": img.get("class"),
            }
            media["images"].append(img_info)

        # Extract videos
        for video in root.findall(f".//{ns}video")[:20]:  # Limit
            video_info = {
                "src": video.get("src"),
                "controls": video.get("controls") is not None,
                "autoplay": video.get("autoplay") is not None,
                "loop": video.get("loop") is not None,
                "width": video.get("width"),
                "height": video.get("height"),
            }
            media["videos"].append(video_info)

        # Extract audio
        for audio in root.findall(f".//{ns}audio")[:20]:  # Limit
            audio_info = {
                "src": audio.get("src"),
                "controls": audio.get("controls") is not None,
                "autoplay": audio.get("autoplay") is not None,
                "loop": audio.get("loop") is not None,
            }
            media["audio"].append(audio_info)

        return media

    def _assess_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess XHTML document quality"""
        metrics = {
            "structure_quality": 0.0,
            "content_quality": 0.0,
            "accessibility_quality": 0.0,
            "standards_compliance": 0.0,
            "overall": 0.0,
        }

        # Structure quality
        structure = findings["document_structure"]
        if structure["has_head"] and structure["has_body"]:
            metrics["structure_quality"] += 0.4

        semantic = findings["semantic_elements"]
        if semantic["total_semantic"] > 0:
            metrics["structure_quality"] += 0.3

        if structure["max_depth"] < 15:  # Not too deeply nested
            metrics["structure_quality"] += 0.3

        # Content quality
        content = findings["content_analysis"]
        if content["headings"]:
            metrics["content_quality"] += 0.3

        if content["paragraphs"] > 0:
            metrics["content_quality"] += 0.2

        if content["text_content_length"] > 100:
            metrics["content_quality"] += 0.2

        metadata = findings["metadata"]
        if metadata["title"] and metadata["description"]:
            metrics["content_quality"] += 0.3

        # Accessibility quality
        accessibility = findings["accessibility"]
        total_images = accessibility["alt_texts"] + accessibility["missing_alt_texts"]
        if total_images > 0:
            alt_ratio = accessibility["alt_texts"] / total_images
            metrics["accessibility_quality"] += alt_ratio * 0.3
        else:
            metrics["accessibility_quality"] += 0.3  # No images to worry about

        if accessibility["aria_attributes"] > 0:
            metrics["accessibility_quality"] += 0.2

        if accessibility["form_labels"] > accessibility["unlabeled_inputs"]:
            metrics["accessibility_quality"] += 0.3
        else:
            metrics["accessibility_quality"] += 0.1

        if len(accessibility["heading_structure"]) > 0:
            metrics["accessibility_quality"] += 0.2

        # Standards compliance
        compliance = findings["standards_compliance"]
        if compliance["has_xmlns"]:
            metrics["standards_compliance"] += 0.25
        if compliance["has_lang"]:
            metrics["standards_compliance"] += 0.25
        if compliance["semantic_structure"]:
            metrics["standards_compliance"] += 0.25
        if compliance["well_formed"]:
            metrics["standards_compliance"] += 0.25

        # Overall
        metrics["overall"] = (
            metrics["structure_quality"] * 0.25
            + metrics["content_quality"] * 0.25
            + metrics["accessibility_quality"] * 0.3
            + metrics["standards_compliance"] * 0.2
        )

        return metrics

    # Utility methods
    def _calculate_max_depth(self, element: Element, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        if not list(element):
            return current_depth

        max_child_depth = current_depth
        for child in element:
            child_depth = self._calculate_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def _extract_text_content(self, element: Element) -> str:
        """Extract all text content from element and children"""
        texts = []
        if element.text:
            texts.append(element.text.strip())

        for child in element:
            texts.append(self._extract_text_content(child))
            if child.tail:
                texts.append(child.tail.strip())

        return " ".join(text for text in texts if text)

    def _detect_content_language(self, root: Element, ns: str) -> Optional[str]:
        """Simple content language detection"""
        # This is a very basic implementation
        # In practice, you might use a proper language detection library

        body = root.find(f"{ns}body")
        if body is not None:
            text_content = self._extract_text_content(body)

            # Simple heuristics based on common words
            if len(text_content) > 100:
                text_lower = text_content.lower()

                # English indicators
                english_words = [
                    "the",
                    "and",
                    "or",
                    "but",
                    "in",
                    "on",
                    "at",
                    "to",
                    "for",
                    "of",
                    "with",
                    "by",
                ]
                english_count = sum(
                    1 for word in english_words if f" {word} " in text_lower
                )

                # Spanish indicators
                spanish_words = [
                    "el",
                    "la",
                    "de",
                    "que",
                    "y",
                    "en",
                    "un",
                    "es",
                    "se",
                    "no",
                    "te",
                    "lo",
                ]
                spanish_count = sum(
                    1 for word in spanish_words if f" {word} " in text_lower
                )

                # French indicators
                french_words = [
                    "le",
                    "de",
                    "et",
                    "à",
                    "un",
                    "il",
                    "être",
                    "et",
                    "en",
                    "avoir",
                    "que",
                    "pour",
                ]
                french_count = sum(
                    1 for word in french_words if f" {word} " in text_lower
                )

                if english_count > spanish_count and english_count > french_count:
                    return "en"
                elif spanish_count > english_count and spanish_count > french_count:
                    return "es"
                elif french_count > english_count and french_count > spanish_count:
                    return "fr"

        return None

    def _get_file_extension(self, filename: str) -> Optional[str]:
        """Extract file extension from filename"""
        if "." in filename:
            return filename.split(".")[-1].lower()
        return None
