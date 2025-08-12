#!/usr/bin/env python3
"""
Properties XML Handler

Handles Java Properties files in XML format.
These are commonly used for configuration in Java applications
and provide a structured alternative to traditional .properties files.
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


class PropertiesXMLHandler(XMLHandler):
    """Handler for Java Properties XML files"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Java Properties XML files have specific DTD
        if root.tag == "properties" or root.tag.endswith("}properties"):
            # Check for properties-specific structure
            if root.find(".//entry") is not None:
                return True, 1.0
            # Even without entries, if it has the comment element typical of properties
            if root.find(".//comment") is not None:
                return True, 0.8
            # Basic properties root
            return True, 0.6

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        # Properties XML files typically reference a specific DTD
        dtd_version = "1.0"  # Standard version

        # Check for comment that might indicate version or purpose
        comment = root.find(".//comment")
        comment_text = comment.text if comment is not None else None

        return DocumentTypeInfo(
            type_name="Java Properties XML",
            confidence=1.0,
            version=dtd_version,
            schema_uri="http://java.sun.com/dtd/properties.dtd",
            metadata={
                "standard": "Java Properties",
                "category": "configuration",
                "format": "XML",
                "comment": comment_text,
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            "properties": self._extract_all_properties(root),
            "property_groups": self._group_properties_by_prefix(root),
            "environment_configs": self._detect_environment_configs(root),
            "security_sensitive": self._find_sensitive_properties(root),
            "placeholders": self._find_placeholders(root),
            "duplicates": self._find_duplicate_keys(root),
            "statistics": self._calculate_statistics(root),
        }

        recommendations = [
            "Review for hardcoded sensitive values",
            "Check for environment-specific configurations",
            "Validate property naming conventions",
            "Extract for configuration management",
            "Monitor for configuration drift",
            "Consider encrypting sensitive properties",
        ]

        ai_use_cases = [
            "Configuration validation",
            "Security scanning for exposed credentials",
            "Environment configuration comparison",
            "Property dependency analysis",
            "Configuration migration assistance",
            "Default value recommendations",
            "Configuration documentation generation",
            "Property usage analysis",
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
                "total_properties": len(findings["properties"]),
                "property_groups": len(findings["property_groups"]),
                "sensitive_properties": len(findings["security_sensitive"]),
                "placeholders": len(findings["placeholders"]),
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_property_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "all_properties": self._extract_properties_dict(root),
            "grouped_properties": self._extract_grouped_properties(root),
            "configuration_metadata": self._extract_metadata(root),
            "property_patterns": self._analyze_property_patterns(root),
        }

    def _extract_all_properties(self, root: Element) -> List[Dict[str, Any]]:
        """Extract all properties with their details"""
        properties = []

        for entry in root.findall(".//entry"):
            key = entry.get("key")
            if key:
                prop_info = {
                    "key": key,
                    "value": entry.text or "",
                    "type": self._infer_property_type(entry.text),
                    "category": self._categorize_property(key),
                    "is_empty": not entry.text or not entry.text.strip(),
                }

                # Check for special patterns
                if prop_info["value"]:
                    prop_info["has_placeholder"] = (
                        "${" in prop_info["value"] or "#{" in prop_info["value"]
                    )
                    prop_info["is_reference"] = prop_info["value"].startswith(
                        "@"
                    ) or prop_info["value"].startswith("$")
                else:
                    prop_info["has_placeholder"] = False
                    prop_info["is_reference"] = False

                properties.append(prop_info)

        # Sort by key for consistency
        properties.sort(key=lambda x: x["key"])

        return properties

    def _group_properties_by_prefix(
        self, root: Element
    ) -> Dict[str, List[Dict[str, str]]]:
        """Group properties by their prefix (e.g., 'database.', 'server.', etc.)"""
        groups = {}

        for entry in root.findall(".//entry"):
            key = entry.get("key")
            if key and "." in key:
                prefix = key.split(".")[0]
                if prefix not in groups:
                    groups[prefix] = []

                groups[prefix].append(
                    {
                        "key": key,
                        "value": entry.text or "",
                        "suffix": ".".join(key.split(".")[1:]),
                    }
                )

        return groups

    def _detect_environment_configs(self, root: Element) -> Dict[str, List[str]]:
        """Detect environment-specific configurations"""
        env_configs = {
            "development": [],
            "testing": [],
            "staging": [],
            "production": [],
        }

        env_patterns = {
            "development": ["dev", "development", "local", "debug"],
            "testing": ["test", "testing", "qa", "quality"],
            "staging": ["stage", "staging", "uat", "preprod"],
            "production": ["prod", "production", "live", "release"],
        }

        for entry in root.findall(".//entry"):
            key = entry.get("key", "").lower()
            value = (entry.text or "").lower()

            for env, patterns in env_patterns.items():
                if any(pattern in key or pattern in value for pattern in patterns):
                    env_configs[env].append(entry.get("key"))

        # Remove duplicates
        for env in env_configs:
            env_configs[env] = list(set(env_configs[env]))

        return env_configs

    def _find_sensitive_properties(self, root: Element) -> List[Dict[str, Any]]:
        """Find potentially sensitive properties"""
        sensitive_properties = []

        sensitive_patterns = [
            "password",
            "passwd",
            "pwd",
            "secret",
            "key",
            "token",
            "credential",
            "auth",
            "private",
            "certificate",
            "cert",
            "api_key",
            "apikey",
            "access_key",
            "encryption",
        ]

        for entry in root.findall(".//entry"):
            key = entry.get("key", "").lower()
            value = entry.text or ""

            # Check if key contains sensitive patterns
            is_sensitive = any(pattern in key for pattern in sensitive_patterns)

            if is_sensitive:
                sensitive_info = {
                    "key": entry.get("key"),
                    "value_length": len(value),
                    "is_encrypted": self._looks_encrypted(value),
                    "is_empty": not value,
                    "is_placeholder": "${" in value or value.startswith("ENC("),
                    "risk_level": self._assess_risk_level(key, value),
                }

                # Don't include actual value for security
                if (
                    not sensitive_info["is_empty"]
                    and not sensitive_info["is_placeholder"]
                ):
                    sensitive_info["value_preview"] = (
                        value[:3] + "***" if len(value) > 3 else "***"
                    )

                sensitive_properties.append(sensitive_info)

        return sensitive_properties

    def _find_placeholders(self, root: Element) -> List[Dict[str, str]]:
        """Find properties with placeholder values"""
        placeholders = []

        placeholder_patterns = [
            (r"\$\{([^}]+)\}", "maven_style"),  # ${property}
            (r"#\{([^}]+)\}", "spring_el"),  # #{expression}
            (r"@([^@]+)@", "ant_style"),  # @property@
            (r"%\(([^)]+)\)s?", "python_style"),  # %(property)s
        ]

        for entry in root.findall(".//entry"):
            key = entry.get("key")
            value = entry.text or ""

            for pattern, style in placeholder_patterns:
                matches = re.findall(pattern, value)
                if matches:
                    placeholders.append(
                        {
                            "key": key,
                            "value": value,
                            "placeholders": matches,
                            "style": style,
                        }
                    )
                    break

        return placeholders

    def _find_duplicate_keys(self, root: Element) -> List[Dict[str, Any]]:
        """Find duplicate property keys"""
        key_occurrences = {}
        duplicates = []

        for i, entry in enumerate(root.findall(".//entry")):
            key = entry.get("key")
            if key:
                if key not in key_occurrences:
                    key_occurrences[key] = []
                key_occurrences[key].append({"index": i, "value": entry.text or ""})

        for key, occurrences in key_occurrences.items():
            if len(occurrences) > 1:
                duplicates.append(
                    {
                        "key": key,
                        "occurrences": len(occurrences),
                        "values": [occ["value"] for occ in occurrences],
                        "all_same": len(set(occ["value"] for occ in occurrences)) == 1,
                    }
                )

        return duplicates

    def _calculate_statistics(self, root: Element) -> Dict[str, Any]:
        """Calculate property statistics"""
        all_entries = root.findall(".//entry")

        stats = {
            "total_properties": len(all_entries),
            "empty_properties": 0,
            "property_types": {},
            "key_lengths": {"min": 0, "max": 0, "avg": 0},
            "value_lengths": {"min": 0, "max": 0, "avg": 0},
            "naming_patterns": {},
        }

        key_lengths = []
        value_lengths = []

        for entry in all_entries:
            key = entry.get("key", "")
            value = entry.text or ""

            # Count empty properties
            if not value.strip():
                stats["empty_properties"] += 1

            # Track lengths
            key_lengths.append(len(key))
            value_lengths.append(len(value))

            # Analyze property types
            prop_type = self._infer_property_type(value)
            stats["property_types"][prop_type] = (
                stats["property_types"].get(prop_type, 0) + 1
            )

            # Analyze naming patterns
            pattern = self._analyze_naming_pattern(key)
            stats["naming_patterns"][pattern] = (
                stats["naming_patterns"].get(pattern, 0) + 1
            )

        # Calculate length statistics
        if key_lengths:
            stats["key_lengths"] = {
                "min": min(key_lengths),
                "max": max(key_lengths),
                "avg": sum(key_lengths) / len(key_lengths),
            }

        if value_lengths:
            stats["value_lengths"] = {
                "min": min(value_lengths),
                "max": max(value_lengths),
                "avg": sum(value_lengths) / len(value_lengths),
            }

        return stats

    def _infer_property_type(self, value: str) -> str:
        """Infer the type of a property value"""
        if not value:
            return "empty"

        value = value.strip()

        # Boolean
        if value.lower() in ["true", "false", "yes", "no", "on", "off", "1", "0"]:
            return "boolean"

        # Numeric
        try:
            int(value)
            return "integer"
        except ValueError:
            try:
                float(value)
                return "float"
            except ValueError:
                pass

        # URL/URI
        if value.startswith(("http://", "https://", "ftp://", "file://", "jdbc:")):
            return "url"

        # File path
        if (
            "/" in value
            or "\\" in value
            or value.endswith((".xml", ".properties", ".conf"))
        ):
            return "path"

        # Email
        if "@" in value and "." in value.split("@")[-1]:
            return "email"

        # Class name (Java)
        if "." in value and value[0].isupper() and " " not in value:
            return "classname"

        # List/Array
        if "," in value or ";" in value:
            return "list"

        # Placeholder
        if "${" in value or "#{" in value:
            return "placeholder"

        return "string"

    def _categorize_property(self, key: str) -> str:
        """Categorize property based on its key"""
        key_lower = key.lower()

        categories = {
            "database": ["db", "database", "jdbc", "datasource", "sql"],
            "server": ["server", "host", "port", "url", "endpoint"],
            "security": ["password", "secret", "key", "token", "auth", "credential"],
            "logging": ["log", "logger", "logging", "debug"],
            "performance": ["cache", "pool", "timeout", "max", "min", "size"],
            "feature": ["enable", "disable", "feature", "flag"],
            "path": ["path", "dir", "directory", "file", "location"],
            "network": ["proxy", "network", "connection", "socket"],
        }

        for category, keywords in categories.items():
            if any(keyword in key_lower for keyword in keywords):
                return category

        return "general"

    def _looks_encrypted(self, value: str) -> bool:
        """Check if a value looks like it might be encrypted"""
        if not value:
            return False

        # Common encryption markers
        if value.startswith(("ENC(", "ENCRYPTED(", "{cipher}")):
            return True

        # Base64-like pattern (long string with specific characters)
        if len(value) > 20 and re.match(r"^[A-Za-z0-9+/=]+$", value):
            return True

        # Hex-like pattern
        if len(value) > 20 and re.match(r"^[0-9a-fA-F]+$", value):
            return True

        return False

    def _assess_risk_level(self, key: str, value: str) -> str:
        """Assess the risk level of a sensitive property"""
        if not value:
            return "low"  # Empty is low risk

        if "${" in value or value.startswith("ENC("):
            return "low"  # Placeholder or encrypted

        if self._looks_encrypted(value):
            return "medium"  # Encrypted but still present

        # High risk patterns
        high_risk_keywords = ["password", "secret", "private", "key"]
        if (
            any(keyword in key.lower() for keyword in high_risk_keywords)
            and len(value) > 3
        ):
            return "high"

        return "medium"

    def _analyze_naming_pattern(self, key: str) -> str:
        """Analyze the naming pattern of a property key"""
        if not key:
            return "empty"

        # Dot notation (most common in Java)
        if "." in key:
            parts = key.split(".")
            if all(part.islower() for part in parts):
                return "dot.lowercase"
            elif all(part[0].isupper() for part in parts if part):
                return "dot.PascalCase"
            else:
                return "dot.mixed"

        # Underscore notation
        if "_" in key:
            if key.isupper():
                return "CONSTANT_CASE"
            elif key.islower():
                return "snake_case"
            else:
                return "mixed_underscore"

        # Hyphen notation
        if "-" in key:
            return "kebab-case"

        # Camel case
        if key[0].islower() and any(c.isupper() for c in key[1:]):
            return "camelCase"

        # Pascal case
        if key[0].isupper() and any(c.islower() for c in key):
            return "PascalCase"

        # Simple lowercase
        if key.islower():
            return "lowercase"

        # Simple uppercase
        if key.isupper():
            return "UPPERCASE"

        return "other"

    def _extract_properties_dict(self, root: Element) -> Dict[str, str]:
        """Extract properties as a simple key-value dictionary"""
        properties = {}

        for entry in root.findall(".//entry"):
            key = entry.get("key")
            if key:
                properties[key] = entry.text or ""

        return properties

    def _extract_grouped_properties(self, root: Element) -> Dict[str, Dict[str, str]]:
        """Extract properties grouped by prefix"""
        grouped = {}

        for entry in root.findall(".//entry"):
            key = entry.get("key")
            if key and "." in key:
                prefix = key.split(".")[0]
                if prefix not in grouped:
                    grouped[prefix] = {}

                # Use the rest of the key as the property name
                prop_name = ".".join(key.split(".")[1:])
                grouped[prefix][prop_name] = entry.text or ""

        return grouped

    def _extract_metadata(self, root: Element) -> Dict[str, Any]:
        """Extract metadata about the properties file"""
        metadata = {}

        # Extract comment if present
        comment = root.find(".//comment")
        if comment is not None and comment.text:
            metadata["comment"] = comment.text.strip()

            # Try to extract metadata from comment
            # Look for common patterns like version, date, author
            comment_text = comment.text.lower()

            # Version
            version_match = re.search(r"version[:\s]+([0-9.]+)", comment_text)
            if version_match:
                metadata["version"] = version_match.group(1)

            # Date
            date_match = re.search(r"date[:\s]+([0-9/-]+)", comment_text)
            if date_match:
                metadata["date"] = date_match.group(1)

            # Author
            author_match = re.search(r"author[:\s]+([^\n]+)", comment_text)
            if author_match:
                metadata["author"] = author_match.group(1).strip()

        # Count total entries
        metadata["total_entries"] = len(root.findall(".//entry"))

        return metadata

    def _analyze_property_patterns(self, root: Element) -> Dict[str, Any]:
        """Analyze patterns in property definitions"""
        patterns = {
            "hierarchical_groups": {},
            "common_prefixes": {},
            "common_suffixes": {},
            "value_patterns": {},
        }

        all_keys = []

        for entry in root.findall(".//entry"):
            key = entry.get("key")
            if key:
                all_keys.append(key)

                # Analyze hierarchical structure
                if "." in key:
                    parts = key.split(".")
                    for i in range(1, len(parts)):
                        prefix = ".".join(parts[:i])
                        patterns["hierarchical_groups"][prefix] = (
                            patterns["hierarchical_groups"].get(prefix, 0) + 1
                        )

        # Find common prefixes (first part before delimiter)
        for key in all_keys:
            if "." in key:
                prefix = key.split(".")[0]
                patterns["common_prefixes"][prefix] = (
                    patterns["common_prefixes"].get(prefix, 0) + 1
                )
            elif "_" in key:
                prefix = key.split("_")[0]
                patterns["common_prefixes"][prefix] = (
                    patterns["common_prefixes"].get(prefix, 0) + 1
                )

        # Find common suffixes (last part after delimiter)
        for key in all_keys:
            if "." in key:
                suffix = key.split(".")[-1]
                patterns["common_suffixes"][suffix] = (
                    patterns["common_suffixes"].get(suffix, 0) + 1
                )
            elif "_" in key:
                suffix = key.split("_")[-1]
                patterns["common_suffixes"][suffix] = (
                    patterns["common_suffixes"].get(suffix, 0) + 1
                )

        # Limit results to most common
        patterns["common_prefixes"] = dict(
            sorted(
                patterns["common_prefixes"].items(), key=lambda x: x[1], reverse=True
            )[:10]
        )
        patterns["common_suffixes"] = dict(
            sorted(
                patterns["common_suffixes"].items(), key=lambda x: x[1], reverse=True
            )[:10]
        )

        return patterns

    def _assess_property_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess the quality of the properties configuration"""
        # Completeness (fewer empty properties is better)
        empty_ratio = findings["statistics"]["empty_properties"] / max(
            findings["statistics"]["total_properties"], 1
        )
        completeness = max(0, 1.0 - empty_ratio)

        # Security (fewer exposed sensitive values is better)
        security_score = 1.0
        high_risk_count = sum(
            1
            for prop in findings["security_sensitive"]
            if prop.get("risk_level") == "high"
        )
        if high_risk_count > 0:
            security_score = max(0, 1.0 - (high_risk_count * 0.2))  # -0.2 per high risk

        # Organization (good use of hierarchical naming)
        organization = 0.0
        if findings["property_groups"]:
            # More groups indicate better organization
            organization = min(len(findings["property_groups"]) / 10, 1.0)

        # Consistency (no duplicates is better)
        consistency = 1.0 if not findings["duplicates"] else 0.5

        # Best practices (use of placeholders for environment-specific values)
        best_practices = 0.0
        if findings["placeholders"]:
            # Having placeholders for configuration is good
            placeholder_ratio = len(findings["placeholders"]) / max(
                findings["statistics"]["total_properties"], 1
            )
            best_practices = min(
                placeholder_ratio * 5, 1.0
            )  # Up to 20% placeholders is good

        return {
            "completeness": completeness,
            "security": security_score,
            "organization": organization,
            "consistency": consistency,
            "best_practices": best_practices,
            "overall": (
                completeness
                + security_score
                + organization
                + consistency
                + best_practices
            )
            / 5,
        }
