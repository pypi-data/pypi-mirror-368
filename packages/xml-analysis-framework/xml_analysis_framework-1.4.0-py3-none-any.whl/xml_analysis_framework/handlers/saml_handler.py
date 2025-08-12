#!/usr/bin/env python3
"""
SAML Handler

Analyzes SAML (Security Assertion Markup Language) assertions, responses, and requests
for security analysis, SSO configuration validation, and identity management.
"""

import sys
import os
from typing import Dict, Optional, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class SAMLHandler(XMLHandler):
    """Handler for SAML assertions, responses, and requests"""

    # SAML namespace URIs
    SAML_20_ASSERTION_NS = "urn:oasis:names:tc:SAML:2.0:assertion"
    SAML_20_PROTOCOL_NS = "urn:oasis:names:tc:SAML:2.0:protocol"
    SAML_11_ASSERTION_NS = "urn:oasis:names:tc:SAML:1.0:assertion"
    SAML_11_PROTOCOL_NS = "urn:oasis:names:tc:SAML:1.0:protocol"

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for SAML root elements
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # Common SAML root elements
        saml_roots = [
            "Assertion",
            "Response",
            "AuthnRequest",
            "LogoutRequest",
            "LogoutResponse",
        ]

        if root_tag in saml_roots:
            confidence = 0.0

            # Check for SAML namespaces in root tag
            if root.tag.startswith("{"):
                root_namespace = root.tag.split("}")[0][1:]
                if any(
                    saml_ns in root_namespace
                    for saml_ns in [
                        self.SAML_20_ASSERTION_NS,
                        self.SAML_20_PROTOCOL_NS,
                        self.SAML_11_ASSERTION_NS,
                        self.SAML_11_PROTOCOL_NS,
                    ]
                ):
                    confidence += 0.7

            # Check declared namespaces
            for uri in namespaces.values():
                if any(
                    saml_ns in uri
                    for saml_ns in [
                        self.SAML_20_ASSERTION_NS,
                        self.SAML_20_PROTOCOL_NS,
                        self.SAML_11_ASSERTION_NS,
                        self.SAML_11_PROTOCOL_NS,
                    ]
                ):
                    confidence += 0.7
                    break

            # Check for typical SAML attributes
            saml_attributes = ["ID", "IssueInstant", "Version", "Issuer"]
            attr_matches = sum(
                1 for attr in saml_attributes if root.get(attr) is not None
            )
            confidence += attr_matches * 0.1

            # Check for common SAML child elements
            common_children = [
                "Issuer",
                "Subject",
                "Conditions",
                "AttributeStatement",
                "AuthnStatement",
            ]
            child_matches = sum(
                1
                for child in common_children
                if self._find_element_by_local_name(root, child) is not None
            )
            confidence += child_matches * 0.05

            if confidence >= 0.7:
                return True, min(confidence, 1.0)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Determine SAML version
        version = self._get_saml_version(root, namespaces)

        # Determine message type
        message_type = self._determine_message_type(root)

        # Extract issuer information
        issuer = self._extract_issuer(root)

        metadata = {
            "protocol": "SAML",
            "category": "security_assertion",
            "message_type": message_type,
            "issuer": issuer,
            "has_signature": self._has_signature(root),
            "has_encryption": self._has_encryption(root),
            "assertion_count": self._count_assertions(root),
        }

        return DocumentTypeInfo(
            type_name=f"SAML {version} {message_type}",
            confidence=0.95,
            version=version,
            metadata=metadata,
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "saml_info": self._analyze_saml_document(root),
            "assertions": self._analyze_assertions(root),
            "subject_info": self._analyze_subject(root),
            "conditions": self._analyze_conditions(root),
            "attributes": self._analyze_attributes(root),
            "authentication": self._analyze_authentication(root),
            "security": self._analyze_security(root),
            "namespaces": self._analyze_namespaces(root),
            "validation_metrics": self._calculate_validation_metrics(root),
        }

        recommendations = [
            "Validate digital signatures on all SAML assertions",
            "Check assertion validity periods and conditions",
            "Analyze attribute statements for sensitive data exposure",
            "Verify issuer trust relationships and certificates",
            "Monitor for SAML injection and manipulation attacks",
            "Review authentication context and session management",
            "Analyze for compliance with SAML security profiles",
            "Check encryption requirements for sensitive assertions",
        ]

        ai_use_cases = [
            "SAML security analysis and vulnerability assessment",
            "SSO configuration validation and optimization",
            "Identity federation security monitoring",
            "SAML assertion fraud detection",
            "Compliance auditing (SOX, HIPAA, PCI-DSS)",
            "Authentication flow analysis and optimization",
            "Certificate and trust chain validation",
            "SAML protocol attack detection",
            "Identity attribute analysis and privacy protection",
        ]

        data_inventory = {
            "assertions": len(findings["assertions"]["assertion_details"]),
            "attributes": len(findings["attributes"]["attribute_statements"]),
            "subjects": 1 if findings["subject_info"]["has_subject"] else 0,
            "conditions": len(findings["conditions"]["condition_types"]),
            "signatures": 1 if findings["security"]["has_signature"] else 0,
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
            quality_metrics=self._assess_saml_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "document_metadata": {
                "version": self._get_saml_version(root, {}),
                "type": self._determine_message_type(root),
                "issuer": self._extract_issuer(root),
                "id": root.get("ID"),
                "issue_instant": root.get("IssueInstant"),
            },
            "security_summary": self._extract_security_summary(root),
            "subject_summary": self._extract_subject_summary(root),
            "assertion_summary": self._extract_assertion_summary(root),
            "conditions_summary": self._extract_conditions_summary(root),
        }

    def _get_saml_version(self, root: Element, namespaces: Dict[str, str]) -> str:
        """Determine SAML version from namespace or version attribute"""
        # Check version attribute first
        version = root.get("Version")
        if version:
            return version

        # Check namespace
        if root.tag.startswith("{"):
            namespace = root.tag.split("}")[0][1:]
            if (
                self.SAML_20_ASSERTION_NS in namespace
                or self.SAML_20_PROTOCOL_NS in namespace
            ):
                return "2.0"
            elif (
                self.SAML_11_ASSERTION_NS in namespace
                or self.SAML_11_PROTOCOL_NS in namespace
            ):
                return "1.1"

        # Check declared namespaces
        for uri in namespaces.values():
            if self.SAML_20_ASSERTION_NS in uri or self.SAML_20_PROTOCOL_NS in uri:
                return "2.0"
            elif self.SAML_11_ASSERTION_NS in uri or self.SAML_11_PROTOCOL_NS in uri:
                return "1.1"

        return "2.0"  # Default to 2.0

    def _determine_message_type(self, root: Element) -> str:
        """Determine SAML message type from root element"""
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        type_mapping = {
            "Assertion": "Assertion",
            "Response": "Response",
            "AuthnRequest": "Authentication Request",
            "LogoutRequest": "Logout Request",
            "LogoutResponse": "Logout Response",
            "ArtifactResolve": "Artifact Resolve",
            "ArtifactResponse": "Artifact Response",
        }

        return type_mapping.get(root_tag, root_tag)

    def _extract_issuer(self, root: Element) -> Optional[str]:
        """Extract issuer information"""
        issuer = self._find_element_by_local_name(root, "Issuer")
        if issuer is not None and issuer.text:
            return issuer.text.strip()
        return None

    def _has_signature(self, root: Element) -> bool:
        """Check if document has digital signature"""
        return self._find_element_by_local_name(root, "Signature") is not None

    def _has_encryption(self, root: Element) -> bool:
        """Check if document has encrypted elements"""
        return (
            self._find_element_by_local_name(root, "EncryptedAssertion") is not None
            or self._find_element_by_local_name(root, "EncryptedID") is not None
            or self._find_element_by_local_name(root, "EncryptedAttribute") is not None
        )

    def _count_assertions(self, root: Element) -> int:
        """Count number of assertions"""
        assertions = []
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "Assertion":
            assertions.append(root)

        # Look for embedded assertions
        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if elem_name == "Assertion" and elem != root:
                assertions.append(elem)

        return len(assertions)

    def _analyze_saml_document(self, root: Element) -> Dict[str, Any]:
        """Analyze SAML document properties"""
        return {
            "version": self._get_saml_version(root, {}),
            "message_type": self._determine_message_type(root),
            "id": root.get("ID"),
            "issue_instant": root.get("IssueInstant"),
            "issuer": self._extract_issuer(root),
            "destination": root.get("Destination"),
            "consent": root.get("Consent"),
            "in_response_to": root.get("InResponseTo"),
            "has_signature": self._has_signature(root),
            "has_encryption": self._has_encryption(root),
        }

    def _analyze_assertions(self, root: Element) -> Dict[str, Any]:
        """Analyze SAML assertions"""
        assertion_info = {
            "assertion_count": 0,
            "assertion_details": [],
            "encrypted_assertions": 0,
        }

        # Find all assertions
        assertions = []
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "Assertion":
            assertions.append(root)

        # Look for embedded assertions
        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if elem_name == "Assertion" and elem != root:
                assertions.append(elem)
            elif elem_name == "EncryptedAssertion":
                assertion_info["encrypted_assertions"] += 1

        assertion_info["assertion_count"] = len(assertions)

        for assertion in assertions:
            details = {
                "id": assertion.get("ID"),
                "issue_instant": assertion.get("IssueInstant"),
                "issuer": self._extract_issuer(assertion),
                "version": assertion.get("Version"),
                "has_signature": self._find_element_by_local_name(
                    assertion, "Signature"
                )
                is not None,
                "subject_present": self._find_element_by_local_name(
                    assertion, "Subject"
                )
                is not None,
                "conditions_present": self._find_element_by_local_name(
                    assertion, "Conditions"
                )
                is not None,
                "statements": self._count_statements(assertion),
            }
            assertion_info["assertion_details"].append(details)

        return assertion_info

    def _analyze_subject(self, root: Element) -> Dict[str, Any]:
        """Analyze subject information"""
        subject_info = {
            "has_subject": False,
            "name_id": None,
            "name_id_format": None,
            "subject_confirmations": [],
            "encrypted_id": False,
        }

        subject = self._find_element_by_local_name(root, "Subject")
        if subject is not None:
            subject_info["has_subject"] = True

            # Analyze NameID
            name_id = self._find_element_by_local_name(subject, "NameID")
            if name_id is not None:
                subject_info["name_id"] = name_id.text
                subject_info["name_id_format"] = name_id.get("Format")

            # Check for encrypted ID
            if self._find_element_by_local_name(subject, "EncryptedID") is not None:
                subject_info["encrypted_id"] = True

            # Analyze subject confirmations
            for confirmation in subject.iter():
                conf_name = (
                    confirmation.tag.split("}")[-1]
                    if "}" in confirmation.tag
                    else confirmation.tag
                )
                if conf_name == "SubjectConfirmation":
                    conf_info = {
                        "method": confirmation.get("Method"),
                        "has_data": self._find_element_by_local_name(
                            confirmation, "SubjectConfirmationData"
                        )
                        is not None,
                    }
                    subject_info["subject_confirmations"].append(conf_info)

        return subject_info

    def _analyze_conditions(self, root: Element) -> Dict[str, Any]:
        """Analyze SAML conditions"""
        conditions_info = {
            "has_conditions": False,
            "not_before": None,
            "not_on_or_after": None,
            "condition_types": [],
            "audience_restrictions": [],
        }

        conditions = self._find_element_by_local_name(root, "Conditions")
        if conditions is not None:
            conditions_info["has_conditions"] = True
            conditions_info["not_before"] = conditions.get("NotBefore")
            conditions_info["not_on_or_after"] = conditions.get("NotOnOrAfter")

            # Analyze condition types
            for child in conditions:
                child_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                conditions_info["condition_types"].append(child_name)

                if child_name == "AudienceRestriction":
                    audiences = []
                    for audience in child:
                        aud_name = (
                            audience.tag.split("}")[-1]
                            if "}" in audience.tag
                            else audience.tag
                        )
                        if aud_name == "Audience" and audience.text:
                            audiences.append(audience.text)
                    conditions_info["audience_restrictions"].extend(audiences)

        return conditions_info

    def _analyze_attributes(self, root: Element) -> Dict[str, Any]:
        """Analyze attribute statements"""
        attr_info = {
            "attribute_statements": [],
            "total_attributes": 0,
            "encrypted_attributes": 0,
        }

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name == "AttributeStatement":
                statement_info = {"attributes": [], "encrypted_attributes": 0}

                for child in elem:
                    child_name = (
                        child.tag.split("}")[-1] if "}" in child.tag else child.tag
                    )

                    if child_name == "Attribute":
                        attr_data = {
                            "name": child.get("Name"),
                            "name_format": child.get("NameFormat"),
                            "friendly_name": child.get("FriendlyName"),
                            "values": [],
                        }

                        for value_elem in child:
                            if value_elem.tag.split("}")[-1] == "AttributeValue":
                                attr_data["values"].append(value_elem.text)

                        statement_info["attributes"].append(attr_data)
                        attr_info["total_attributes"] += 1

                    elif child_name == "EncryptedAttribute":
                        statement_info["encrypted_attributes"] += 1
                        attr_info["encrypted_attributes"] += 1

                attr_info["attribute_statements"].append(statement_info)

        return attr_info

    def _analyze_authentication(self, root: Element) -> Dict[str, Any]:
        """Analyze authentication statements"""
        auth_info = {"authn_statements": [], "session_info": {}}

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name == "AuthnStatement":
                statement_info = {
                    "authn_instant": elem.get("AuthnInstant"),
                    "session_index": elem.get("SessionIndex"),
                    "session_not_on_or_after": elem.get("SessionNotOnOrAfter"),
                    "authn_context": None,
                    "locality": None,
                }

                # Analyze authentication context
                authn_context = self._find_element_by_local_name(elem, "AuthnContext")
                if authn_context is not None:
                    context_ref = self._find_element_by_local_name(
                        authn_context, "AuthnContextClassRef"
                    )
                    if context_ref is not None and context_ref.text:
                        statement_info["authn_context"] = context_ref.text

                # Analyze locality
                locality = self._find_element_by_local_name(elem, "SubjectLocality")
                if locality is not None:
                    statement_info["locality"] = {
                        "address": locality.get("Address"),
                        "dns_name": locality.get("DNSName"),
                    }

                auth_info["authn_statements"].append(statement_info)

        return auth_info

    def _analyze_security(self, root: Element) -> Dict[str, Any]:
        """Analyze security-related elements"""
        security_info = {
            "has_signature": self._has_signature(root),
            "has_encryption": self._has_encryption(root),
            "signature_details": [],
            "encryption_details": [],
            "security_risks": [],
        }

        # Analyze signatures
        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name == "Signature":
                # Check if this is a direct child of root
                is_root_child = any(child == elem for child in root)
                sig_info = {
                    "location": "root" if is_root_child else "nested",
                    "has_key_info": self._find_element_by_local_name(elem, "KeyInfo")
                    is not None,
                }
                security_info["signature_details"].append(sig_info)

            elif elem_name in [
                "EncryptedAssertion",
                "EncryptedID",
                "EncryptedAttribute",
            ]:
                enc_info = {
                    "type": elem_name,
                    "has_key_info": self._find_element_by_local_name(elem, "KeyInfo")
                    is not None,
                }
                security_info["encryption_details"].append(enc_info)

        # Check for security risks
        if not security_info["has_signature"]:
            security_info["security_risks"].append("No digital signature present")

        if self._extract_issuer(root) is None:
            security_info["security_risks"].append("No issuer specified")

        # Check for weak name ID formats
        subject_info = self._analyze_subject(root)
        if (
            subject_info["name_id_format"]
            == "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
        ):
            security_info["security_risks"].append(
                "Unspecified NameID format may pose security risk"
            )

        return security_info

    def _analyze_namespaces(self, root: Element) -> Dict[str, Any]:
        """Analyze namespace declarations"""
        namespaces_info = {
            "declared_namespaces": {},
            "saml_version": None,
            "common_namespaces": [],
        }

        # Extract all namespace declarations
        for key, value in root.attrib.items():
            if key.startswith("xmlns"):
                prefix = key.split(":", 1)[1] if ":" in key else "default"
                namespaces_info["declared_namespaces"][prefix] = value

                # Identify SAML version from namespace
                if (
                    self.SAML_20_ASSERTION_NS in value
                    or self.SAML_20_PROTOCOL_NS in value
                ):
                    namespaces_info["saml_version"] = "2.0"
                elif (
                    self.SAML_11_ASSERTION_NS in value
                    or self.SAML_11_PROTOCOL_NS in value
                ):
                    namespaces_info["saml_version"] = "1.1"

                # Identify common namespaces
                if "xmldsig" in value:
                    namespaces_info["common_namespaces"].append("XML Digital Signature")
                elif "xmlenc" in value:
                    namespaces_info["common_namespaces"].append("XML Encryption")
                elif "xsi" in value:
                    namespaces_info["common_namespaces"].append("XML Schema Instance")

        return namespaces_info

    def _calculate_validation_metrics(self, root: Element) -> Dict[str, Any]:
        """Calculate SAML validation metrics"""
        metrics = {
            "total_elements": 0,
            "assertion_count": 0,
            "attribute_count": 0,
            "condition_count": 0,
            "security_elements": 0,
            "complexity_score": 0,
            "validation_score": 0,
        }

        # Count elements
        metrics["total_elements"] = len(list(root.iter()))
        metrics["assertion_count"] = self._count_assertions(root)

        # Count attributes
        attr_info = self._analyze_attributes(root)
        metrics["attribute_count"] = attr_info["total_attributes"]

        # Count conditions
        conditions_info = self._analyze_conditions(root)
        metrics["condition_count"] = len(conditions_info["condition_types"])

        # Count security elements
        if self._has_signature(root):
            metrics["security_elements"] += 1
        if self._has_encryption(root):
            metrics["security_elements"] += 1

        # Calculate complexity score
        metrics["complexity_score"] = (
            metrics["assertion_count"] * 0.3
            + metrics["attribute_count"] * 0.1
            + metrics["condition_count"] * 0.2
            + metrics["security_elements"] * 0.4
        )

        # Calculate validation score
        validation_points = 0
        if self._has_signature(root):
            validation_points += 0.4
        if self._extract_issuer(root):
            validation_points += 0.2
        if conditions_info["has_conditions"]:
            validation_points += 0.2
        if self._analyze_subject(root)["has_subject"]:
            validation_points += 0.2

        metrics["validation_score"] = validation_points

        return metrics

    def _count_statements(self, assertion: Element) -> Dict[str, int]:
        """Count different types of statements in assertion"""
        statements = {
            "AuthnStatement": 0,
            "AttributeStatement": 0,
            "AuthzDecisionStatement": 0,
        }

        for elem in assertion.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if elem_name in statements:
                statements[elem_name] += 1

        return statements

    def _extract_security_summary(self, root: Element) -> Dict[str, Any]:
        """Extract security summary information"""
        security_analysis = self._analyze_security(root)
        return {
            "has_signature": security_analysis["has_signature"],
            "has_encryption": security_analysis["has_encryption"],
            "signature_count": len(security_analysis["signature_details"]),
            "encryption_count": len(security_analysis["encryption_details"]),
            "security_risks": security_analysis["security_risks"],
        }

    def _extract_subject_summary(self, root: Element) -> Dict[str, Any]:
        """Extract subject summary information"""
        subject_analysis = self._analyze_subject(root)
        return {
            "has_subject": subject_analysis["has_subject"],
            "name_id": subject_analysis["name_id"],
            "name_id_format": subject_analysis["name_id_format"],
            "confirmation_methods": [
                conf["method"] for conf in subject_analysis["subject_confirmations"]
            ],
        }

    def _extract_assertion_summary(self, root: Element) -> Dict[str, Any]:
        """Extract assertion summary information"""
        assertion_analysis = self._analyze_assertions(root)
        return {
            "assertion_count": assertion_analysis["assertion_count"],
            "encrypted_count": assertion_analysis["encrypted_assertions"],
            "issuers": list(
                set(
                    detail["issuer"]
                    for detail in assertion_analysis["assertion_details"]
                    if detail["issuer"]
                )
            ),
        }

    def _extract_conditions_summary(self, root: Element) -> Optional[Dict[str, Any]]:
        """Extract conditions summary information"""
        conditions_analysis = self._analyze_conditions(root)
        if conditions_analysis["has_conditions"]:
            return {
                "not_before": conditions_analysis["not_before"],
                "not_on_or_after": conditions_analysis["not_on_or_after"],
                "condition_types": conditions_analysis["condition_types"],
                "audiences": conditions_analysis["audience_restrictions"],
            }
        return None

    def _find_element_by_local_name(
        self, parent: Element, local_name: str
    ) -> Optional[Element]:
        """Find element by local name, ignoring namespace"""
        for elem in parent:
            elem_local_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if elem_local_name == local_name:
                return elem
        return None

    def _assess_saml_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess SAML document quality and security"""

        # Security quality
        security_score = 0.0
        if findings["security"]["has_signature"]:
            security_score += 0.4
        if findings["security"]["has_encryption"]:
            security_score += 0.2
        if not findings["security"]["security_risks"]:
            security_score += 0.3
        if findings["saml_info"]["issuer"]:
            security_score += 0.1

        # Structure quality
        structure_score = 0.0
        if findings["subject_info"]["has_subject"]:
            structure_score += 0.3
        if findings["conditions"]["has_conditions"]:
            structure_score += 0.3
        if findings["assertions"]["assertion_count"] > 0:
            structure_score += 0.4

        # Compliance quality
        compliance_score = 0.8  # Base score

        # Check time validity
        conditions = findings["conditions"]
        if conditions["has_conditions"]:
            if conditions["not_before"] and conditions["not_on_or_after"]:
                compliance_score += 0.2

        compliance_score = min(compliance_score, 1.0)

        # Completeness quality
        completeness_score = 0.0
        if findings["attributes"]["total_attributes"] > 0:
            completeness_score += 0.3
        if findings["authentication"]["authn_statements"]:
            completeness_score += 0.3
        if findings["subject_info"]["name_id"]:
            completeness_score += 0.4

        return {
            "security": security_score,
            "structure": structure_score,
            "compliance": compliance_score,
            "completeness": completeness_score,
            "overall": (
                security_score + structure_score + compliance_score + completeness_score
            )
            / 4,
        }
