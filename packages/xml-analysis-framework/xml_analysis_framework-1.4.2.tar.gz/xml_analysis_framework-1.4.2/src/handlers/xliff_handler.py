#!/usr/bin/env python3
"""
XLIFF Handler

Analyzes XLIFF (XML Localization Interchange File Format) files used in
translation and localization workflows. Extracts translation units,
states, metadata, and provides translation quality metrics and workflow insights.
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


class XLIFFHandler(XMLHandler):
    """Handler for XLIFF (XML Localization Interchange File Format) files"""

    XLIFF_NAMESPACES = [
        "urn:oasis:names:tc:xliff:document:1.2",
        "urn:oasis:names:tc:xliff:document:2.0",
        "urn:oasis:names:tc:xliff:document:2.1",
        "xliff.oasis-open.org",
    ]

    XLIFF_VERSIONS = {
        "1.2": "urn:oasis:names:tc:xliff:document:1.2",
        "2.0": "urn:oasis:names:tc:xliff:document:2.0",
        "2.1": "urn:oasis:names:tc:xliff:document:2.1",
    }

    def _get_namespace(self, root: Element) -> str:
        """Extract namespace prefix from root element"""
        if "}" in root.tag:
            return root.tag.split("}")[0] + "}"
        return ""

    def _find_elements_by_local_name(
        self, root: Element, local_name: str
    ) -> List[Element]:
        """Find elements by local name, ignoring namespace prefixes"""
        return [elem for elem in root.iter() if elem.tag.split("}")[-1] == local_name]

    def _find_element_by_local_name(
        self, root: Element, local_name: str
    ) -> Optional[Element]:
        """Find first element by local name, ignoring namespace prefixes"""
        for elem in root.iter():
            if elem.tag.split("}")[-1] == local_name:
                return elem
        return None

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for XLIFF namespace
        for uri in namespaces.values():
            if any(xliff_ns in uri for xliff_ns in self.XLIFF_NAMESPACES):
                return True, 1.0

        # Check root element
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if root_tag.lower() == "xliff":
            return True, 0.95

        # Check for XLIFF-specific elements
        ns = self._get_namespace(root)
        xliff_elements = ["file", "trans-unit", "source", "target", "body"]
        found_elements = sum(
            1
            for elem in xliff_elements
            if root.find(f".//{ns}{elem}") is not None
            or root.find(f".//{elem}") is not None
        )

        if found_elements >= 3:
            return True, min(found_elements * 0.25, 0.9)

        # Check for translation units with source/target
        trans_units = self._find_elements_by_local_name(root, "trans-unit")

        if trans_units:
            has_source_target = any(
                (
                    self._find_element_by_local_name(unit, "source") is not None
                    and self._find_element_by_local_name(unit, "target") is not None
                )
                for unit in trans_units[:5]  # Check first 5
            )
            if has_source_target:
                return True, 0.8

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Detect XLIFF version
        version = "1.2"  # Default

        # Check version attribute
        if "version" in root.attrib:
            version = root.get("version", "1.2")

        # Check namespace for version
        for uri in namespaces.values():
            if "2.1" in uri:
                version = "2.1"
            elif "2.0" in uri:
                version = "2.0"
            elif "1.2" in uri:
                version = "1.2"

        # Detect document characteristics
        _ = self._get_namespace(root)  # Namespace for potential future use

        # Count translation units and files
        trans_units = self._find_elements_by_local_name(root, "trans-unit")
        files = self._find_elements_by_local_name(root, "file")

        # Determine document type
        doc_type = "standard"
        if len(files) > 1:
            doc_type = "multi_file"
        elif any(unit.get("approved") == "yes" for unit in trans_units):
            doc_type = "approved_translation"
        elif any(unit.get("translate") == "no" for unit in trans_units):
            doc_type = "mixed_translation"

        # Determine complexity
        total_units = len(trans_units)
        complexity = (
            "simple"
            if total_units < 100
            else "medium" if total_units < 1000 else "complex"
        )

        # Detect workflow state
        workflow_state = "new"
        states = [unit.get("state", "new") for unit in trans_units if unit.get("state")]
        if states:
            if "final" in states or "signed-off" in states:
                workflow_state = "final"
            elif "translated" in states or "reviewed" in states:
                workflow_state = "in_progress"
            elif "needs-translation" in states:
                workflow_state = "pending"

        return DocumentTypeInfo(
            type_name="XLIFF Translation",
            confidence=0.95,
            version=version,
            metadata={
                "standard": "XLIFF",
                "category": "localization",
                "document_type": doc_type,
                "complexity": complexity,
                "workflow_state": workflow_state,
                "translation_units": total_units,
                "file_count": len(files),
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "file_info": self._analyze_file_info(root),
            "translation_files": self._analyze_translation_files(root),
            "translation_units": self._analyze_translation_units(root),
            "languages": self._analyze_languages(root),
            "workflow_state": self._analyze_workflow_state(root),
            "translation_memory": self._analyze_translation_memory(root),
            "notes_comments": self._analyze_notes_and_comments(root),
            "quality_metrics": self._calculate_quality_metrics(root),
            "localization_metadata": self._analyze_localization_metadata(root),
            "translation_tools": self._analyze_tool_information(root),
        }

        recommendations = [
            "Validate translation completeness and consistency",
            "Review untranslated and fuzzy segments",
            "Implement quality assurance checks",
            "Standardize translation memory usage",
            "Optimize translator workflow and tools",
            "Implement terminology management",
            "Add linguistic validation rules",
            "Track translation progress and metrics",
            "Integrate with CAT tools and TMS systems",
            "Generate localization reports and analytics",
        ]

        ai_use_cases = [
            "Automated translation quality assessment",
            "Machine translation post-editing workflows",
            "Translation memory optimization",
            "Terminology extraction and consistency checking",
            "Workflow automation for localization projects",
            "Translation progress tracking and reporting",
            "Quality estimation for machine translations",
            "Multilingual content analysis and insights",
            "CAT tool integration and optimization",
            "Localization project management automation",
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
                "total_files": findings["translation_files"]["file_count"],
                "translation_units": findings["translation_units"]["unit_count"],
                "source_language": findings["languages"]["source_language"],
                "target_languages": len(findings["languages"]["target_languages"]),
                "translated_units": findings["workflow_state"]["translated_count"],
                "completion_rate": findings["quality_metrics"]["completion_rate"],
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_translation_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "translation_project": self._extract_project_metadata(root),
            "translation_catalog": self._extract_translation_catalog(root),
            "language_pairs": self._extract_language_pairs(root),
            "workflow_status": self._extract_workflow_status(root),
            "translation_statistics": self._extract_translation_statistics(root),
        }

    def _analyze_file_info(self, root: Element) -> Dict[str, Any]:
        """Analyze XLIFF file information"""
        file_info = {
            "version": root.get("version", "1.2"),
            "xmlns": root.get("xmlns"),
            "tool_id": None,
            "tool_name": None,
            "tool_version": None,
            "date": None,
            "generator": None,
        }

        # Extract tool information from header or attributes
        header = self._find_element_by_local_name(root, "header")
        if header is not None:
            tool = self._find_element_by_local_name(header, "tool")
            if tool is not None:
                file_info["tool_id"] = tool.get("tool-id")
                file_info["tool_name"] = tool.get("tool-name")
                file_info["tool_version"] = tool.get("tool-version")

        # Check for generator or creation info
        file_info["generator"] = root.get("generator") or root.get("tool-id")
        file_info["date"] = root.get("date") or root.get("created")

        return file_info

    def _analyze_translation_files(self, root: Element) -> Dict[str, Any]:
        """Analyze translation file structure"""
        files_info = {
            "file_count": 0,
            "files": [],
            "source_languages": set(),
            "target_languages": set(),
            "original_files": [],
        }

        files = self._find_elements_by_local_name(root, "file")
        files_info["file_count"] = len(files)

        for file in files:
            file_data = {
                "original": file.get("original"),
                "source_language": file.get("source-language"),
                "target_language": file.get("target-language"),
                "datatype": file.get("datatype"),
                "tool_id": file.get("tool-id"),
                "date": file.get("date"),
                "translation_units": len(
                    self._find_elements_by_local_name(file, "trans-unit")
                ),
            }

            # Track languages
            if file_data["source_language"]:
                files_info["source_languages"].add(file_data["source_language"])
            if file_data["target_language"]:
                files_info["target_languages"].add(file_data["target_language"])

            # Track original files
            if file_data["original"]:
                files_info["original_files"].append(file_data["original"])

            files_info["files"].append(file_data)

        files_info["source_languages"] = list(files_info["source_languages"])
        files_info["target_languages"] = list(files_info["target_languages"])

        return files_info

    def _analyze_translation_units(self, root: Element) -> Dict[str, Any]:
        """Analyze translation units"""
        units_info = {
            "unit_count": 0,
            "units": [],
            "states": {},
            "approved_count": 0,
            "locked_count": 0,
            "fuzzy_count": 0,
            "empty_targets": 0,
            "identical_source_target": 0,
        }

        trans_units = self._find_elements_by_local_name(root, "trans-unit")
        units_info["unit_count"] = len(trans_units)

        for unit in trans_units[:200]:  # Limit for performance
            unit_data = {
                "id": unit.get("id"),
                "state": unit.get("state", "new"),
                "approved": unit.get("approved") == "yes",
                "locked": unit.get("locked") == "yes",
                "translate": unit.get("translate", "yes") == "yes",
                "resname": unit.get("resname"),
                "source_text": None,
                "target_text": None,
                "notes": [],
            }

            # Extract source text
            source = self._find_element_by_local_name(unit, "source")
            if source is not None:
                unit_data["source_text"] = self._extract_text_content(source)

            # Extract target text
            target = self._find_element_by_local_name(unit, "target")
            if target is not None:
                unit_data["target_text"] = self._extract_text_content(target)
                if target.get("state"):
                    unit_data["state"] = target.get("state")

            # Extract notes
            for note in self._find_elements_by_local_name(unit, "note"):
                note_data = {
                    "content": note.text,
                    "from": note.get("from"),
                    "priority": note.get("priority"),
                }
                unit_data["notes"].append(note_data)

            # Track statistics
            if unit_data["approved"]:
                units_info["approved_count"] += 1
            if unit_data["locked"]:
                units_info["locked_count"] += 1
            if unit_data["state"] in ["needs-review-translation", "fuzzy-match"]:
                units_info["fuzzy_count"] += 1
            if not unit_data["target_text"] or not unit_data["target_text"].strip():
                units_info["empty_targets"] += 1
            if (
                unit_data["source_text"]
                and unit_data["target_text"]
                and unit_data["source_text"].strip() == unit_data["target_text"].strip()
            ):
                units_info["identical_source_target"] += 1

            # Track states
            state = unit_data["state"]
            units_info["states"][state] = units_info["states"].get(state, 0) + 1

            units_info["units"].append(unit_data)

        return units_info

    def _analyze_languages(self, root: Element) -> Dict[str, Any]:
        """Analyze language information"""
        lang_info = {
            "source_language": None,
            "target_languages": [],
            "language_pairs": [],
            "multilingual": False,
        }

        # Extract from file elements
        files = self._find_elements_by_local_name(root, "file")
        source_langs = set()
        target_langs = set()

        for file in files:
            src_lang = file.get("source-language")
            tgt_lang = file.get("target-language")

            if src_lang:
                source_langs.add(src_lang)
            if tgt_lang:
                target_langs.add(tgt_lang)

            if src_lang and tgt_lang:
                pair = f"{src_lang}->{tgt_lang}"
                if pair not in lang_info["language_pairs"]:
                    lang_info["language_pairs"].append(pair)

        # Set primary languages
        if source_langs:
            lang_info["source_language"] = list(source_langs)[0]
        lang_info["target_languages"] = list(target_langs)

        # Check if multilingual
        lang_info["multilingual"] = len(target_langs) > 1 or len(source_langs) > 1

        return lang_info

    def _analyze_workflow_state(self, root: Element) -> Dict[str, Any]:
        """Analyze translation workflow state"""
        workflow_info = {
            "total_units": 0,
            "new_count": 0,
            "translated_count": 0,
            "reviewed_count": 0,
            "approved_count": 0,
            "final_count": 0,
            "needs_work_count": 0,
            "completion_percentage": 0.0,
            "state_distribution": {},
        }

        trans_units = self._find_elements_by_local_name(root, "trans-unit")
        workflow_info["total_units"] = len(trans_units)

        for unit in trans_units:
            state = unit.get("state", "new")

            # Normalize state names
            if state in ["translated", "final", "signed-off"]:
                workflow_info["translated_count"] += 1
            elif state in ["needs-review-translation", "needs-review-l10n"]:
                workflow_info["reviewed_count"] += 1
            elif state in ["final", "signed-off"]:
                workflow_info["final_count"] += 1
            elif state == "new":
                workflow_info["new_count"] += 1
            elif state in ["needs-translation", "needs-adaptation"]:
                workflow_info["needs_work_count"] += 1

            # Check approved attribute
            if unit.get("approved") == "yes":
                workflow_info["approved_count"] += 1

            # Track state distribution
            workflow_info["state_distribution"][state] = (
                workflow_info["state_distribution"].get(state, 0) + 1
            )

        # Calculate completion percentage
        if workflow_info["total_units"] > 0:
            completed = workflow_info["translated_count"] + workflow_info["final_count"]
            workflow_info["completion_percentage"] = (
                completed / workflow_info["total_units"]
            ) * 100

        return workflow_info

    def _analyze_translation_memory(self, root: Element) -> Dict[str, Any]:
        """Analyze translation memory information"""
        tm_info = {
            "has_tm_matches": False,
            "match_types": {},
            "match_scores": [],
            "leveraged_matches": 0,
            "fuzzy_matches": 0,
            "exact_matches": 0,
        }

        # Look for TM match information in alt-trans elements
        alt_trans = self._find_elements_by_local_name(root, "alt-trans")
        tm_info["has_tm_matches"] = len(alt_trans) > 0

        for alt in alt_trans:
            match_quality = alt.get("match-quality")
            origin = alt.get("origin")

            if match_quality:
                try:
                    score = int(match_quality)
                    tm_info["match_scores"].append(score)

                    if score == 100:
                        tm_info["exact_matches"] += 1
                    elif score >= 75:
                        tm_info["fuzzy_matches"] += 1
                    else:
                        tm_info["leveraged_matches"] += 1
                except ValueError:
                    pass

            if origin:
                tm_info["match_types"][origin] = (
                    tm_info["match_types"].get(origin, 0) + 1
                )

        return tm_info

    def _analyze_notes_and_comments(self, root: Element) -> Dict[str, Any]:
        """Analyze notes and comments"""
        notes_info = {
            "note_count": 0,
            "notes": [],
            "note_sources": {},
            "priority_levels": {},
            "translator_notes": 0,
            "reviewer_notes": 0,
        }

        notes = self._find_elements_by_local_name(root, "note")
        notes_info["note_count"] = len(notes)

        for note in notes:
            note_data = {
                "content": note.text,
                "from": note.get("from"),
                "priority": note.get("priority"),
                "annotates": note.get("annotates"),
            }

            # Track note sources
            if note_data["from"]:
                notes_info["note_sources"][note_data["from"]] = (
                    notes_info["note_sources"].get(note_data["from"], 0) + 1
                )

                if "translator" in note_data["from"].lower():
                    notes_info["translator_notes"] += 1
                elif "reviewer" in note_data["from"].lower():
                    notes_info["reviewer_notes"] += 1

            # Track priority levels
            if note_data["priority"]:
                notes_info["priority_levels"][note_data["priority"]] = (
                    notes_info["priority_levels"].get(note_data["priority"], 0) + 1
                )

            notes_info["notes"].append(note_data)

        return notes_info

    def _analyze_localization_metadata(self, root: Element) -> Dict[str, Any]:
        """Analyze localization-specific metadata"""
        l10n_info = {
            "datatypes": set(),
            "original_formats": set(),
            "encoding_info": None,
            "phase_info": [],
            "tool_chain": [],
        }

        # Extract datatypes from file elements
        files = self._find_elements_by_local_name(root, "file")
        for file in files:
            datatype = file.get("datatype")
            if datatype:
                l10n_info["datatypes"].add(datatype)

            original = file.get("original")
            if original:
                # Extract file extension as format indicator
                if "." in original:
                    ext = original.split(".")[-1].lower()
                    l10n_info["original_formats"].add(ext)

        # Extract phase information
        phases = self._find_elements_by_local_name(root, "phase")
        for phase in phases:
            phase_data = {
                "phase_name": phase.get("phase-name"),
                "process_name": phase.get("process-name"),
                "company_name": phase.get("company-name"),
                "tool_id": phase.get("tool-id"),
                "date": phase.get("date"),
            }
            l10n_info["phase_info"].append(phase_data)

        # Extract tool chain information
        tools = self._find_elements_by_local_name(root, "tool")
        for tool in tools:
            tool_data = {
                "tool_id": tool.get("tool-id"),
                "tool_name": tool.get("tool-name"),
                "tool_version": tool.get("tool-version"),
                "tool_company": tool.get("tool-company"),
            }
            l10n_info["tool_chain"].append(tool_data)

        l10n_info["datatypes"] = list(l10n_info["datatypes"])
        l10n_info["original_formats"] = list(l10n_info["original_formats"])

        return l10n_info

    def _analyze_tool_information(self, root: Element) -> Dict[str, Any]:
        """Analyze translation tool information"""
        tool_info = {
            "primary_tool": None,
            "tool_count": 0,
            "tool_versions": {},
            "workflow_tools": [],
        }

        # Extract from header tools
        tools = self._find_elements_by_local_name(root, "tool")
        tool_info["tool_count"] = len(tools)

        for tool in tools:
            tool_name = tool.get("tool-name")
            tool_version = tool.get("tool-version")

            if tool_name and not tool_info["primary_tool"]:
                tool_info["primary_tool"] = tool_name

            if tool_name and tool_version:
                tool_info["tool_versions"][tool_name] = tool_version

            tool_data = {
                "id": tool.get("tool-id"),
                "name": tool_name,
                "version": tool_version,
                "company": tool.get("tool-company"),
            }
            tool_info["workflow_tools"].append(tool_data)

        # Also check file-level tool information
        files = self._find_elements_by_local_name(root, "file")
        for file in files:
            tool_id = file.get("tool-id")
            if tool_id and tool_id not in [
                t["id"] for t in tool_info["workflow_tools"]
            ]:
                tool_info["workflow_tools"].append(
                    {"id": tool_id, "name": None, "version": None, "company": None}
                )

        return tool_info

    def _calculate_quality_metrics(self, root: Element) -> Dict[str, Any]:
        """Calculate translation quality metrics"""
        metrics = {
            "completion_rate": 0.0,
            "approval_rate": 0.0,
            "review_rate": 0.0,
            "empty_target_rate": 0.0,
            "identical_rate": 0.0,
            "leverage_rate": 0.0,
            "average_match_score": 0.0,
        }

        trans_units = self._find_elements_by_local_name(root, "trans-unit")
        total_units = len(trans_units)

        if total_units == 0:
            return metrics

        translated_count = 0
        approved_count = 0
        reviewed_count = 0
        empty_targets = 0
        identical_count = 0

        for unit in trans_units:
            state = unit.get("state", "new")
            approved = unit.get("approved") == "yes"

            # Count completion states
            if state in ["translated", "final", "signed-off"]:
                translated_count += 1
            if approved:
                approved_count += 1
            if state in ["needs-review-translation", "needs-review-l10n"]:
                reviewed_count += 1

            # Check target content
            target = self._find_element_by_local_name(unit, "target")
            source = self._find_element_by_local_name(unit, "source")

            if target is not None:
                target_text = self._extract_text_content(target)
                if not target_text or not target_text.strip():
                    empty_targets += 1
                elif source is not None:
                    source_text = self._extract_text_content(source)
                    if (
                        source_text
                        and target_text
                        and source_text.strip() == target_text.strip()
                    ):
                        identical_count += 1

        # Calculate rates
        metrics["completion_rate"] = (translated_count / total_units) * 100
        metrics["approval_rate"] = (approved_count / total_units) * 100
        metrics["review_rate"] = (reviewed_count / total_units) * 100
        metrics["empty_target_rate"] = (empty_targets / total_units) * 100
        metrics["identical_rate"] = (identical_count / total_units) * 100

        # Calculate TM leverage
        alt_trans = self._find_elements_by_local_name(root, "alt-trans")
        if alt_trans:
            match_scores = []
            for alt in alt_trans:
                match_quality = alt.get("match-quality")
                if match_quality:
                    try:
                        match_scores.append(int(match_quality))
                    except ValueError:
                        pass

            if match_scores:
                metrics["average_match_score"] = sum(match_scores) / len(match_scores)
                metrics["leverage_rate"] = (
                    len([s for s in match_scores if s >= 75]) / len(match_scores)
                ) * 100

        return metrics

    def _extract_text_content(self, element: Element) -> str:
        """Extract text content from element, handling inline tags"""
        if element.text:
            text = element.text
        else:
            text = ""

        # Handle inline elements and their tail text
        for child in element:
            if child.tail:
                text += child.tail

        return text.strip()

    def _extract_project_metadata(self, root: Element) -> Dict[str, Any]:
        """Extract project-level metadata"""
        metadata = {
            "version": root.get("version"),
            "xmlns": root.get("xmlns"),
            "tool_id": root.get("tool-id"),
            "file_count": len(self._find_elements_by_local_name(root, "file")),
            "total_units": len(self._find_elements_by_local_name(root, "trans-unit")),
            "creation_date": None,
            "project_id": None,
        }

        # Extract creation date from various sources
        header = self._find_element_by_local_name(root, "header")
        if header is not None:
            metadata["creation_date"] = header.get("creation-date")

        # Extract project identifier
        files = self._find_elements_by_local_name(root, "file")
        if files:
            # Use first file's original as project indicator
            metadata["project_id"] = files[0].get("original", "").split("/")[-1]

        return metadata

    def _extract_translation_catalog(self, root: Element) -> List[Dict[str, Any]]:
        """Extract translation catalog"""
        catalog = []

        trans_units = self._find_elements_by_local_name(root, "trans-unit")
        for unit in trans_units[:100]:  # Limit for performance
            source = self._find_element_by_local_name(unit, "source")
            target = self._find_element_by_local_name(unit, "target")

            entry = {
                "id": unit.get("id"),
                "source": (
                    self._extract_text_content(source) if source is not None else None
                ),
                "target": (
                    self._extract_text_content(target) if target is not None else None
                ),
                "state": unit.get("state", "new"),
                "approved": unit.get("approved") == "yes",
                "resname": unit.get("resname"),
            }
            catalog.append(entry)

        return catalog

    def _extract_language_pairs(self, root: Element) -> List[Dict[str, Any]]:
        """Extract language pair information"""
        pairs = []

        files = self._find_elements_by_local_name(root, "file")
        for file in files:
            pair = {
                "source_language": file.get("source-language"),
                "target_language": file.get("target-language"),
                "original_file": file.get("original"),
                "datatype": file.get("datatype"),
                "unit_count": len(
                    self._find_elements_by_local_name(file, "trans-unit")
                ),
            }
            pairs.append(pair)

        return pairs

    def _extract_workflow_status(self, root: Element) -> Dict[str, Any]:
        """Extract workflow status information"""
        status = {
            "overall_state": "new",
            "phase_info": [],
            "completion_stats": {},
            "last_modified": None,
        }

        # Analyze overall state based on unit states
        trans_units = self._find_elements_by_local_name(root, "trans-unit")
        states = [unit.get("state", "new") for unit in trans_units]

        if states:
            state_counts = {}
            for state in states:
                state_counts[state] = state_counts.get(state, 0) + 1

            status["completion_stats"] = state_counts

            # Determine overall state
            if "final" in states or "signed-off" in states:
                status["overall_state"] = "final"
            elif "translated" in states:
                status["overall_state"] = "translated"
            elif "needs-review-translation" in states:
                status["overall_state"] = "review"

        # Extract phase information
        phases = self._find_elements_by_local_name(root, "phase")
        for phase in phases:
            phase_data = {
                "name": phase.get("phase-name"),
                "process": phase.get("process-name"),
                "date": phase.get("date"),
                "company": phase.get("company-name"),
            }
            status["phase_info"].append(phase_data)

        return status

    def _extract_translation_statistics(self, root: Element) -> Dict[str, Any]:
        """Extract translation statistics"""
        stats = {
            "total_words": 0,
            "translated_words": 0,
            "source_word_count": 0,
            "target_word_count": 0,
            "character_counts": {"source": 0, "target": 0},
            "segment_counts": {"total": 0, "translated": 0, "approved": 0, "locked": 0},
        }

        trans_units = self._find_elements_by_local_name(root, "trans-unit")
        stats["segment_counts"]["total"] = len(trans_units)

        for unit in trans_units:
            state = unit.get("state", "new")
            approved = unit.get("approved") == "yes"
            locked = unit.get("locked") == "yes"

            if state in ["translated", "final", "signed-off"]:
                stats["segment_counts"]["translated"] += 1
            if approved:
                stats["segment_counts"]["approved"] += 1
            if locked:
                stats["segment_counts"]["locked"] += 1

            # Count words and characters
            source = self._find_element_by_local_name(unit, "source")
            target = self._find_element_by_local_name(unit, "target")

            if source is not None:
                source_text = self._extract_text_content(source)
                if source_text:
                    stats["source_word_count"] += len(source_text.split())
                    stats["character_counts"]["source"] += len(source_text)

            if target is not None:
                target_text = self._extract_text_content(target)
                if target_text:
                    stats["target_word_count"] += len(target_text.split())
                    stats["character_counts"]["target"] += len(target_text)

        stats["total_words"] = stats["source_word_count"]
        stats["translated_words"] = stats["target_word_count"]

        return stats

    def _assess_translation_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess translation quality metrics"""
        metrics = {
            "completeness": 0.0,
            "consistency": 0.0,
            "workflow_health": 0.0,
            "localization_readiness": 0.0,
            "overall": 0.0,
        }

        # Completeness (based on translation progress)
        quality_data = findings["quality_metrics"]
        metrics["completeness"] = quality_data["completion_rate"] / 100.0

        # Consistency (based on identical content and empty targets)
        consistency_score = 1.0
        if quality_data["empty_target_rate"] > 0:
            consistency_score -= (quality_data["empty_target_rate"] / 100.0) * 0.5
        if quality_data["identical_rate"] > 20:  # Too many identical source/target
            consistency_score -= ((quality_data["identical_rate"] - 20) / 100.0) * 0.3

        metrics["consistency"] = max(0.0, consistency_score)

        # Workflow health (based on review and approval rates)
        workflow_score = 0.0
        if quality_data["review_rate"] > 0:
            workflow_score += 0.3
        if quality_data["approval_rate"] > 0:
            workflow_score += 0.4
        if quality_data["leverage_rate"] > 0:
            workflow_score += 0.3

        metrics["workflow_health"] = workflow_score

        # Localization readiness
        l10n_data = findings["localization_metadata"]
        notes_data = findings["notes_comments"]

        readiness_score = 0.5  # Base score
        if l10n_data["datatypes"]:
            readiness_score += 0.2
        if l10n_data["phase_info"]:
            readiness_score += 0.2
        if notes_data["note_count"] > 0:
            readiness_score += 0.1

        metrics["localization_readiness"] = min(readiness_score, 1.0)

        # Overall quality
        metrics["overall"] = (
            metrics["completeness"] * 0.4
            + metrics["consistency"] * 0.25
            + metrics["workflow_health"] * 0.2
            + metrics["localization_readiness"] * 0.15
        )

        return metrics
