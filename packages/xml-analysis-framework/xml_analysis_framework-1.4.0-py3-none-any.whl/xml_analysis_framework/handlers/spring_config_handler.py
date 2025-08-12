#!/usr/bin/env python3
"""
Spring Framework XML Configuration Handler

Analyzes Spring Framework XML configuration files including bean definitions,
dependency injection configurations, and application context files. Supports
extraction of beans, profiles, property sources, and various Spring features
like AOP, security, and transaction management.
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


class SpringConfigHandler(XMLHandler):
    """Handler for Spring Framework XML configuration files"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for Spring namespaces
        spring_indicators = [
            "springframework.org/schema/beans",
            "springframework.org/schema/context",
            "springframework.org/schema/mvc",
        ]

        if any(ind in str(namespaces.values()) for ind in spring_indicators):
            return True, 1.0

        # Check for beans root element
        if root.tag == "beans" or root.tag.endswith("}beans"):
            return True, 0.7

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Detect Spring version from schema
        version = "5.x"  # Default
        for uri in namespaces.values():
            if "springframework.org/schema" in uri:
                version_match = re.search(r"/(\d+\.\d+)\.xsd", uri)
                if version_match:
                    version = version_match.group(1)
                    break

        return DocumentTypeInfo(
            type_name="Spring Configuration",
            confidence=1.0,
            version=version,
            metadata={
                "framework": "Spring Framework",
                "category": "dependency_injection",
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "beans": self._analyze_beans(root),
            "profiles": self._extract_profiles(root),
            "imports": self._extract_imports(root),
            "property_sources": self._extract_property_sources(root),
            "aop_config": self._check_aop_usage(root),
            "security_config": self._check_security_config(root),
        }

        recommendations = [
            "Review bean dependencies for circular references",
            "Check for hardcoded values that should be externalized",
            "Validate security configurations",
            "Consider migrating to annotation-based config",
        ]

        ai_use_cases = [
            "Dependency graph visualization",
            "Security misconfiguration detection",
            "Migration to modern Spring Boot",
            "Configuration optimization",
            "Circular dependency detection",
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
                "beans": len(findings["beans"]["all"]),
                "profiles": len(findings["profiles"]),
                "property_sources": len(findings["property_sources"]),
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_spring_config_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "bean_definitions": self._extract_bean_definitions(root),
            "component_scans": self._extract_component_scans(root),
            "configurations": self._extract_configurations(root),
        }

    def _analyze_beans(
        self, root: Element, namespaces: Dict[str, str] = None
    ) -> Dict[str, Any]:
        beans = []
        bean_classes = {}

        for bean in root.findall(".//*[@id]"):
            if bean.tag.endswith("bean") or bean.tag == "bean":
                bean_info = {
                    "id": bean.get("id"),
                    "class": bean.get("class"),
                    "scope": bean.get("scope", "singleton"),
                    "lazy": bean.get("lazy-init", "false"),
                    "parent": bean.get("parent"),
                }
                beans.append(bean_info)

                # Count bean classes
                if bean_info["class"]:
                    bean_classes[bean_info["class"]] = (
                        bean_classes.get(bean_info["class"], 0) + 1
                    )

        return {
            "all": beans,
            "count": len(beans),
            "by_scope": self._count_by_attribute(beans, "scope"),
            "lazy_count": sum(1 for b in beans if b["lazy"] == "true"),
            "common_classes": {k: v for k, v in bean_classes.items() if v > 1},
        }

    def _extract_profiles(self, root: Element) -> List[str]:
        profiles = set()

        for elem in root.findall(".//*[@profile]"):
            profile = elem.get("profile")
            if profile:
                # Handle multiple profiles
                for p in profile.split(","):
                    profiles.add(p.strip())

        return list(profiles)

    def _extract_imports(self, root: Element) -> List[str]:
        imports = []

        for imp in root.findall(".//import"):
            resource = imp.get("resource")
            if resource:
                imports.append(resource)

        return imports

    def _extract_property_sources(self, root: Element) -> List[Dict[str, str]]:
        sources = []

        # Look for property placeholder configurers
        for elem in root.findall(".//*"):
            if "PropertyPlaceholderConfigurer" in elem.get("class", ""):
                location = elem.find('.//property[@name="location"]')
                if location is not None:
                    sources.append(
                        {"type": "properties", "location": location.get("value")}
                    )

        return sources

    def _check_aop_usage(self, root: Element) -> bool:
        # Check for AOP namespace or AOP-related beans
        for elem in root.iter():
            if "aop" in elem.tag or "aspectj" in elem.tag.lower():
                return True
        return False

    def _check_security_config(self, root: Element) -> Dict[str, Any]:
        security = {"present": False, "authentication": False, "authorization": False}

        for elem in root.iter():
            if "security" in elem.tag:
                security["present"] = True
            if "authentication" in elem.tag:
                security["authentication"] = True
            if "authorization" in elem.tag or "access" in elem.tag:
                security["authorization"] = True

        return security

    def _extract_bean_definitions(self, root: Element) -> List[Dict[str, Any]]:
        # Simplified version - full implementation would extract all properties
        return self._analyze_beans(root)["all"][:20]  # First 20 beans

    def _extract_component_scans(self, root: Element) -> List[str]:
        scans = []

        for scan in root.findall(".//*component-scan"):
            base_package = scan.get("base-package")
            if base_package:
                scans.append(base_package)

        return scans

    def _extract_configurations(self, root: Element) -> Dict[str, Any]:
        return {
            "transaction_management": self._check_transaction_config(root),
            "caching": self._check_cache_config(root),
            "scheduling": self._check_scheduling_config(root),
        }

    def _check_transaction_config(self, root: Element) -> bool:
        return any("transaction" in elem.tag for elem in root.iter())

    def _check_cache_config(self, root: Element) -> bool:
        return any("cache" in elem.tag for elem in root.iter())

    def _check_scheduling_config(self, root: Element) -> bool:
        return any(
            "task" in elem.tag or "scheduling" in elem.tag for elem in root.iter()
        )

    def _count_by_attribute(self, items: List[Dict], attr: str) -> Dict[str, int]:
        counts = {}
        for item in items:
            value = item.get(attr)
            if value:
                counts[value] = counts.get(value, 0) + 1
        return counts

    def _assess_spring_config_quality(
        self, findings: Dict[str, Any]
    ) -> Dict[str, float]:
        # Assess configuration quality
        beans = findings["beans"]

        # Check for good practices
        uses_profiles = len(findings["profiles"]) > 0
        externalizes_config = len(findings["property_sources"]) > 0
        reasonable_bean_count = (
            beans["count"] < 100
        )  # Large XML configs are hard to maintain

        return {
            "maintainability": 0.8 if reasonable_bean_count else 0.3,
            "flexibility": 1.0 if uses_profiles else 0.5,
            "configuration_management": 1.0 if externalizes_config else 0.4,
        }
