#!/usr/bin/env python3
"""
OpenAPI XML Handler

Handles OpenAPI/Swagger specifications in XML format.
While JSON is more common, XML representations exist and are used
in some enterprise environments.
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


class OpenAPIXMLHandler(XMLHandler):
    """Handler for OpenAPI/Swagger specifications in XML format"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # Check for OpenAPI root elements
        if root_tag in ["openapi", "swagger"]:
            return True, 1.0

        # Check for OpenAPI/Swagger indicators
        indicators = ["paths", "components", "info", "servers", "definitions"]
        found_indicators = 0

        for indicator in indicators:
            if root.find(f".//{indicator}") is not None:
                found_indicators += 1

        if found_indicators >= 2:
            return True, min(found_indicators * 0.3, 0.9)

        # Check for Swagger namespaces
        if any("swagger.io" in uri for uri in namespaces.values()):
            return True, 0.8

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Determine version
        version = "3.0.0"  # Default to OpenAPI 3.0

        # Check for version attribute or element
        if root.get("version"):
            version = root.get("version")
        elif root.find(".//openapi") is not None:
            version_elem = root.find(".//openapi")
            if version_elem.text:
                version = version_elem.text
        elif root.find(".//swagger") is not None:
            version_elem = root.find(".//swagger")
            if version_elem.text:
                version = version_elem.text

        # Determine if it's Swagger 2.0 or OpenAPI 3.x
        api_type = "OpenAPI" if version.startswith("3") else "Swagger"

        return DocumentTypeInfo(
            type_name=f"{api_type} Specification",
            confidence=0.9,
            version=version,
            metadata={
                "standard": api_type,
                "category": "api_specification",
                "format": "XML",
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        # Determine version for proper parsing
        version = self._determine_version(root)
        is_openapi3 = version.startswith("3")

        findings = {
            "api_info": self._extract_api_info(root),
            "servers": (
                self._extract_servers(root)
                if is_openapi3
                else self._extract_host_info(root)
            ),
            "paths": self._analyze_paths(root),
            "operations": self._analyze_operations(root),
            "schemas": self._analyze_schemas(root, is_openapi3),
            "security": self._analyze_security(root),
            "tags": self._extract_tags(root),
            "external_docs": self._extract_external_docs(root),
        }

        recommendations = [
            "Generate API client libraries",
            "Create interactive API documentation",
            "Validate against OpenAPI specification",
            "Extract for API gateway configuration",
            "Monitor for breaking changes",
            "Generate API test suites",
        ]

        ai_use_cases = [
            "API documentation generation",
            "Client SDK generation",
            "API test case generation",
            "Breaking change detection",
            "API security analysis",
            "Usage pattern analysis",
            "API versioning recommendations",
            "Performance optimization suggestions",
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
            # Analysis fields 'API')} Specification",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory={
                "paths": len(findings["paths"]),
                "operations": findings["operations"]["total"],
                "schemas": len(findings["schemas"]),
                "security_schemes": len(findings["security"].get("schemes", [])),
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_api_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        version = self._determine_version(root)
        is_openapi3 = version.startswith("3")

        return {
            "api_metadata": self._extract_api_info(root),
            "endpoints": self._extract_all_endpoints(root),
            "request_schemas": self._extract_request_schemas(root, is_openapi3),
            "response_schemas": self._extract_response_schemas(root, is_openapi3),
            "authentication": self._extract_auth_methods(root),
        }

    def _determine_version(self, root: Element) -> str:
        """Determine OpenAPI/Swagger version"""
        # Check for version in various places
        if root.get("version"):
            return root.get("version")

        openapi_elem = root.find(".//openapi")
        if openapi_elem is not None and openapi_elem.text:
            return openapi_elem.text

        swagger_elem = root.find(".//swagger")
        if swagger_elem is not None and swagger_elem.text:
            return swagger_elem.text

        # Default based on structure
        if root.find(".//components") is not None:
            return "3.0.0"
        elif root.find(".//definitions") is not None:
            return "2.0"

        return "3.0.0"

    def _extract_api_info(self, root: Element) -> Dict[str, Any]:
        """Extract API information"""
        info = root.find(".//info")
        if info is None:
            return {}

        api_info = {
            "title": self._get_child_text(info, "title"),
            "version": self._get_child_text(info, "version"),
            "description": self._get_child_text(info, "description"),
            "terms_of_service": self._get_child_text(info, "termsOfService"),
        }

        # Contact info
        contact = info.find(".//contact")
        if contact is not None:
            api_info["contact"] = {
                "name": self._get_child_text(contact, "name"),
                "email": self._get_child_text(contact, "email"),
                "url": self._get_child_text(contact, "url"),
            }

        # License info
        license_elem = info.find(".//license")
        if license_elem is not None:
            api_info["license"] = {
                "name": self._get_child_text(license_elem, "name"),
                "url": self._get_child_text(license_elem, "url"),
            }

        return api_info

    def _extract_servers(self, root: Element) -> List[Dict[str, Any]]:
        """Extract server information (OpenAPI 3.x)"""
        servers = []

        for server in root.findall(".//servers/server"):
            server_info = {
                "url": self._get_child_text(server, "url"),
                "description": self._get_child_text(server, "description"),
                "variables": {},
            }

            # Extract server variables
            variables = server.find(".//variables")
            if variables is not None:
                for var in variables:
                    var_name = var.tag
                    server_info["variables"][var_name] = {
                        "default": self._get_child_text(var, "default"),
                        "description": self._get_child_text(var, "description"),
                        "enum": [e.text for e in var.findall(".//enum") if e.text],
                    }

            servers.append(server_info)

        return servers

    def _extract_host_info(self, root: Element) -> List[Dict[str, Any]]:
        """Extract host information (Swagger 2.0)"""
        host = self._get_child_text(root, "host")
        base_path = self._get_child_text(root, "basePath", "/")
        schemes = [s.text for s in root.findall(".//schemes/scheme") if s.text]

        if not host:
            return []

        servers = []
        if schemes:
            for scheme in schemes:
                servers.append(
                    {
                        "url": f"{scheme}://{host}{base_path}",
                        "description": f"{scheme.upper()} endpoint",
                    }
                )
        else:
            servers.append(
                {
                    "url": f"https://{host}{base_path}",
                    "description": "Default HTTPS endpoint",
                }
            )

        return servers

    def _analyze_paths(self, root: Element) -> List[Dict[str, Any]]:
        """Analyze API paths"""
        paths_elem = root.find(".//paths")
        if paths_elem is None:
            return []

        paths = []

        for path_elem in paths_elem:
            if path_elem.tag.startswith("{"):  # Skip namespace elements
                continue

            path = path_elem.tag
            path_info = {"path": path, "operations": [], "parameters": []}

            # Extract operations
            http_methods = ["get", "post", "put", "delete", "patch", "options", "head"]
            for method in http_methods:
                op_elem = path_elem.find(f".//{method}")
                if op_elem is not None:
                    path_info["operations"].append(
                        {
                            "method": method.upper(),
                            "operation_id": self._get_child_text(
                                op_elem, "operationId"
                            ),
                            "summary": self._get_child_text(op_elem, "summary"),
                            "tags": [
                                t.text for t in op_elem.findall(".//tags/tag") if t.text
                            ],
                        }
                    )

            # Extract path parameters
            for param in path_elem.findall(".//parameters/parameter"):
                if self._get_child_text(param, "in") == "path":
                    path_info["parameters"].append(
                        {
                            "name": self._get_child_text(param, "name"),
                            "type": self._get_child_text(param, "type"),
                            "required": self._get_child_text(param, "required")
                            == "true",
                        }
                    )

            paths.append(path_info)

        return paths

    def _analyze_operations(self, root: Element) -> Dict[str, Any]:
        """Analyze all operations"""
        operations = {"total": 0, "by_method": {}, "by_tag": {}, "deprecated": []}

        paths_elem = root.find(".//paths")
        if paths_elem is None:
            return operations

        http_methods = ["get", "post", "put", "delete", "patch", "options", "head"]

        for path_elem in paths_elem:
            if path_elem.tag.startswith("{"):
                continue

            path = path_elem.tag

            for method in http_methods:
                op_elem = path_elem.find(f".//{method}")
                if op_elem is not None:
                    operations["total"] += 1

                    # Count by method
                    operations["by_method"][method.upper()] = (
                        operations["by_method"].get(method.upper(), 0) + 1
                    )

                    # Count by tag
                    tags = [t.text for t in op_elem.findall(".//tags/tag") if t.text]
                    for tag in tags:
                        operations["by_tag"][tag] = operations["by_tag"].get(tag, 0) + 1

                    # Check if deprecated
                    if self._get_child_text(op_elem, "deprecated") == "true":
                        operations["deprecated"].append(
                            {
                                "path": path,
                                "method": method.upper(),
                                "operation_id": self._get_child_text(
                                    op_elem, "operationId"
                                ),
                            }
                        )

        return operations

    def _analyze_schemas(
        self, root: Element, is_openapi3: bool
    ) -> List[Dict[str, Any]]:
        """Analyze data schemas"""
        schemas = []

        if is_openapi3:
            # OpenAPI 3.x schemas in components
            schemas_elem = root.find(".//components/schemas")
            if schemas_elem is not None:
                for schema_elem in schemas_elem:
                    if schema_elem.tag.startswith("{"):
                        continue

                    schemas.append(
                        self._extract_schema_info(schema_elem.tag, schema_elem)
                    )
        else:
            # Swagger 2.0 definitions
            defs_elem = root.find(".//definitions")
            if defs_elem is not None:
                for def_elem in defs_elem:
                    if def_elem.tag.startswith("{"):
                        continue

                    schemas.append(self._extract_schema_info(def_elem.tag, def_elem))

        return schemas

    def _extract_schema_info(self, name: str, schema_elem: Element) -> Dict[str, Any]:
        """Extract schema information"""
        schema_info = {
            "name": name,
            "type": self._get_child_text(schema_elem, "type", "object"),
            "properties": [],
            "required": [],
        }

        # Extract properties
        props_elem = schema_elem.find(".//properties")
        if props_elem is not None:
            for prop_elem in props_elem:
                if prop_elem.tag.startswith("{"):
                    continue

                prop_info = {
                    "name": prop_elem.tag,
                    "type": self._get_child_text(prop_elem, "type"),
                    "format": self._get_child_text(prop_elem, "format"),
                    "description": self._get_child_text(prop_elem, "description"),
                }
                schema_info["properties"].append(prop_info)

        # Extract required fields
        required_elem = schema_elem.find(".//required")
        if required_elem is not None:
            schema_info["required"] = [r.text for r in required_elem if r.text]

        # Check for inheritance
        all_of = schema_elem.find(".//allOf")
        if all_of is not None:
            schema_info["inheritance"] = "allOf"

        return schema_info

    def _analyze_security(self, root: Element) -> Dict[str, Any]:
        """Analyze security definitions"""
        security = {"schemes": [], "requirements": []}

        # OpenAPI 3.x security schemes
        sec_schemes = root.find(".//components/securitySchemes")
        if sec_schemes is not None:
            for scheme_elem in sec_schemes:
                if scheme_elem.tag.startswith("{"):
                    continue

                scheme_info = {
                    "name": scheme_elem.tag,
                    "type": self._get_child_text(scheme_elem, "type"),
                    "scheme": self._get_child_text(scheme_elem, "scheme"),
                    "bearer_format": self._get_child_text(scheme_elem, "bearerFormat"),
                    "flows": self._extract_oauth_flows(scheme_elem),
                }
                security["schemes"].append(scheme_info)
        else:
            # Swagger 2.0 security definitions
            sec_defs = root.find(".//securityDefinitions")
            if sec_defs is not None:
                for sec_def in sec_defs:
                    if sec_def.tag.startswith("{"):
                        continue

                    scheme_info = {
                        "name": sec_def.tag,
                        "type": self._get_child_text(sec_def, "type"),
                        "in": self._get_child_text(sec_def, "in"),
                        "name_param": self._get_child_text(sec_def, "name"),
                        "flow": self._get_child_text(sec_def, "flow"),
                        "scopes": self._extract_scopes(sec_def),
                    }
                    security["schemes"].append(scheme_info)

        # Global security requirements
        for sec_req in root.findall(".//security"):
            req_info = {}
            for child in sec_req:
                if not child.tag.startswith("{"):
                    req_info[child.tag] = [s.text for s in child if s.text]
            if req_info:
                security["requirements"].append(req_info)

        return security

    def _extract_oauth_flows(self, scheme_elem: Element) -> Dict[str, Any]:
        """Extract OAuth flows (OpenAPI 3.x)"""
        flows = {}
        flows_elem = scheme_elem.find(".//flows")

        if flows_elem is not None:
            for flow_type in [
                "implicit",
                "password",
                "clientCredentials",
                "authorizationCode",
            ]:
                flow_elem = flows_elem.find(f".//{flow_type}")
                if flow_elem is not None:
                    flows[flow_type] = {
                        "authorization_url": self._get_child_text(
                            flow_elem, "authorizationUrl"
                        ),
                        "token_url": self._get_child_text(flow_elem, "tokenUrl"),
                        "refresh_url": self._get_child_text(flow_elem, "refreshUrl"),
                        "scopes": self._extract_scopes(flow_elem),
                    }

        return flows

    def _extract_scopes(self, parent_elem: Element) -> Dict[str, str]:
        """Extract OAuth scopes"""
        scopes = {}
        scopes_elem = parent_elem.find(".//scopes")

        if scopes_elem is not None:
            for scope_elem in scopes_elem:
                if not scope_elem.tag.startswith("{"):
                    scopes[scope_elem.tag] = scope_elem.text or ""

        return scopes

    def _extract_tags(self, root: Element) -> List[Dict[str, str]]:
        """Extract tag definitions"""
        tags = []

        for tag_elem in root.findall(".//tags/tag"):
            tag_info = {
                "name": self._get_child_text(tag_elem, "name"),
                "description": self._get_child_text(tag_elem, "description"),
            }

            # External docs for tag
            ext_docs = tag_elem.find(".//externalDocs")
            if ext_docs is not None:
                tag_info["external_docs"] = {
                    "description": self._get_child_text(ext_docs, "description"),
                    "url": self._get_child_text(ext_docs, "url"),
                }

            tags.append(tag_info)

        return tags

    def _extract_external_docs(self, root: Element) -> Optional[Dict[str, str]]:
        """Extract external documentation"""
        ext_docs = root.find(".//externalDocs")
        if ext_docs is not None:
            return {
                "description": self._get_child_text(ext_docs, "description"),
                "url": self._get_child_text(ext_docs, "url"),
            }
        return None

    def _extract_all_endpoints(self, root: Element) -> List[Dict[str, Any]]:
        """Extract all API endpoints"""
        endpoints = []
        paths_elem = root.find(".//paths")

        if paths_elem is None:
            return endpoints

        http_methods = ["get", "post", "put", "delete", "patch", "options", "head"]

        for path_elem in paths_elem:
            if path_elem.tag.startswith("{"):
                continue

            path = path_elem.tag

            for method in http_methods:
                op_elem = path_elem.find(f".//{method}")
                if op_elem is not None:
                    endpoints.append(
                        {
                            "path": path,
                            "method": method.upper(),
                            "operation_id": self._get_child_text(
                                op_elem, "operationId"
                            ),
                            "summary": self._get_child_text(op_elem, "summary"),
                            "deprecated": self._get_child_text(op_elem, "deprecated")
                            == "true",
                        }
                    )

        return endpoints

    def _extract_request_schemas(
        self, root: Element, is_openapi3: bool
    ) -> List[Dict[str, Any]]:
        """Extract request body schemas"""
        request_schemas = []
        paths_elem = root.find(".//paths")

        if paths_elem is None:
            return request_schemas

        for path_elem in paths_elem:
            if path_elem.tag.startswith("{"):
                continue

            path = path_elem.tag

            for method in ["post", "put", "patch"]:
                op_elem = path_elem.find(f".//{method}")
                if op_elem is not None:
                    if is_openapi3:
                        # OpenAPI 3.x request body
                        req_body = op_elem.find(".//requestBody")
                        if req_body is not None:
                            content = req_body.find(".//content")
                            if content is not None:
                                for media_type in content:
                                    if not media_type.tag.startswith("{"):
                                        schema_ref = media_type.find(".//schema/$ref")
                                        if schema_ref is not None:
                                            request_schemas.append(
                                                {
                                                    "path": path,
                                                    "method": method.upper(),
                                                    "media_type": media_type.tag,
                                                    "schema_ref": schema_ref.text,
                                                }
                                            )
                    else:
                        # Swagger 2.0 parameters
                        for param in op_elem.findall(".//parameters/parameter"):
                            if self._get_child_text(param, "in") == "body":
                                schema_elem = param.find(".//schema")
                                if schema_elem is not None:
                                    request_schemas.append(
                                        {
                                            "path": path,
                                            "method": method.upper(),
                                            "name": self._get_child_text(param, "name"),
                                            "required": self._get_child_text(
                                                param, "required"
                                            )
                                            == "true",
                                        }
                                    )

        return request_schemas[:20]  # Limit

    def _extract_response_schemas(
        self, root: Element, is_openapi3: bool
    ) -> List[Dict[str, Any]]:
        """Extract response schemas"""
        response_schemas = []
        paths_elem = root.find(".//paths")

        if paths_elem is None:
            return response_schemas

        for path_elem in paths_elem:
            if path_elem.tag.startswith("{"):
                continue

            path = path_elem.tag

            for op_elem in path_elem:
                if op_elem.tag.startswith("{") or op_elem.tag not in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                ]:
                    continue

                method = op_elem.tag
                responses = op_elem.find(".//responses")

                if responses is not None:
                    for response in responses:
                        if not response.tag.startswith("{"):
                            status_code = response.tag

                            if is_openapi3:
                                content = response.find(".//content")
                                if content is not None:
                                    for media_type in content:
                                        if not media_type.tag.startswith("{"):
                                            response_schemas.append(
                                                {
                                                    "path": path,
                                                    "method": method.upper(),
                                                    "status_code": status_code,
                                                    "media_type": media_type.tag,
                                                }
                                            )
                            else:
                                schema = response.find(".//schema")
                                if schema is not None:
                                    response_schemas.append(
                                        {
                                            "path": path,
                                            "method": method.upper(),
                                            "status_code": status_code,
                                            "description": self._get_child_text(
                                                response, "description"
                                            ),
                                        }
                                    )

        return response_schemas[:20]  # Limit

    def _extract_auth_methods(self, root: Element) -> List[Dict[str, str]]:
        """Extract authentication methods"""
        auth_methods = []

        # From security schemes
        security = self._analyze_security(root)
        for scheme in security["schemes"]:
            auth_methods.append(
                {
                    "name": scheme["name"],
                    "type": scheme["type"],
                    "description": f"{scheme['type']} authentication",
                }
            )

        return auth_methods

    def _get_child_text(
        self, parent: Element, child_name: str, default: str = None
    ) -> Optional[str]:
        """Get text content of a child element"""
        child = parent.find(f".//{child_name}")
        return child.text if child is not None else default

    def _assess_api_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess API specification quality"""
        # Documentation completeness
        total_ops = findings["operations"]["total"]
        doc_score = 0.0

        if total_ops > 0:
            # Check if operations have summaries (would need more detailed analysis)
            doc_score = 0.7  # Placeholder

        # Security implementation
        security_score = 0.0
        if findings["security"]["schemes"]:
            security_score = min(len(findings["security"]["schemes"]) * 0.3, 1.0)

        # API organization (tags)
        org_score = 0.0
        if findings["tags"]:
            org_score = min(len(findings["tags"]) * 0.2, 1.0)

        # Deprecation management
        deprecation_score = 1.0
        if findings["operations"]["deprecated"]:
            deprecation_ratio = len(findings["operations"]["deprecated"]) / max(
                total_ops, 1
            )
            deprecation_score = max(0, 1.0 - deprecation_ratio * 2)  # Penalize heavily

        # Schema coverage
        schema_score = min(
            len(findings["schemas"]) / 10, 1.0
        )  # Assume 10+ schemas is good

        return {
            "documentation": doc_score,
            "security": security_score,
            "organization": org_score,
            "deprecation_management": deprecation_score,
            "schema_coverage": schema_score,
            "overall": (
                doc_score
                + security_score
                + org_score
                + deprecation_score
                + schema_score
            )
            / 5,
        }
