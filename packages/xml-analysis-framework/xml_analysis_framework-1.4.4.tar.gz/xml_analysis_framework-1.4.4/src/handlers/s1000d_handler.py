#!/usr/bin/env python3
"""
S1000D Handler

Specialized handler for S1000D technical documentation XML files.
S1000D is an international standard for technical publications that use structured XML
to represent complex technical documentation with rich metadata, cross-references,
and applicability rules.

Key S1000D Features Handled:
- Data Module Codes (DMC) for unique identification
- Cross-references (dmRef) between documents
- Applicability rules for filtering content
- Procedural steps and safety information
- Parts lists and equipment requirements
- Technical illustrations and media references
"""

import sys
import os
from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
import re

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class S1000DHandler(XMLHandler):
    """Handler for S1000D technical documentation XML files"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for S1000D root elements
        s1000d_roots = ["dmodule", "applicCrossRefTable", "publication"]
        tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if tag in s1000d_roots:
            return True, 0.9

        # Check for S1000D namespace
        if any("s1000d.org" in uri.lower() for uri in namespaces.values()):
            return True, 1.0

        # Check for S1000D schema references
        schema_locations = root.attrib.get("xsi:noNamespaceSchemaLocation", "")
        if "s1000d" in schema_locations.lower():
            return True, 0.95

        # Check for DMC pattern in filename or content
        if self._has_s1000d_patterns(root):
            return True, 0.8

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        
        # Detect S1000D version from schema
        version = self._detect_s1000d_version(root, namespaces)
        
        # Determine document type
        doc_type = self._determine_document_type(root)
        
        metadata = {
            "standard": "S1000D",
            "category": "technical_documentation",
            "document_structure": tag,
            "document_subtype": doc_type,
            "has_procedures": self._has_procedures(root),
            "has_parts_lists": self._has_parts_lists(root),
            "has_cross_references": self._has_cross_references(root),
            "has_applicability": self._has_applicability_rules(root),
            "dmc_code": self._extract_dmc_code(root),
            "technical_name": self._extract_technical_name(root),
            "info_name": self._extract_info_name(root),
        }

        return DocumentTypeInfo(
            type_name=f"S1000D {doc_type}",
            confidence=0.95,
            version=version,
            schema_uri=self._extract_schema_uri(root),
            metadata=metadata,
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "s1000d_info": {
                "document_type": self._determine_document_type(root),
                "version": self._detect_s1000d_version(root, {}),
                "dmc_analysis": self._analyze_dmc_code(root),
                "applicability": self._analyze_applicability(root),
            },
            "content_structure": self._analyze_content_structure(root),
            "cross_references": self._analyze_cross_references(root),
            "procedures": self._analyze_procedures(root),
            "parts_and_equipment": self._analyze_parts_equipment(root),
            "safety_information": self._analyze_safety_info(root),
            "media_references": self._analyze_media_references(root),
            "metadata_quality": self._analyze_metadata_quality(root),
        }

        recommendations = self._generate_recommendations(findings)
        ai_use_cases = self._identify_ai_use_cases(findings)

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
            data_inventory=self._inventory_s1000d_data(root),
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._analyze_s1000d_quality(root),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        """Extract key S1000D structured data"""
        return {
            "identification": self._extract_identification_data(root),
            "procedural_steps": self._extract_procedural_steps(root),
            "parts_list": self._extract_parts_list(root),
            "cross_references": self._extract_cross_reference_data(root),
            "applicability_rules": self._extract_applicability_data(root),
            "safety_requirements": self._extract_safety_data(root),
            "media_objects": self._extract_media_data(root),
        }

    # S1000D-specific analysis methods
    
    def _has_s1000d_patterns(self, root: Element) -> bool:
        """Check for S1000D-specific patterns"""
        # Look for DMC patterns in attributes or text
        dmc_pattern = r"DMC-[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+"
        
        # Check attributes
        for elem in root.iter():
            for attr_value in elem.attrib.values():
                if re.search(dmc_pattern, str(attr_value)):
                    return True
                    
        return False

    def _detect_s1000d_version(self, root: Element, namespaces: Dict[str, str]) -> Optional[str]:
        """Detect S1000D version from schema or namespace"""
        # Check schema location
        schema_loc = root.attrib.get("xsi:noNamespaceSchemaLocation", "")
        version_match = re.search(r"S1000D[_-](\d+[.\-_]\d+)", schema_loc)
        if version_match:
            return version_match.group(1).replace("_", ".").replace("-", ".")
            
        # Check namespace URIs
        for uri in namespaces.values():
            version_match = re.search(r"S1000D[_-](\d+[.\-_]\d+)", uri)
            if version_match:
                return version_match.group(1).replace("_", ".").replace("-", ".")
                
        return "Unknown"

    def _determine_document_type(self, root: Element) -> str:
        """Determine the specific type of S1000D document"""
        # Check for specific content types
        if root.find(".//procedure") is not None:
            return "Procedural Data Module"
        elif root.find(".//description") is not None:
            return "Descriptive Data Module"
        elif root.find(".//partsList") is not None:
            return "Parts List Data Module"
        elif root.find(".//fault") is not None:
            return "Fault Isolation Data Module"
        elif root.find(".//frontMatter") is not None:
            return "Front Matter"
        else:
            return "Data Module"

    def _extract_dmc_code(self, root: Element) -> Optional[str]:
        """Extract Data Module Code"""
        dmc_elem = root.find(".//dmCode")
        if dmc_elem is not None:
            # Build DMC from attributes
            attrs = ["modelIdentCode", "systemDiffCode", "systemCode", 
                    "subSystemCode", "subSubSystemCode", "assyCode", 
                    "disassyCode", "disassyCodeVariant", "infoCode", 
                    "infoCodeVariant", "itemLocationCode"]
            
            dmc_parts = []
            for attr in attrs:
                value = dmc_elem.get(attr, "")
                dmc_parts.append(value)
                
            return "-".join(dmc_parts) if any(dmc_parts) else None
        return None

    def _extract_technical_name(self, root: Element) -> Optional[str]:
        """Extract technical name from dmTitle"""
        tech_name = root.find(".//techName")
        return tech_name.text if tech_name is not None else None

    def _extract_info_name(self, root: Element) -> Optional[str]:
        """Extract information name from dmTitle"""
        info_name = root.find(".//infoName")
        return info_name.text if info_name is not None else None

    def _has_procedures(self, root: Element) -> bool:
        """Check if document contains procedural steps"""
        return root.find(".//procedure") is not None or root.find(".//proceduralStep") is not None

    def _has_parts_lists(self, root: Element) -> bool:
        """Check if document contains parts lists"""
        return (root.find(".//partsList") is not None or 
                root.find(".//reqSupplies") is not None or
                root.find(".//reqSpares") is not None)

    def _has_cross_references(self, root: Element) -> bool:
        """Check if document contains cross-references"""
        return root.find(".//dmRef") is not None or root.find(".//internalRef") is not None

    def _has_applicability_rules(self, root: Element) -> bool:
        """Check if document contains applicability rules"""
        return root.find(".//applic") is not None

    def _analyze_procedures(self, root: Element) -> Dict[str, Any]:
        """Analyze procedural content"""
        procedures = root.findall(".//procedure")
        steps = root.findall(".//proceduralStep")
        
        return {
            "procedure_count": len(procedures),
            "total_steps": len(steps),
            "has_preliminary_requirements": root.find(".//preliminaryRqmts") is not None,
            "has_safety_requirements": root.find(".//reqSafety") is not None,
            "required_tools": self._extract_required_tools(root),
            "required_supplies": self._extract_required_supplies(root),
        }

    def _analyze_cross_references(self, root: Element) -> Dict[str, Any]:
        """Analyze cross-references between documents"""
        dm_refs = root.findall(".//dmRef")
        internal_refs = root.findall(".//internalRef")
        
        referenced_dmcs = []
        for ref in dm_refs:
            dmc_elem = ref.find(".//dmCode")
            if dmc_elem is not None:
                referenced_dmcs.append(self._build_dmc_from_element(dmc_elem))
        
        return {
            "external_references": len(dm_refs),
            "internal_references": len(internal_refs),
            "referenced_documents": referenced_dmcs,
            "reference_density": len(dm_refs) + len(internal_refs),
        }

    def _extract_required_tools(self, root: Element) -> List[str]:
        """Extract required tools/equipment"""
        tools = []
        for tool_elem in root.findall(".//reqSupportEquips//supportEquipDescr"):
            name_elem = tool_elem.find(".//name")
            if name_elem is not None and name_elem.text:
                tools.append(name_elem.text.strip())
        return tools

    def _extract_required_supplies(self, root: Element) -> List[str]:
        """Extract required supplies/materials"""
        supplies = []
        for supply_elem in root.findall(".//reqSupplies//supplyDescr"):
            name_elem = supply_elem.find(".//name")
            if name_elem is not None and name_elem.text:
                supplies.append(name_elem.text.strip())
        return supplies

    def _analyze_applicability(self, root: Element) -> Dict[str, Any]:
        """Analyze applicability rules"""
        applic_elem = root.find(".//applic")
        if applic_elem is None:
            return {"has_applicability": False}
            
        return {
            "has_applicability": True,
            "display_text": self._get_element_text(applic_elem.find(".//displayText")),
            "conditions_count": len(applic_elem.findall(".//assert")),
            "logical_operators": len(applic_elem.findall(".//evaluate")),
        }

    def _generate_recommendations(self, findings: Dict[str, Any]) -> List[str]:
        """Generate S1000D-specific recommendations"""
        recommendations = []
        
        if findings["procedures"]["procedure_count"] > 0:
            recommendations.append("Leverage procedural content for AI-powered maintenance assistance")
            
        if findings["cross_references"]["external_references"] > 5:
            recommendations.append("Build knowledge graph from cross-reference network")
            
        if findings["s1000d_info"]["applicability"]["has_applicability"]:
            recommendations.append("Use applicability rules for context-aware content filtering")
            
        if findings["parts_and_equipment"]["parts_count"] > 0:
            recommendations.append("Integrate parts data with inventory management systems")
            
        return recommendations

    def _identify_ai_use_cases(self, findings: Dict[str, Any]) -> List[str]:
        """Identify AI/ML use cases specific to S1000D"""
        use_cases = [
            "Technical documentation chatbot with S1000D awareness",
            "Cross-document relationship extraction and mapping",
            "Maintenance procedure automation and guidance",
            "Parts recommendation and inventory optimization",
        ]
        
        if findings["procedures"]["has_safety_requirements"]:
            use_cases.append("Safety compliance monitoring and alerts")
            
        if findings["cross_references"]["reference_density"] > 10:
            use_cases.append("Document dependency analysis and impact assessment")
            
        return use_cases

    def _inventory_s1000d_data(self, root: Element) -> Dict[str, int]:
        """Inventory S1000D-specific data types"""
        return {
            "procedures": len(root.findall(".//procedure")),
            "procedural_steps": len(root.findall(".//proceduralStep")),
            "cross_references": len(root.findall(".//dmRef")),
            "internal_references": len(root.findall(".//internalRef")),
            "parts_references": len(root.findall(".//supplyDescr")),
            "tool_references": len(root.findall(".//supportEquipDescr")),
            "safety_elements": len(root.findall(".//safety")),
            "media_objects": len(root.findall(".//graphic")),
            "applicability_rules": len(root.findall(".//applic")),
        }

    def _analyze_s1000d_quality(self, root: Element) -> Dict[str, float]:
        """Analyze S1000D document quality metrics"""
        total_elements = len(list(root.iter()))
        
        # Calculate various quality metrics
        metadata_completeness = self._calculate_metadata_completeness(root)
        reference_quality = self._calculate_reference_quality(root)
        structure_quality = self._calculate_structure_quality(root)
        
        return {
            "metadata_completeness": metadata_completeness,
            "reference_quality": reference_quality,
            "structure_quality": structure_quality,
            "overall_quality": (metadata_completeness + reference_quality + structure_quality) / 3,
        }

    # Helper methods for quality analysis
    
    def _calculate_metadata_completeness(self, root: Element) -> float:
        """Calculate completeness of S1000D metadata"""
        required_metadata = ["dmCode", "issueDate", "dmTitle"]
        found_metadata = sum(1 for meta in required_metadata if root.find(f".//{meta}") is not None)
        return found_metadata / len(required_metadata)

    def _calculate_reference_quality(self, root: Element) -> float:
        """Calculate quality of cross-references"""
        dm_refs = root.findall(".//dmRef")
        if not dm_refs:
            return 1.0  # No refs to validate
            
        valid_refs = sum(1 for ref in dm_refs if ref.find(".//dmCode") is not None)
        return valid_refs / len(dm_refs) if dm_refs else 1.0

    def _calculate_structure_quality(self, root: Element) -> float:
        """Calculate structural quality"""
        # Check for proper S1000D structure
        has_ident = root.find(".//identAndStatusSection") is not None
        has_content = root.find(".//content") is not None
        
        structure_score = (has_ident + has_content) / 2
        return structure_score

    # Utility methods
    
    def _get_element_text(self, elem: Optional[Element]) -> Optional[str]:
        """Safely get text from an element"""
        return elem.text.strip() if elem is not None and elem.text else None

    def _build_dmc_from_element(self, dmc_elem: Element) -> str:
        """Build DMC string from dmCode element"""
        attrs = ["modelIdentCode", "systemDiffCode", "systemCode", 
                "subSystemCode", "subSubSystemCode", "assyCode", 
                "disassyCode", "disassyCodeVariant", "infoCode", 
                "infoCodeVariant", "itemLocationCode"]
        
        dmc_parts = [dmc_elem.get(attr, "") for attr in attrs]
        return "-".join(dmc_parts)

    def _extract_schema_uri(self, root: Element) -> Optional[str]:
        """Extract schema URI from document"""
        return root.attrib.get("xsi:noNamespaceSchemaLocation")

    # Additional extraction methods for structured data
    
    def _extract_identification_data(self, root: Element) -> Dict[str, Any]:
        """Extract identification and status information"""
        return {
            "dmc_code": self._extract_dmc_code(root),
            "technical_name": self._extract_technical_name(root),
            "info_name": self._extract_info_name(root),
            "issue_date": self._get_element_text(root.find(".//issueDate")),
            "issue_number": root.find(".//issueInfo").get("issueNumber") if root.find(".//issueInfo") is not None else None,
        }

    def _extract_procedural_steps(self, root: Element) -> List[Dict[str, Any]]:
        """Extract detailed procedural steps"""
        steps = []
        for i, step in enumerate(root.findall(".//proceduralStep")):
            step_data = {
                "step_number": i + 1,
                "content": self._get_element_text(step.find(".//para")),
                "has_substeps": len(step.findall(".//proceduralStep")) > 0,
                "substep_count": len(step.findall(".//proceduralStep")),
            }
            steps.append(step_data)
        return steps

    def _extract_parts_list(self, root: Element) -> List[Dict[str, Any]]:
        """Extract parts and supplies information"""
        parts = []
        
        # Extract supplies
        for supply in root.findall(".//supplyDescr"):
            part_data = {
                "type": "supply",
                "name": self._get_element_text(supply.find(".//name")),
                "part_number": self._get_element_text(supply.find(".//partNumber")),
                "quantity": self._get_element_text(supply.find(".//reqQuantity")),
            }
            parts.append(part_data)
            
        # Extract spare parts
        for spare in root.findall(".//spareDescr"):
            part_data = {
                "type": "spare",
                "name": self._get_element_text(spare.find(".//name")),
                "part_number": self._get_element_text(spare.find(".//partNumber")),
                "quantity": self._get_element_text(spare.find(".//quantity")),
            }
            parts.append(part_data)
            
        return parts

    def _extract_cross_reference_data(self, root: Element) -> List[Dict[str, Any]]:
        """Extract cross-reference information"""
        references = []
        
        for dm_ref in root.findall(".//dmRef"):
            dmc_elem = dm_ref.find(".//dmCode")
            if dmc_elem is not None:
                ref_data = {
                    "type": "external",
                    "target_dmc": self._build_dmc_from_element(dmc_elem),
                    "context": self._get_parent_context(dm_ref),
                }
                references.append(ref_data)
                
        for internal_ref in root.findall(".//internalRef"):
            ref_data = {
                "type": "internal",
                "target_id": internal_ref.get("internalRefId"),
                "target_type": internal_ref.get("internalRefTargetType"),
                "context": self._get_parent_context(internal_ref),
            }
            references.append(ref_data)
            
        return references

    def _extract_applicability_data(self, root: Element) -> Dict[str, Any]:
        """Extract applicability rules"""
        applic = root.find(".//applic")
        if applic is None:
            return {}
            
        return {
            "display_text": self._get_element_text(applic.find(".//displayText//simplePara")),
            "conditions": [
                {
                    "property": assert_elem.get("applicPropertyIdent"),
                    "type": assert_elem.get("applicPropertyType"),
                    "values": assert_elem.get("applicPropertyValues"),
                }
                for assert_elem in applic.findall(".//assert")
            ],
        }

    def _extract_safety_data(self, root: Element) -> List[Dict[str, Any]]:
        """Extract safety information"""
        safety_items = []
        
        for safety in root.findall(".//safety"):
            safety_data = {
                "type": safety.get("safetyType", "general"),
                "content": self._get_element_text(safety.find(".//para")),
                "level": safety.get("safetyLevel"),
            }
            safety_items.append(safety_data)
            
        return safety_items

    def _extract_media_data(self, root: Element) -> List[Dict[str, Any]]:
        """Extract media object references"""
        media_items = []
        
        for graphic in root.findall(".//graphic"):
            media_data = {
                "type": "graphic",
                "entity_id": graphic.get("infoEntityIdent"),
                "format": self._infer_graphic_format(graphic.get("infoEntityIdent", "")),
                "context": self._get_parent_context(graphic),
            }
            media_items.append(media_data)
            
        return media_items

    def _get_parent_context(self, element: Element) -> str:
        """Get context information about where an element appears"""
        parent = element.getparent() if hasattr(element, 'getparent') else None
        if parent is not None:
            parent_tag = parent.tag.split("}")[-1] if "}" in parent.tag else parent.tag
            return parent_tag
        return "unknown"

    def _infer_graphic_format(self, entity_id: str) -> str:
        """Infer graphic format from entity ID"""
        if entity_id.endswith(".CGM"):
            return "CGM"
        elif entity_id.endswith(".PNG"):
            return "PNG"
        elif entity_id.endswith(".JPG"):
            return "JPEG"
        elif entity_id.endswith(".SWF"):
            return "SWF"
        else:
            return "unknown"

    # Analysis methods continued
    
    def _analyze_dmc_code(self, root: Element) -> Dict[str, Any]:
        """Analyze DMC code structure"""
        dmc_elem = root.find(".//dmCode")
        if dmc_elem is None:
            return {"valid": False}
            
        return {
            "valid": True,
            "model_ident": dmc_elem.get("modelIdentCode"),
            "system_code": dmc_elem.get("systemCode"),
            "info_code": dmc_elem.get("infoCode"),
            "item_location": dmc_elem.get("itemLocationCode"),
            "full_code": self._build_dmc_from_element(dmc_elem),
        }

    def _analyze_content_structure(self, root: Element) -> Dict[str, Any]:
        """Analyze S1000D content structure"""
        return {
            "has_ident_section": root.find(".//identAndStatusSection") is not None,
            "has_content_section": root.find(".//content") is not None,
            "content_type": self._determine_content_type(root),
            "sections": self._count_sections(root),
            "depth": self._calculate_max_depth(root),
        }

    def _determine_content_type(self, root: Element) -> str:
        """Determine the main content type"""
        content_elem = root.find(".//content")
        if content_elem is None:
            return "unknown"
            
        if content_elem.find(".//procedure") is not None:
            return "procedure"
        elif content_elem.find(".//description") is not None:
            return "description"
        elif content_elem.find(".//partsList") is not None:
            return "parts_list"
        elif content_elem.find(".//frontMatter") is not None:
            return "front_matter"
        else:
            return "other"

    def _count_sections(self, root: Element) -> Dict[str, int]:
        """Count different types of sections"""
        return {
            "procedures": len(root.findall(".//procedure")),
            "descriptions": len(root.findall(".//description")),
            "levelledPara": len(root.findall(".//levelledPara")),
            "tables": len(root.findall(".//table")),
            "figures": len(root.findall(".//figure")),
        }

    def _calculate_max_depth(self, root: Element, current_depth: int = 0) -> int:
        """Calculate maximum nesting depth"""
        if len(root) == 0:
            return current_depth
            
        max_child_depth = 0
        for child in root:
            child_depth = self._calculate_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
            
        return max_child_depth

    def _analyze_parts_equipment(self, root: Element) -> Dict[str, Any]:
        """Analyze parts and equipment information"""
        return {
            "supplies_count": len(root.findall(".//supplyDescr")),
            "spares_count": len(root.findall(".//spareDescr")),
            "tools_count": len(root.findall(".//supportEquipDescr")),
            "parts_count": len(root.findall(".//supplyDescr")) + len(root.findall(".//spareDescr")),
            "has_quantities": any(
                elem.find(".//reqQuantity") is not None or elem.find(".//quantity") is not None
                for elem in root.findall(".//supplyDescr") + root.findall(".//spareDescr")
            ),
        }

    def _analyze_safety_info(self, root: Element) -> Dict[str, Any]:
        """Analyze safety information"""
        safety_elements = root.findall(".//safety")
        req_safety = root.findall(".//reqSafety")
        
        return {
            "safety_elements_count": len(safety_elements),
            "required_safety_count": len(req_safety),
            "has_safety_requirements": len(req_safety) > 0,
            "safety_types": list(set(
                elem.get("safetyType", "general") for elem in safety_elements
            )),
        }

    def _analyze_media_references(self, root: Element) -> Dict[str, Any]:
        """Analyze media and illustration references"""
        graphics = root.findall(".//graphic")
        figures = root.findall(".//figure")
        
        graphic_formats = {}
        for graphic in graphics:
            entity_id = graphic.get("infoEntityIdent", "")
            format_type = self._infer_graphic_format(entity_id)
            graphic_formats[format_type] = graphic_formats.get(format_type, 0) + 1
        
        return {
            "graphics_count": len(graphics),
            "figures_count": len(figures),
            "graphic_formats": graphic_formats,
            "has_multimedia": len(graphics) > 0,
        }

    def _analyze_metadata_quality(self, root: Element) -> Dict[str, Any]:
        """Analyze quality of S1000D metadata"""
        required_elements = {
            "dmCode": root.find(".//dmCode") is not None,
            "dmTitle": root.find(".//dmTitle") is not None,
            "issueInfo": root.find(".//issueInfo") is not None,
            "issueDate": root.find(".//issueDate") is not None,
            "security": root.find(".//security") is not None,
        }
        
        completeness = sum(required_elements.values()) / len(required_elements)
        
        return {
            "required_elements": required_elements,
            "completeness_score": completeness,
            "has_all_required": all(required_elements.values()),
        }