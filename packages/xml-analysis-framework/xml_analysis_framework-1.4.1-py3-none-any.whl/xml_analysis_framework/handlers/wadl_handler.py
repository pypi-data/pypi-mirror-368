#!/usr/bin/env python3
"""
WADL (Web Application Description Language) Handler

Analyzes WADL files which describe REST APIs and web services.
Extracts resource definitions, methods, parameters, response formats,
and generates API documentation and analysis for REST services.
"""

import re
import sys
import os
from typing import Dict, List, Any, Tuple, TYPE_CHECKING
from urllib.parse import urljoin

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class WADLHandler(XMLHandler):
    """Handler for WADL (Web Application Description Language) files"""

    WADL_NAMESPACE = "http://wadl.dev.java.net/2009/02"
    WADL_NAMESPACE_ALT = "http://research.sun.com/wadl/2006/10"

    def _get_namespace(self, root: Element) -> str:
        """Extract namespace prefix from root element"""
        if "}" in root.tag:
            return root.tag.split("}")[0] + "}"
        return ""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for WADL namespace
        wadl_namespaces = [
            "wadl.dev.java.net",
            "research.sun.com/wadl",
            "java.net/wadl",
        ]

        if any(
            wadl_ns in uri for uri in namespaces.values() for wadl_ns in wadl_namespaces
        ):
            return True, 1.0

        # Check root element
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if root_tag.lower() == "application":
            # Check for WADL-specific elements
            ns = self._get_namespace(root)
            wadl_elements = [
                "resources",
                "resource",
                "method",
                "param",
                "representation",
            ]
            found = sum(
                1 for elem in wadl_elements if root.find(f".//{ns}{elem}") is not None
            )
            if found >= 2:
                return True, min(found * 0.2, 0.9)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Detect WADL version
        version = "1.0"  # Default
        for uri in namespaces.values():
            if "2009/02" in uri:
                version = "1.0"
            elif "2006/10" in uri:
                version = "0.9"

        # Detect API characteristics
        ns = self._get_namespace(root)
        api_type = "rest_api"

        # Check for specific patterns
        methods = []
        for method in root.findall(f".//{ns}method"):
            method_name = method.get("name", "").upper()
            if method_name:
                methods.append(method_name)

        if "POST" in methods and "PUT" in methods and "DELETE" in methods:
            api_type = "full_crud_api"
        elif "GET" in methods and len(methods) == 1:
            api_type = "read_only_api"
        elif any(method in ["POST", "PUT", "PATCH"] for method in methods):
            api_type = "write_api"

        return DocumentTypeInfo(
            type_name="WADL API Description",
            confidence=0.95,
            version=version,
            metadata={
                "standard": "WADL",
                "category": "api_description",
                "api_type": api_type,
                "methods": list(set(methods)),
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "application_info": self._analyze_application(root),
            "resources": self._analyze_resources(root),
            "methods": self._analyze_methods(root),
            "parameters": self._analyze_parameters(root),
            "representations": self._analyze_representations(root),
            "grammars": self._analyze_grammars(root),
            "documentation": self._analyze_documentation(root),
            "security": self._analyze_security_patterns(root),
            "api_metrics": self._calculate_api_metrics(root),
        }

        recommendations = [
            "Generate interactive API documentation",
            "Create client SDKs from WADL specification",
            "Validate API endpoints against specification",
            "Analyze API design patterns and best practices",
            "Extract for API testing and automation",
            "Monitor API coverage and usage patterns",
            "Generate OpenAPI/Swagger equivalents",
            "Audit security and authentication patterns",
        ]

        ai_use_cases = [
            "Automated API documentation generation",
            "Client code generation and scaffolding",
            "API testing and validation automation",
            "REST API pattern analysis",
            "Service dependency mapping",
            "API versioning and compatibility checking",
            "Security vulnerability assessment",
            "Performance optimization recommendations",
            "API usage analytics and insights",
            "Microservices architecture analysis",
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
                "total_resources": findings["resources"]["resource_count"],
                "total_methods": findings["methods"]["method_count"],
                "total_parameters": findings["parameters"]["parameter_count"],
                "representation_formats": len(
                    findings["representations"]["media_types"]
                ),
                "documentation_coverage": findings["documentation"]["coverage_score"],
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_api_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "api_specification": self._extract_api_spec(root),
            "endpoint_catalog": self._extract_endpoints(root),
            "data_models": self._extract_data_models(root),
            "authentication_info": self._extract_auth_info(root),
            "error_responses": self._extract_error_responses(root),
        }

    def _analyze_application(self, root: Element) -> Dict[str, Any]:
        """Analyze application-level information"""
        ns = self._get_namespace(root)
        app_info = {
            "base_uri": None,
            "version": None,
            "title": None,
            "description": None,
            "xmlns": None,
        }

        # Extract application attributes
        app_info["xmlns"] = root.get("xmlns") or ns.strip("{}")

        # Look for resources element with base attribute
        resources = root.find(f"{ns}resources")
        if resources is not None:
            app_info["base_uri"] = resources.get("base")

        # Look for documentation
        doc = root.find(f"{ns}doc")
        if doc is not None:
            if doc.get("title"):
                app_info["title"] = doc.get("title")
            if doc.text:
                app_info["description"] = doc.text.strip()

        return app_info

    def _analyze_resources(self, root: Element) -> Dict[str, Any]:
        """Analyze resource definitions"""
        ns = self._get_namespace(root)
        resources_info = {
            "resource_count": 0,
            "resources": [],
            "base_paths": set(),
            "path_patterns": [],
        }

        for resource in root.findall(f".//{ns}resource"):
            resource_info = {
                "id": resource.get("id"),
                "path": resource.get("path"),
                "type": resource.get("type"),
                "queryType": resource.get("queryType"),
                "methods": [],
                "child_resources": 0,
                "parameters": 0,
                "documentation": None,
            }

            # Extract path information
            if resource_info["path"]:
                resources_info["path_patterns"].append(resource_info["path"])
                # Extract base path (everything before path variables)
                base_path = re.sub(r"\{[^}]+\}", "", resource_info["path"]).rstrip("/")
                if base_path:
                    resources_info["base_paths"].add(base_path)

            # Count methods
            resource_info["methods"] = [
                method.get("name")
                for method in resource.findall(f"{ns}method")
                if method.get("name")
            ]

            # Count child resources
            resource_info["child_resources"] = len(resource.findall(f"{ns}resource"))

            # Count parameters
            resource_info["parameters"] = len(resource.findall(f"{ns}param"))

            # Extract documentation
            doc = resource.find(f"{ns}doc")
            if doc is not None and doc.text:
                resource_info["documentation"] = doc.text.strip()

            resources_info["resources"].append(resource_info)

        resources_info["resource_count"] = len(resources_info["resources"])
        resources_info["base_paths"] = list(resources_info["base_paths"])

        return resources_info

    def _analyze_methods(self, root: Element) -> Dict[str, Any]:
        """Analyze HTTP methods"""
        ns = self._get_namespace(root)
        methods_info = {
            "method_count": 0,
            "methods": [],
            "method_distribution": {},
            "response_codes": set(),
        }

        for method in root.findall(f".//{ns}method"):
            method_info = {
                "id": method.get("id"),
                "name": method.get("name"),
                "href": method.get("href"),
                "request_representations": [],
                "response_representations": [],
                "parameters": 0,
                "documentation": None,
                "responses": [],
            }

            # Count method distribution
            method_name = method_info["name"]
            if method_name:
                methods_info["method_distribution"][method_name] = (
                    methods_info["method_distribution"].get(method_name, 0) + 1
                )

            # Analyze request
            request = method.find(f"{ns}request")
            if request is not None:
                for rep in request.findall(f"{ns}representation"):
                    media_type = rep.get("mediaType")
                    if media_type:
                        method_info["request_representations"].append(media_type)

                method_info["parameters"] += len(request.findall(f"{ns}param"))

            # Analyze responses
            for response in method.findall(f"{ns}response"):
                response_info = {
                    "status": response.get("status"),
                    "representations": [],
                }

                if response_info["status"]:
                    methods_info["response_codes"].add(response_info["status"])

                for rep in response.findall(f"{ns}representation"):
                    media_type = rep.get("mediaType")
                    if media_type:
                        response_info["representations"].append(media_type)
                        method_info["response_representations"].append(media_type)

                method_info["responses"].append(response_info)

            # Extract documentation
            doc = method.find(f"{ns}doc")
            if doc is not None and doc.text:
                method_info["documentation"] = doc.text.strip()

            methods_info["methods"].append(method_info)

        methods_info["method_count"] = len(methods_info["methods"])
        methods_info["response_codes"] = list(methods_info["response_codes"])

        return methods_info

    def _analyze_parameters(self, root: Element) -> Dict[str, Any]:
        """Analyze parameters"""
        ns = self._get_namespace(root)
        params_info = {
            "parameter_count": 0,
            "parameters": [],
            "parameter_styles": {},
            "parameter_types": {},
            "required_params": 0,
            "optional_params": 0,
        }

        for param in root.findall(f".//{ns}param"):
            param_info = {
                "id": param.get("id"),
                "name": param.get("name"),
                "style": param.get("style"),
                "type": param.get("type"),
                "default": param.get("default"),
                "required": param.get("required", "false").lower() == "true",
                "repeating": param.get("repeating", "false").lower() == "true",
                "path": param.get("path"),
                "documentation": None,
                "options": [],
            }

            # Count parameter styles
            if param_info["style"]:
                params_info["parameter_styles"][param_info["style"]] = (
                    params_info["parameter_styles"].get(param_info["style"], 0) + 1
                )

            # Count parameter types
            if param_info["type"]:
                params_info["parameter_types"][param_info["type"]] = (
                    params_info["parameter_types"].get(param_info["type"], 0) + 1
                )

            # Count required vs optional
            if param_info["required"]:
                params_info["required_params"] += 1
            else:
                params_info["optional_params"] += 1

            # Extract options
            for option in param.findall(f"{ns}option"):
                option_info = {
                    "value": option.get("value"),
                    "mediaType": option.get("mediaType"),
                }
                param_info["options"].append(option_info)

            # Extract documentation
            doc = param.find(f"{ns}doc")
            if doc is not None and doc.text:
                param_info["documentation"] = doc.text.strip()

            params_info["parameters"].append(param_info)

        params_info["parameter_count"] = len(params_info["parameters"])

        return params_info

    def _analyze_representations(self, root: Element) -> Dict[str, Any]:
        """Analyze representation formats"""
        ns = self._get_namespace(root)
        repr_info = {
            "representation_count": 0,
            "representations": [],
            "media_types": set(),
            "elements": set(),
            "profiles": set(),
        }

        for representation in root.findall(f".//{ns}representation"):
            repr_data = {
                "id": representation.get("id"),
                "mediaType": representation.get("mediaType"),
                "element": representation.get("element"),
                "profile": representation.get("profile"),
                "href": representation.get("href"),
                "parameters": 0,
                "documentation": None,
            }

            # Collect media types
            if repr_data["mediaType"]:
                repr_info["media_types"].add(repr_data["mediaType"])

            # Collect elements
            if repr_data["element"]:
                repr_info["elements"].add(repr_data["element"])

            # Collect profiles
            if repr_data["profile"]:
                repr_info["profiles"].add(repr_data["profile"])

            # Count parameters
            repr_data["parameters"] = len(representation.findall(f"{ns}param"))

            # Extract documentation
            doc = representation.find(f"{ns}doc")
            if doc is not None and doc.text:
                repr_data["documentation"] = doc.text.strip()

            repr_info["representations"].append(repr_data)

        repr_info["representation_count"] = len(repr_info["representations"])
        repr_info["media_types"] = list(repr_info["media_types"])
        repr_info["elements"] = list(repr_info["elements"])
        repr_info["profiles"] = list(repr_info["profiles"])

        return repr_info

    def _analyze_grammars(self, root: Element) -> Dict[str, Any]:
        """Analyze grammar definitions"""
        ns = self._get_namespace(root)
        grammars_info = {
            "has_grammars": False,
            "includes": [],
            "schemas": 0,
            "documentation": None,
        }

        grammars = root.find(f"{ns}grammars")
        if grammars is not None:
            grammars_info["has_grammars"] = True

            # Extract includes
            for include in grammars.findall(f"{ns}include"):
                include_info = {
                    "href": include.get("href"),
                    "media_type": include.get("mediaType"),
                }
                grammars_info["includes"].append(include_info)

            # Count schemas (XSD schemas within grammars)
            # Look for both XSD namespace and generic schema elements
            xsd_schemas = grammars.findall(
                ".//{http://www.w3.org/2001/XMLSchema}schema"
            )
            generic_schemas = grammars.findall(".//schema")
            grammars_info["schemas"] = len(xsd_schemas) + len(generic_schemas)

            # Extract documentation
            doc = grammars.find(f"{ns}doc")
            if doc is not None and doc.text:
                grammars_info["documentation"] = doc.text.strip()

        return grammars_info

    def _analyze_documentation(self, root: Element) -> Dict[str, Any]:
        """Analyze documentation coverage"""
        ns = self._get_namespace(root)
        doc_info = {
            "total_elements": 0,
            "documented_elements": 0,
            "coverage_score": 0.0,
            "documentation_entries": [],
        }

        # Count all documentable elements
        documentable_elements = [
            f"{ns}application",
            f"{ns}resources",
            f"{ns}resource",
            f"{ns}method",
            f"{ns}param",
            f"{ns}representation",
        ]

        for elem_type in documentable_elements:
            elements = root.findall(f".//{elem_type}")
            doc_info["total_elements"] += len(elements)

            for element in elements:
                doc = element.find(f"{ns}doc")
                if doc is not None and (doc.text or doc.get("title")):
                    doc_info["documented_elements"] += 1

                    doc_entry = {
                        "element_type": elem_type.split("}")[-1],
                        "element_id": element.get("id"),
                        "title": doc.get("title"),
                        "content": doc.text.strip() if doc.text else None,
                        "lang": doc.get("{http://www.w3.org/XML/1998/namespace}lang"),
                    }
                    doc_info["documentation_entries"].append(doc_entry)

        # Calculate coverage score
        if doc_info["total_elements"] > 0:
            doc_info["coverage_score"] = (
                doc_info["documented_elements"] / doc_info["total_elements"]
            )

        return doc_info

    def _analyze_security_patterns(self, root: Element) -> Dict[str, Any]:
        """Analyze security patterns and authentication"""
        security_info = {
            "has_authentication": False,
            "auth_methods": [],
            "security_headers": [],
            "https_required": False,
            "api_keys": 0,
        }

        # Look for common authentication patterns in parameters
        ns = self._get_namespace(root)
        for param in root.findall(f".//{ns}param"):
            param_name = param.get("name", "").lower()
            param_style = param.get("style", "")

            # Check for common auth parameter names
            auth_indicators = [
                "authorization",
                "auth",
                "token",
                "api_key",
                "apikey",
                "access_token",
                "bearer",
                "key",
                "secret",
            ]

            if any(auth in param_name for auth in auth_indicators):
                security_info["has_authentication"] = True
                auth_method = (
                    f"{param_style}:{param_name}" if param_style else param_name
                )
                security_info["auth_methods"].append(auth_method)

                if "key" in param_name:
                    security_info["api_keys"] += 1

        # Check for HTTPS requirement in base URI
        app_info = self._analyze_application(root)
        if app_info["base_uri"] and app_info["base_uri"].startswith("https://"):
            security_info["https_required"] = True

        # Look for security-related headers in representations
        for representation in root.findall(f".//{ns}representation"):
            for param in representation.findall(f"{ns}param"):
                param_name = param.get("name", "").lower()
                if param.get("style") == "header" and any(
                    sec in param_name for sec in ["auth", "token", "key", "bearer"]
                ):
                    security_info["security_headers"].append(param_name)

        return security_info

    def _calculate_api_metrics(self, root: Element) -> Dict[str, Any]:
        """Calculate API complexity and design metrics"""
        metrics = {
            "complexity_score": 0.0,
            "resource_depth": 0,
            "avg_methods_per_resource": 0.0,
            "avg_params_per_method": 0.0,
            "crud_completeness": 0.0,
            "documentation_ratio": 0.0,
        }

        # Get analysis data
        resources = self._analyze_resources(root)
        methods = self._analyze_methods(root)
        documentation = self._analyze_documentation(root)

        # Calculate resource depth (max nesting)
        ns = self._get_namespace(root)
        metrics["resource_depth"] = self._calculate_max_resource_depth(root, ns)

        # Calculate averages
        if resources["resource_count"] > 0:
            total_methods = sum(len(r["methods"]) for r in resources["resources"])
            metrics["avg_methods_per_resource"] = (
                total_methods / resources["resource_count"]
            )

        if methods["method_count"] > 0:
            total_params = sum(m["parameters"] for m in methods["methods"])
            metrics["avg_params_per_method"] = total_params / methods["method_count"]

        # Calculate CRUD completeness
        http_methods = set(methods["method_distribution"].keys())
        crud_methods = {"GET", "POST", "PUT", "DELETE"}
        if crud_methods:
            metrics["crud_completeness"] = len(http_methods & crud_methods) / len(
                crud_methods
            )

        # Documentation ratio
        metrics["documentation_ratio"] = documentation["coverage_score"]

        # Overall complexity score
        complexity_factors = [
            min(resources["resource_count"] / 20.0, 1.0) * 0.3,  # Resource count
            min(metrics["resource_depth"] / 5.0, 1.0) * 0.2,  # Nesting depth
            min(methods["method_count"] / 50.0, 1.0) * 0.3,  # Method count
            min(metrics["avg_params_per_method"] / 10.0, 1.0)
            * 0.2,  # Parameter complexity
        ]
        metrics["complexity_score"] = sum(complexity_factors)

        return metrics

    def _extract_api_spec(self, root: Element) -> Dict[str, Any]:
        """Extract high-level API specification"""
        app_info = self._analyze_application(root)
        resources = self._analyze_resources(root)
        methods = self._analyze_methods(root)

        return {
            "base_uri": app_info["base_uri"],
            "title": app_info["title"],
            "description": app_info["description"],
            "version": app_info["version"],
            "resource_count": resources["resource_count"],
            "method_count": methods["method_count"],
            "supported_methods": list(methods["method_distribution"].keys()),
            "base_paths": resources["base_paths"][:10],  # Limit for readability
        }

    def _extract_endpoints(self, root: Element) -> List[Dict[str, Any]]:
        """Extract API endpoints with methods"""
        endpoints = []
        ns = self._get_namespace(root)

        # Get base URI
        app_info = self._analyze_application(root)
        base_uri = app_info["base_uri"] or ""

        for resource in root.findall(f".//{ns}resource")[:50]:  # Limit for performance
            resource_path = resource.get("path", "")

            for method in resource.findall(f"{ns}method"):
                endpoint = {
                    "path": resource_path,
                    "full_url": (
                        urljoin(base_uri, resource_path) if base_uri else resource_path
                    ),
                    "method": method.get("name"),
                    "method_id": method.get("id"),
                    "parameters": [],
                    "request_formats": [],
                    "response_formats": [],
                    "description": None,
                }

                # Extract parameters
                for param in method.findall(f".//{ns}param"):
                    param_info = {
                        "name": param.get("name"),
                        "style": param.get("style"),
                        "type": param.get("type"),
                        "required": param.get("required", "false").lower() == "true",
                    }
                    endpoint["parameters"].append(param_info)

                # Extract request formats
                request = method.find(f"{ns}request")
                if request is not None:
                    for rep in request.findall(f"{ns}representation"):
                        media_type = rep.get("mediaType")
                        if media_type:
                            endpoint["request_formats"].append(media_type)

                # Extract response formats
                for response in method.findall(f"{ns}response"):
                    for rep in response.findall(f"{ns}representation"):
                        media_type = rep.get("mediaType")
                        if media_type:
                            endpoint["response_formats"].append(media_type)

                # Extract documentation
                doc = method.find(f"{ns}doc")
                if doc is not None and doc.text:
                    endpoint["description"] = doc.text.strip()

                endpoints.append(endpoint)

        return endpoints

    def _extract_data_models(self, root: Element) -> Dict[str, Any]:
        """Extract data models from grammars and representations"""
        models = {"schemas": [], "elements": [], "media_types": []}

        ns = self._get_namespace(root)

        # Extract from grammars
        grammars = root.find(f"{ns}grammars")
        if grammars is not None:
            # Extract schema references
            for include in grammars.findall(f"{ns}include"):
                schema_info = {
                    "type": "external_schema",
                    "href": include.get("href"),
                    "media_type": include.get("mediaType"),
                }
                models["schemas"].append(schema_info)

            # Extract inline schemas
            xsd_schemas = grammars.findall(
                ".//{http://www.w3.org/2001/XMLSchema}schema"
            )
            for schema in xsd_schemas:
                schema_info = {
                    "type": "inline_xsd",
                    "target_namespace": schema.get("targetNamespace"),
                    "element_count": len(
                        schema.findall(".//{http://www.w3.org/2001/XMLSchema}element")
                    ),
                }
                models["schemas"].append(schema_info)

        # Extract elements from representations
        representations = self._analyze_representations(root)
        models["elements"] = representations["elements"]
        models["media_types"] = representations["media_types"]

        return models

    def _extract_auth_info(self, root: Element) -> Dict[str, Any]:
        """Extract authentication information"""
        security = self._analyze_security_patterns(root)

        return {
            "has_authentication": security["has_authentication"],
            "auth_methods": security["auth_methods"],
            "api_key_count": security["api_keys"],
            "requires_https": security["https_required"],
            "security_headers": security["security_headers"],
        }

    def _extract_error_responses(self, root: Element) -> List[Dict[str, Any]]:
        """Extract error response definitions"""
        errors = []
        ns = self._get_namespace(root)

        for response in root.findall(f".//{ns}response"):
            status = response.get("status")
            if status and (status.startswith("4") or status.startswith("5")):
                error_info = {
                    "status_code": status,
                    "representations": [],
                    "documentation": None,
                }

                # Extract error representations
                for rep in response.findall(f"{ns}representation"):
                    media_type = rep.get("mediaType")
                    if media_type:
                        error_info["representations"].append(media_type)

                # Extract error documentation
                doc = response.find(f"{ns}doc")
                if doc is not None and doc.text:
                    error_info["documentation"] = doc.text.strip()

                errors.append(error_info)

        return errors[:20]  # Limit

    def _assess_api_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess API design quality"""
        metrics = {
            "design_quality": 0.0,
            "documentation_quality": 0.0,
            "completeness": 0.0,
            "consistency": 0.0,
            "overall": 0.0,
        }

        # Design quality (RESTful patterns, HTTP method usage)
        methods_dist = findings["methods"]["method_distribution"]
        api_metrics = findings["api_metrics"]

        # Check for RESTful design
        design_score = 0.0
        if "GET" in methods_dist:
            design_score += 0.3  # Read operations
        if any(method in methods_dist for method in ["POST", "PUT", "PATCH"]):
            design_score += 0.3  # Write operations
        if "DELETE" in methods_dist:
            design_score += 0.2  # Delete operations
        if api_metrics["crud_completeness"] > 0.75:
            design_score += 0.2  # CRUD completeness

        metrics["design_quality"] = min(design_score, 1.0)

        # Documentation quality
        doc_coverage = findings["documentation"]["coverage_score"]
        metrics["documentation_quality"] = doc_coverage

        # Completeness (resources, methods, parameters)
        completeness_factors = []
        if findings["resources"]["resource_count"] > 0:
            completeness_factors.append(0.4)
        if findings["methods"]["method_count"] > 0:
            completeness_factors.append(0.4)
        if findings["parameters"]["parameter_count"] > 0:
            completeness_factors.append(0.2)

        metrics["completeness"] = sum(completeness_factors)

        # Consistency (parameter naming, response formats)
        consistency_score = 0.5  # Base score

        # Check media type consistency
        repr_info = findings["representations"]
        if len(repr_info["media_types"]) <= 3:  # Not too many different formats
            consistency_score += 0.2

        # Check parameter style consistency
        param_styles = findings["parameters"]["parameter_styles"]
        if len(param_styles) <= 2:  # Consistent parameter styles
            consistency_score += 0.3

        metrics["consistency"] = min(consistency_score, 1.0)

        # Overall quality
        metrics["overall"] = (
            metrics["design_quality"] * 0.3
            + metrics["documentation_quality"] * 0.25
            + metrics["completeness"] * 0.25
            + metrics["consistency"] * 0.2
        )

        return metrics

    def _calculate_max_resource_depth(
        self, root: Element, ns: str, current_depth: int = 0
    ) -> int:
        """Calculate maximum resource nesting depth"""
        max_depth = current_depth

        for resource in root.findall(f"{ns}resource"):
            child_depth = self._calculate_max_resource_depth(
                resource, ns, current_depth + 1
            )
            max_depth = max(max_depth, child_depth)

        return max_depth
