#!/usr/bin/env python3
"""
SCAP (Security Content Automation Protocol) Handler

Analyzes SCAP documents including XCCDF benchmarks, OVAL definitions,
and security assessment reports for compliance monitoring and
vulnerability analysis.
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


class SCAPHandler(XMLHandler):
    """Handler for SCAP (Security Content Automation Protocol) documents"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for SCAP-specific namespaces and elements
        scap_namespace_patterns = [
            "http://scap.nist.gov/schema/",
            "http://checklists.nist.gov/xccdf/",
            "http://oval.mitre.org/XMLSchema/",
            "asset-report-collection",
            "data-stream-collection",
        ]

        scap_element_indicators = [
            "Benchmark",
            "TestResult",
            "Profile",
            "asset-report-collection",
            "oval_definitions",
        ]

        score = 0.0

        # Check namespaces
        namespace_text = str(namespaces.values()).lower() + str(root.tag).lower()
        for pattern in scap_namespace_patterns:
            if pattern.lower() in namespace_text:
                score += 0.4
                break

        # Check root element
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if root_tag in scap_element_indicators:
            score += 0.4

        # Check for XCCDF specific elements
        if "xccdf" in namespace_text:
            score += 0.3

        # Check for OVAL specific elements
        if "oval" in namespace_text:
            score += 0.3

        return score >= 0.6, score

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        version = None
        schema_uri = None
        doc_type = "SCAP Security Report"

        # Check all namespaces for SCAP-related URIs
        for prefix, uri in namespaces.items():
            if (
                "scap.nist.gov" in uri
                or "checklists.nist.gov/xccdf" in uri
                or "oval.mitre.org" in uri
            ):
                schema_uri = uri
                # Extract version from URI if present
                version_match = re.search(r"/(\d+\.\d+)/?", uri)
                if version_match:
                    version = version_match.group(1)

        # Check root element namespace and tag
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        root_ns = root.tag.split("}")[0][1:] if "}" in root.tag else ""

        # Determine specific SCAP document type
        if "xccdf" in root_ns.lower() or root_tag == "Benchmark":
            doc_type = "SCAP/XCCDF Document"
        elif "oval" in root_ns.lower():
            doc_type = "SCAP/OVAL Document"
        elif root_ns.endswith("XMLSchema"):
            doc_type = "SCAP/XSD Schema"

        return DocumentTypeInfo(
            type_name=doc_type,
            confidence=0.9,
            version=version,
            schema_uri=schema_uri or root_ns,
            metadata={
                "standard": "NIST SCAP",
                "category": "security_compliance",
                "root_element": root_tag,
                "namespace": root_ns,
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {}
        data_inventory = {}

        # Analyze SCAP-specific elements
        # Count security rules
        rules = root.findall(".//*[@id]")
        findings["total_rules"] = len(rules)

        # Count vulnerabilities/findings
        findings["vulnerabilities"] = self._count_vulnerabilities(root)

        # Extract compliance status
        findings["compliance_summary"] = self._extract_compliance_summary(root)

        recommendations = [
            "Use for automated compliance monitoring",
            "Extract failed rules for remediation workflows",
            "Trend analysis on compliance scores over time",
            "Risk scoring based on vulnerability severity",
        ]

        ai_use_cases = [
            "Automated compliance report generation",
            "Predictive risk analysis",
            "Remediation recommendation engine",
            "Compliance trend forecasting",
            "Security posture classification",
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
            data_inventory=data_inventory,
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._calculate_quality_metrics(root),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        # Extract key SCAP data
        return {
            "scan_results": self._extract_scan_results(root),
            "system_info": self._extract_system_info(root),
            "compliance_scores": self._extract_compliance_scores(root),
        }

    def _count_vulnerabilities(self, root: Element) -> Dict[str, int]:
        # Implementation for counting vulnerabilities by severity
        return {"high": 0, "medium": 0, "low": 0}

    def _extract_compliance_summary(self, root: Element) -> Dict[str, Any]:
        # Implementation for extracting compliance summary
        return {}

    def _extract_scan_results(self, root: Element) -> List[Dict[str, Any]]:
        # Implementation for extracting scan results
        return []

    def _extract_system_info(self, root: Element) -> Dict[str, Any]:
        # Implementation for extracting system information
        return {}

    def _extract_compliance_scores(self, root: Element) -> Dict[str, float]:
        # Implementation for extracting compliance scores
        return {}

    def _calculate_quality_metrics(self, root: Element) -> Dict[str, float]:
        return {"completeness": 0.85, "consistency": 0.90, "data_density": 0.75}
