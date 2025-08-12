#!/usr/bin/env python3
"""
Ivy Handler

Analyzes Apache Ivy dependency management files for dependency analysis,
security scanning, license compliance, and build optimization.
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


class IvyHandler(XMLHandler):
    """Handler for Apache Ivy dependency management files"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for Ivy root elements
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # Primary Ivy file types
        if root_tag == "ivy-module":
            confidence = 0.8

            # Check for required attributes
            if root.get("version"):
                confidence += 0.1

            # Check for info element
            if self._find_element_by_local_name(root, "info") is not None:
                confidence += 0.1

            return True, confidence

        # Ivy settings files
        elif root_tag == "ivysettings":
            confidence = 0.9
            return True, confidence

        # Check for Ivy-specific patterns in any XML
        ivy_indicators = [
            "ivy-module",
            "dependencies",
            "dependency",
            "publications",
            "artifact",
        ]
        indicator_count = sum(
            1
            for indicator in ivy_indicators
            if any(indicator in elem.tag for elem in root.iter())
        )

        if indicator_count >= 3:  # Multiple Ivy indicators
            return True, min(0.6 + (indicator_count * 0.1), 1.0)

        # Check for Ivy namespace or attributes
        if any("ivy" in str(value).lower() for value in namespaces.values()):
            return True, 0.7

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # Determine file type
        if root_tag == "ivy-module":
            file_type = "Module Descriptor"
            category = "ivy_module"
        elif root_tag == "ivysettings":
            file_type = "Settings"
            category = "ivy_settings"
        else:
            file_type = "Module Descriptor"  # Default
            category = "ivy_unknown"

        # Extract module information
        module_info = self._extract_module_info(root)

        metadata = {
            "tool": "Apache Ivy",
            "category": category,
            "file_type": file_type,
            "module_organization": module_info.get("organisation"),
            "module_name": module_info.get("module"),
            "module_revision": module_info.get("revision"),
            "dependency_count": self._count_dependencies(root),
            "publication_count": self._count_publications(root),
        }

        return DocumentTypeInfo(
            type_name=f"Ivy {file_type}",
            confidence=0.95,
            version=root.get("version", "2.0"),
            metadata=metadata,
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "ivy-module":
            findings = self._analyze_module(root)
        elif root_tag == "ivysettings":
            findings = self._analyze_settings(root)
        else:
            # Generic analysis
            findings = {
                "ivy_info": self._analyze_ivy_elements(root),
                "dependencies": self._analyze_dependencies(root),
                "publications": self._analyze_publications(root),
                "security": self._analyze_security(root),
            }

        recommendations = [
            "Review dependency versions for known security vulnerabilities",
            "Analyze transitive dependencies for license compliance",
            "Check for deprecated or unmaintained dependencies",
            "Validate repository URLs and accessibility",
            "Review artifact publication settings for security",
            "Analyze dependency conflicts and version ranges",
            "Check for circular dependency issues",
            "Validate module metadata and descriptions",
        ]

        ai_use_cases = [
            "Dependency vulnerability scanning and analysis",
            "License compliance auditing and reporting",
            "Build optimization and dependency management",
            "Security assessment of third-party libraries",
            "Dependency graph analysis and visualization",
            "Version conflict resolution and management",
            "Repository and artifact analysis",
            "Supply chain security monitoring",
            "Automated dependency updates and maintenance",
        ]

        # Calculate data inventory
        data_inventory = {}
        if "dependencies" in findings:
            data_inventory["dependencies"] = len(
                findings["dependencies"]["dependency_details"]
            )
        if "publications" in findings:
            data_inventory["publications"] = len(
                findings["publications"]["publication_details"]
            )
        if "configurations" in findings:
            data_inventory["configurations"] = len(
                findings["configurations"]["configuration_details"]
            )

        # Get document type info
        doc_type = self.detect_type(file_path, root=root, namespaces={})
        
        return SpecializedAnalysis(
            # From DocumentTypeInfo
            type_name=doc_type.type_name,
            confidence=doc_type.confidence,
            version=doc_type.version,
            schema_uri=doc_type.schema_uri,
            metadata=doc_type.metadata,
            # Analysis fields {}).get('file_type', 'Module')}",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory=data_inventory,
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_ivy_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "module_metadata": {
                "version": root.get("version", "2.0"),
                "file_type": self._determine_file_type(root),
                "module_info": self._extract_module_info(root),
            },
            "dependency_summary": self._extract_dependency_summary(root),
            "publication_summary": self._extract_publication_summary(root),
            "configuration_summary": self._extract_configuration_summary(root),
        }

    def _analyze_module(self, root: Element) -> Dict[str, Any]:
        """Analyze Ivy module descriptor"""
        findings = {
            "ivy_info": {
                "file_type": "Module Descriptor",
                "version": root.get("version", "2.0"),
            },
            "module_info": self._analyze_module_info(root),
            "configurations": self._analyze_configurations(root),
            "publications": self._analyze_publications(root),
            "dependencies": self._analyze_dependencies(root),
            "conflicts": self._analyze_conflicts(root),
            "security": self._analyze_module_security(root),
            "repositories": self._analyze_repositories(root),
        }
        return findings

    def _analyze_settings(self, root: Element) -> Dict[str, Any]:
        """Analyze Ivy settings file"""
        findings = {
            "ivy_info": {
                "file_type": "Settings",
                "version": root.get("version", "2.0"),
            },
            "settings": self._analyze_ivy_settings(root),
            "resolvers": self._analyze_resolvers(root),
            "modules": self._analyze_module_settings(root),
            "security": self._analyze_settings_security(root),
        }
        return findings

    def _extract_module_info(self, root: Element) -> Dict[str, Any]:
        """Extract basic module information"""
        info = self._find_element_by_local_name(root, "info")
        if info is not None:
            return {
                "organisation": info.get("organisation"),
                "module": info.get("module"),
                "revision": info.get("revision"),
                "status": info.get("status"),
                "publication": info.get("publication"),
                "description": self._get_element_text(
                    self._find_element_by_local_name(info, "description")
                ),
            }
        return {}

    def _analyze_module_info(self, root: Element) -> Dict[str, Any]:
        """Analyze module information section"""
        module_info = {
            "has_info": False,
            "organisation": None,
            "module": None,
            "revision": None,
            "status": None,
            "publication_date": None,
            "description": None,
            "license": None,
            "homepage": None,
            "authors": [],
        }

        info = self._find_element_by_local_name(root, "info")
        if info is not None:
            module_info["has_info"] = True
            module_info["organisation"] = info.get("organisation")
            module_info["module"] = info.get("module")
            module_info["revision"] = info.get("revision")
            module_info["status"] = info.get("status")
            module_info["publication_date"] = info.get("publication")

            # Extract description
            desc = self._find_element_by_local_name(info, "description")
            if desc is not None:
                module_info["description"] = desc.text

            # Extract license
            license_elem = self._find_element_by_local_name(info, "license")
            if license_elem is not None:
                module_info["license"] = {
                    "name": license_elem.get("name"),
                    "url": license_elem.get("url"),
                }

            # Extract homepage
            homepage = self._find_element_by_local_name(info, "ivyauthor")
            if homepage is not None:
                module_info["homepage"] = homepage.get("url")

            # Extract authors
            for author in info.iter():
                if author.tag.split("}")[-1] == "ivyauthor":
                    author_info = {"name": author.get("name"), "url": author.get("url")}
                    module_info["authors"].append(author_info)

        return module_info

    def _analyze_configurations(self, root: Element) -> Dict[str, Any]:
        """Analyze configuration definitions"""
        config_info = {
            "configuration_count": 0,
            "configuration_details": [],
            "default_configuration": None,
            "extends_relationships": [],
        }

        configurations = self._find_element_by_local_name(root, "configurations")
        if configurations is not None:
            config_info["default_configuration"] = configurations.get(
                "defaultconfmapping"
            )

            for conf in configurations.iter():
                if conf.tag.split("}")[-1] == "conf":
                    conf_detail = {
                        "name": conf.get("name"),
                        "description": conf.get("description"),
                        "visibility": conf.get("visibility", "public"),
                        "extends": conf.get("extends"),
                        "deprecated": conf.get("deprecated"),
                    }

                    config_info["configuration_details"].append(conf_detail)
                    config_info["configuration_count"] += 1

                    if conf_detail["extends"]:
                        config_info["extends_relationships"].append(
                            {
                                "child": conf_detail["name"],
                                "parent": conf_detail["extends"],
                            }
                        )

        return config_info

    def _analyze_publications(self, root: Element) -> Dict[str, Any]:
        """Analyze publication artifacts"""
        pub_info = {
            "publication_count": 0,
            "publication_details": [],
            "artifact_types": {},
            "configurations_published": [],
        }

        publications = self._find_element_by_local_name(root, "publications")
        if publications is not None:
            for artifact in publications.iter():
                if artifact.tag.split("}")[-1] == "artifact":
                    artifact_detail = {
                        "name": artifact.get("name"),
                        "type": artifact.get("type", "jar"),
                        "ext": artifact.get("ext"),
                        "conf": artifact.get("conf"),
                        "url": artifact.get("url"),
                        "classifier": artifact.get("classifier"),
                    }

                    pub_info["publication_details"].append(artifact_detail)
                    pub_info["publication_count"] += 1

                    # Count artifact types
                    artifact_type = artifact_detail["type"]
                    pub_info["artifact_types"][artifact_type] = (
                        pub_info["artifact_types"].get(artifact_type, 0) + 1
                    )

                    # Track configurations
                    if artifact_detail["conf"]:
                        configs = artifact_detail["conf"].split(",")
                        pub_info["configurations_published"].extend(configs)

        # Remove duplicates from configurations
        pub_info["configurations_published"] = list(
            set(pub_info["configurations_published"])
        )

        return pub_info

    def _analyze_dependencies(self, root: Element) -> Dict[str, Any]:
        """Analyze dependency declarations"""
        dep_info = {
            "dependency_count": 0,
            "dependency_details": [],
            "organizations": [],
            "version_patterns": {"fixed": 0, "ranges": 0, "dynamic": 0, "latest": 0},
            "transitive_disabled": 0,
            "optional_dependencies": 0,
        }

        dependencies = self._find_element_by_local_name(root, "dependencies")
        if dependencies is not None:
            for dep in dependencies.iter():
                if dep.tag.split("}")[-1] == "dependency":
                    dep_detail = {
                        "org": dep.get("org"),
                        "name": dep.get("name"),
                        "rev": dep.get("rev"),
                        "conf": dep.get("conf"),
                        "transitive": dep.get("transitive", "true") == "true",
                        "changing": dep.get("changing", "false") == "true",
                        "force": dep.get("force", "false") == "true",
                        "branch": dep.get("branch"),
                        "artifacts": [],
                        "excludes": [],
                    }

                    # Analyze version pattern
                    version = dep_detail["rev"]
                    if version:
                        if "+" in version or "latest" in version.lower():
                            if "latest" in version.lower():
                                dep_info["version_patterns"]["latest"] += 1
                            else:
                                dep_info["version_patterns"]["dynamic"] += 1
                        elif "[" in version or "(" in version:
                            dep_info["version_patterns"]["ranges"] += 1
                        else:
                            dep_info["version_patterns"]["fixed"] += 1

                    # Count transitive and optional
                    if not dep_detail["transitive"]:
                        dep_info["transitive_disabled"] += 1

                    # Extract artifacts
                    for artifact in dep:
                        if artifact.tag.split("}")[-1] == "artifact":
                            artifact_info = {
                                "name": artifact.get("name"),
                                "type": artifact.get("type"),
                                "ext": artifact.get("ext"),
                                "conf": artifact.get("conf"),
                            }
                            dep_detail["artifacts"].append(artifact_info)

                    # Extract excludes
                    for exclude in dep:
                        if exclude.tag.split("}")[-1] == "exclude":
                            exclude_info = {
                                "org": exclude.get("org"),
                                "module": exclude.get("module"),
                                "name": exclude.get("name"),
                                "type": exclude.get("type"),
                                "ext": exclude.get("ext"),
                                "conf": exclude.get("conf"),
                            }
                            dep_detail["excludes"].append(exclude_info)

                    dep_info["dependency_details"].append(dep_detail)
                    dep_info["dependency_count"] += 1

                    # Track organizations
                    if (
                        dep_detail["org"]
                        and dep_detail["org"] not in dep_info["organizations"]
                    ):
                        dep_info["organizations"].append(dep_detail["org"])

        return dep_info

    def _analyze_conflicts(self, root: Element) -> Dict[str, Any]:
        """Analyze conflict resolution settings"""
        conflict_info = {"conflict_managers": [], "default_conflict_manager": None}

        # Look for conflict managers in dependencies
        dependencies = self._find_element_by_local_name(root, "dependencies")
        if dependencies is not None:
            conflict_info["default_conflict_manager"] = dependencies.get(
                "defaultconfmapping"
            )

            for manager in dependencies.iter():
                if manager.tag.split("}")[-1] == "conflict":
                    manager_info = {
                        "org": manager.get("org"),
                        "module": manager.get("module"),
                        "manager": manager.get("manager"),
                        "rev": manager.get("rev"),
                    }
                    conflict_info["conflict_managers"].append(manager_info)

        return conflict_info

    def _analyze_repositories(self, root: Element) -> Dict[str, Any]:
        """Analyze repository information (limited in module files)"""
        repo_info = {"repository_count": 0, "repository_urls": []}

        # In module files, repository info is usually minimal
        # Most repository configuration is in settings files
        for elem in root.iter():
            if "url" in elem.attrib:
                url = elem.get("url")
                if url and url.startswith("http"):
                    repo_info["repository_urls"].append(url)
                    repo_info["repository_count"] += 1

        return repo_info

    def _analyze_module_security(self, root: Element) -> Dict[str, Any]:
        """Analyze security aspects of module"""
        security_info = {
            "security_risks": [],
            "dynamic_versions": 0,
            "external_repositories": 0,
            "transitive_enabled_count": 0,
            "changing_dependencies": 0,
        }

        # Analyze dependencies for security risks
        dep_analysis = self._analyze_dependencies(root)

        # Count dynamic versions (security risk)
        security_info["dynamic_versions"] = (
            dep_analysis["version_patterns"]["dynamic"]
            + dep_analysis["version_patterns"]["latest"]
        )

        if security_info["dynamic_versions"] > 0:
            security_info["security_risks"].append(
                f'{security_info["dynamic_versions"]} dependencies use dynamic versions'
            )

        # Count changing dependencies
        security_info["changing_dependencies"] = sum(
            1
            for dep in dep_analysis["dependency_details"]
            if dep.get("changing", False)
        )

        if security_info["changing_dependencies"] > 0:
            security_info["security_risks"].append(
                f'{security_info["changing_dependencies"]} dependencies marked as changing'
            )

        # Count transitive dependencies
        security_info["transitive_enabled_count"] = sum(
            1
            for dep in dep_analysis["dependency_details"]
            if dep.get("transitive", True)
        )

        # Check for external URLs
        repo_analysis = self._analyze_repositories(root)
        security_info["external_repositories"] = len(
            [
                url
                for url in repo_analysis["repository_urls"]
                if not any(
                    safe in url for safe in ["localhost", "127.0.0.1", "internal"]
                )
            ]
        )

        if security_info["external_repositories"] > 0:
            security_info["security_risks"].append(
                f'{security_info["external_repositories"]} external repository URLs found'
            )

        return security_info

    def _analyze_ivy_settings(self, root: Element) -> Dict[str, Any]:
        """Analyze Ivy settings configuration"""
        settings_info = {
            "default_resolver": None,
            "default_conflict_manager": None,
            "validate": None,
            "check_exact_revision": None,
            "override_publish_dir": None,
        }

        # Extract settings attributes
        settings_info["default_resolver"] = root.get("defaultResolver")
        settings_info["default_conflict_manager"] = root.get("defaultConflictManager")
        settings_info["validate"] = root.get("validate")
        settings_info["check_exact_revision"] = root.get("checkExactRevision")

        return settings_info

    def _analyze_resolvers(self, root: Element) -> Dict[str, Any]:
        """Analyze resolver configurations"""
        resolver_info = {
            "resolver_count": 0,
            "resolver_details": [],
            "resolver_types": {},
        }

        resolvers = self._find_element_by_local_name(root, "resolvers")
        if resolvers is not None:
            for resolver in resolvers:
                resolver_name = resolver.tag.split("}")[-1]
                if resolver_name != "resolvers":  # Skip the parent element
                    resolver_detail = {
                        "type": resolver_name,
                        "name": resolver.get("name"),
                        "url": resolver.get("url"),
                        "pattern": resolver.get("pattern"),
                        "checkmodified": resolver.get("checkmodified"),
                        "changingPattern": resolver.get("changingPattern"),
                    }

                    resolver_info["resolver_details"].append(resolver_detail)
                    resolver_info["resolver_count"] += 1

                    # Count resolver types
                    resolver_info["resolver_types"][resolver_name] = (
                        resolver_info["resolver_types"].get(resolver_name, 0) + 1
                    )

        return resolver_info

    def _analyze_module_settings(self, root: Element) -> Dict[str, Any]:
        """Analyze module-specific settings"""
        module_settings = {"module_count": 0, "module_patterns": []}

        modules = self._find_element_by_local_name(root, "modules")
        if modules is not None:
            for module in modules:
                if module.tag.split("}")[-1] == "module":
                    pattern_info = {
                        "organisation": module.get("organisation"),
                        "name": module.get("name"),
                        "resolver": module.get("resolver"),
                        "conflict_manager": module.get("conflict-manager"),
                    }
                    module_settings["module_patterns"].append(pattern_info)
                    module_settings["module_count"] += 1

        return module_settings

    def _analyze_settings_security(self, root: Element) -> Dict[str, Any]:
        """Analyze security aspects of settings"""
        security_info = {
            "security_risks": [],
            "http_repositories": 0,
            "validation_disabled": False,
        }

        # Check validation settings
        if root.get("validate") == "false":
            security_info["validation_disabled"] = True
            security_info["security_risks"].append("Ivy validation is disabled")

        # Check for HTTP repositories (vs HTTPS)
        resolver_analysis = self._analyze_resolvers(root)
        for resolver in resolver_analysis["resolver_details"]:
            url = resolver.get("url")
            if url and url.startswith("http://"):
                security_info["http_repositories"] += 1

        if security_info["http_repositories"] > 0:
            security_info["security_risks"].append(
                f'{security_info["http_repositories"]} resolvers use insecure HTTP'
            )

        return security_info

    def _count_dependencies(self, root: Element) -> int:
        """Count number of dependencies"""
        count = 0
        for elem in root.iter():
            if elem.tag.split("}")[-1] == "dependency":
                count += 1
        return count

    def _count_publications(self, root: Element) -> int:
        """Count number of publications"""
        count = 0
        for elem in root.iter():
            if elem.tag.split("}")[-1] == "artifact":
                count += 1
        return count

    def _determine_file_type(self, root: Element) -> str:
        """Determine if this is a module or settings file"""
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "ivy-module":
            return "Module Descriptor"
        elif root_tag == "ivysettings":
            return "Settings"
        else:
            return "Module Descriptor"  # Default

    def _extract_dependency_summary(self, root: Element) -> Dict[str, Any]:
        """Extract dependency summary information"""
        dep_analysis = self._analyze_dependencies(root)
        return {
            "dependency_count": dep_analysis["dependency_count"],
            "organizations": dep_analysis["organizations"][:10],  # Limit to first 10
            "version_patterns": dep_analysis["version_patterns"],
            "transitive_disabled": dep_analysis["transitive_disabled"],
        }

    def _extract_publication_summary(self, root: Element) -> Dict[str, Any]:
        """Extract publication summary information"""
        pub_analysis = self._analyze_publications(root)
        return {
            "publication_count": pub_analysis["publication_count"],
            "artifact_types": pub_analysis["artifact_types"],
            "configurations_published": pub_analysis["configurations_published"][
                :5
            ],  # Limit to first 5
        }

    def _extract_configuration_summary(self, root: Element) -> Dict[str, Any]:
        """Extract configuration summary"""
        config_analysis = self._analyze_configurations(root)
        return {
            "configuration_count": config_analysis["configuration_count"],
            "default_configuration": config_analysis["default_configuration"],
            "extends_relationships": len(config_analysis["extends_relationships"]),
        }

    def _analyze_ivy_elements(self, root: Element) -> Dict[str, Any]:
        """Generic analysis of Ivy elements"""
        return {
            "file_type": self._determine_file_type(root),
            "version": root.get("version", "2.0"),
            "element_count": len(list(root.iter())),
        }

    def _analyze_security(self, root: Element) -> Dict[str, Any]:
        """Generic security analysis"""
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "ivy-module":
            return self._analyze_module_security(root)
        else:
            return self._analyze_settings_security(root)

    def _find_element_by_local_name(
        self, parent: Element, local_name: str
    ) -> Optional[Element]:
        """Find element by local name, ignoring namespace"""
        for elem in parent:
            elem_local_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if elem_local_name == local_name:
                return elem
        return None

    def _get_element_text(self, element: Optional[Element]) -> Optional[str]:
        """Safely get text from element"""
        return element.text if element is not None else None

    def _assess_ivy_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess Ivy configuration quality"""

        # Security quality
        security_score = 1.0
        if "security" in findings and findings["security"]["security_risks"]:
            risk_count = len(findings["security"]["security_risks"])
            security_score = max(0.0, 1.0 - (risk_count * 0.15))

        # Dependency management quality
        dependency_score = 0.0
        if "dependencies" in findings:
            deps = findings["dependencies"]
            if deps["dependency_count"] > 0:
                dependency_score += 0.4

                # Prefer fixed versions over dynamic
                total_deps = deps["dependency_count"]
                fixed_ratio = (
                    deps["version_patterns"]["fixed"] / total_deps
                    if total_deps > 0
                    else 0
                )
                dependency_score += fixed_ratio * 0.3

                # Bonus for having excludes (shows dependency management)
                if any(dep["excludes"] for dep in deps["dependency_details"]):
                    dependency_score += 0.1

                # Bonus for organization diversity
                if len(deps["organizations"]) > 1:
                    dependency_score += 0.2
        else:
            dependency_score = 0.8  # Settings files don't need dependency quality

        # Configuration quality
        config_score = 0.0
        if "module_info" in findings and findings["module_info"]["has_info"]:
            module_info = findings["module_info"]
            if module_info["organisation"] and module_info["module"]:
                config_score += 0.4
            if module_info["revision"]:
                config_score += 0.2
            if module_info["description"]:
                config_score += 0.2
            if module_info["license"]:
                config_score += 0.2
        elif "settings" in findings:
            # Settings file quality
            config_score = 0.8
        else:
            config_score = 0.5  # Moderate score for unknown type

        # Publication quality
        publication_score = 0.0
        if "publications" in findings:
            pubs = findings["publications"]
            if pubs["publication_count"] > 0:
                publication_score += 0.5

                # Bonus for artifact type diversity
                if len(pubs["artifact_types"]) > 1:
                    publication_score += 0.3

                # Bonus for configuration mapping
                if pubs["configurations_published"]:
                    publication_score += 0.2
        else:
            publication_score = (
                0.7  # Non-publishing modules or settings get moderate score
            )

        return {
            "security": security_score,
            "dependency_management": dependency_score,
            "configuration": config_score,
            "publication": publication_score,
            "overall": (
                security_score + dependency_score + config_score + publication_score
            )
            / 4,
        }
