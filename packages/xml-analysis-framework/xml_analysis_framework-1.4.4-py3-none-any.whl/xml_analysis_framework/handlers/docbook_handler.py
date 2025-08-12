#!/usr/bin/env python3
"""
DocBook Handler

Analyzes DocBook XML documentation files for structure analysis, content organization,
technical documentation quality assessment, and documentation generation workflows.
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


class DocBookHandler(XMLHandler):
    """Handler for DocBook XML documentation files"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for DocBook elements
        docbook_roots = ["book", "article", "chapter", "section", "para"]
        tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if tag in docbook_roots:
            return True, 0.8

        # Check for DocBook namespace
        if any("docbook.org" in uri for uri in namespaces.values()):
            return True, 1.0

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # Detect DocBook version
        version = self._detect_docbook_version(root, namespaces)

        metadata = {
            "framework": "DocBook",
            "category": "technical_documentation",
            "document_type": tag,
            "has_chapters": len(root.findall(".//chapter")) > 0,
            "has_sections": len(root.findall(".//section")) > 0,
            "element_count": len(list(root.iter())),
        }

        return DocumentTypeInfo(
            type_name="DocBook Documentation",
            confidence=0.9,
            version=version,
            metadata=metadata,
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "docbook_info": {
                "document_type": (
                    root.tag.split("}")[-1] if "}" in root.tag else root.tag
                ),
                "version": self._detect_docbook_version(root, {}),
                "namespaces": self._extract_namespace_info(root),
            },
            "structure": self._analyze_document_structure(root),
            "metadata": self._extract_metadata(root),
            "content_stats": self._analyze_content(root),
            "media": self._find_media_references(root),
            "cross_references": self._find_cross_references(root),
            "accessibility": self._analyze_accessibility_features(root),
            "quality_indicators": self._analyze_quality_indicators(root),
            "localization": self._analyze_localization_features(root),
            "publishing": self._analyze_publishing_features(root),
        }

        recommendations = [
            "Extract for documentation search system integration",
            "Generate multiple output formats (HTML, PDF, EPUB)",
            "Check for broken cross-references and validate links",
            "Analyze readability and completeness metrics",
            "Validate accessibility compliance (WCAG guidelines)",
            "Review document structure for logical organization",
            "Check media references for missing files",
            "Optimize for multi-format publishing workflows",
            "Validate DocBook schema compliance",
        ]

        ai_use_cases = [
            "Documentation quality analysis and improvement suggestions",
            "Automatic summary and abstract generation",
            "Technical content extraction and indexing",
            "Glossary and index generation from content",
            "Documentation translation and localization support",
            "Cross-reference validation and link checking",
            "Content accessibility analysis and enhancement",
            "Multi-format publishing optimization",
            "Document structure analysis and reorganization suggestions",
            "Technical writing style analysis and improvement",
        ]

        data_inventory = {
            "chapters": len(findings["structure"]["chapters"]),
            "sections": findings["structure"]["total_sections"],
            "paragraphs": findings["content_stats"]["paragraphs"],
            "media_items": len(findings["media"]["media_references"]),
            "cross_references": len(
                findings["cross_references"]["internal_references"]
            ),
            "code_examples": len(findings["content_stats"]["code_examples"]),
            "tables": findings["content_stats"]["tables"],
            "lists": findings["content_stats"]["lists"],
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
            quality_metrics=self._assess_documentation_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "document_metadata": {
                "title": self._extract_title(root),
                "type": root.tag.split("}")[-1] if "}" in root.tag else root.tag,
                "version": self._detect_docbook_version(root, {}),
                "language": root.get("lang")
                or root.get("{http://www.w3.org/XML/1998/namespace}lang"),
            },
            "content_summary": self._extract_content_summary(root),
            "structural_summary": self._extract_structural_summary(root),
            "technical_summary": self._extract_technical_summary(root),
        }

    def _detect_docbook_version(self, root: Element, namespaces: Dict[str, str]) -> str:
        """Detect DocBook version from namespace or DTD"""
        # Check namespace for version
        for uri in namespaces.values():
            if "docbook.org" in uri:
                if "/5.0/" in uri:
                    return "5.0"
                elif "/4.5/" in uri:
                    return "4.5"
                elif "/4.4/" in uri:
                    return "4.4"
                elif "/4.3/" in uri:
                    return "4.3"

        # Check root tag namespace
        if "}" in root.tag:
            namespace = root.tag.split("}")[0][1:]
            if "docbook.org" in namespace:
                if "/5.0/" in namespace:
                    return "5.0"
                elif "/4." in namespace:
                    return "4.x"

        # Default assumption
        return "5.0"

    def _extract_namespace_info(self, root: Element) -> Dict[str, Any]:
        """Extract namespace information"""
        namespaces = {}
        for key, value in root.attrib.items():
            if key.startswith("xmlns"):
                prefix = key.split(":", 1)[1] if ":" in key else "default"
                namespaces[prefix] = value

        return {
            "declared_namespaces": namespaces,
            "docbook_namespace": any(
                "docbook.org" in uri for uri in namespaces.values()
            ),
            "xlink_namespace": "xlink" in namespaces,
        }

    def _analyze_document_structure(self, root: Element) -> Dict[str, Any]:
        """Analyze document structure and hierarchy"""
        # Handle namespaced elements properly
        ns_prefix = "{http://docbook.org/ns/docbook}" if "}" in root.tag else ""

        structure = {
            "document_type": root.tag.split("}")[-1] if "}" in root.tag else root.tag,
            "chapters": [],
            "total_sections": 0,
            "max_depth": 0,
            "parts": [],
            "appendices": [],
            "hierarchy_analysis": {},
        }

        # Analyze parts
        for part in root.findall(f".//{ns_prefix}part"):
            title_elem = part.find(f".//{ns_prefix}title")
            structure["parts"].append(
                {
                    "title": (
                        title_elem.text if title_elem is not None else "Untitled Part"
                    ),
                    "chapters": len(part.findall(f".//{ns_prefix}chapter")),
                    "sections": len(part.findall(f".//{ns_prefix}section")),
                }
            )

        # Analyze chapters
        for chapter in root.findall(f".//{ns_prefix}chapter"):
            title_elem = chapter.find(f".//{ns_prefix}title")
            chapter_info = {
                "title": (
                    title_elem.text if title_elem is not None else "Untitled Chapter"
                ),
                "sections": len(chapter.findall(f".//{ns_prefix}section")),
                "subsections": len(
                    chapter.findall(f".//{ns_prefix}section//{ns_prefix}section")
                ),
                "id": chapter.get("id")
                or chapter.get("{http://www.w3.org/XML/1998/namespace}id"),
            }
            structure["chapters"].append(chapter_info)

        # Analyze appendices
        for appendix in root.findall(f".//{ns_prefix}appendix"):
            title_elem = appendix.find(f".//{ns_prefix}title")
            structure["appendices"].append(
                {
                    "title": (
                        title_elem.text
                        if title_elem is not None
                        else "Untitled Appendix"
                    ),
                    "sections": len(appendix.findall(f".//{ns_prefix}section")),
                }
            )

        # Count all sections
        structure["total_sections"] = len(root.findall(f".//{ns_prefix}section"))

        # Calculate hierarchy depth
        structure["max_depth"] = self._calculate_max_depth(root)

        # Analyze hierarchy consistency
        structure["hierarchy_analysis"] = self._analyze_hierarchy_consistency(root)

        return structure

    def _extract_metadata(self, root: Element) -> Dict[str, Any]:
        """Extract document metadata from info elements"""
        # DocBook 5.x uses 'info', 4.x uses specific info elements
        info = (
            root.find(".//info")
            or root.find(".//bookinfo")
            or root.find(".//articleinfo")
            or root.find(".//chapterinfo")
        )

        if info is None:
            return {
                "has_metadata": False,
                "title": self._extract_title(root),
                "extracted_from": "root_title_only",
            }

        metadata = {
            "has_metadata": True,
            "title": getattr(info.find(".//title"), "text", None),
            "subtitle": getattr(info.find(".//subtitle"), "text", None),
            "author": self._extract_author_info(info),
            "date": getattr(info.find(".//date"), "text", None),
            "publisher": getattr(
                info.find(".//publisher//publishername"), "text", None
            ),
            "copyright": self._extract_copyright_info(info),
            "abstract": self._extract_abstract(info),
            "keywords": self._extract_keywords(info),
            "revision_history": self._extract_revision_history(info),
        }

        return metadata

    def _analyze_content(self, root: Element) -> Dict[str, Any]:
        """Analyze content statistics and types"""
        # Handle namespaced elements properly
        ns_prefix = "{http://docbook.org/ns/docbook}" if "}" in root.tag else ""

        content_stats = {
            "paragraphs": len(root.findall(f".//{ns_prefix}para")),
            "lists": len(root.findall(f".//{ns_prefix}itemizedlist"))
            + len(root.findall(f".//{ns_prefix}orderedlist")),
            "tables": len(root.findall(f".//{ns_prefix}table"))
            + len(root.findall(f".//{ns_prefix}informaltable")),
            "figures": len(root.findall(f".//{ns_prefix}figure")),
            "examples": len(root.findall(f".//{ns_prefix}example")),
            "equations": len(root.findall(f".//{ns_prefix}equation"))
            + len(root.findall(f".//{ns_prefix}informalequation")),
            "code_examples": self._count_code_examples(root),
            "admonitions": {
                "notes": len(root.findall(f".//{ns_prefix}note")),
                "warnings": len(root.findall(f".//{ns_prefix}warning")),
                "cautions": len(root.findall(f".//{ns_prefix}caution")),
                "important": len(root.findall(f".//{ns_prefix}important")),
                "tips": len(root.findall(f".//{ns_prefix}tip")),
            },
            "footnotes": len(root.findall(f".//{ns_prefix}footnote")),
            "bibliographic_entries": len(root.findall(f".//{ns_prefix}biblioentry")),
        }

        # Add content density analysis
        total_elements = len(list(root.iter()))
        content_stats["content_density"] = {
            "paragraph_density": (
                content_stats["paragraphs"] / total_elements
                if total_elements > 0
                else 0
            ),
            "example_density": (
                len(content_stats["code_examples"]) / total_elements
                if total_elements > 0
                else 0
            ),
            "media_density": (
                (content_stats["figures"] + content_stats["tables"]) / total_elements
                if total_elements > 0
                else 0
            ),
        }

        return content_stats

    def _find_media_references(self, root: Element) -> Dict[str, Any]:
        """Find and analyze media references"""
        media_info = {
            "media_references": [],
            "media_types": {},
            "broken_references_check": [],
            "accessibility_analysis": {},
        }

        # Find image references
        for elem in root.findall(".//imagedata"):
            media_ref = {
                "type": "image",
                "fileref": elem.get("fileref"),
                "format": elem.get("format"),
                "width": elem.get("width"),
                "depth": elem.get("depth"),
                "scale": elem.get("scale"),
                "align": elem.get("align"),
                "parent_element": (
                    elem.getparent().tag if hasattr(elem, "getparent") else "unknown"
                ),
            }
            media_info["media_references"].append(media_ref)

            # Count media types
            format_type = elem.get("format", "unknown")
            media_info["media_types"][format_type] = (
                media_info["media_types"].get(format_type, 0) + 1
            )

        # Find video/audio references
        for elem in root.findall(".//videodata"):
            media_info["media_references"].append(
                {
                    "type": "video",
                    "fileref": elem.get("fileref"),
                    "format": elem.get("format"),
                }
            )

        for elem in root.findall(".//audiodata"):
            media_info["media_references"].append(
                {
                    "type": "audio",
                    "fileref": elem.get("fileref"),
                    "format": elem.get("format"),
                }
            )

        # Analyze accessibility features for media
        media_info["accessibility_analysis"] = self._analyze_media_accessibility(root)

        return media_info

    def _find_cross_references(self, root: Element) -> Dict[str, Any]:
        """Find and analyze cross-references"""
        xref_info = {
            "internal_references": [],
            "external_references": [],
            "link_analysis": {},
            "reference_targets": set(),
            "orphaned_references": [],
        }

        # Find all elements with IDs (potential targets)
        for elem in root.iter():
            elem_id = elem.get("id") or elem.get(
                "{http://www.w3.org/XML/1998/namespace}id"
            )
            if elem_id:
                xref_info["reference_targets"].add(elem_id)

        # Find xref elements
        for xref in root.findall(".//xref"):
            linkend = xref.get("linkend")
            if linkend:
                xref_info["internal_references"].append(
                    {
                        "linkend": linkend,
                        "exists": linkend in xref_info["reference_targets"],
                        "element": "xref",
                    }
                )

        # Find link elements
        for link in root.findall(".//link"):
            linkend = link.get("linkend")
            if linkend:
                xref_info["internal_references"].append(
                    {
                        "linkend": linkend,
                        "exists": linkend in xref_info["reference_targets"],
                        "element": "link",
                    }
                )

        # Find external links
        for ulink in root.findall(".//ulink"):
            url = ulink.get("url")
            if url:
                xref_info["external_references"].append(
                    {"url": url, "text": ulink.text, "element": "ulink"}
                )

        # Analyze broken references
        for ref in xref_info["internal_references"]:
            if not ref["exists"]:
                xref_info["orphaned_references"].append(ref["linkend"])

        # Generate link analysis
        xref_info["link_analysis"] = {
            "total_internal": len(xref_info["internal_references"]),
            "total_external": len(xref_info["external_references"]),
            "broken_internal": len(xref_info["orphaned_references"]),
            "reference_density": len(xref_info["internal_references"])
            / max(len(list(root.iter())), 1),
        }

        return xref_info

    def _analyze_accessibility_features(self, root: Element) -> Dict[str, Any]:
        """Analyze accessibility features"""
        accessibility = {
            "alt_text_coverage": 0,
            "table_accessibility": {},
            "structure_accessibility": {},
            "language_support": {},
            "accessibility_score": 0.0,
            "recommendations": [],
        }

        # Check alt text for images
        images = root.findall(".//imagedata")
        images_with_alt = 0
        for img in images:
            # Check for alt attribute or textobject
            parent_figure = img.getparent() if hasattr(img, "getparent") else None
            if parent_figure and parent_figure.find(".//textobject"):
                images_with_alt += 1

        if images:
            accessibility["alt_text_coverage"] = images_with_alt / len(images)

        # Check table accessibility
        tables = root.findall(".//table") + root.findall(".//informaltable")
        tables_with_headers = sum(1 for table in tables if table.find(".//thead"))
        accessibility["table_accessibility"] = {
            "total_tables": len(tables),
            "tables_with_headers": tables_with_headers,
            "header_coverage": tables_with_headers / len(tables) if tables else 0,
        }

        # Check structural accessibility
        accessibility["structure_accessibility"] = {
            "has_title": root.find(".//title") is not None,
            "has_toc": root.find(".//toc") is not None,
            "section_hierarchy": len(root.findall(".//section")) > 0,
        }

        # Calculate accessibility score
        score = 0
        if accessibility["alt_text_coverage"] > 0.8:
            score += 0.3
        if accessibility["table_accessibility"]["header_coverage"] > 0.8:
            score += 0.3
        if accessibility["structure_accessibility"]["has_title"]:
            score += 0.2
        if accessibility["structure_accessibility"]["section_hierarchy"]:
            score += 0.2

        accessibility["accessibility_score"] = score

        # Generate recommendations
        if accessibility["alt_text_coverage"] < 0.8:
            accessibility["recommendations"].append(
                "Add alt text or textobject for images"
            )
        if accessibility["table_accessibility"]["header_coverage"] < 0.8:
            accessibility["recommendations"].append(
                "Add proper table headers for accessibility"
            )
        if not accessibility["structure_accessibility"]["has_toc"]:
            accessibility["recommendations"].append(
                "Consider adding table of contents for navigation"
            )

        return accessibility

    def _analyze_quality_indicators(self, root: Element) -> Dict[str, Any]:
        """Analyze documentation quality indicators"""
        quality = {
            "completeness_indicators": {},
            "consistency_checks": {},
            "best_practices": {},
            "quality_score": 0.0,
        }

        # Completeness indicators
        has_abstract = root.find(".//abstract") is not None
        has_examples = len(root.findall(".//example")) > 0
        has_index = root.find(".//index") is not None
        has_bibliography = root.find(".//bibliography") is not None

        quality["completeness_indicators"] = {
            "has_abstract": has_abstract,
            "has_examples": has_examples,
            "has_index": has_index,
            "has_bibliography": has_bibliography,
            "completeness_score": sum(
                [has_abstract, has_examples, has_index, has_bibliography]
            )
            / 4,
        }

        # Consistency checks
        sections_with_titles = len(
            [s for s in root.findall(".//section") if s.find(".//title") is not None]
        )
        total_sections = len(root.findall(".//section"))

        quality["consistency_checks"] = {
            "section_title_consistency": (
                sections_with_titles / total_sections if total_sections > 0 else 1.0
            ),
            "id_consistency": self._check_id_consistency(root),
        }

        # Best practices
        quality["best_practices"] = {
            "uses_semantic_markup": self._check_semantic_markup(root),
            "proper_nesting": self._check_proper_nesting(root),
            "metadata_present": root.find(".//info") is not None,
        }

        # Calculate overall quality score
        quality["quality_score"] = (
            quality["completeness_indicators"]["completeness_score"] * 0.4
            + quality["consistency_checks"]["section_title_consistency"] * 0.3
            + sum(quality["best_practices"].values())
            / len(quality["best_practices"])
            * 0.3
        )

        return quality

    def _analyze_localization_features(self, root: Element) -> Dict[str, Any]:
        """Analyze localization and internationalization features"""
        localization = {
            "language_info": {},
            "translatable_content": {},
            "localization_support": {},
        }

        # Check language attributes
        lang = root.get("lang") or root.get(
            "{http://www.w3.org/XML/1998/namespace}lang"
        )
        localization["language_info"] = {
            "primary_language": lang,
            "has_language_attribute": lang is not None,
            "multiple_languages": len(
                set(
                    elem.get("lang")
                    or elem.get("{http://www.w3.org/XML/1998/namespace}lang")
                    for elem in root.iter()
                    if elem.get("lang")
                    or elem.get("{http://www.w3.org/XML/1998/namespace}lang")
                )
            )
            > 1,
        }

        # Analyze translatable content
        text_elements = len(
            [elem for elem in root.iter() if elem.text and elem.text.strip()]
        )
        localization["translatable_content"] = {
            "text_elements": text_elements,
            "estimated_word_count": self._estimate_word_count(root),
        }

        return localization

    def _analyze_publishing_features(self, root: Element) -> Dict[str, Any]:
        """Analyze publishing and output generation features"""
        publishing = {
            "output_hints": {},
            "formatting_elements": {},
            "publishing_metadata": {},
        }

        # Check for output-specific elements
        publishing["output_hints"] = {
            "has_page_breaks": len(root.findall(".//pagebreak")) > 0,
            "has_index_terms": len(root.findall(".//indexterm")) > 0,
            "has_processing_instructions": len(
                [elem for elem in root.iter() if elem.tag.startswith("<?")]
            )
            > 0,
        }

        # Check formatting elements
        publishing["formatting_elements"] = {
            "emphasis_elements": len(root.findall(".//emphasis")),
            "literal_elements": len(root.findall(".//literal")),
            "subscript_superscript": len(root.findall(".//subscript"))
            + len(root.findall(".//superscript")),
        }

        return publishing

    def _count_code_examples(self, root: Element) -> List[Dict[str, Any]]:
        """Count and analyze code examples"""
        code_examples = []

        for example in root.findall(".//programlisting"):
            code_info = {
                "language": example.get("language", "unknown"),
                "linenumbering": example.get("linenumbering") == "numbered",
                "length": len(example.text) if example.text else 0,
                "has_title": (
                    example.getparent()
                    and example.getparent().find(".//title") is not None
                    if hasattr(example, "getparent")
                    else False
                ),
            }
            code_examples.append(code_info)

        # Also check screen elements (command line examples)
        for screen in root.findall(".//screen"):
            code_examples.append(
                {
                    "language": "shell",
                    "type": "screen_output",
                    "length": len(screen.text) if screen.text else 0,
                }
            )

        return code_examples[:20]  # Limit to first 20 examples

    def _calculate_max_depth(self, root: Element, depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        if not list(root):
            return depth
        return max(self._calculate_max_depth(child, depth + 1) for child in root)

    def _analyze_hierarchy_consistency(self, root: Element) -> Dict[str, Any]:
        """Analyze document hierarchy consistency"""
        hierarchy = {
            "consistent_numbering": True,
            "proper_nesting": True,
            "missing_titles": 0,
        }

        # Check for missing titles in structural elements
        structural_elements = ["chapter", "section", "appendix", "part"]
        for elem_type in structural_elements:
            elements = root.findall(f".//{elem_type}")
            for elem in elements:
                if elem.find(".//title") is None:
                    hierarchy["missing_titles"] += 1

        return hierarchy

    def _extract_author_info(self, info: Element) -> Dict[str, Any]:
        """Extract comprehensive author information"""
        authors = []

        for author in info.findall(".//author"):
            author_info = {}

            # Name components
            firstname = author.find(".//firstname")
            surname = author.find(".//surname")
            othername = author.find(".//othername")

            if firstname is not None and surname is not None:
                author_info["name"] = f"{firstname.text} {surname.text}"
                if othername is not None:
                    author_info["name"] = (
                        f"{firstname.text} {othername.text} {surname.text}"
                    )

            # Contact info
            email = author.find(".//email")
            if email is not None:
                author_info["email"] = email.text

            # Affiliation
            affiliation = author.find(".//affiliation")
            if affiliation is not None:
                orgname = affiliation.find(".//orgname")
                if orgname is not None:
                    author_info["organization"] = orgname.text

            authors.append(author_info)

        return authors if authors else None

    def _extract_copyright_info(self, info: Element) -> Optional[Dict[str, Any]]:
        """Extract copyright information"""
        copyright_elem = info.find(".//copyright")
        if copyright_elem is None:
            return None

        copyright_info = {}

        year = copyright_elem.find(".//year")
        if year is not None:
            copyright_info["year"] = year.text

        holder = copyright_elem.find(".//holder")
        if holder is not None:
            copyright_info["holder"] = holder.text

        return copyright_info

    def _extract_abstract(self, info: Element) -> Optional[str]:
        """Extract document abstract"""
        abstract = info.find(".//abstract")
        if abstract is not None:
            # Combine all paragraph text
            paras = abstract.findall(".//para")
            if paras:
                return " ".join(para.text for para in paras if para.text)
            return abstract.text
        return None

    def _extract_keywords(self, info: Element) -> List[str]:
        """Extract keywords"""
        keywords = []
        keywordset = info.find(".//keywordset")
        if keywordset is not None:
            for keyword in keywordset.findall(".//keyword"):
                if keyword.text:
                    keywords.append(keyword.text)
        return keywords

    def _extract_revision_history(self, info: Element) -> List[Dict[str, Any]]:
        """Extract revision history"""
        revisions = []
        revhistory = info.find(".//revhistory")
        if revhistory is not None:
            for revision in revhistory.findall(".//revision"):
                rev_info = {}

                revnumber = revision.find(".//revnumber")
                if revnumber is not None:
                    rev_info["number"] = revnumber.text

                date = revision.find(".//date")
                if date is not None:
                    rev_info["date"] = date.text

                authorinitials = revision.find(".//authorinitials")
                if authorinitials is not None:
                    rev_info["author"] = authorinitials.text

                revremark = revision.find(".//revremark")
                if revremark is not None:
                    rev_info["remark"] = revremark.text

                revisions.append(rev_info)

        return revisions

    def _analyze_media_accessibility(self, root: Element) -> Dict[str, Any]:
        """Analyze media accessibility features"""
        accessibility = {
            "images_with_alt": 0,
            "total_images": 0,
            "media_descriptions": 0,
        }

        for mediaobject in root.findall(".//mediaobject"):
            accessibility["total_images"] += 1

            # Check for textobject (alt text equivalent)
            if mediaobject.find(".//textobject"):
                accessibility["images_with_alt"] += 1

        return accessibility

    def _check_id_consistency(self, root: Element) -> float:
        """Check consistency of ID attributes"""
        elements_with_ids = 0
        structural_elements = 0

        for elem in (
            root.findall(".//chapter")
            + root.findall(".//section")
            + root.findall(".//appendix")
        ):
            structural_elements += 1
            if elem.get("id") or elem.get("{http://www.w3.org/XML/1998/namespace}id"):
                elements_with_ids += 1

        return (
            elements_with_ids / structural_elements if structural_elements > 0 else 1.0
        )

    def _check_semantic_markup(self, root: Element) -> bool:
        """Check for proper semantic markup usage"""
        semantic_elements = [
            "emphasis",
            "literal",
            "filename",
            "command",
            "option",
            "replaceable",
        ]
        return any(len(root.findall(f".//{elem}")) > 0 for elem in semantic_elements)

    def _check_proper_nesting(self, root: Element) -> bool:
        """Check for proper element nesting"""
        # This is a simplified check - would need more comprehensive validation
        return True  # Assume proper nesting unless we detect issues

    def _estimate_word_count(self, root: Element) -> int:
        """Estimate word count for translatable content"""
        word_count = 0
        for elem in root.iter():
            if elem.text and elem.text.strip():
                word_count += len(elem.text.strip().split())
        return word_count

    def _extract_title(self, root: Element) -> str:
        """Extract document title"""
        # Handle namespaced elements properly
        ns_prefix = "{http://docbook.org/ns/docbook}" if "}" in root.tag else ""
        title = root.find(f".//{ns_prefix}title")
        return title.text if title is not None else "Untitled Document"

    def _extract_content_summary(self, root: Element) -> Dict[str, Any]:
        """Extract content summary"""
        content = self._analyze_content(root)
        return {
            "total_paragraphs": content["paragraphs"],
            "content_types": {
                "narrative": content["paragraphs"],
                "examples": len(content["code_examples"]),
                "tables": content["tables"],
                "figures": content["figures"],
            },
            "estimated_reading_time": content["paragraphs"]
            * 0.5,  # Rough estimate in minutes
        }

    def _extract_structural_summary(self, root: Element) -> Dict[str, Any]:
        """Extract structural summary"""
        structure = self._analyze_document_structure(root)
        return {
            "document_type": structure["document_type"],
            "major_sections": len(structure["chapters"]),
            "total_sections": structure["total_sections"],
            "max_nesting_depth": structure["max_depth"],
            "has_appendices": len(structure["appendices"]) > 0,
        }

    def _extract_technical_summary(self, root: Element) -> Dict[str, Any]:
        """Extract technical summary"""
        return {
            "docbook_version": self._detect_docbook_version(root, {}),
            "namespace_count": len(
                [k for k in root.attrib.keys() if k.startswith("xmlns")]
            ),
            "cross_references": len(root.findall(".//xref")),
            "external_links": len(root.findall(".//ulink")),
            "media_objects": len(root.findall(".//mediaobject")),
        }

    def _assess_documentation_quality(
        self, findings: Dict[str, Any]
    ) -> Dict[str, float]:
        """Assess overall documentation quality"""

        # Content quality
        content = findings["content_stats"]
        structure = findings["structure"]

        content_score = 0.0
        if content["paragraphs"] > 10:  # Substantial content
            content_score += 0.3
        if len(content["code_examples"]) > 0:  # Has examples
            content_score += 0.3
        if (
            content["admonitions"]["notes"] + content["admonitions"]["warnings"] > 0
        ):  # Has helpful notes
            content_score += 0.2
        if content["tables"] > 0 or content["figures"] > 0:  # Has visual aids
            content_score += 0.2

        # Structure quality
        structure_score = 0.0
        if structure["total_sections"] > 0:  # Well structured
            structure_score += 0.4
        if len(structure["chapters"]) > 1:  # Multi-chapter document
            structure_score += 0.3
        if structure["max_depth"] <= 5:  # Reasonable depth
            structure_score += 0.3

        # Metadata quality
        metadata = findings["metadata"]
        metadata_score = 0.0
        if metadata["has_metadata"]:
            metadata_score += 0.5
        if metadata.get("author"):
            metadata_score += 0.3
        if metadata.get("abstract"):
            metadata_score += 0.2

        # Accessibility quality
        accessibility_score = findings["accessibility"]["accessibility_score"]

        # Cross-reference quality
        xref = findings["cross_references"]
        xref_score = 1.0
        if xref["link_analysis"]["total_internal"] > 0:
            broken_ratio = (
                xref["link_analysis"]["broken_internal"]
                / xref["link_analysis"]["total_internal"]
            )
            xref_score = max(0.0, 1.0 - broken_ratio)

        return {
            "content_quality": content_score,
            "structure_quality": structure_score,
            "metadata_quality": metadata_score,
            "accessibility": accessibility_score,
            "reference_integrity": xref_score,
            "overall": (
                content_score
                + structure_score
                + metadata_score
                + accessibility_score
                + xref_score
            )
            / 5,
        }
