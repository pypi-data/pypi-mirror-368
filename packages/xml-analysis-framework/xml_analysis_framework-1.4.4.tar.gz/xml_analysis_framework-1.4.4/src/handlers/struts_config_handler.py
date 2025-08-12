#!/usr/bin/env python3
"""
Struts Configuration Handler

Analyzes Apache Struts framework configuration files (struts-config.xml).
Extracts action mappings, form beans, controller configuration, data sources,
message resources, and plugin definitions for enterprise Java web applications.
"""

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


class StrutsConfigHandler(XMLHandler):
    """Handler for Apache Struts configuration files"""

    STRUTS_NAMESPACE = "http://struts.apache.org/dtds/struts-config"
    STRUTS_DTD_PATTERNS = [
        "struts-config",
        "apache.org/dtds/struts-config",
        "jakarta.apache.org/struts/dtds",
    ]

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for Struts namespace or DTD references
        for uri in namespaces.values():
            if any(pattern in uri.lower() for pattern in self.STRUTS_DTD_PATTERNS):
                return True, 1.0

        # Check root element
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if root_tag.lower() == "struts-config":
            return True, 0.95

        # Check for Struts-specific elements
        struts_elements = [
            "action-mappings",
            "form-beans",
            "global-forwards",
            "controller",
        ]
        found_elements = sum(
            1 for elem in struts_elements if root.find(f".//{elem}") is not None
        )

        if found_elements >= 2:
            return True, min(found_elements * 0.25, 0.9)

        # Check for action elements with Struts attributes
        actions = root.findall(".//action")
        if actions:
            struts_attrs = ["path", "type", "forward", "include"]
            action_score = 0
            for action in actions[:5]:  # Check first 5 actions
                attrs = list(action.attrib.keys())
                if any(attr in struts_attrs for attr in attrs):
                    action_score += 0.2

            if action_score >= 0.4:
                return True, min(action_score + 0.3, 0.8)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Detect Struts version
        version = "1.x"  # Default

        # Check DTD version
        for uri in namespaces.values():
            if "struts-config_1_0" in uri:
                version = "1.0"
            elif "struts-config_1_1" in uri:
                version = "1.1"
            elif "struts-config_1_2" in uri:
                version = "1.2"
            elif "struts-config_1_3" in uri:
                version = "1.3"
            elif "struts-config_1_4" in uri:
                version = "1.4"

        # Detect configuration type
        config_type = "standard"

        # Check for modular configuration
        if root.find("message-resources") is not None:
            config_type = "internationalized"

        # Check for tiles integration
        if any(
            plugin.get("className", "").find("tiles") != -1
            for plugin in root.findall(".//plug-in")
        ):
            config_type = "tiles_integrated"

        # Check for validator integration
        if any(
            plugin.get("className", "").find("validator") != -1
            for plugin in root.findall(".//plug-in")
        ):
            config_type = "validator_integrated"

        # Count actions to determine complexity
        action_count = len(root.findall(".//action"))
        complexity = (
            "simple"
            if action_count < 10
            else "medium" if action_count < 50 else "complex"
        )

        return DocumentTypeInfo(
            type_name="Struts Configuration",
            confidence=0.95,
            version=version,
            metadata={
                "framework": "Apache Struts",
                "category": "web_framework_config",
                "config_type": config_type,
                "complexity": complexity,
                "action_count": action_count,
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "configuration_info": self._analyze_configuration(root),
            "action_mappings": self._analyze_action_mappings(root),
            "form_beans": self._analyze_form_beans(root),
            "global_forwards": self._analyze_global_forwards(root),
            "controller_config": self._analyze_controller(root),
            "data_sources": self._analyze_data_sources(root),
            "message_resources": self._analyze_message_resources(root),
            "exception_config": self._analyze_exception_config(root),
            "plugins": self._analyze_plugins(root),
            "security_analysis": self._analyze_security_patterns(root),
            "architecture_metrics": self._calculate_architecture_metrics(root),
        }

        recommendations = [
            "Migrate to modern Spring MVC or Spring Boot framework",
            "Implement RESTful API design patterns",
            "Add comprehensive input validation and sanitization",
            "Implement proper error handling and logging",
            "Configure security filters and authentication",
            "Optimize action mapping patterns for better performance",
            "Implement internationalization best practices",
            "Add monitoring and health check endpoints",
            "Document API endpoints and business logic",
            "Implement automated testing for actions and forms",
        ]

        ai_use_cases = [
            "Legacy application modernization planning",
            "Automated migration to Spring Framework",
            "Security vulnerability assessment",
            "Performance optimization recommendations",
            "Code complexity analysis and refactoring",
            "Architecture pattern recognition",
            "Dependency mapping and analysis",
            "Configuration validation and best practices",
            "Documentation generation from configuration",
            "Testing strategy development for legacy code",
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
                "total_actions": findings["action_mappings"]["action_count"],
                "form_beans": findings["form_beans"]["bean_count"],
                "global_forwards": findings["global_forwards"]["forward_count"],
                "data_sources": findings["data_sources"]["source_count"],
                "plugins": findings["plugins"]["plugin_count"],
                "message_resources": findings["message_resources"]["resource_count"],
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_configuration_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "application_structure": self._extract_application_structure(root),
            "action_catalog": self._extract_action_catalog(root),
            "form_definitions": self._extract_form_definitions(root),
            "navigation_flow": self._extract_navigation_flow(root),
            "resource_configuration": self._extract_resource_config(root),
        }

    def _analyze_configuration(self, root: Element) -> Dict[str, Any]:
        """Analyze overall configuration structure"""
        config_info = {
            "root_element": root.tag,
            "has_dtd": False,
            "dtd_version": None,
            "namespaces": {},
            "main_sections": [],
        }

        # Check for DTD
        if hasattr(root, "getroottree"):
            tree = root.getroottree()
            if hasattr(tree, "docinfo") and tree.docinfo.public_id:
                config_info["has_dtd"] = True
                config_info["dtd_version"] = tree.docinfo.public_id

        # Extract namespaces
        if "}" in root.tag:
            namespace = root.tag.split("}")[0] + "}"
            config_info["namespaces"]["default"] = namespace.strip("{}")

        # Identify main configuration sections
        main_sections = [
            "data-sources",
            "form-beans",
            "global-exceptions",
            "global-forwards",
            "action-mappings",
            "controller",
            "message-resources",
            "plug-ins",
        ]

        for section in main_sections:
            if root.find(section) is not None:
                config_info["main_sections"].append(section)

        return config_info

    def _analyze_action_mappings(self, root: Element) -> Dict[str, Any]:
        """Analyze action mappings"""
        action_info = {
            "action_count": 0,
            "actions": [],
            "path_patterns": [],
            "action_types": {},
            "forward_patterns": {},
            "scope_usage": {},
        }

        actions = root.findall(".//action")
        action_info["action_count"] = len(actions)

        for action in actions:
            action_data = {
                "path": action.get("path"),
                "type": action.get("type"),
                "name": action.get("name"),
                "scope": action.get("scope", "request"),
                "validate": action.get("validate", "true").lower() == "true",
                "input": action.get("input"),
                "parameter": action.get("parameter"),
                "attribute": action.get("attribute"),
                "forwards": [],
                "exceptions": [],
            }

            # Track patterns
            if action_data["path"]:
                action_info["path_patterns"].append(action_data["path"])

            # Track action types
            if action_data["type"]:
                action_info["action_types"][action_data["type"]] = (
                    action_info["action_types"].get(action_data["type"], 0) + 1
                )

            # Track scope usage
            scope = action_data["scope"]
            action_info["scope_usage"][scope] = (
                action_info["scope_usage"].get(scope, 0) + 1
            )

            # Extract forwards
            for forward in action.findall("forward"):
                forward_data = {
                    "name": forward.get("name"),
                    "path": forward.get("path"),
                    "redirect": forward.get("redirect", "false").lower() == "true",
                    "contextRelative": forward.get("contextRelative", "false").lower()
                    == "true",
                }
                action_data["forwards"].append(forward_data)

                # Track forward patterns
                if forward_data["name"]:
                    action_info["forward_patterns"][forward_data["name"]] = (
                        action_info["forward_patterns"].get(forward_data["name"], 0) + 1
                    )

            # Extract exceptions
            for exception in action.findall("exception"):
                exception_data = {
                    "key": exception.get("key"),
                    "type": exception.get("type"),
                    "path": exception.get("path"),
                    "scope": exception.get("scope"),
                }
                action_data["exceptions"].append(exception_data)

            action_info["actions"].append(action_data)

        return action_info

    def _analyze_form_beans(self, root: Element) -> Dict[str, Any]:
        """Analyze form bean definitions"""
        form_info = {
            "bean_count": 0,
            "beans": [],
            "form_types": {},
            "dynamic_forms": 0,
            "validation_enabled": 0,
        }

        form_beans = root.findall(".//form-bean")
        form_info["bean_count"] = len(form_beans)

        for bean in form_beans:
            bean_data = {
                "name": bean.get("name"),
                "type": bean.get("type"),
                "dynamic": bean.get("dynamic", "false").lower() == "true",
                "properties": [],
            }

            # Track form types
            if bean_data["type"]:
                form_info["form_types"][bean_data["type"]] = (
                    form_info["form_types"].get(bean_data["type"], 0) + 1
                )

            # Count dynamic forms
            if bean_data["dynamic"]:
                form_info["dynamic_forms"] += 1

            # Extract form properties (for dynamic forms)
            for prop in bean.findall("form-property"):
                prop_data = {
                    "name": prop.get("name"),
                    "type": prop.get("type"),
                    "initial": prop.get("initial"),
                    "size": prop.get("size"),
                }
                bean_data["properties"].append(prop_data)

            form_info["beans"].append(bean_data)

        return form_info

    def _analyze_global_forwards(self, root: Element) -> Dict[str, Any]:
        """Analyze global forward definitions"""
        forward_info = {
            "forward_count": 0,
            "forwards": [],
            "redirect_count": 0,
            "context_relative_count": 0,
        }

        forwards = root.findall(".//global-forwards/forward")
        forward_info["forward_count"] = len(forwards)

        for forward in forwards:
            forward_data = {
                "name": forward.get("name"),
                "path": forward.get("path"),
                "redirect": forward.get("redirect", "false").lower() == "true",
                "contextRelative": forward.get("contextRelative", "false").lower()
                == "true",
            }

            if forward_data["redirect"]:
                forward_info["redirect_count"] += 1

            if forward_data["contextRelative"]:
                forward_info["context_relative_count"] += 1

            forward_info["forwards"].append(forward_data)

        return forward_info

    def _analyze_controller(self, root: Element) -> Dict[str, Any]:
        """Analyze controller configuration"""
        controller_info = {
            "has_controller": False,
            "buffer_size": None,
            "content_type": None,
            "debug": None,
            "input_forward": None,
            "locale": None,
            "max_file_size": None,
            "multipart_class": None,
            "no_cache": None,
            "process_class": None,
            "temp_dir": None,
        }

        controller = root.find("controller")
        if controller is not None:
            controller_info["has_controller"] = True

            # Extract controller attributes
            attrs = [
                "bufferSize",
                "contentType",
                "debug",
                "inputForward",
                "locale",
                "maxFileSize",
                "multipartClass",
                "nocache",
                "processorClass",
                "tempDir",
            ]

            for attr in attrs:
                value = controller.get(attr)
                if value:
                    key = attr.lower().replace("class", "_class")
                    controller_info[key] = value

        return controller_info

    def _analyze_data_sources(self, root: Element) -> Dict[str, Any]:
        """Analyze data source configurations"""
        ds_info = {
            "source_count": 0,
            "sources": [],
            "driver_types": {},
            "connection_pools": 0,
        }

        data_sources = root.findall(".//data-source")
        ds_info["source_count"] = len(data_sources)

        for ds in data_sources:
            ds_data = {"key": ds.get("key"), "type": ds.get("type"), "properties": {}}

            # Extract set-property elements
            for prop in ds.findall("set-property"):
                prop_name = prop.get("property")
                prop_value = prop.get("value")
                if prop_name:
                    ds_data["properties"][prop_name] = prop_value

                    # Track driver types
                    if prop_name == "driverClassName" and prop_value:
                        ds_info["driver_types"][prop_value] = (
                            ds_info["driver_types"].get(prop_value, 0) + 1
                        )

                    # Count connection pools
                    if "pool" in prop_name.lower():
                        ds_info["connection_pools"] += 1

            ds_info["sources"].append(ds_data)

        return ds_info

    def _analyze_message_resources(self, root: Element) -> Dict[str, Any]:
        """Analyze message resource configurations"""
        msg_info = {
            "resource_count": 0,
            "resources": [],
            "internationalization": False,
            "null_handling": {},
            "factory_types": {},
        }

        resources = root.findall(".//message-resources")
        msg_info["resource_count"] = len(resources)

        for resource in resources:
            resource_data = {
                "parameter": resource.get("parameter"),
                "key": resource.get("key"),
                "factory": resource.get("factory"),
                "null": resource.get("null"),
                "escape": resource.get("escape"),
            }

            # Check for internationalization
            if resource_data["parameter"] and (
                "_" in resource_data["parameter"]
                or "messages" in resource_data["parameter"].lower()
            ):
                msg_info["internationalization"] = True

            # Track null handling
            if resource_data["null"]:
                msg_info["null_handling"][resource_data["null"]] = (
                    msg_info["null_handling"].get(resource_data["null"], 0) + 1
                )

            # Track factory types
            if resource_data["factory"]:
                msg_info["factory_types"][resource_data["factory"]] = (
                    msg_info["factory_types"].get(resource_data["factory"], 0) + 1
                )

            msg_info["resources"].append(resource_data)

        return msg_info

    def _analyze_exception_config(self, root: Element) -> Dict[str, Any]:
        """Analyze exception handling configuration"""
        exc_info = {
            "global_exceptions": 0,
            "action_exceptions": 0,
            "exception_types": {},
            "error_pages": [],
        }

        # Global exceptions
        global_exceptions = root.findall(".//global-exceptions/exception")
        exc_info["global_exceptions"] = len(global_exceptions)

        # Action-level exceptions
        action_exceptions = root.findall(".//action-mappings/action/exception")
        exc_info["action_exceptions"] = len(action_exceptions)

        # Analyze all exceptions
        all_exceptions = global_exceptions + action_exceptions
        for exception in all_exceptions:
            exc_type = exception.get("type")
            if exc_type:
                exc_info["exception_types"][exc_type] = (
                    exc_info["exception_types"].get(exc_type, 0) + 1
                )

            path = exception.get("path")
            if path:
                exc_info["error_pages"].append(
                    {
                        "type": exc_type,
                        "path": path,
                        "key": exception.get("key"),
                        "scope": exception.get("scope"),
                    }
                )

        return exc_info

    def _analyze_plugins(self, root: Element) -> Dict[str, Any]:
        """Analyze plugin configurations"""
        plugin_info = {
            "plugin_count": 0,
            "plugins": [],
            "plugin_types": {},
            "tiles_integration": False,
            "validator_integration": False,
        }

        plugins = root.findall(".//plug-in")
        plugin_info["plugin_count"] = len(plugins)

        for plugin in plugins:
            plugin_data = {"className": plugin.get("className"), "properties": {}}

            # Extract plugin properties
            for prop in plugin.findall("set-property"):
                prop_name = prop.get("property")
                prop_value = prop.get("value")
                if prop_name:
                    plugin_data["properties"][prop_name] = prop_value

            # Track plugin types
            class_name = plugin_data["className"]
            if class_name:
                plugin_info["plugin_types"][class_name] = (
                    plugin_info["plugin_types"].get(class_name, 0) + 1
                )

                # Check for specific integrations
                if "tiles" in class_name.lower():
                    plugin_info["tiles_integration"] = True
                elif "validator" in class_name.lower():
                    plugin_info["validator_integration"] = True

            plugin_info["plugins"].append(plugin_data)

        return plugin_info

    def _analyze_security_patterns(self, root: Element) -> Dict[str, Any]:
        """Analyze security-related patterns"""
        security_info = {
            "validation_enabled": 0,
            "secure_forwards": 0,
            "input_validation": 0,
            "xss_protection": False,
            "csrf_protection": False,
            "security_roles": [],
            "potential_vulnerabilities": [],
        }

        # Check validation on actions
        actions = root.findall(".//action")
        for action in actions:
            if action.get("validate", "true").lower() == "true":
                security_info["validation_enabled"] += 1

            # Check for input attribute (potential XSS risk)
            if action.get("input"):
                security_info["input_validation"] += 1

        # Check for secure forwards (HTTPS)
        forwards = root.findall(".//forward")
        for forward in forwards:
            path = forward.get("path", "")
            if path.startswith("https://"):
                security_info["secure_forwards"] += 1

        # Check for security-related plugins
        plugins = root.findall(".//plug-in")
        for plugin in plugins:
            class_name = plugin.get("className", "").lower()
            if "security" in class_name or "auth" in class_name:
                security_info["xss_protection"] = True
            elif "csrf" in class_name or "token" in class_name:
                security_info["csrf_protection"] = True

        # Identify potential vulnerabilities
        if security_info["validation_enabled"] == 0:
            security_info["potential_vulnerabilities"].append(
                "No input validation configured"
            )

        if not security_info["xss_protection"]:
            security_info["potential_vulnerabilities"].append(
                "No XSS protection detected"
            )

        if not security_info["csrf_protection"]:
            security_info["potential_vulnerabilities"].append(
                "No CSRF protection detected"
            )

        return security_info

    def _calculate_architecture_metrics(self, root: Element) -> Dict[str, Any]:
        """Calculate architecture and complexity metrics"""
        metrics = {
            "complexity_score": 0.0,
            "coupling_score": 0.0,
            "maintainability_score": 0.0,
            "testability_score": 0.0,
            "action_to_form_ratio": 0.0,
            "forward_reuse_factor": 0.0,
        }

        # Get component counts
        action_count = len(root.findall(".//action"))
        form_count = len(root.findall(".//form-bean"))
        forward_count = len(root.findall(".//forward"))

        # Calculate complexity score
        complexity_factors = [
            min(action_count / 50.0, 1.0) * 0.4,  # Action complexity
            min(form_count / 30.0, 1.0) * 0.3,  # Form complexity
            min(forward_count / 40.0, 1.0) * 0.3,  # Navigation complexity
        ]
        metrics["complexity_score"] = sum(complexity_factors)

        # Calculate coupling score (based on shared forwards and forms)
        if action_count > 0:
            # Count actions that share forms
            form_usage = {}
            for action in root.findall(".//action"):
                form_name = action.get("name")
                if form_name:
                    form_usage[form_name] = form_usage.get(form_name, 0) + 1

            shared_forms = sum(1 for count in form_usage.values() if count > 1)
            metrics["coupling_score"] = min(shared_forms / max(form_count, 1), 1.0)

        # Action to form ratio
        if form_count > 0:
            metrics["action_to_form_ratio"] = action_count / form_count

        # Forward reuse factor
        if forward_count > 0:
            forward_names = [
                f.get("name") for f in root.findall(".//forward") if f.get("name")
            ]
            unique_forwards = len(set(forward_names))
            if unique_forwards > 0:
                metrics["forward_reuse_factor"] = forward_count / unique_forwards

        # Maintainability score (inverse of complexity)
        metrics["maintainability_score"] = max(0.0, 1.0 - metrics["complexity_score"])

        # Testability score (based on validation and structure)
        validation_ratio = 0
        if action_count > 0:
            validated_actions = sum(
                1
                for action in root.findall(".//action")
                if action.get("validate", "true").lower() == "true"
            )
            validation_ratio = validated_actions / action_count

        metrics["testability_score"] = (
            validation_ratio * 0.6 + metrics["maintainability_score"] * 0.4
        )

        return metrics

    def _extract_application_structure(self, root: Element) -> Dict[str, Any]:
        """Extract high-level application structure"""
        structure = {
            "configuration_sections": [],
            "component_counts": {},
            "integration_points": [],
        }

        # Main sections
        sections = [
            "data-sources",
            "form-beans",
            "global-forwards",
            "action-mappings",
            "controller",
            "message-resources",
            "plug-ins",
        ]

        for section in sections:
            if root.find(section) is not None:
                structure["configuration_sections"].append(section)

        # Component counts
        structure["component_counts"] = {
            "actions": len(root.findall(".//action")),
            "forms": len(root.findall(".//form-bean")),
            "forwards": len(root.findall(".//forward")),
            "data_sources": len(root.findall(".//data-source")),
            "plugins": len(root.findall(".//plug-in")),
        }

        # Integration points
        plugins = root.findall(".//plug-in")
        for plugin in plugins:
            class_name = plugin.get("className", "")
            if class_name:
                structure["integration_points"].append(class_name)

        return structure

    def _extract_action_catalog(self, root: Element) -> List[Dict[str, Any]]:
        """Extract comprehensive action catalog"""
        actions = []

        for action in root.findall(".//action")[:100]:  # Limit for performance
            action_data = {
                "path": action.get("path"),
                "type": action.get("type"),
                "name": action.get("name"),
                "input": action.get("input"),
                "forwards": [
                    f.get("name") for f in action.findall("forward") if f.get("name")
                ],
                "exceptions": [
                    e.get("type") for e in action.findall("exception") if e.get("type")
                ],
                "validation": action.get("validate", "true").lower() == "true",
            }
            actions.append(action_data)

        return actions

    def _extract_form_definitions(self, root: Element) -> List[Dict[str, Any]]:
        """Extract form bean definitions"""
        forms = []

        for form in root.findall(".//form-bean"):
            form_data = {
                "name": form.get("name"),
                "type": form.get("type"),
                "dynamic": form.get("dynamic", "false").lower() == "true",
                "properties": [],
            }

            # Extract properties for dynamic forms
            for prop in form.findall("form-property"):
                prop_data = {
                    "name": prop.get("name"),
                    "type": prop.get("type"),
                    "initial": prop.get("initial"),
                }
                form_data["properties"].append(prop_data)

            forms.append(form_data)

        return forms

    def _extract_navigation_flow(self, root: Element) -> Dict[str, Any]:
        """Extract navigation flow information"""
        flow = {
            "global_forwards": [],
            "action_flows": [],
            "entry_points": [],
            "error_pages": [],
        }

        # Global forwards
        for forward in root.findall(".//global-forwards/forward"):
            flow["global_forwards"].append(
                {
                    "name": forward.get("name"),
                    "path": forward.get("path"),
                    "redirect": forward.get("redirect", "false").lower() == "true",
                }
            )

        # Action flows
        for action in root.findall(".//action"):
            forwards = [
                f.get("name") for f in action.findall("forward") if f.get("name")
            ]
            if forwards:
                flow["action_flows"].append(
                    {"path": action.get("path"), "forwards": forwards}
                )

        # Entry points (actions without input)
        for action in root.findall(".//action"):
            if not action.get("input") and action.get("path"):
                flow["entry_points"].append(action.get("path"))

        return flow

    def _extract_resource_config(self, root: Element) -> Dict[str, Any]:
        """Extract resource configuration"""
        resources = {"data_sources": [], "message_resources": [], "plugins": []}

        # Data sources
        for ds in root.findall(".//data-source"):
            ds_data = {
                "key": ds.get("key"),
                "type": ds.get("type"),
                "properties": {
                    prop.get("property"): prop.get("value")
                    for prop in ds.findall("set-property")
                    if prop.get("property")
                },
            }
            resources["data_sources"].append(ds_data)

        # Message resources
        for msg in root.findall(".//message-resources"):
            resources["message_resources"].append(
                {
                    "parameter": msg.get("parameter"),
                    "key": msg.get("key"),
                    "factory": msg.get("factory"),
                }
            )

        # Plugins
        for plugin in root.findall(".//plug-in"):
            resources["plugins"].append(
                {
                    "className": plugin.get("className"),
                    "properties": {
                        prop.get("property"): prop.get("value")
                        for prop in plugin.findall("set-property")
                        if prop.get("property")
                    },
                }
            )

        return resources

    def _assess_configuration_quality(
        self, findings: Dict[str, Any]
    ) -> Dict[str, float]:
        """Assess configuration quality metrics"""
        metrics = {
            "design_quality": 0.0,
            "security_quality": 0.0,
            "maintainability": 0.0,
            "completeness": 0.0,
            "overall": 0.0,
        }

        # Design quality
        arch_metrics = findings["architecture_metrics"]
        metrics["design_quality"] = arch_metrics["maintainability_score"]

        # Security quality
        security = findings["security_analysis"]
        total_actions = findings["action_mappings"]["action_count"]

        security_score = 0.0
        if total_actions > 0:
            validation_score = security["validation_enabled"] / total_actions
            security_score += validation_score * 0.4

        if security["xss_protection"]:
            security_score += 0.3
        if security["csrf_protection"]:
            security_score += 0.3

        metrics["security_quality"] = min(security_score, 1.0)

        # Maintainability
        metrics["maintainability"] = arch_metrics["maintainability_score"]

        # Completeness
        completeness_factors = []
        if findings["action_mappings"]["action_count"] > 0:
            completeness_factors.append(0.3)
        if findings["form_beans"]["bean_count"] > 0:
            completeness_factors.append(0.2)
        if findings["controller_config"]["has_controller"]:
            completeness_factors.append(0.2)
        if findings["message_resources"]["resource_count"] > 0:
            completeness_factors.append(0.15)
        if findings["exception_config"]["global_exceptions"] > 0:
            completeness_factors.append(0.15)

        metrics["completeness"] = sum(completeness_factors)

        # Overall quality
        metrics["overall"] = (
            metrics["design_quality"] * 0.3
            + metrics["security_quality"] * 0.25
            + metrics["maintainability"] * 0.25
            + metrics["completeness"] * 0.2
        )

        return metrics
