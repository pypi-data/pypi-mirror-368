#!/usr/bin/env python3
"""
SOAP Envelope Handler

Analyzes SOAP 1.1 and 1.2 message envelopes to extract headers, body content,
fault information, and security details for web service analysis and security scanning.
"""

import sys
import os
from typing import Dict, Optional, Any, Tuple, TYPE_CHECKING
import defusedxml.ElementTree as ET

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class SOAPEnvelopeHandler(XMLHandler):
    """Handler for SOAP 1.1 and 1.2 message envelopes"""

    # SOAP namespace URIs
    SOAP_11_NS = "http://schemas.xmlsoap.org/soap/envelope/"
    SOAP_12_NS = "http://www.w3.org/2003/05/soap-envelope"

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for SOAP Envelope root element
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "Envelope":
            confidence = 0.0

            # Check for SOAP namespaces in root tag namespace
            if root.tag.startswith("{"):
                root_namespace = root.tag.split("}")[0][1:]
                if self.SOAP_11_NS == root_namespace:
                    confidence += 0.6
                elif self.SOAP_12_NS == root_namespace:
                    confidence += 0.6

            # Also check declared namespaces
            for uri in namespaces.values():
                if self.SOAP_11_NS in uri:
                    confidence += 0.6
                    break
                elif self.SOAP_12_NS in uri:
                    confidence += 0.6
                    break

            # Check for typical SOAP structure (Body is required)
            if root.find(".//Body") is not None or any(
                "Body" in elem.tag for elem in root
            ):
                confidence += 0.3

            # Check for Header (optional but common)
            if root.find(".//Header") is not None or any(
                "Header" in elem.tag for elem in root
            ):
                confidence += 0.1

            if confidence >= 0.6:
                return True, min(confidence, 1.0)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Determine SOAP version
        version = "1.1"  # Default

        # Check root tag namespace first
        if root.tag.startswith("{"):
            root_namespace = root.tag.split("}")[0][1:]
            if self.SOAP_12_NS == root_namespace:
                version = "1.2"

        # Also check declared namespaces
        for uri in namespaces.values():
            if self.SOAP_12_NS in uri:
                version = "1.2"
                break

        # Determine message type
        message_type = self._determine_message_type(root)

        # Extract target service information
        target_service = self._extract_target_service(root)

        metadata = {
            "protocol": "SOAP",
            "category": "web_service_message",
            "message_type": message_type,
            "target_service": target_service,
            "has_security": self._has_security_headers(root),
            "has_addressing": self._has_ws_addressing(root),
        }

        return DocumentTypeInfo(
            type_name=f"SOAP {version} {message_type}",
            confidence=0.95,
            version=version,
            metadata=metadata,
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "envelope_info": self._analyze_envelope(root),
            "headers": self._analyze_headers(root),
            "body": self._analyze_body(root),
            "security": self._analyze_security(root),
            "addressing": self._analyze_ws_addressing(root),
            "faults": self._analyze_faults(root),
            "namespaces": self._analyze_namespaces(root),
            "message_metrics": self._calculate_message_metrics(root),
        }

        recommendations = [
            "Analyze for security vulnerabilities in SOAP headers",
            "Validate input parameters for injection attacks",
            "Check authentication and authorization mechanisms",
            "Monitor for sensitive data exposure in messages",
            "Analyze message routing and addressing patterns",
            "Extract for API security testing",
            "Review fault handling and error disclosure",
        ]

        ai_use_cases = [
            "Web service security analysis",
            "API vulnerability scanning",
            "Message routing optimization",
            "Authentication pattern detection",
            "Fault analysis and error handling",
            "Performance bottleneck identification",
            "Compliance monitoring (SOX, PCI, etc.)",
            "Service dependency mapping",
            "Message transformation analysis",
        ]

        data_inventory = {
            "headers": len(findings["headers"]["header_elements"]),
            "body_elements": len(findings["body"]["body_elements"]),
            "security_tokens": len(findings["security"]["security_tokens"]),
            "faults": len(findings["faults"]["fault_details"]),
            "namespaces": len(findings["namespaces"]["declared_namespaces"]),
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
            quality_metrics=self._assess_message_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "message_metadata": {
                "version": self._get_soap_version(root),
                "type": self._determine_message_type(root),
                "target_service": self._extract_target_service(root),
            },
            "security_summary": self._extract_security_summary(root),
            "operation_info": self._extract_operation_info(root),
            "addressing_info": self._extract_addressing_summary(root),
            "fault_summary": self._extract_fault_summary(root),
        }

    def _determine_message_type(self, root: Element) -> str:
        """Determine if this is a request, response, or fault message"""

        # Check for fault first - look in Body
        body = self._find_element_by_local_name(root, "Body")
        if body is not None:
            if self._find_element_by_local_name(body, "Fault") is not None:
                return "Fault"

        # Look for response patterns
        body = self._find_element_by_local_name(root, "Body")
        if body is not None:
            for child in body:
                child_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if "Response" in child_name or "Result" in child_name:
                    return "Response"

        # Check for WS-Addressing action
        action = self._extract_ws_addressing_action(root)
        if action:
            if "Response" in action or "/response" in action.lower():
                return "Response"

        # Default to request
        return "Request"

    def _get_soap_version(self, root: Element) -> str:
        """Determine SOAP version from namespace"""
        if root.tag.startswith("{"):
            namespace = root.tag.split("}")[0][1:]
            if self.SOAP_12_NS == namespace:
                return "1.2"
        return "1.1"

    def _extract_target_service(self, root: Element) -> Optional[str]:
        """Extract target service from WS-Addressing To header"""
        headers = self._find_element_by_local_name(root, "Header")
        if headers is not None:
            to_elem = self._find_element_by_local_name(headers, "To")
            if to_elem is not None and to_elem.text:
                return to_elem.text
        return None

    def _has_security_headers(self, root: Element) -> bool:
        """Check if message has security headers"""
        headers = self._find_element_by_local_name(root, "Header")
        if headers is not None:
            # Common security header names
            security_elements = [
                "Security",
                "UsernameToken",
                "BinarySecurityToken",
                "Authentication",
            ]
            for elem in headers.iter():
                local_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if local_name in security_elements:
                    return True
        return False

    def _has_ws_addressing(self, root: Element) -> bool:
        """Check if message uses WS-Addressing"""
        headers = self._find_element_by_local_name(root, "Header")
        if headers is not None:
            addressing_elements = [
                "To",
                "From",
                "ReplyTo",
                "Action",
                "MessageID",
                "RelatesTo",
            ]
            for elem in headers.iter():
                local_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if local_name in addressing_elements:
                    return True
        return False

    def _analyze_envelope(self, root: Element) -> Dict[str, Any]:
        """Analyze SOAP envelope properties"""
        return {
            "version": self._get_soap_version(root),
            "message_type": self._determine_message_type(root),
            "has_header": self._find_element_by_local_name(root, "Header") is not None,
            "has_body": self._find_element_by_local_name(root, "Body") is not None,
            "envelope_attributes": dict(root.attrib),
            "encoding_style": root.get("encodingStyle", "document/literal"),
        }

    def _analyze_headers(self, root: Element) -> Dict[str, Any]:
        """Analyze SOAP headers"""
        headers_info = {
            "header_count": 0,
            "header_elements": [],
            "must_understand_headers": [],
            "actor_headers": [],
            "security_headers": [],
            "addressing_headers": [],
        }

        header = self._find_element_by_local_name(root, "Header")
        if header is not None:
            for child in header:
                child_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag

                header_info = {
                    "name": child_name,
                    "namespace": (
                        child.tag.split("}")[0][1:] if "}" in child.tag else None
                    ),
                    "must_understand": child.get("mustUnderstand") == "1",
                    "actor": child.get("actor"),
                    "role": child.get("role"),
                    "attributes": dict(child.attrib),
                }

                headers_info["header_elements"].append(header_info)
                headers_info["header_count"] += 1

                # Categorize headers
                if header_info["must_understand"]:
                    headers_info["must_understand_headers"].append(child_name)

                if header_info["actor"] or header_info["role"]:
                    headers_info["actor_headers"].append(child_name)

                # Check for security headers
                if any(
                    sec in child_name
                    for sec in ["Security", "Auth", "Token", "Credential"]
                ):
                    headers_info["security_headers"].append(child_name)

                # Check for addressing headers
                if any(
                    addr in child_name
                    for addr in ["To", "From", "Action", "MessageID", "RelatesTo"]
                ):
                    headers_info["addressing_headers"].append(child_name)

        return headers_info

    def _analyze_body(self, root: Element) -> Dict[str, Any]:
        """Analyze SOAP body content"""
        body_info = {
            "has_body": False,
            "body_elements": [],
            "operation": None,
            "parameters": [],
            "is_fault": False,
            "body_size_estimate": 0,
        }

        body = self._find_element_by_local_name(root, "Body")
        if body is not None:
            body_info["has_body"] = True
            body_info["body_size_estimate"] = len(ET.tostring(body, encoding="unicode"))

            for child in body:
                child_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag

                element_info = {
                    "name": child_name,
                    "namespace": (
                        child.tag.split("}")[0][1:] if "}" in child.tag else None
                    ),
                    "parameter_count": len(list(child)),
                    "attributes": dict(child.attrib),
                }

                body_info["body_elements"].append(element_info)

                # Determine operation name
                if child_name == "Fault":
                    body_info["is_fault"] = True
                    body_info["operation"] = "Fault"
                elif not body_info["operation"]:
                    body_info["operation"] = child_name

                # Extract parameters
                for param in child:
                    param_name = (
                        param.tag.split("}")[-1] if "}" in param.tag else param.tag
                    )
                    body_info["parameters"].append(
                        {
                            "name": param_name,
                            "value": param.text,
                            "type": param.get("type"),
                            "has_children": len(list(param)) > 0,
                        }
                    )

        return body_info

    def _analyze_security(self, root: Element) -> Dict[str, Any]:
        """Analyze security-related headers and tokens"""
        security_info = {
            "has_security": False,
            "security_tokens": [],
            "authentication_methods": [],
            "encryption_info": {},
            "signature_info": {},
            "security_risks": [],
        }

        headers = self._find_element_by_local_name(root, "Header")
        if headers is not None:
            # Look for WS-Security elements
            for elem in headers.iter():
                elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

                if elem_name == "Security":
                    security_info["has_security"] = True

                    # Analyze security tokens
                    for token_elem in elem:
                        token_name = (
                            token_elem.tag.split("}")[-1]
                            if "}" in token_elem.tag
                            else token_elem.tag
                        )

                        token_info = {
                            "type": token_name,
                            "attributes": dict(token_elem.attrib),
                        }

                        if token_name == "UsernameToken":
                            username = self._find_element_by_local_name(
                                token_elem, "Username"
                            )
                            password = self._find_element_by_local_name(
                                token_elem, "Password"
                            )

                            token_info["username"] = (
                                username.text if username is not None else None
                            )
                            token_info["password_type"] = (
                                password.get("Type") if password is not None else None
                            )

                            security_info["authentication_methods"].append(
                                "UsernameToken"
                            )

                            # Check for security risks
                            if password is not None and password.get(
                                "Type", ""
                            ).endswith("#PasswordText"):
                                security_info["security_risks"].append(
                                    "Plain text password in UsernameToken"
                                )

                        elif token_name == "BinarySecurityToken":
                            token_info["encoding_type"] = token_elem.get("EncodingType")
                            token_info["value_type"] = token_elem.get("ValueType")
                            security_info["authentication_methods"].append(
                                "BinarySecurityToken"
                            )

                        security_info["security_tokens"].append(token_info)

                # Check for authentication headers outside WS-Security
                elif elem_name in ["Authentication", "Credentials"]:
                    security_info["has_security"] = True
                    security_info["authentication_methods"].append(elem_name)

        return security_info

    def _analyze_ws_addressing(self, root: Element) -> Dict[str, Any]:
        """Analyze WS-Addressing headers"""
        addressing_info = {
            "has_addressing": False,
            "to": None,
            "from": None,
            "reply_to": None,
            "fault_to": None,
            "action": None,
            "message_id": None,
            "relates_to": [],
            "addressing_version": None,
        }

        headers = self._find_element_by_local_name(root, "Header")
        if headers is not None:
            addressing_elements = {
                "To": "to",
                "From": "from",
                "ReplyTo": "reply_to",
                "FaultTo": "fault_to",
                "Action": "action",
                "MessageID": "message_id",
            }

            for elem in headers.iter():
                elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

                if elem_name in addressing_elements:
                    addressing_info["has_addressing"] = True
                    field_name = addressing_elements[elem_name]
                    addressing_info[field_name] = elem.text

                    # Determine addressing version from namespace
                    if "}" in elem.tag:
                        namespace = elem.tag.split("}")[0][1:]
                        if "2005/08/addressing" in namespace:
                            addressing_info["addressing_version"] = "1.0"
                        elif "2004/08/addressing" in namespace:
                            addressing_info["addressing_version"] = "2004/08"

                elif elem_name == "RelatesTo":
                    addressing_info["has_addressing"] = True
                    addressing_info["relates_to"].append(
                        {
                            "value": elem.text,
                            "relationship_type": elem.get("RelationshipType", "Reply"),
                        }
                    )

        return addressing_info

    def _analyze_faults(self, root: Element) -> Dict[str, Any]:
        """Analyze SOAP fault information"""
        fault_info = {"is_fault": False, "fault_details": [], "fault_summary": {}}

        fault = self._find_element_by_local_name(root, "Fault")
        if fault is not None:
            fault_info["is_fault"] = True

            # SOAP 1.1 fault structure
            fault_code = self._find_element_by_local_name(fault, "faultcode")
            fault_string = self._find_element_by_local_name(fault, "faultstring")
            fault_actor = self._find_element_by_local_name(fault, "faultactor")
            detail = self._find_element_by_local_name(fault, "detail")

            # SOAP 1.2 fault structure
            if fault_code is None:
                fault_code = self._find_element_by_local_name(fault, "Code")
            if fault_string is None:
                fault_string = self._find_element_by_local_name(fault, "Reason")

            fault_details = {
                "code": fault_code.text if fault_code is not None else None,
                "string": fault_string.text if fault_string is not None else None,
                "actor": fault_actor.text if fault_actor is not None else None,
                "detail": (
                    self._extract_fault_detail(detail) if detail is not None else None
                ),
            }

            fault_info["fault_details"].append(fault_details)
            fault_info["fault_summary"] = fault_details

        return fault_info

    def _analyze_namespaces(self, root: Element) -> Dict[str, Any]:
        """Analyze namespace declarations"""
        namespaces_info = {
            "declared_namespaces": {},
            "soap_namespace": None,
            "target_namespace": None,
            "common_namespaces": [],
        }

        # Extract all namespace declarations
        for key, value in root.attrib.items():
            if key.startswith("xmlns"):
                prefix = key.split(":", 1)[1] if ":" in key else "default"
                namespaces_info["declared_namespaces"][prefix] = value

                # Identify SOAP namespace
                if self.SOAP_11_NS in value or self.SOAP_12_NS in value:
                    namespaces_info["soap_namespace"] = value

                # Identify common namespaces
                if "addressing" in value:
                    namespaces_info["common_namespaces"].append("WS-Addressing")
                elif "wssecurity" in value or "secext" in value:
                    namespaces_info["common_namespaces"].append("WS-Security")
                elif "xmlsoap.org" in value and "wsdl" in value:
                    namespaces_info["common_namespaces"].append("WSDL")

        return namespaces_info

    def _calculate_message_metrics(self, root: Element) -> Dict[str, Any]:
        """Calculate message complexity and size metrics"""
        metrics = {
            "total_elements": 0,
            "header_elements": 0,
            "body_elements": 0,
            "max_depth": 0,
            "namespace_count": 0,
            "security_complexity": 0,
            "message_size_estimate": 0,
        }

        # Count elements
        metrics["total_elements"] = len(list(root.iter()))

        header = self._find_element_by_local_name(root, "Header")
        if header is not None:
            metrics["header_elements"] = (
                len(list(header.iter())) - 1
            )  # Exclude header itself

        body = self._find_element_by_local_name(root, "Body")
        if body is not None:
            metrics["body_elements"] = len(list(body.iter())) - 1  # Exclude body itself

        # Calculate depth
        metrics["max_depth"] = self._calculate_max_depth(root)

        # Count namespaces
        metrics["namespace_count"] = len(
            [k for k in root.attrib.keys() if k.startswith("xmlns")]
        )

        # Security complexity score
        if self._has_security_headers(root):
            metrics["security_complexity"] += 1
        if self._has_ws_addressing(root):
            metrics["security_complexity"] += 0.5

        # Estimate message size
        try:
            metrics["message_size_estimate"] = len(
                ET.tostring(root, encoding="unicode")
            )
        except Exception:
            metrics["message_size_estimate"] = 0

        return metrics

    def _extract_security_summary(self, root: Element) -> Dict[str, Any]:
        """Extract security summary information"""
        return {
            "has_security": self._has_security_headers(root),
            "authentication_present": len(
                self._analyze_security(root)["authentication_methods"]
            )
            > 0,
            "security_risks": self._analyze_security(root)["security_risks"],
            "token_count": len(self._analyze_security(root)["security_tokens"]),
        }

    def _extract_operation_info(self, root: Element) -> Dict[str, Any]:
        """Extract operation information from body"""
        body_analysis = self._analyze_body(root)
        return {
            "operation": body_analysis["operation"],
            "is_fault": body_analysis["is_fault"],
            "parameter_count": len(body_analysis["parameters"]),
            "parameters": body_analysis["parameters"][:5],  # Limit to first 5
        }

    def _extract_addressing_summary(self, root: Element) -> Dict[str, Any]:
        """Extract WS-Addressing summary"""
        addressing = self._analyze_ws_addressing(root)
        return {
            "has_addressing": addressing["has_addressing"],
            "action": addressing["action"],
            "message_id": addressing["message_id"],
            "target": addressing["to"],
        }

    def _extract_fault_summary(self, root: Element) -> Optional[Dict[str, str]]:
        """Extract fault summary if present"""
        fault_analysis = self._analyze_faults(root)
        if fault_analysis["is_fault"] and fault_analysis["fault_details"]:
            fault = fault_analysis["fault_details"][0]
            return {
                "code": fault["code"],
                "message": fault["string"],
                "actor": fault["actor"],
            }
        return None

    def _extract_ws_addressing_action(self, root: Element) -> Optional[str]:
        """Extract WS-Addressing Action header"""
        headers = self._find_element_by_local_name(root, "Header")
        if headers is not None:
            action = self._find_element_by_local_name(headers, "Action")
            if action is not None:
                return action.text
        return None

    def _extract_fault_detail(self, detail: Element) -> Dict[str, Any]:
        """Extract fault detail information"""
        detail_info = {"elements": [], "text_content": detail.text}

        for child in detail:
            child_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            detail_info["elements"].append(
                {
                    "name": child_name,
                    "text": child.text,
                    "attributes": dict(child.attrib),
                }
            )

        return detail_info

    def _find_element_by_local_name(
        self, parent: Element, local_name: str
    ) -> Optional[Element]:
        """Find element by local name, ignoring namespace"""
        for elem in parent:
            elem_local_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if elem_local_name == local_name:
                return elem
        return None

    def _calculate_max_depth(self, elem: Element, depth: int = 0) -> int:
        """Calculate maximum depth of element tree"""
        if not list(elem):
            return depth
        return max(self._calculate_max_depth(child, depth + 1) for child in elem)

    def _assess_message_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess SOAP message quality and security"""

        # Security quality
        security_score = 0.0
        if findings["security"]["has_security"]:
            security_score += 0.4
            if not findings["security"]["security_risks"]:
                security_score += 0.3
            if "BinarySecurityToken" in findings["security"]["authentication_methods"]:
                security_score += 0.2
            else:
                security_score += 0.1

        # Message structure quality
        structure_score = 0.0
        if findings["envelope_info"]["has_header"]:
            structure_score += 0.3
        if findings["envelope_info"]["has_body"]:
            structure_score += 0.4
        if findings["addressing"]["has_addressing"]:
            structure_score += 0.3

        # Complexity management (lower complexity is better for maintainability)
        complexity_metrics = findings["message_metrics"]
        complexity_score = 1.0
        if complexity_metrics["total_elements"] > 50:
            complexity_score -= 0.2
        if complexity_metrics["max_depth"] > 10:
            complexity_score -= 0.2
        if complexity_metrics["namespace_count"] > 10:
            complexity_score -= 0.1
        complexity_score = max(0, complexity_score)

        # Standards compliance
        compliance_score = 0.8  # Base score
        if findings["faults"]["is_fault"]:
            # Fault messages should have proper structure
            if findings["faults"]["fault_summary"].get("code") and findings["faults"][
                "fault_summary"
            ].get("string"):
                compliance_score += 0.2
        elif findings["addressing"]["has_addressing"]:
            # Request/response should have proper addressing
            compliance_score += 0.2

        compliance_score = min(compliance_score, 1.0)

        return {
            "security": security_score,
            "structure": structure_score,
            "complexity_management": complexity_score,
            "standards_compliance": compliance_score,
            "overall": (
                security_score + structure_score + complexity_score + compliance_score
            )
            / 4,
        }
