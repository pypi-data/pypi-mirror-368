#!/usr/bin/env python3
"""
Maven POM (Project Object Model) Handler

Analyzes Maven POM files for dependency management, build configuration,
and project structure analysis. Supports extraction of project metadata,
dependencies, plugins, and build configurations for software composition
analysis and security assessments.
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


class MavenPOMHandler(XMLHandler):
    """Handler for Maven Project Object Model (POM) files"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check if root is 'project' and has Maven namespace
        if root.tag == "project" or root.tag.endswith("}project"):
            if "maven.apache.org" in str(namespaces.values()):
                return True, 1.0
            # Even without namespace, if it has Maven-like structure
            if (
                root.find(".//groupId") is not None
                and root.find(".//artifactId") is not None
            ):
                return True, 0.8
        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        pom_version = root.find(".//modelVersion")
        version = pom_version.text if pom_version is not None else "4.0.0"

        return DocumentTypeInfo(
            type_name="Maven POM",
            confidence=1.0,
            version=version,
            schema_uri="http://maven.apache.org/POM/4.0.0",
            metadata={"build_tool": "Maven", "category": "build_configuration"},
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "project_info": self._extract_project_info(root),
            "dependencies": self._analyze_dependencies(root),
            "plugins": self._analyze_plugins(root),
            "repositories": self._extract_repositories(root),
            "properties": self._extract_properties(root),
        }

        recommendations = [
            "Analyze dependency tree for security vulnerabilities",
            "Check for outdated dependencies",
            "Extract for software composition analysis",
            "Monitor for license compliance",
        ]

        ai_use_cases = [
            "Dependency vulnerability detection",
            "License compliance checking",
            "Technical debt analysis",
            "Build optimization recommendations",
            "Dependency update suggestions",
        ]

        data_inventory = {
            "dependencies": len(findings["dependencies"]["all"]),
            "plugins": len(findings["plugins"]),
            "properties": len(findings["properties"]),
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
            quality_metrics=self._calculate_pom_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "coordinates": {
                "groupId": getattr(root.find(".//groupId"), "text", None),
                "artifactId": getattr(root.find(".//artifactId"), "text", None),
                "version": getattr(root.find(".//version"), "text", None),
                "packaging": getattr(root.find(".//packaging"), "text", "jar"),
            },
            "dependencies": self._extract_dependency_list(root),
            "build_config": self._extract_build_config(root),
        }

    def _extract_project_info(self, root: Element) -> Dict[str, Any]:
        return {
            "name": getattr(root.find(".//name"), "text", None),
            "description": getattr(root.find(".//description"), "text", None),
            "url": getattr(root.find(".//url"), "text", None),
            "parent": self._extract_parent_info(root),
        }

    def _analyze_dependencies(self, root: Element) -> Dict[str, Any]:
        deps = root.findall(".//dependency")

        scopes = {}
        for dep in deps:
            scope = getattr(dep.find(".//scope"), "text", "compile")
            scopes[scope] = scopes.get(scope, 0) + 1

        return {
            "all": [self._extract_dependency(d) for d in deps],
            "count": len(deps),
            "by_scope": scopes,
            "management": len(root.findall(".//dependencyManagement//dependency")),
        }

    def _analyze_plugins(self, root: Element) -> List[Dict[str, str]]:
        plugins = []
        for plugin in root.findall(".//plugin"):
            plugins.append(
                {
                    "groupId": getattr(
                        plugin.find(".//groupId"), "text", "org.apache.maven.plugins"
                    ),
                    "artifactId": getattr(plugin.find(".//artifactId"), "text", None),
                    "version": getattr(plugin.find(".//version"), "text", None),
                }
            )
        return plugins

    def _extract_repositories(self, root: Element) -> List[Dict[str, str]]:
        repos = []
        for repo in root.findall(".//repository"):
            repos.append(
                {
                    "id": getattr(repo.find(".//id"), "text", None),
                    "url": getattr(repo.find(".//url"), "text", None),
                }
            )
        return repos

    def _extract_properties(self, root: Element) -> Dict[str, str]:
        props = {}
        properties = root.find(".//properties")
        if properties is not None:
            for prop in properties:
                props[prop.tag] = prop.text
        return props

    def _extract_parent_info(self, root: Element) -> Optional[Dict[str, str]]:
        parent = root.find(".//parent")
        if parent is None:
            return None
        return {
            "groupId": getattr(parent.find(".//groupId"), "text", None),
            "artifactId": getattr(parent.find(".//artifactId"), "text", None),
            "version": getattr(parent.find(".//version"), "text", None),
        }

    def _extract_dependency(self, dep: Element) -> Dict[str, str]:
        return {
            "groupId": getattr(dep.find(".//groupId"), "text", None),
            "artifactId": getattr(dep.find(".//artifactId"), "text", None),
            "version": getattr(dep.find(".//version"), "text", None),
            "scope": getattr(dep.find(".//scope"), "text", "compile"),
        }

    def _extract_dependency_list(self, root: Element) -> List[Dict[str, str]]:
        return [self._extract_dependency(d) for d in root.findall(".//dependency")[:20]]

    def _extract_build_config(self, root: Element) -> Dict[str, Any]:
        build = root.find(".//build")
        if build is None:
            return {}

        return {
            "sourceDirectory": getattr(build.find(".//sourceDirectory"), "text", None),
            "outputDirectory": getattr(build.find(".//outputDirectory"), "text", None),
            "finalName": getattr(build.find(".//finalName"), "text", None),
        }

    def _calculate_pom_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        has_description = 1.0 if findings["project_info"]["description"] else 0.0
        has_url = 1.0 if findings["project_info"]["url"] else 0.0
        deps_with_version = sum(
            1 for d in findings["dependencies"]["all"] if d.get("version")
        )
        total_deps = len(findings["dependencies"]["all"])

        return {
            "completeness": (has_description + has_url) / 2,
            "dependency_management": (
                deps_with_version / total_deps if total_deps > 0 else 1.0
            ),
            "best_practices": (
                0.8 if findings["dependencies"]["management"] > 0 else 0.4
            ),
        }
