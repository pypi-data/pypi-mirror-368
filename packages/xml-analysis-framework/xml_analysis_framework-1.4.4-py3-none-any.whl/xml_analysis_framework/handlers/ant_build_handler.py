#!/usr/bin/env python3
"""
Apache Ant Build Handler

Analyzes Apache Ant build.xml files to extract build targets, tasks,
properties, and dependencies for build analysis and CI/CD optimization.
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


class AntBuildHandler(XMLHandler):
    """Handler for Apache Ant build.xml files"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for Ant project root element
        if root.tag == "project" or root.tag.endswith("}project"):
            confidence = 0.0

            # Strong indicators for Ant build files
            if root.get("name") is not None:
                confidence += 0.3
            if root.get("default") is not None:
                confidence += 0.3
            if root.get("basedir") is not None:
                confidence += 0.2

            # Check for typical Ant elements
            ant_elements = ["target", "property", "taskdef", "path", "fileset"]
            found_elements = sum(
                1 for elem in ant_elements if root.find(f".//{elem}") is not None
            )
            confidence += min(found_elements * 0.1, 0.4)

            # Check for Ant-specific namespaces or attributes
            if any("antlib" in str(uri) for uri in namespaces.values()):
                confidence += 0.2

            # If we have decent confidence, it's likely an Ant build file
            if confidence >= 0.5:
                return True, min(confidence, 1.0)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        project_name = root.get("name", "unknown")
        default_target = root.get("default", "none")

        # Try to determine Ant version from comments or attributes
        version = None

        # Look for version information in comments
        # Note: defusedxml doesn't preserve comments during parsing
        # So we'll skip comment-based version detection
        version = None

        metadata = {
            "build_tool": "Apache Ant",
            "category": "build_configuration",
            "project_name": project_name,
            "default_target": default_target,
        }

        # Check for Ivy integration
        if any("ivy" in str(uri) for uri in namespaces.values()):
            metadata["dependency_manager"] = "Apache Ivy"

        return DocumentTypeInfo(
            type_name="Apache Ant Build",
            confidence=0.95,
            version=version,
            metadata=metadata,
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "project_info": self._extract_project_info(root),
            "targets": self._analyze_targets(root),
            "properties": self._extract_properties(root),
            "paths": self._analyze_paths(root),
            "filesets": self._analyze_filesets(root),
            "dependencies": self._analyze_dependencies(root),
            "tasks": self._analyze_tasks(root),
            "build_metrics": self._calculate_build_metrics(root),
        }

        recommendations = [
            "Analyze target dependencies for build optimization",
            "Check for hardcoded paths and credentials",
            "Extract for CI/CD pipeline configuration",
            "Review build performance and parallelization opportunities",
            "Validate property management and externalization",
            "Assess dependency management strategy",
        ]

        ai_use_cases = [
            "Build optimization recommendations",
            "CI/CD pipeline generation",
            "Dependency vulnerability scanning",
            "Build performance analysis",
            "Configuration management automation",
            "Technical debt assessment",
            "Build reproducibility analysis",
            "Security scanning of build scripts",
        ]

        data_inventory = {
            "targets": len(findings["targets"]),
            "properties": len(findings["properties"]),
            "paths": len(findings["paths"]),
            "filesets": len(findings["filesets"]),
            "dependencies": findings["dependencies"]["total_count"],
            "tasks": findings["tasks"]["total_count"],
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
            quality_metrics=self._assess_build_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "project_metadata": {
                "name": root.get("name"),
                "default_target": root.get("default"),
                "base_directory": root.get("basedir", "."),
            },
            "build_targets": self._extract_target_list(root),
            "build_properties": self._extract_property_summary(root),
            "dependency_info": self._extract_dependency_summary(root),
            "task_summary": self._extract_task_summary(root),
        }

    def _extract_project_info(self, root: Element) -> Dict[str, Any]:
        project_info = {
            "name": root.get("name"),
            "default_target": root.get("default"),
            "base_directory": root.get("basedir", "."),
            "description": None,
        }

        # Extract description
        description = root.find(".//description")
        if description is not None and description.text:
            project_info["description"] = description.text.strip()

        return project_info

    def _analyze_targets(self, root: Element) -> List[Dict[str, Any]]:
        targets = []

        for target in root.findall(".//target"):
            target_info = {
                "name": target.get("name"),
                "depends": (
                    target.get("depends", "").split(",")
                    if target.get("depends")
                    else []
                ),
                "if": target.get("if"),
                "unless": target.get("unless"),
                "description": target.get("description"),
                "task_count": len(
                    [child for child in target if child.tag != "description"]
                ),
                "tasks": [],
            }

            # Extract tasks within this target
            for task in target:
                if task.tag not in ["description"]:
                    target_info["tasks"].append(
                        {"name": task.tag, "attributes": dict(task.attrib)}
                    )

            targets.append(target_info)

        return targets

    def _extract_properties(self, root: Element) -> Dict[str, Any]:
        properties = {
            "inline_properties": {},
            "property_files": [],
            "environment_properties": [],
        }

        for prop in root.findall(".//property"):
            name = prop.get("name")
            value = prop.get("value")
            file_attr = prop.get("file")
            environment = prop.get("environment")

            if name and value:
                properties["inline_properties"][name] = value
            elif file_attr:
                properties["property_files"].append(file_attr)
            elif environment:
                properties["environment_properties"].append(environment)

        return properties

    def _analyze_paths(self, root: Element) -> List[Dict[str, Any]]:
        paths = []

        for path in root.findall(".//path"):
            path_info = {"id": path.get("id"), "elements": []}

            # Analyze path elements
            for elem in path:
                if elem.tag == "pathelement":
                    path_info["elements"].append(
                        {
                            "type": "path_element",
                            "location": elem.get("location"),
                            "path": elem.get("path"),
                        }
                    )
                elif elem.tag == "fileset":
                    path_info["elements"].append(
                        {
                            "type": "fileset",
                            "dir": elem.get("dir"),
                            "includes": elem.get("includes"),
                            "excludes": elem.get("excludes"),
                        }
                    )

            paths.append(path_info)

        return paths

    def _analyze_filesets(self, root: Element) -> List[Dict[str, Any]]:
        filesets = []

        for fileset in root.findall(".//fileset"):
            fileset_info = {
                "dir": fileset.get("dir"),
                "includes": fileset.get("includes"),
                "excludes": fileset.get("excludes"),
                "id": fileset.get("id"),
                "patterns": [],
            }

            # Extract include/exclude patterns
            for include in fileset.findall(".//include"):
                if include.get("name"):
                    fileset_info["patterns"].append(
                        {"type": "include", "pattern": include.get("name")}
                    )

            for exclude in fileset.findall(".//exclude"):
                if exclude.get("name"):
                    fileset_info["patterns"].append(
                        {"type": "exclude", "pattern": exclude.get("name")}
                    )

            filesets.append(fileset_info)

        return filesets

    def _analyze_dependencies(self, root: Element) -> Dict[str, Any]:
        dependencies = {
            "ivy_dependencies": [],
            "jar_references": [],
            "lib_directories": [],
            "total_count": 0,
        }

        # Check for Ivy dependencies
        for dep in root.findall(".//*[@org][@name]"):
            if "ivy" in dep.tag:
                dep_info = {
                    "org": dep.get("org"),
                    "name": dep.get("name"),
                    "rev": dep.get("rev"),
                    "conf": dep.get("conf"),
                }
                dependencies["ivy_dependencies"].append(dep_info)
                dependencies["total_count"] += 1

        # Check for JAR file references
        for elem in root.iter():
            for attr_name, attr_value in elem.attrib.items():
                if attr_value and ".jar" in attr_value:
                    dependencies["jar_references"].append(
                        {
                            "element": elem.tag,
                            "attribute": attr_name,
                            "jar_path": attr_value,
                        }
                    )
                    dependencies["total_count"] += 1

        # Check for lib directories
        for elem in root.iter():
            for attr_name, attr_value in elem.attrib.items():
                if attr_value and (
                    "lib" in attr_value.lower() or "libs" in attr_value.lower()
                ):
                    if attr_value not in [
                        d["path"] for d in dependencies["lib_directories"]
                    ]:
                        dependencies["lib_directories"].append(
                            {"path": attr_value, "context": elem.tag}
                        )

        return dependencies

    def _analyze_tasks(self, root: Element) -> Dict[str, Any]:
        task_summary = {
            "total_count": 0,
            "by_type": {},
            "custom_tasks": [],
            "deprecated_tasks": [],
        }

        # Common Ant tasks
        common_tasks = [
            "javac",
            "jar",
            "copy",
            "delete",
            "mkdir",
            "echo",
            "exec",
            "zip",
            "war",
            "tar",
            "replace",
            "concat",
            "sql",
            "junit",
            "java",
            "ant",
            "subant",
            "parallel",
            "sequential",
        ]

        deprecated_tasks = ["style", "mail"]  # Known deprecated Ant tasks

        # Count all task elements
        for target in root.findall(".//target"):
            for task in target:
                if task.tag not in ["description"]:
                    task_name = task.tag
                    task_summary["total_count"] += 1
                    task_summary["by_type"][task_name] = (
                        task_summary["by_type"].get(task_name, 0) + 1
                    )

                    # Check for custom tasks (not in common list)
                    if task_name not in common_tasks and task_name not in [
                        t["name"] for t in task_summary["custom_tasks"]
                    ]:
                        task_summary["custom_tasks"].append(
                            {"name": task_name, "count": 1}
                        )

                    # Check for deprecated tasks
                    if task_name in deprecated_tasks:
                        task_summary["deprecated_tasks"].append(task_name)

        return task_summary

    def _calculate_build_metrics(self, root: Element) -> Dict[str, Any]:
        metrics = {
            "complexity_score": 0.0,
            "target_count": len(root.findall(".//target")),
            "dependency_depth": 0,
            "property_count": len(root.findall(".//property")),
            "conditional_targets": 0,
        }

        # Calculate dependency depth
        targets = root.findall(".//target")
        max_depth = 0
        for target in targets:
            depends = target.get("depends", "")
            if depends:
                depth = len(depends.split(","))
                max_depth = max(max_depth, depth)
        metrics["dependency_depth"] = max_depth

        # Count conditional targets
        for target in targets:
            if target.get("if") or target.get("unless"):
                metrics["conditional_targets"] += 1

        # Calculate complexity score
        complexity_factors = [
            min(metrics["target_count"] / 20, 1.0) * 0.3,
            min(metrics["dependency_depth"] / 5, 1.0) * 0.3,
            min(metrics["property_count"] / 50, 1.0) * 0.2,
            min(metrics["conditional_targets"] / 10, 1.0) * 0.2,
        ]
        metrics["complexity_score"] = sum(complexity_factors)

        return metrics

    def _extract_target_list(self, root: Element) -> List[Dict[str, str]]:
        targets = []
        for target in root.findall(".//target")[:10]:  # Limit to first 10
            targets.append(
                {
                    "name": target.get("name", ""),
                    "description": target.get("description", ""),
                    "depends": target.get("depends", ""),
                }
            )
        return targets

    def _extract_property_summary(self, root: Element) -> Dict[str, Any]:
        return {
            "total_properties": len(root.findall(".//property")),
            "property_files": [
                p.get("file")
                for p in root.findall(".//property[@file]")
                if p.get("file")
            ],
            "sample_properties": {
                p.get("name"): p.get("value")
                for p in root.findall(".//property[@name][@value]")[:5]
            },
        }

    def _extract_dependency_summary(self, root: Element) -> Dict[str, Any]:
        return {
            "has_ivy": any(
                "ivy" in str(uri) for uri in [elem.tag for elem in root.iter()]
            ),
            "jar_count": len(
                [
                    attr
                    for elem in root.iter()
                    for attr in elem.attrib.values()
                    if ".jar" in str(attr)
                ]
            ),
            "lib_dirs": list(
                set(
                    [
                        attr
                        for elem in root.iter()
                        for attr in elem.attrib.values()
                        if "lib" in str(attr).lower() and len(str(attr)) < 100
                    ]
                )
            )[:5],
        }

    def _extract_task_summary(self, root: Element) -> Dict[str, Any]:
        tasks = {}
        for target in root.findall(".//target"):
            for task in target:
                if task.tag != "description":
                    tasks[task.tag] = tasks.get(task.tag, 0) + 1

        return {
            "total_tasks": sum(tasks.values()),
            "unique_task_types": len(tasks),
            "most_common_tasks": sorted(
                tasks.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

    def _assess_build_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess build script quality"""

        # Complexity management (lower complexity is better)
        complexity_score = min(findings["build_metrics"]["complexity_score"], 1.0)
        complexity_quality = max(0, 1.0 - complexity_score)

        # Documentation completeness
        total_targets = len(findings["targets"])
        documented_targets = sum(1 for t in findings["targets"] if t.get("description"))
        documentation_quality = (
            documented_targets / total_targets if total_targets > 0 else 0
        )

        # Property management
        inline_props = len(findings["properties"]["inline_properties"])
        external_props = len(findings["properties"]["property_files"])
        if inline_props + external_props > 0:
            externalization_ratio = external_props / (inline_props + external_props)
        else:
            externalization_ratio = 1.0

        # Dependency management
        dependency_quality = 0.5  # Default neutral score
        if findings["dependencies"]["total_count"] > 0:
            ivy_ratio = (
                len(findings["dependencies"]["ivy_dependencies"])
                / findings["dependencies"]["total_count"]
            )
            dependency_quality = ivy_ratio * 0.5 + 0.5  # Ivy usage is better

        # Best practices
        best_practices = 0.0
        project_info = findings["project_info"]

        # Has project description
        if project_info.get("description"):
            best_practices += 0.25

        # Uses default target
        if project_info.get("default_target"):
            best_practices += 0.25

        # Has reasonable number of targets (not too few, not too many)
        target_count = len(findings["targets"])
        if 3 <= target_count <= 20:
            best_practices += 0.25

        # Uses properties for configuration
        if len(findings["properties"]["property_files"]) > 0:
            best_practices += 0.25

        return {
            "complexity_management": complexity_quality,
            "documentation": documentation_quality,
            "property_externalization": externalization_ratio,
            "dependency_management": dependency_quality,
            "best_practices": best_practices,
            "overall": (
                complexity_quality
                + documentation_quality
                + externalization_ratio
                + dependency_quality
                + best_practices
            )
            / 5,
        }
