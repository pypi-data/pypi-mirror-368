#!/usr/bin/env python3
"""
Enterprise Configuration Handler

Handles various enterprise XML configuration files including:
- Java EE web.xml (deployment descriptors)
- Tomcat server.xml and context.xml
- JBoss/WildFly configuration files
- WebLogic config.xml
- Generic application server configurations
"""

import re
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


class EnterpriseConfigHandler(XMLHandler):
    """Handler for enterprise application server configuration files"""

    # Known configuration file patterns
    CONFIG_PATTERNS = {
        "web.xml": {
            "root_elements": ["web-app"],
            "namespaces": [
                "java.sun.com/xml/ns/javaee",
                "java.sun.com/xml/ns/j2ee",
                "xmlns.jcp.org/xml/ns/javaee",
            ],
            "type": "Java EE Deployment Descriptor",
        },
        "server.xml": {
            "root_elements": ["Server"],
            "indicators": ["Connector", "Engine", "Host", "Context"],
            "type": "Tomcat Server Configuration",
        },
        "context.xml": {
            "root_elements": ["Context"],
            "indicators": ["Resource", "ResourceLink", "Valve"],
            "type": "Tomcat Context Configuration",
        },
        "standalone.xml": {
            "root_elements": ["server"],
            "namespaces": ["urn:jboss:domain"],
            "type": "JBoss/WildFly Configuration",
        },
        "config.xml": {
            "root_elements": ["domain", "config"],
            "indicators": ["server", "machine", "cluster"],
            "type": "WebLogic Configuration",
        },
        "applicationContext.xml": {
            "root_elements": ["beans"],
            "namespaces": ["springframework.org/schema/beans"],
            "type": "Spring Application Context",
        },
    }

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # Check each known pattern
        for config_name, pattern in self.CONFIG_PATTERNS.items():
            score = 0.0

            # Check root element
            if "root_elements" in pattern and root_tag in pattern["root_elements"]:
                score += 0.5

            # Check namespaces
            if "namespaces" in pattern:
                for ns in pattern["namespaces"]:
                    if any(ns in uri for uri in namespaces.values()):
                        score += 0.5
                        break

            # Check for indicator elements
            if "indicators" in pattern and score < 1.0:
                indicator_count = 0
                for indicator in pattern["indicators"]:
                    if root.find(f".//{indicator}") is not None:
                        indicator_count += 1

                if indicator_count > 0:
                    score += min(indicator_count * 0.2, 0.5)

            if score >= 0.5:
                return True, score

        # Generic enterprise config detection
        enterprise_indicators = [
            "servlet",
            "filter",
            "listener",
            "datasource",
            "connection-pool",
            "security",
            "realm",
            "valve",
            "cluster",
            "deployment",
        ]

        indicator_count = sum(
            1 for ind in enterprise_indicators if root.find(f".//{ind}") is not None
        )
        if indicator_count >= 2:
            return True, min(indicator_count * 0.2, 0.6)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # Determine specific configuration type
        config_type = "Generic Enterprise Configuration"
        version = None

        # Check web.xml
        if root_tag == "web-app":
            config_type = "Java EE Deployment Descriptor"
            version = root.get("version", "3.0")

            # Determine Java EE version from namespace
            for uri in namespaces.values():
                if "javaee" in uri:
                    if "javaee/7" in uri:
                        version = "3.1"  # Java EE 7
                    elif "javaee/6" in uri:
                        version = "3.0"  # Java EE 6
                    elif "j2ee" in uri:
                        version = "2.4"  # J2EE

        # Check Tomcat server.xml
        elif root_tag == "Server":
            config_type = "Tomcat Server Configuration"
            # Try to detect Tomcat version from comments or attributes
            # Note: defusedxml doesn't preserve comments during parsing
            # So we'll skip comment-based version detection
            version = None

        # Check JBoss/WildFly
        elif "urn:jboss:domain" in str(namespaces.values()):
            config_type = "JBoss/WildFly Configuration"
            # Extract version from namespace
            for uri in namespaces.values():
                version_match = re.search(r"domain:(\d+\.\d+)", uri)
                if version_match:
                    version = version_match.group(1)

        return DocumentTypeInfo(
            type_name=config_type,
            confidence=0.9,
            version=version,
            metadata={
                "category": "enterprise_configuration",
                "root_element": root_tag,
                "file_type": self._guess_file_type(root, namespaces),
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        config_type = self._determine_config_type(root)

        # Route to specific analysis based on type
        if "web.xml" in config_type or "Deployment Descriptor" in config_type:
            findings = self._analyze_web_xml(root)
        elif "Tomcat" in config_type and "Server" in config_type:
            findings = self._analyze_tomcat_server(root)
        elif "JBoss" in config_type or "WildFly" in config_type:
            findings = self._analyze_jboss_config(root)
        else:
            findings = self._analyze_generic_config(root)

        recommendations = [
            "Review security configurations for vulnerabilities",
            "Check for hardcoded passwords and credentials",
            "Analyze resource pool settings for optimization",
            "Validate against security best practices",
            "Extract for configuration management database",
            "Monitor for configuration drift",
        ]

        ai_use_cases = [
            "Security misconfiguration detection",
            "Performance optimization recommendations",
            "Configuration compliance checking",
            "Automated documentation generation",
            "Migration planning assistance",
            "Configuration anomaly detection",
            "Resource optimization analysis",
            "Dependency impact analysis",
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
            data_inventory=self._create_inventory(findings),
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_config_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        config_type = self._determine_config_type(root)

        base_data = {
            "configuration_type": config_type,
            "security_settings": self._extract_security_settings(root),
            "resource_definitions": self._extract_resources(root),
            "deployment_info": self._extract_deployment_info(root),
        }

        # Add type-specific data
        if "web.xml" in config_type:
            base_data["servlets"] = self._extract_servlets(root)
            base_data["filters"] = self._extract_filters(root)
        elif "Tomcat" in config_type:
            base_data["connectors"] = self._extract_connectors(root)
            base_data["hosts"] = self._extract_hosts(root)

        return base_data

    def _analyze_web_xml(self, root: Element) -> Dict[str, Any]:
        """Analyze Java EE web.xml deployment descriptor"""
        findings = {
            "servlets": self._analyze_servlets(root),
            "filters": self._analyze_filters(root),
            "listeners": self._analyze_listeners(root),
            "security": self._analyze_web_security(root),
            "context_params": self._extract_context_params(root),
            "error_pages": self._extract_error_pages(root),
            "welcome_files": self._extract_welcome_files(root),
            "session_config": self._extract_session_config(root),
        }

        return findings

    def _analyze_tomcat_server(self, root: Element) -> Dict[str, Any]:
        """Analyze Tomcat server.xml configuration"""
        findings = {
            "server_info": self._extract_server_info(root),
            "connectors": self._analyze_connectors(root),
            "engines": self._analyze_engines(root),
            "hosts": self._analyze_hosts(root),
            "valves": self._analyze_valves(root),
            "realms": self._analyze_realms(root),
            "resources": self._analyze_global_resources(root),
        }

        return findings

    def _analyze_jboss_config(self, root: Element) -> Dict[str, Any]:
        """Analyze JBoss/WildFly configuration"""
        findings = {
            "profiles": self._extract_profiles(root),
            "subsystems": self._analyze_subsystems(root),
            "interfaces": self._extract_interfaces(root),
            "socket_bindings": self._extract_socket_bindings(root),
            "deployments": self._extract_deployments(root),
            "datasources": self._extract_jboss_datasources(root),
        }

        return findings

    def _analyze_generic_config(self, root: Element) -> Dict[str, Any]:
        """Generic analysis for unknown enterprise configs"""
        findings = {
            "structure": self._analyze_structure(root),
            "security_elements": self._find_security_elements(root),
            "connection_settings": self._find_connection_settings(root),
            "resource_pools": self._find_resource_pools(root),
            "deployment_settings": self._find_deployment_settings(root),
        }

        return findings

    # Web.xml specific methods
    def _analyze_servlets(self, root: Element) -> List[Dict[str, Any]]:
        servlets = []

        # Handle different namespace possibilities
        servlet_tags = (
            root.findall(".//servlet")
            + root.findall(".//{http://java.sun.com/xml/ns/javaee}servlet")
            + root.findall(".//{http://xmlns.jcp.org/xml/ns/javaee}servlet")
        )

        for servlet in servlet_tags:
            servlet_info = {
                "name": self._get_child_text(servlet, "servlet-name"),
                "class": self._get_child_text(servlet, "servlet-class"),
                "jsp_file": self._get_child_text(servlet, "jsp-file"),
                "init_params": self._extract_init_params(servlet),
                "load_on_startup": self._get_child_text(servlet, "load-on-startup"),
            }

            servlets.append(servlet_info)

        # Extract servlet mappings
        mappings = {}
        mapping_tags = (
            root.findall(".//servlet-mapping")
            + root.findall(".//{http://java.sun.com/xml/ns/javaee}servlet-mapping")
            + root.findall(".//{http://xmlns.jcp.org/xml/ns/javaee}servlet-mapping")
        )

        for mapping in mapping_tags:
            name = self._get_child_text(mapping, "servlet-name")
            pattern = self._get_child_text(mapping, "url-pattern")
            if name and pattern:
                if name not in mappings:
                    mappings[name] = []
                mappings[name].append(pattern)

        # Add mappings to servlet info
        for servlet in servlets:
            servlet["url_patterns"] = mappings.get(servlet["name"], [])

        return servlets

    def _analyze_filters(self, root: Element) -> List[Dict[str, Any]]:
        filters = []

        filter_tags = (
            root.findall(".//filter")
            + root.findall(".//{http://java.sun.com/xml/ns/javaee}filter")
            + root.findall(".//{http://xmlns.jcp.org/xml/ns/javaee}filter")
        )

        for filter_elem in filter_tags:
            filter_info = {
                "name": self._get_child_text(filter_elem, "filter-name"),
                "class": self._get_child_text(filter_elem, "filter-class"),
                "init_params": self._extract_init_params(filter_elem),
            }
            filters.append(filter_info)

        # Extract filter mappings
        filter_mappings = {}
        mapping_tags = (
            root.findall(".//filter-mapping")
            + root.findall(".//{http://java.sun.com/xml/ns/javaee}filter-mapping")
            + root.findall(".//{http://xmlns.jcp.org/xml/ns/javaee}filter-mapping")
        )

        for mapping in mapping_tags:
            name = self._get_child_text(mapping, "filter-name")
            pattern = self._get_child_text(mapping, "url-pattern")
            servlet = self._get_child_text(mapping, "servlet-name")

            if name:
                if name not in filter_mappings:
                    filter_mappings[name] = {"patterns": [], "servlets": []}
                if pattern:
                    filter_mappings[name]["patterns"].append(pattern)
                if servlet:
                    filter_mappings[name]["servlets"].append(servlet)

        # Add mappings to filter info
        for filter_info in filters:
            mappings = filter_mappings.get(filter_info["name"], {})
            filter_info["url_patterns"] = mappings.get("patterns", [])
            filter_info["servlet_names"] = mappings.get("servlets", [])

        return filters

    def _analyze_listeners(self, root: Element) -> List[str]:
        listeners = []

        listener_tags = (
            root.findall(".//listener")
            + root.findall(".//{http://java.sun.com/xml/ns/javaee}listener")
            + root.findall(".//{http://xmlns.jcp.org/xml/ns/javaee}listener")
        )

        for listener in listener_tags:
            listener_class = self._get_child_text(listener, "listener-class")
            if listener_class:
                listeners.append(listener_class)

        return listeners

    def _analyze_web_security(self, root: Element) -> Dict[str, Any]:
        security = {"constraints": [], "roles": [], "login_config": None}

        # Security constraints
        constraint_tags = (
            root.findall(".//security-constraint")
            + root.findall(".//{http://java.sun.com/xml/ns/javaee}security-constraint")
            + root.findall(".//{http://xmlns.jcp.org/xml/ns/javaee}security-constraint")
        )

        for constraint in constraint_tags:
            constraint_info = {
                "web_resources": [],
                "auth_constraint": None,
                "user_data_constraint": None,
            }

            # Web resource collections
            for resource in constraint.findall(".//web-resource-collection"):
                resource_info = {
                    "name": self._get_child_text(resource, "web-resource-name"),
                    "patterns": [
                        p.text for p in resource.findall(".//url-pattern") if p.text
                    ],
                    "methods": [
                        m.text for m in resource.findall(".//http-method") if m.text
                    ],
                }
                constraint_info["web_resources"].append(resource_info)

            # Auth constraint
            auth = constraint.find(".//auth-constraint")
            if auth is not None:
                constraint_info["auth_constraint"] = {
                    "roles": [r.text for r in auth.findall(".//role-name") if r.text]
                }

            # User data constraint
            user_data = constraint.find(".//user-data-constraint")
            if user_data is not None:
                transport = user_data.find(".//transport-guarantee")
                if transport is not None:
                    constraint_info["user_data_constraint"] = transport.text

            security["constraints"].append(constraint_info)

        # Security roles
        role_tags = (
            root.findall(".//security-role")
            + root.findall(".//{http://java.sun.com/xml/ns/javaee}security-role")
            + root.findall(".//{http://xmlns.jcp.org/xml/ns/javaee}security-role")
        )

        for role in role_tags:
            role_name = self._get_child_text(role, "role-name")
            if role_name:
                security["roles"].append(role_name)

        # Login config
        login_config = (
            root.find(".//login-config")
            or root.find(".//{http://java.sun.com/xml/ns/javaee}login-config")
            or root.find(".//{http://xmlns.jcp.org/xml/ns/javaee}login-config")
        )

        if login_config is not None:
            security["login_config"] = {
                "auth_method": self._get_child_text(login_config, "auth-method"),
                "realm_name": self._get_child_text(login_config, "realm-name"),
                "form_config": self._extract_form_config(login_config),
            }

        return security

    # Tomcat specific methods
    def _analyze_connectors(self, root: Element) -> List[Dict[str, Any]]:
        connectors = []

        for connector in root.findall(".//Connector"):
            connector_info = {
                "port": connector.get("port"),
                "protocol": connector.get("protocol", "HTTP/1.1"),
                "secure": connector.get("secure", "false") == "true",
                "scheme": connector.get("scheme", "http"),
                "ssl_enabled": connector.get("SSLEnabled", "false") == "true",
            }

            # Extract all attributes for detailed analysis
            connector_info["attributes"] = dict(connector.attrib)

            connectors.append(connector_info)

        return connectors

    def _analyze_engines(self, root: Element) -> List[Dict[str, Any]]:
        engines = []

        for engine in root.findall(".//Engine"):
            engine_info = {
                "name": engine.get("name"),
                "default_host": engine.get("defaultHost"),
                "hosts": [],
            }

            # Get nested hosts
            for host in engine.findall(".//Host"):
                host_info = {
                    "name": host.get("name"),
                    "app_base": host.get("appBase"),
                    "unpack_wars": host.get("unpackWARs", "true") == "true",
                    "auto_deploy": host.get("autoDeploy", "true") == "true",
                }
                engine_info["hosts"].append(host_info)

            engines.append(engine_info)

        return engines

    def _analyze_hosts(self, root: Element) -> List[Dict[str, Any]]:
        hosts = []

        for host in root.findall(".//Host"):
            host_info = {
                "name": host.get("name"),
                "app_base": host.get("appBase"),
                "contexts": [],
                "valves": [],
            }

            # Get contexts
            for context in host.findall(".//Context"):
                context_info = {
                    "path": context.get("path"),
                    "doc_base": context.get("docBase"),
                    "reloadable": context.get("reloadable", "false") == "true",
                }
                host_info["contexts"].append(context_info)

            # Get valves
            for valve in host.findall(".//Valve"):
                valve_info = {
                    "class_name": valve.get("className"),
                    "attributes": dict(valve.attrib),
                }
                host_info["valves"].append(valve_info)

            hosts.append(host_info)

        return hosts

    def _analyze_valves(self, root: Element) -> List[Dict[str, Any]]:
        valves = []

        for valve in root.findall(".//Valve"):
            valve_info = {
                "class_name": valve.get("className"),
                "pattern": valve.get("pattern"),
                "directory": valve.get("directory"),
                "prefix": valve.get("prefix"),
                "suffix": valve.get("suffix"),
            }

            # Identify valve type
            class_name = valve.get("className", "")
            if "AccessLogValve" in class_name:
                valve_info["type"] = "access_log"
            elif "RemoteIpValve" in class_name:
                valve_info["type"] = "remote_ip"
            elif "ErrorReportValve" in class_name:
                valve_info["type"] = "error_report"
            else:
                valve_info["type"] = "custom"

            valves.append(valve_info)

        return valves

    def _analyze_realms(self, root: Element) -> List[Dict[str, Any]]:
        realms = []

        for realm in root.findall(".//Realm"):
            realm_info = {
                "class_name": realm.get("className"),
                "attributes": dict(realm.attrib),
            }

            # Identify realm type
            class_name = realm.get("className", "")
            if "UserDatabaseRealm" in class_name:
                realm_info["type"] = "user_database"
            elif "JDBCRealm" in class_name:
                realm_info["type"] = "jdbc"
            elif "DataSourceRealm" in class_name:
                realm_info["type"] = "datasource"
            elif "JNDIRealm" in class_name:
                realm_info["type"] = "jndi"
            else:
                realm_info["type"] = "custom"

            realms.append(realm_info)

        return realms

    def _analyze_global_resources(self, root: Element) -> List[Dict[str, Any]]:
        resources = []

        global_resources = root.find(".//GlobalNamingResources")
        if global_resources is not None:
            for resource in global_resources.findall(".//Resource"):
                resource_info = {
                    "name": resource.get("name"),
                    "auth": resource.get("auth"),
                    "type": resource.get("type"),
                    "attributes": dict(resource.attrib),
                }
                resources.append(resource_info)

        return resources

    # JBoss/WildFly specific methods
    def _extract_profiles(self, root: Element) -> List[Dict[str, Any]]:
        profiles = []

        for profile in root.findall(".//{urn:jboss:domain:*}profile"):
            profile_info = {"name": profile.get("name"), "subsystems": []}

            # Count subsystems
            for subsystem in profile.findall(".//{urn:jboss:domain:*}subsystem"):
                profile_info["subsystems"].append(subsystem.tag.split("}")[-1])

            profiles.append(profile_info)

        return profiles

    def _analyze_subsystems(self, root: Element) -> Dict[str, Any]:
        subsystems = {}

        # Common subsystems to look for
        subsystem_patterns = [
            "datasources",
            "security",
            "web",
            "ejb3",
            "transactions",
            "messaging",
            "logging",
            "deployment-scanner",
        ]

        for pattern in subsystem_patterns:
            elements = root.findall(f'.//*[local-name()="{pattern}"]')
            if elements:
                subsystems[pattern] = len(elements)

        return subsystems

    def _extract_interfaces(self, root: Element) -> List[Dict[str, str]]:
        interfaces = []

        for interface in root.findall('.//*[local-name()="interface"]'):
            interfaces.append(
                {
                    "name": interface.get("name"),
                    "inet_address": (
                        interface.find('.//*[local-name()="inet-address"]').get(
                            "value", ""
                        )
                        if interface.find('.//*[local-name()="inet-address"]')
                        is not None
                        else ""
                    ),
                }
            )

        return interfaces

    def _extract_socket_bindings(self, root: Element) -> List[Dict[str, Any]]:
        bindings = []

        for binding in root.findall('.//*[local-name()="socket-binding"]'):
            bindings.append(
                {
                    "name": binding.get("name"),
                    "port": binding.get("port"),
                    "interface": binding.get("interface"),
                }
            )

        return bindings[:10]  # Limit to first 10

    def _extract_deployments(self, root: Element) -> List[Dict[str, str]]:
        deployments = []

        for deployment in root.findall('.//*[local-name()="deployment"]'):
            deployments.append(
                {
                    "name": deployment.get("name"),
                    "runtime_name": deployment.get(
                        "runtime-name", deployment.get("name")
                    ),
                }
            )

        return deployments

    def _extract_jboss_datasources(self, root: Element) -> List[Dict[str, Any]]:
        datasources = []

        for ds in root.findall('.//*[local-name()="datasource"]'):
            datasources.append(
                {
                    "jndi_name": ds.get("jndi-name"),
                    "pool_name": ds.get("pool-name"),
                    "enabled": ds.get("enabled", "true") == "true",
                    "driver": (
                        ds.find('.//*[local-name()="driver"]').text
                        if ds.find('.//*[local-name()="driver"]') is not None
                        else None
                    ),
                }
            )

        return datasources

    # Generic analysis methods
    def _analyze_structure(self, root: Element) -> Dict[str, Any]:
        return {
            "root_element": root.tag,
            "total_elements": len(list(root.iter())),
            "max_depth": self._calculate_max_depth(root),
            "unique_tags": len(set(elem.tag for elem in root.iter())),
        }

    def _find_security_elements(self, root: Element) -> List[Dict[str, Any]]:
        security_elements = []
        security_keywords = [
            "security",
            "auth",
            "role",
            "permission",
            "credential",
            "password",
            "realm",
        ]

        for elem in root.iter():
            tag_lower = elem.tag.lower()
            if any(keyword in tag_lower for keyword in security_keywords):
                security_elements.append(
                    {
                        "tag": elem.tag,
                        "attributes": dict(elem.attrib),
                        "has_sensitive_data": self._check_sensitive_data(elem),
                    }
                )

        return security_elements[:20]  # Limit results

    def _find_connection_settings(self, root: Element) -> List[Dict[str, Any]]:
        connections = []
        connection_keywords = [
            "connection",
            "datasource",
            "pool",
            "jdbc",
            "url",
            "host",
            "port",
        ]

        for elem in root.iter():
            tag_lower = elem.tag.lower()
            if any(keyword in tag_lower for keyword in connection_keywords):
                connections.append({"tag": elem.tag, "attributes": dict(elem.attrib)})

        return connections[:15]

    def _find_resource_pools(self, root: Element) -> List[Dict[str, Any]]:
        pools = []
        pool_keywords = ["pool", "max-size", "min-size", "timeout"]

        for elem in root.iter():
            if any(
                keyword in elem.tag.lower() or keyword in str(elem.attrib).lower()
                for keyword in pool_keywords
            ):
                pools.append({"tag": elem.tag, "configuration": dict(elem.attrib)})

        return pools

    def _find_deployment_settings(self, root: Element) -> Dict[str, Any]:
        deployment_info = {"contexts": [], "applications": [], "modules": []}

        # Look for context paths
        for elem in root.iter():
            if "context" in elem.tag.lower() and elem.get("path"):
                deployment_info["contexts"].append(elem.get("path"))
            elif "application" in elem.tag.lower() and elem.get("name"):
                deployment_info["applications"].append(elem.get("name"))
            elif "module" in elem.tag.lower() and elem.get("name"):
                deployment_info["modules"].append(elem.get("name"))

        return deployment_info

    # Utility methods
    def _determine_config_type(self, root: Element) -> str:
        """Determine the specific configuration type"""
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "web-app":
            return "Java EE Web Application Deployment Descriptor"
        elif root_tag == "Server":
            return "Tomcat Server Configuration"
        elif root_tag == "Context":
            return "Tomcat Context Configuration"
        elif "jboss" in root.tag:
            return "JBoss/WildFly Configuration"
        else:
            return "Enterprise Application Configuration"

    def _guess_file_type(self, root: Element, namespaces: Dict[str, str]) -> str:
        """Guess the configuration file type"""
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "web-app":
            return "web.xml"
        elif root_tag == "Server":
            return "server.xml"
        elif root_tag == "Context":
            return "context.xml"
        elif "jboss" in str(namespaces.values()):
            return "standalone.xml"
        else:
            return "config.xml"

    def _get_child_text(self, parent: Element, child_name: str) -> Optional[str]:
        """Get text content of a child element"""
        child = parent.find(f".//{child_name}")
        if child is None:
            # Try with common namespaces
            for ns in [
                "{http://java.sun.com/xml/ns/javaee}",
                "{http://xmlns.jcp.org/xml/ns/javaee}",
            ]:
                child = parent.find(f".//{ns}{child_name}")
                if child is not None:
                    break

        return child.text if child is not None else None

    def _extract_init_params(self, parent: Element) -> Dict[str, str]:
        """Extract init parameters"""
        params = {}

        for param in parent.findall(".//init-param"):
            name = self._get_child_text(param, "param-name")
            value = self._get_child_text(param, "param-value")
            if name and value:
                params[name] = value

        return params

    def _extract_context_params(self, root: Element) -> Dict[str, str]:
        """Extract context parameters"""
        params = {}

        for param in root.findall(".//context-param"):
            name = self._get_child_text(param, "param-name")
            value = self._get_child_text(param, "param-value")
            if name and value:
                params[name] = value

        return params

    def _extract_error_pages(self, root: Element) -> List[Dict[str, str]]:
        """Extract error page mappings"""
        error_pages = []

        for page in root.findall(".//error-page"):
            page_info = {}

            error_code = self._get_child_text(page, "error-code")
            exception_type = self._get_child_text(page, "exception-type")
            location = self._get_child_text(page, "location")

            if error_code:
                page_info["error_code"] = error_code
            if exception_type:
                page_info["exception_type"] = exception_type
            if location:
                page_info["location"] = location

            if page_info:
                error_pages.append(page_info)

        return error_pages

    def _extract_welcome_files(self, root: Element) -> List[str]:
        """Extract welcome file list"""
        welcome_files = []

        welcome_list = root.find(".//welcome-file-list")
        if welcome_list is not None:
            for file_elem in welcome_list.findall(".//welcome-file"):
                if file_elem.text:
                    welcome_files.append(file_elem.text)

        return welcome_files

    def _extract_session_config(self, root: Element) -> Dict[str, Any]:
        """Extract session configuration"""
        session_config = {}

        config = root.find(".//session-config")
        if config is not None:
            timeout = self._get_child_text(config, "session-timeout")
            if timeout:
                session_config["timeout_minutes"] = timeout

            # Cookie config
            cookie_config = config.find(".//cookie-config")
            if cookie_config is not None:
                session_config["cookie"] = {
                    "name": self._get_child_text(cookie_config, "name"),
                    "domain": self._get_child_text(cookie_config, "domain"),
                    "path": self._get_child_text(cookie_config, "path"),
                    "secure": self._get_child_text(cookie_config, "secure") == "true",
                    "http_only": self._get_child_text(cookie_config, "http-only")
                    == "true",
                }

        return session_config

    def _extract_form_config(self, login_config: Element) -> Optional[Dict[str, str]]:
        """Extract form login configuration"""
        form_config = login_config.find(".//form-login-config")
        if form_config is not None:
            return {
                "login_page": self._get_child_text(form_config, "form-login-page"),
                "error_page": self._get_child_text(form_config, "form-error-page"),
            }
        return None

    def _extract_server_info(self, root: Element) -> Dict[str, Any]:
        """Extract server-level information"""
        server = root

        return {
            "port": server.get("port", "8005"),
            "shutdown": server.get("shutdown", "SHUTDOWN"),
            "services": len(server.findall(".//Service")),
        }

    def _extract_security_settings(self, root: Element) -> Dict[str, Any]:
        """Extract security-related settings"""
        return {
            "security_constraints": len(root.findall(".//security-constraint")),
            "security_roles": [r.text for r in root.findall(".//role-name") if r.text],
            "auth_methods": list(
                set(m.text for m in root.findall(".//auth-method") if m.text)
            ),
            "ssl_enabled": any(
                c.get("SSLEnabled") == "true" for c in root.findall(".//Connector")
            ),
        }

    def _extract_resources(self, root: Element) -> List[Dict[str, Any]]:
        """Extract resource definitions"""
        resources = []

        # Standard resources
        for resource in root.findall(".//Resource"):
            resources.append(
                {
                    "name": resource.get("name"),
                    "type": resource.get("type"),
                    "auth": resource.get("auth"),
                }
            )

        # DataSources
        for ds in root.findall(".//DataSource"):
            resources.append(
                {
                    "name": ds.get("name"),
                    "type": "DataSource",
                    "jndi_name": ds.get("jndiName"),
                }
            )

        return resources[:20]  # Limit

    def _extract_deployment_info(self, root: Element) -> Dict[str, Any]:
        """Extract deployment-related information"""
        return {
            "contexts": [
                c.get("path") for c in root.findall(".//Context") if c.get("path")
            ],
            "web_apps": [
                w.get("docBase") for w in root.findall(".//Context") if w.get("docBase")
            ],
            "auto_deploy": any(
                h.get("autoDeploy") == "true" for h in root.findall(".//Host")
            ),
        }

    def _extract_servlets(self, root: Element) -> List[Dict[str, str]]:
        """Extract servlet definitions"""
        servlets = []

        for servlet in root.findall(".//servlet"):
            servlets.append(
                {
                    "name": self._get_child_text(servlet, "servlet-name"),
                    "class": self._get_child_text(servlet, "servlet-class"),
                    "load_on_startup": self._get_child_text(servlet, "load-on-startup"),
                }
            )

        return servlets[:20]

    def _extract_filters(self, root: Element) -> List[Dict[str, str]]:
        """Extract filter definitions"""
        filters = []

        for filter_elem in root.findall(".//filter"):
            filters.append(
                {
                    "name": self._get_child_text(filter_elem, "filter-name"),
                    "class": self._get_child_text(filter_elem, "filter-class"),
                }
            )

        return filters[:20]

    def _extract_connectors(self, root: Element) -> List[Dict[str, Any]]:
        """Extract connector configurations"""
        connectors = []

        for connector in root.findall(".//Connector"):
            connectors.append(
                {
                    "port": connector.get("port"),
                    "protocol": connector.get("protocol"),
                    "secure": connector.get("secure") == "true",
                    "ssl_enabled": connector.get("SSLEnabled") == "true",
                }
            )

        return connectors

    def _extract_hosts(self, root: Element) -> List[Dict[str, str]]:
        """Extract host configurations"""
        hosts = []

        for host in root.findall(".//Host"):
            hosts.append(
                {
                    "name": host.get("name"),
                    "app_base": host.get("appBase"),
                    "auto_deploy": host.get("autoDeploy"),
                }
            )

        return hosts

    def _calculate_max_depth(self, elem: Element, depth: int = 0) -> int:
        """Calculate maximum depth of XML tree"""
        if not list(elem):
            return depth
        return max(self._calculate_max_depth(child, depth + 1) for child in elem)

    def _check_sensitive_data(self, elem: Element) -> bool:
        """Check if element might contain sensitive data"""
        sensitive_keywords = ["password", "secret", "key", "token", "credential"]

        # Check tag name
        if any(keyword in elem.tag.lower() for keyword in sensitive_keywords):
            return True

        # Check attributes
        for attr_name, attr_value in elem.attrib.items():
            if any(keyword in attr_name.lower() for keyword in sensitive_keywords):
                return True
            # Check for non-empty password values
            if "password" in attr_name.lower() and attr_value and attr_value != "*":
                return True

        return False

    def _create_inventory(self, findings: Dict[str, Any]) -> Dict[str, int]:
        """Create data inventory from findings"""
        inventory = {}

        # Count various elements based on findings structure
        if "servlets" in findings:
            inventory["servlets"] = len(findings["servlets"])
        if "filters" in findings:
            inventory["filters"] = len(findings["filters"])
        if "connectors" in findings:
            inventory["connectors"] = len(findings["connectors"])
        if "datasources" in findings:
            inventory["datasources"] = len(findings["datasources"])
        if "security" in findings and "constraints" in findings["security"]:
            inventory["security_constraints"] = len(findings["security"]["constraints"])

        return inventory

    def _assess_config_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess configuration quality"""
        scores = {}

        # Security score
        security_score = 0.0
        if "security" in findings:
            if findings["security"].get("constraints"):
                security_score += 0.3
            if findings["security"].get("login_config"):
                security_score += 0.3
            if findings["security"].get("roles"):
                security_score += 0.2
            # Check for HTTPS
            if "connectors" in findings:
                if any(
                    c.get("secure") or c.get("ssl_enabled")
                    for c in findings["connectors"]
                ):
                    security_score += 0.2
        scores["security"] = min(security_score, 1.0)

        # Configuration completeness
        completeness = 0.0
        expected_elements = ["servlets", "security", "session_config", "error_pages"]
        for element in expected_elements:
            if element in findings and findings[element]:
                completeness += 0.25
        scores["completeness"] = completeness

        # Best practices
        best_practices = 0.0

        # Check session timeout
        if "session_config" in findings and findings["session_config"].get(
            "timeout_minutes"
        ):
            best_practices += 0.25

        # Check error handling
        if "error_pages" in findings and len(findings["error_pages"]) > 0:
            best_practices += 0.25

        # Check for secure cookies
        if "session_config" in findings and "cookie" in findings["session_config"]:
            cookie = findings["session_config"]["cookie"]
            if cookie.get("secure") and cookie.get("http_only"):
                best_practices += 0.5

        scores["best_practices"] = best_practices

        # Overall quality
        scores["overall"] = sum(scores.values()) / len(scores)

        return scores
