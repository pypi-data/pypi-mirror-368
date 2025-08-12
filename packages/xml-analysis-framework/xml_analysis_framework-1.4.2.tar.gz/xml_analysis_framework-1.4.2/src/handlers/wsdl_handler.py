#!/usr/bin/env python3
"""
WSDL (Web Services Description Language) Handler

Analyzes WSDL files to extract service definitions, operations,
message schemas, and binding information for SOAP web services.
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


class WSDLHandler(XMLHandler):
    """Handler for WSDL (Web Services Description Language) documents"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for WSDL root element
        if root.tag.endswith("definitions") or root.tag == "definitions":
            # Check for WSDL namespace
            if any("schemas.xmlsoap.org/wsdl" in uri for uri in namespaces.values()):
                return True, 1.0
            return True, 0.7

        # WSDL 2.0 uses 'description' as root
        if root.tag.endswith("description") or root.tag == "description":
            if any("w3.org/ns/wsdl" in uri for uri in namespaces.values()):
                return True, 0.9

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Determine WSDL version
        version = "1.1"  # Default
        if root.tag.endswith("description") or any(
            "w3.org/ns/wsdl" in uri for uri in namespaces.values()
        ):
            version = "2.0"

        target_namespace = root.get("targetNamespace", "")

        return DocumentTypeInfo(
            type_name="WSDL Service Definition",
            confidence=1.0,
            version=version,
            schema_uri=target_namespace,
            metadata={
                "standard": f"WSDL {version}",
                "category": "web_service_definition",
                "protocol": "SOAP",
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        # Determine version for proper parsing
        is_wsdl2 = root.tag.endswith("description") or "w3.org/ns/wsdl" in str(
            root.attrib.values()
        )

        if is_wsdl2:
            findings = self._analyze_wsdl2(root)
        else:
            findings = self._analyze_wsdl1(root)

        recommendations = [
            "Generate client code from WSDL",
            "Extract operation documentation",
            "Analyze service dependencies",
            "Create API test cases from operations",
            "Map SOAP operations to REST endpoints",
            "Monitor deprecated operations",
        ]

        ai_use_cases = [
            "SOAP to REST API migration",
            "Service dependency mapping",
            "API documentation generation",
            "Test case generation",
            "Service compatibility checking",
            "Operation complexity analysis",
            "Security policy extraction",
            "Performance bottleneck identification",
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
                "services": len(findings.get("services", [])),
                "operations": findings.get("total_operations", 0),
                "messages": len(findings.get("messages", [])),
                "types": len(findings.get("types", [])),
                "bindings": len(findings.get("bindings", [])),
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_wsdl_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        is_wsdl2 = root.tag.endswith("description")

        if is_wsdl2:
            return self._extract_wsdl2_data(root)
        else:
            return self._extract_wsdl1_data(root)

    def _analyze_wsdl1(self, root: Element) -> Dict[str, Any]:
        """Analyze WSDL 1.1 document"""
        findings = {
            "services": self._extract_services(root),
            "port_types": self._extract_port_types(root),
            "operations": self._extract_operations(root),
            "messages": self._extract_messages(root),
            "types": self._extract_types(root),
            "bindings": self._extract_bindings(root),
            "imports": self._extract_imports(root),
            "total_operations": 0,
        }

        # Count total operations
        for port_type in findings["port_types"]:
            findings["total_operations"] += len(port_type.get("operations", []))

        return findings

    def _analyze_wsdl2(self, root: Element) -> Dict[str, Any]:
        """Analyze WSDL 2.0 document"""
        # WSDL 2.0 has different structure
        findings = {
            "services": self._extract_services_v2(root),
            "interfaces": self._extract_interfaces_v2(root),
            "operations": self._extract_operations_v2(root),
            "types": self._extract_types(root),  # Similar to 1.1
            "bindings": self._extract_bindings_v2(root),
            "imports": self._extract_imports(root),
            "total_operations": 0,
        }

        # Count operations
        for interface in findings["interfaces"]:
            findings["total_operations"] += len(interface.get("operations", []))

        return findings

    def _extract_services(self, root: Element) -> List[Dict[str, Any]]:
        """Extract service definitions from WSDL 1.1"""
        services = []

        for service in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}service"):
            service_info = {
                "name": service.get("name"),
                "documentation": self._get_documentation(service),
                "ports": [],
            }

            # Extract ports
            for port in service.findall(".//{http://schemas.xmlsoap.org/wsdl/}port"):
                port_info = {
                    "name": port.get("name"),
                    "binding": port.get("binding"),
                    "address": None,
                }

                # Get SOAP address
                soap_addr = port.find(
                    ".//{http://schemas.xmlsoap.org/wsdl/soap/}address"
                )
                if soap_addr is not None:
                    port_info["address"] = soap_addr.get("location")

                # Check for SOAP 1.2
                soap12_addr = port.find(
                    ".//{http://schemas.xmlsoap.org/wsdl/soap12/}address"
                )
                if soap12_addr is not None:
                    port_info["address"] = soap12_addr.get("location")
                    port_info["soap_version"] = "1.2"

                service_info["ports"].append(port_info)

            services.append(service_info)

        return services

    def _extract_port_types(self, root: Element) -> List[Dict[str, Any]]:
        """Extract port types (interfaces) from WSDL 1.1"""
        port_types = []

        for pt in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}portType"):
            pt_info = {"name": pt.get("name"), "operations": []}

            # Extract operations
            for op in pt.findall(".//{http://schemas.xmlsoap.org/wsdl/}operation"):
                op_info = {
                    "name": op.get("name"),
                    "documentation": self._get_documentation(op),
                    "input": None,
                    "output": None,
                    "faults": [],
                }

                # Input message
                input_elem = op.find(".//{http://schemas.xmlsoap.org/wsdl/}input")
                if input_elem is not None:
                    op_info["input"] = input_elem.get("message")

                # Output message
                output_elem = op.find(".//{http://schemas.xmlsoap.org/wsdl/}output")
                if output_elem is not None:
                    op_info["output"] = output_elem.get("message")

                # Fault messages
                for fault in op.findall(".//{http://schemas.xmlsoap.org/wsdl/}fault"):
                    op_info["faults"].append(
                        {"name": fault.get("name"), "message": fault.get("message")}
                    )

                pt_info["operations"].append(op_info)

            port_types.append(pt_info)

        return port_types

    def _extract_operations(self, root: Element) -> List[Dict[str, Any]]:
        """Extract all operations with details"""
        operations = []

        for pt in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}portType"):
            port_type_name = pt.get("name")

            for op in pt.findall(".//{http://schemas.xmlsoap.org/wsdl/}operation"):
                operations.append(
                    {
                        "name": op.get("name"),
                        "port_type": port_type_name,
                        "pattern": self._determine_mep(op),  # Message Exchange Pattern
                        "documentation": self._get_documentation(op),
                    }
                )

        return operations

    def _extract_messages(self, root: Element) -> List[Dict[str, Any]]:
        """Extract message definitions"""
        messages = []

        for msg in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}message"):
            msg_info = {"name": msg.get("name"), "parts": []}

            # Extract parts
            for part in msg.findall(".//{http://schemas.xmlsoap.org/wsdl/}part"):
                part_info = {
                    "name": part.get("name"),
                    "type": part.get("type"),
                    "element": part.get("element"),
                }
                msg_info["parts"].append(part_info)

            messages.append(msg_info)

        return messages

    def _extract_types(self, root: Element) -> List[Dict[str, Any]]:
        """Extract type definitions from embedded schemas"""
        types = []

        types_section = root.find(".//{http://schemas.xmlsoap.org/wsdl/}types")
        if types_section is None:
            return types

        # Find all schemas
        for schema in types_section.findall(
            ".//{http://www.w3.org/2001/XMLSchema}schema"
        ):
            target_ns = schema.get("targetNamespace", "default")

            # Extract complex types
            for ct in schema.findall(
                ".//{http://www.w3.org/2001/XMLSchema}complexType"
            ):
                types.append(
                    {"name": ct.get("name"), "namespace": target_ns, "kind": "complex"}
                )

            # Extract simple types
            for st in schema.findall(".//{http://www.w3.org/2001/XMLSchema}simpleType"):
                types.append(
                    {"name": st.get("name"), "namespace": target_ns, "kind": "simple"}
                )

            # Extract elements
            for elem in schema.findall(".//{http://www.w3.org/2001/XMLSchema}element"):
                if elem.get("name"):
                    types.append(
                        {
                            "name": elem.get("name"),
                            "namespace": target_ns,
                            "kind": "element",
                        }
                    )

        return types

    def _extract_bindings(self, root: Element) -> List[Dict[str, Any]]:
        """Extract binding definitions"""
        bindings = []

        for binding in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}binding"):
            binding_info = {
                "name": binding.get("name"),
                "type": binding.get("type"),
                "protocol": "unknown",
                "style": None,
                "transport": None,
                "operations": [],
            }

            # Check for SOAP binding
            soap_binding = binding.find(
                ".//{http://schemas.xmlsoap.org/wsdl/soap/}binding"
            )
            if soap_binding is not None:
                binding_info["protocol"] = "SOAP"
                binding_info["style"] = soap_binding.get("style", "document")
                binding_info["transport"] = soap_binding.get("transport")

            # Extract operation bindings
            for op in binding.findall(".//{http://schemas.xmlsoap.org/wsdl/}operation"):
                op_binding = {
                    "name": op.get("name"),
                    "soap_action": None,
                    "style": None,
                }

                soap_op = op.find(".//{http://schemas.xmlsoap.org/wsdl/soap/}operation")
                if soap_op is not None:
                    op_binding["soap_action"] = soap_op.get("soapAction")
                    op_binding["style"] = soap_op.get("style")

                binding_info["operations"].append(op_binding)

            bindings.append(binding_info)

        return bindings

    def _extract_imports(self, root: Element) -> List[Dict[str, str]]:
        """Extract import statements"""
        imports = []

        for imp in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}import"):
            imports.append(
                {"namespace": imp.get("namespace"), "location": imp.get("location")}
            )

        return imports

    # WSDL 2.0 specific methods
    def _extract_services_v2(self, root: Element) -> List[Dict[str, Any]]:
        """Extract services from WSDL 2.0"""
        services = []

        for service in root.findall(".//{http://www.w3.org/ns/wsdl}service"):
            service_info = {
                "name": service.get("name"),
                "interface": service.get("interface"),
                "endpoints": [],
            }

            for endpoint in service.findall(".//{http://www.w3.org/ns/wsdl}endpoint"):
                service_info["endpoints"].append(
                    {
                        "name": endpoint.get("name"),
                        "binding": endpoint.get("binding"),
                        "address": endpoint.get("address"),
                    }
                )

            services.append(service_info)

        return services

    def _extract_interfaces_v2(self, root: Element) -> List[Dict[str, Any]]:
        """Extract interfaces from WSDL 2.0 (equivalent to portType in 1.1)"""
        interfaces = []

        for interface in root.findall(".//{http://www.w3.org/ns/wsdl}interface"):
            interface_info = {
                "name": interface.get("name"),
                "extends": interface.get("extends"),
                "operations": [],
            }

            for op in interface.findall(".//{http://www.w3.org/ns/wsdl}operation"):
                interface_info["operations"].append(
                    {
                        "name": op.get("name"),
                        "pattern": op.get("pattern"),
                        "style": op.get("style"),
                    }
                )

            interfaces.append(interface_info)

        return interfaces

    def _extract_operations_v2(self, root: Element) -> List[Dict[str, Any]]:
        """Extract operations from WSDL 2.0"""
        operations = []

        for interface in root.findall(".//{http://www.w3.org/ns/wsdl}interface"):
            interface_name = interface.get("name")

            for op in interface.findall(".//{http://www.w3.org/ns/wsdl}operation"):
                operations.append(
                    {
                        "name": op.get("name"),
                        "interface": interface_name,
                        "pattern": op.get("pattern", "in-out"),
                        "safe": op.get("safe", "false") == "true",
                    }
                )

        return operations

    def _extract_bindings_v2(self, root: Element) -> List[Dict[str, Any]]:
        """Extract bindings from WSDL 2.0"""
        bindings = []

        for binding in root.findall(".//{http://www.w3.org/ns/wsdl}binding"):
            bindings.append(
                {
                    "name": binding.get("name"),
                    "interface": binding.get("interface"),
                    "type": binding.get("type"),
                    "protocol": self._extract_protocol_v2(binding),
                }
            )

        return bindings

    def _extract_protocol_v2(self, binding: Element) -> str:
        """Determine protocol from WSDL 2.0 binding"""
        binding_type = binding.get("type", "")

        if "soap" in binding_type.lower():
            return "SOAP"
        elif "http" in binding_type.lower():
            return "HTTP"
        else:
            return "unknown"

    def _determine_mep(self, operation: Element) -> str:
        """Determine Message Exchange Pattern"""
        has_input = (
            operation.find(".//{http://schemas.xmlsoap.org/wsdl/}input") is not None
        )
        has_output = (
            operation.find(".//{http://schemas.xmlsoap.org/wsdl/}output") is not None
        )

        if has_input and has_output:
            return "request-response"
        elif has_input and not has_output:
            return "one-way"
        elif not has_input and has_output:
            return "notification"
        else:
            return "unknown"

    def _get_documentation(self, element: Element) -> Optional[str]:
        """Extract documentation from element"""
        doc = element.find(".//{http://schemas.xmlsoap.org/wsdl/}documentation")
        if doc is not None and doc.text:
            return doc.text.strip()
        return None

    def _extract_wsdl1_data(self, root: Element) -> Dict[str, Any]:
        """Extract key data for WSDL 1.1"""
        return {
            "service_endpoints": self._extract_all_endpoints(root),
            "operation_signatures": self._extract_operation_signatures(root),
            "soap_actions": self._extract_soap_actions(root),
            "message_schemas": self._extract_message_schemas(root),
        }

    def _extract_wsdl2_data(self, root: Element) -> Dict[str, Any]:
        """Extract key data for WSDL 2.0"""
        return {
            "service_endpoints": self._extract_all_endpoints_v2(root),
            "interface_hierarchy": self._extract_interface_hierarchy(root),
            "operation_patterns": self._extract_operation_patterns_v2(root),
        }

    def _extract_all_endpoints(self, root: Element) -> List[Dict[str, str]]:
        """Extract all service endpoints"""
        endpoints = []

        for service in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}service"):
            service_name = service.get("name")

            for port in service.findall(".//{http://schemas.xmlsoap.org/wsdl/}port"):
                # SOAP address
                addr = port.find(".//{http://schemas.xmlsoap.org/wsdl/soap/}address")
                if addr is not None:
                    endpoints.append(
                        {
                            "service": service_name,
                            "port": port.get("name"),
                            "url": addr.get("location"),
                            "protocol": "SOAP",
                        }
                    )

        return endpoints

    def _extract_operation_signatures(self, root: Element) -> List[Dict[str, Any]]:
        """Extract operation signatures with input/output"""
        signatures = []

        for pt in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}portType"):
            for op in pt.findall(".//{http://schemas.xmlsoap.org/wsdl/}operation"):
                sig = {
                    "operation": op.get("name"),
                    "port_type": pt.get("name"),
                    "input": None,
                    "output": None,
                }

                input_elem = op.find(".//{http://schemas.xmlsoap.org/wsdl/}input")
                if input_elem is not None:
                    sig["input"] = self._resolve_message_type(
                        root, input_elem.get("message")
                    )

                output_elem = op.find(".//{http://schemas.xmlsoap.org/wsdl/}output")
                if output_elem is not None:
                    sig["output"] = self._resolve_message_type(
                        root, output_elem.get("message")
                    )

                signatures.append(sig)

        return signatures[:20]  # Limit to first 20

    def _extract_soap_actions(self, root: Element) -> List[Dict[str, str]]:
        """Extract SOAP actions for operations"""
        actions = []

        for binding in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}binding"):
            for op in binding.findall(".//{http://schemas.xmlsoap.org/wsdl/}operation"):
                soap_op = op.find(".//{http://schemas.xmlsoap.org/wsdl/soap/}operation")
                if soap_op is not None and soap_op.get("soapAction"):
                    actions.append(
                        {
                            "operation": op.get("name"),
                            "binding": binding.get("name"),
                            "action": soap_op.get("soapAction"),
                        }
                    )

        return actions

    def _extract_message_schemas(self, root: Element) -> List[Dict[str, Any]]:
        """Extract message schemas"""
        schemas = []

        for msg in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}message")[:10]:
            schema = {"message": msg.get("name"), "parts": []}

            for part in msg.findall(".//{http://schemas.xmlsoap.org/wsdl/}part"):
                schema["parts"].append(
                    {
                        "name": part.get("name"),
                        "type": part.get("type") or part.get("element"),
                    }
                )

            schemas.append(schema)

        return schemas

    def _resolve_message_type(self, root: Element, message_ref: str) -> Optional[str]:
        """Resolve message reference to type"""
        if not message_ref:
            return None

        # Remove namespace prefix if present
        msg_name = message_ref.split(":")[-1]

        # Find message
        for msg in root.findall(".//{http://schemas.xmlsoap.org/wsdl/}message"):
            if msg.get("name") == msg_name:
                # Get first part's type
                part = msg.find(".//{http://schemas.xmlsoap.org/wsdl/}part")
                if part is not None:
                    return part.get("type") or part.get("element")

        return message_ref

    def _extract_all_endpoints_v2(self, root: Element) -> List[Dict[str, str]]:
        """Extract endpoints from WSDL 2.0"""
        endpoints = []

        for service in root.findall(".//{http://www.w3.org/ns/wsdl}service"):
            for endpoint in service.findall(".//{http://www.w3.org/ns/wsdl}endpoint"):
                endpoints.append(
                    {
                        "service": service.get("name"),
                        "endpoint": endpoint.get("name"),
                        "address": endpoint.get("address"),
                        "binding": endpoint.get("binding"),
                    }
                )

        return endpoints

    def _extract_interface_hierarchy(self, root: Element) -> Dict[str, List[str]]:
        """Extract interface inheritance in WSDL 2.0"""
        hierarchy = {}

        for interface in root.findall(".//{http://www.w3.org/ns/wsdl}interface"):
            name = interface.get("name")
            extends = interface.get("extends")

            if extends:
                hierarchy[name] = [e.strip() for e in extends.split()]
            else:
                hierarchy[name] = []

        return hierarchy

    def _extract_operation_patterns_v2(self, root: Element) -> List[Dict[str, str]]:
        """Extract operation patterns from WSDL 2.0"""
        patterns = []

        for interface in root.findall(".//{http://www.w3.org/ns/wsdl}interface"):
            for op in interface.findall(".//{http://www.w3.org/ns/wsdl}operation"):
                patterns.append(
                    {
                        "interface": interface.get("name"),
                        "operation": op.get("name"),
                        "pattern": op.get("pattern", "in-out"),
                    }
                )

        return patterns

    def _assess_wsdl_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess WSDL quality metrics"""
        # Documentation coverage
        doc_count = 0
        total_items = 0

        # Count documented operations
        for pt in findings.get("port_types", []):
            for op in pt.get("operations", []):
                total_items += 1
                if op.get("documentation"):
                    doc_count += 1

        doc_coverage = doc_count / max(total_items, 1)

        # Service completeness
        services = findings.get("services", [])
        endpoints_defined = sum(len(s.get("ports", [])) for s in services)
        service_completeness = min(endpoints_defined / max(len(services), 1), 1.0)

        # Type definition coverage
        types_defined = len(findings.get("types", []))
        type_coverage = min(types_defined / 20, 1.0)  # Assume 20+ types is good

        # Binding completeness
        bindings = findings.get("bindings", [])
        binding_completeness = 1.0 if bindings else 0.0

        return {
            "documentation": doc_coverage,
            "service_completeness": service_completeness,
            "type_coverage": type_coverage,
            "binding_completeness": binding_completeness,
            "overall_quality": (
                doc_coverage
                + service_completeness
                + type_coverage
                + binding_completeness
            )
            / 4,
        }
