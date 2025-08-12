#!/usr/bin/env python3
"""
Hibernate Configuration Handler

Analyzes Hibernate ORM configuration files and mapping files for database schema analysis,
ORM optimization, security assessment, and migration planning.
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


class HibernateHandler(XMLHandler):
    """Handler for Hibernate ORM configuration and mapping files"""

    # Hibernate DTD/namespace patterns
    HIBERNATE_CONFIG_DTD = "hibernate-configuration"
    HIBERNATE_MAPPING_DTD = "hibernate-mapping"

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for Hibernate root elements
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # Hibernate configuration files
        if root_tag == "hibernate-configuration":
            confidence = 0.8

            # Check for session-factory element
            if self._find_element_by_local_name(root, "session-factory") is not None:
                confidence += 0.2

            return True, confidence

        # Hibernate mapping files
        elif root_tag == "hibernate-mapping":
            confidence = 0.8

            # Check for class/subclass elements
            if (
                self._find_element_by_local_name(root, "class") is not None
                or self._find_element_by_local_name(root, "subclass") is not None
            ):
                confidence += 0.2

            return True, confidence

        # Check DOCTYPE declarations
        elif hasattr(root, "getroot"):
            # This is a more complex check for DOCTYPE
            pass

        # Check for Hibernate-specific patterns in any XML
        hibernate_indicators = [
            "session-factory",
            "class",
            "property",
            "id",
            "generator",
        ]
        indicator_count = sum(
            1
            for indicator in hibernate_indicators
            if any(indicator in elem.tag for elem in root.iter())
        )

        if indicator_count >= 3:  # Multiple Hibernate indicators
            return True, min(0.6 + (indicator_count * 0.1), 1.0)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # Determine file type
        if root_tag == "hibernate-configuration":
            file_type = "Configuration"
            category = "hibernate_configuration"
        elif root_tag == "hibernate-mapping":
            file_type = "Mapping"
            category = "hibernate_mapping"
        else:
            file_type = "Configuration"  # Default
            category = "hibernate_unknown"

        # Extract database information
        database_info = self._extract_database_info(root)

        metadata = {
            "orm": "Hibernate",
            "category": category,
            "file_type": file_type,
            "database_driver": database_info.get("driver"),
            "database_url": database_info.get("url"),
            "has_connection_pool": database_info.get("has_connection_pool", False),
            "entity_count": self._count_entities(root),
        }

        return DocumentTypeInfo(
            type_name=f"Hibernate {file_type}",
            confidence=0.95,
            version=self._detect_hibernate_version(root),
            metadata=metadata,
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "hibernate-configuration":
            findings = self._analyze_configuration(root)
        elif root_tag == "hibernate-mapping":
            findings = self._analyze_mapping(root)
        else:
            # Generic analysis
            findings = {
                "hibernate_info": self._analyze_hibernate_elements(root),
                "database_info": self._extract_database_info(root),
                "entities": self._analyze_entities(root),
                "security": self._analyze_security(root),
            }

        recommendations = [
            "Review database connection security and credentials",
            "Analyze entity mappings for performance optimization",
            "Check for SQL injection vulnerabilities in HQL queries",
            "Validate connection pool configuration for scalability",
            "Review caching strategy and second-level cache settings",
            "Analyze lazy loading patterns for N+1 query issues",
            "Check database schema naming conventions",
            "Validate transaction management configuration",
        ]

        ai_use_cases = [
            "Database schema analysis and optimization",
            "ORM performance tuning and query optimization",
            "Security assessment of database configurations",
            "Migration planning and schema evolution",
            "Entity relationship mapping and documentation",
            "Connection pool monitoring and tuning",
            "Cache configuration optimization",
            "Database access pattern analysis",
            "Compliance auditing for data protection regulations",
        ]

        # Calculate data inventory based on findings
        data_inventory = {}
        if "entities" in findings:
            data_inventory["entities"] = len(findings["entities"]["entity_details"])
        if "properties" in findings:
            data_inventory["properties"] = len(
                findings["properties"]["property_details"]
            )
        if "database_info" in findings and findings["database_info"]:
            data_inventory["connections"] = 1

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
            quality_metrics=self._assess_hibernate_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        return {
            "hibernate_metadata": {
                "version": self._detect_hibernate_version(root),
                "file_type": self._determine_file_type(root),
                "entity_count": self._count_entities(root),
            },
            "database_summary": self._extract_database_summary(root),
            "entity_summary": self._extract_entity_summary(root),
            "configuration_summary": self._extract_configuration_summary(root),
        }

    def _analyze_configuration(self, root: Element) -> Dict[str, Any]:
        """Analyze Hibernate configuration file"""
        findings = {
            "hibernate_info": {
                "file_type": "Configuration",
                "version": self._detect_hibernate_version(root),
            },
            "session_factory": self._analyze_session_factory(root),
            "database_info": self._extract_database_info(root),
            "properties": self._analyze_configuration_properties(root),
            "mappings": self._analyze_mapping_resources(root),
            "security": self._analyze_configuration_security(root),
            "performance": self._analyze_performance_settings(root),
        }
        return findings

    def _analyze_mapping(self, root: Element) -> Dict[str, Any]:
        """Analyze Hibernate mapping file"""
        findings = {
            "hibernate_info": {
                "file_type": "Mapping",
                "version": self._detect_hibernate_version(root),
                "package": root.get("package"),
            },
            "entities": self._analyze_entities(root),
            "relationships": self._analyze_relationships(root),
            "identifiers": self._analyze_identifiers(root),
            "properties": self._analyze_entity_properties(root),
            "collections": self._analyze_collections(root),
            "inheritance": self._analyze_inheritance(root),
            "sql_queries": self._analyze_sql_queries(root),
            "security": self._analyze_mapping_security(root),
        }
        return findings

    def _analyze_session_factory(self, root: Element) -> Dict[str, Any]:
        """Analyze session-factory configuration"""
        session_factory_info = {
            "present": False,
            "name": None,
            "property_count": 0,
            "mapping_count": 0,
            "class_cache_count": 0,
            "collection_cache_count": 0,
        }

        session_factory = self._find_element_by_local_name(root, "session-factory")
        if session_factory is not None:
            session_factory_info["present"] = True
            session_factory_info["name"] = session_factory.get("name")

            # Count properties
            properties = [
                elem
                for elem in session_factory.iter()
                if elem.tag.split("}")[-1] == "property"
            ]
            session_factory_info["property_count"] = len(properties)

            # Count mappings
            mappings = [
                elem
                for elem in session_factory.iter()
                if elem.tag.split("}")[-1]
                in ["mapping", "class-cache", "collection-cache"]
            ]
            session_factory_info["mapping_count"] = len(
                [m for m in mappings if m.tag.split("}")[-1] == "mapping"]
            )
            session_factory_info["class_cache_count"] = len(
                [m for m in mappings if m.tag.split("}")[-1] == "class-cache"]
            )
            session_factory_info["collection_cache_count"] = len(
                [m for m in mappings if m.tag.split("}")[-1] == "collection-cache"]
            )

        return session_factory_info

    def _extract_database_info(self, root: Element) -> Dict[str, Any]:
        """Extract database connection information"""
        db_info = {
            "driver": None,
            "url": None,
            "username": None,
            "dialect": None,
            "has_connection_pool": False,
            "pool_size": None,
            "show_sql": False,
        }

        # Look for database properties
        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name == "property" and elem.get("name"):
                prop_name = elem.get("name")
                prop_value = elem.text

                if "connection.driver_class" in prop_name:
                    db_info["driver"] = prop_value
                elif "connection.url" in prop_name:
                    db_info["url"] = prop_value
                elif "connection.username" in prop_name:
                    db_info["username"] = prop_value
                elif "dialect" in prop_name:
                    db_info["dialect"] = prop_value
                elif "pool_size" in prop_name:
                    db_info["pool_size"] = prop_value
                    db_info["has_connection_pool"] = True
                elif "show_sql" in prop_name:
                    db_info["show_sql"] = prop_value and prop_value.lower() == "true"
                elif "c3p0" in prop_name or "hikari" in prop_name:
                    db_info["has_connection_pool"] = True

        return db_info

    def _analyze_configuration_properties(self, root: Element) -> Dict[str, Any]:
        """Analyze configuration properties"""
        props_info = {
            "property_count": 0,
            "property_details": [],
            "categories": {
                "connection": 0,
                "dialect": 0,
                "cache": 0,
                "transaction": 0,
                "other": 0,
            },
        }

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name == "property" and elem.get("name"):
                prop_name = elem.get("name")
                prop_value = elem.text

                prop_detail = {
                    "name": prop_name,
                    "value": prop_value,
                    "category": self._categorize_property(prop_name),
                }

                props_info["property_details"].append(prop_detail)
                props_info["property_count"] += 1
                props_info["categories"][prop_detail["category"]] += 1

        return props_info

    def _analyze_mapping_resources(self, root: Element) -> Dict[str, Any]:
        """Analyze mapping resource declarations"""
        mapping_info = {
            "mapping_count": 0,
            "mapping_details": [],
            "resource_types": {"resource": 0, "class": 0, "jar": 0, "package": 0},
        }

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name == "mapping":
                mapping_detail = {
                    "resource": elem.get("resource"),
                    "class": elem.get("class"),
                    "jar": elem.get("jar"),
                    "package": elem.get("package"),
                }

                mapping_info["mapping_details"].append(mapping_detail)
                mapping_info["mapping_count"] += 1

                # Count by type
                for res_type in mapping_info["resource_types"]:
                    if mapping_detail[res_type]:
                        mapping_info["resource_types"][res_type] += 1

        return mapping_info

    def _analyze_entities(self, root: Element) -> Dict[str, Any]:
        """Analyze entity/class mappings"""
        entity_info = {
            "entity_count": 0,
            "entity_details": [],
            "inheritance_strategies": [],
            "table_names": [],
        }

        # Find all class elements
        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name in ["class", "subclass", "joined-subclass", "union-subclass"]:
                entity_detail = {
                    "type": elem_name,
                    "name": elem.get("name"),
                    "table": elem.get("table"),
                    "schema": elem.get("schema"),
                    "catalog": elem.get("catalog"),
                    "abstract": elem.get("abstract") == "true",
                    "property_count": len(
                        [e for e in elem if e.tag.split("}")[-1] == "property"]
                    ),
                    "id_present": any(e.tag.split("}")[-1] == "id" for e in elem),
                }

                entity_info["entity_details"].append(entity_detail)
                entity_info["entity_count"] += 1

                if entity_detail["table"]:
                    entity_info["table_names"].append(entity_detail["table"])

                if elem_name in ["subclass", "joined-subclass", "union-subclass"]:
                    entity_info["inheritance_strategies"].append(elem_name)

        return entity_info

    def _analyze_relationships(self, root: Element) -> Dict[str, Any]:
        """Analyze entity relationships"""
        rel_info = {
            "relationship_count": 0,
            "relationship_types": {
                "one-to-one": 0,
                "one-to-many": 0,
                "many-to-one": 0,
                "many-to-many": 0,
            },
            "relationship_details": [],
        }

        relationship_elements = [
            "one-to-one",
            "one-to-many",
            "many-to-one",
            "many-to-many",
        ]

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name in relationship_elements:
                rel_detail = {
                    "type": elem_name,
                    "name": elem.get("name"),
                    "class": elem.get("class"),
                    "column": elem.get("column"),
                    "foreign_key": elem.get("foreign-key"),
                    "cascade": elem.get("cascade"),
                    "fetch": elem.get("fetch"),
                    "lazy": elem.get("lazy"),
                }

                rel_info["relationship_details"].append(rel_detail)
                rel_info["relationship_count"] += 1
                rel_info["relationship_types"][elem_name] += 1

        return rel_info

    def _analyze_identifiers(self, root: Element) -> Dict[str, Any]:
        """Analyze entity identifiers"""
        id_info = {"id_strategies": [], "composite_ids": 0, "id_details": []}

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name == "id":
                generator = self._find_element_by_local_name(elem, "generator")
                generator_class = (
                    generator.get("class") if generator is not None else None
                )

                id_detail = {
                    "name": elem.get("name"),
                    "column": elem.get("column"),
                    "type": elem.get("type"),
                    "generator": generator_class,
                }

                id_info["id_details"].append(id_detail)
                if generator_class:
                    id_info["id_strategies"].append(generator_class)

            elif elem_name == "composite-id":
                id_info["composite_ids"] += 1

        return id_info

    def _analyze_entity_properties(self, root: Element) -> Dict[str, Any]:
        """Analyze entity properties"""
        prop_info = {
            "property_count": 0,
            "property_details": [],
            "column_types": {},
            "nullable_properties": 0,
            "unique_properties": 0,
        }

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name == "property":
                prop_detail = {
                    "name": elem.get("name"),
                    "column": elem.get("column"),
                    "type": elem.get("type"),
                    "not_null": elem.get("not-null") == "true",
                    "unique": elem.get("unique") == "true",
                    "length": elem.get("length"),
                    "precision": elem.get("precision"),
                    "scale": elem.get("scale"),
                }

                prop_info["property_details"].append(prop_detail)
                prop_info["property_count"] += 1

                if prop_detail["type"]:
                    prop_info["column_types"][prop_detail["type"]] = (
                        prop_info["column_types"].get(prop_detail["type"], 0) + 1
                    )

                if not prop_detail["not_null"]:
                    prop_info["nullable_properties"] += 1

                if prop_detail["unique"]:
                    prop_info["unique_properties"] += 1

        return prop_info

    def _analyze_collections(self, root: Element) -> Dict[str, Any]:
        """Analyze collection mappings"""
        collection_info = {
            "collection_count": 0,
            "collection_types": {"set": 0, "list": 0, "map": 0, "bag": 0, "array": 0},
            "collection_details": [],
        }

        collection_elements = ["set", "list", "map", "bag", "array"]

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name in collection_elements:
                collection_detail = {
                    "type": elem_name,
                    "name": elem.get("name"),
                    "table": elem.get("table"),
                    "cascade": elem.get("cascade"),
                    "fetch": elem.get("fetch"),
                    "lazy": elem.get("lazy"),
                    "inverse": elem.get("inverse") == "true",
                }

                collection_info["collection_details"].append(collection_detail)
                collection_info["collection_count"] += 1
                collection_info["collection_types"][elem_name] += 1

        return collection_info

    def _analyze_inheritance(self, root: Element) -> Dict[str, Any]:
        """Analyze inheritance mappings"""
        inheritance_info = {
            "has_inheritance": False,
            "strategies": [],
            "subclass_count": 0,
            "discriminator_present": False,
        }

        # Check for inheritance elements
        inheritance_elements = ["subclass", "joined-subclass", "union-subclass"]

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name in inheritance_elements:
                inheritance_info["has_inheritance"] = True
                inheritance_info["subclass_count"] += 1
                if elem_name not in inheritance_info["strategies"]:
                    inheritance_info["strategies"].append(elem_name)

            elif elem_name == "discriminator":
                inheritance_info["discriminator_present"] = True

        return inheritance_info

    def _analyze_sql_queries(self, root: Element) -> Dict[str, Any]:
        """Analyze SQL queries and HQL"""
        query_info = {
            "sql_query_count": 0,
            "hql_query_count": 0,
            "named_queries": [],
            "query_details": [],
        }

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if elem_name == "sql-query":
                query_detail = {
                    "type": "sql",
                    "name": elem.get("name"),
                    "query_text": elem.text,
                }
                query_info["query_details"].append(query_detail)
                query_info["sql_query_count"] += 1
                if query_detail["name"]:
                    query_info["named_queries"].append(query_detail["name"])

            elif elem_name == "query":
                query_detail = {
                    "type": "hql",
                    "name": elem.get("name"),
                    "query_text": elem.text,
                }
                query_info["query_details"].append(query_detail)
                query_info["hql_query_count"] += 1
                if query_detail["name"]:
                    query_info["named_queries"].append(query_detail["name"])

        return query_info

    def _analyze_configuration_security(self, root: Element) -> Dict[str, Any]:
        """Analyze security aspects of configuration"""
        security_info = {
            "security_risks": [],
            "credentials_exposed": False,
            "sql_logging_enabled": False,
            "connection_validation": False,
        }

        db_info = self._extract_database_info(root)

        # Check for exposed credentials
        if db_info.get("username") or any(
            "password" in prop.get("name", "")
            for elem in root.iter()
            for prop in [elem]
            if elem.tag.split("}")[-1] == "property"
        ):
            security_info["credentials_exposed"] = True
            security_info["security_risks"].append(
                "Database credentials visible in configuration"
            )

        # Check for SQL logging
        if db_info.get("show_sql"):
            security_info["sql_logging_enabled"] = True
            security_info["security_risks"].append(
                "SQL logging enabled - may expose sensitive data"
            )

        # Check for connection validation
        for elem in root.iter():
            if (
                elem.tag.split("}")[-1] == "property"
                and elem.get("name")
                and "validation" in elem.get("name")
            ):
                security_info["connection_validation"] = True
                break

        if not security_info["connection_validation"]:
            security_info["security_risks"].append(
                "No connection validation configured"
            )

        return security_info

    def _analyze_mapping_security(self, root: Element) -> Dict[str, Any]:
        """Analyze security aspects of mapping"""
        security_info = {
            "security_risks": [],
            "native_sql_queries": 0,
            "dynamic_insert_update": False,
        }

        # Count native SQL queries (potential injection risk)
        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if elem_name == "sql-query":
                security_info["native_sql_queries"] += 1

        if security_info["native_sql_queries"] > 0:
            security_info["security_risks"].append(
                f'{security_info["native_sql_queries"]} native SQL queries found - '
                f"review for injection risks"
            )

        # Check for dynamic insert/update
        for elem in root.iter():
            if elem.tag.split("}")[-1] in ["class", "subclass"] and (
                elem.get("dynamic-insert") == "true"
                or elem.get("dynamic-update") == "true"
            ):
                security_info["dynamic_insert_update"] = True
                break

        return security_info

    def _analyze_performance_settings(self, root: Element) -> Dict[str, Any]:
        """Analyze performance-related settings"""
        perf_info = {
            "batch_size": None,
            "fetch_size": None,
            "cache_settings": [],
            "lazy_loading": False,
            "connection_pool_configured": False,
        }

        for elem in root.iter():
            if elem.tag.split("}")[-1] == "property" and elem.get("name"):
                prop_name = elem.get("name")
                prop_value = elem.text

                if "batch_size" in prop_name:
                    perf_info["batch_size"] = prop_value
                elif "fetch_size" in prop_name:
                    perf_info["fetch_size"] = prop_value
                elif "cache" in prop_name:
                    perf_info["cache_settings"].append(
                        {"property": prop_name, "value": prop_value}
                    )
                elif "pool" in prop_name:
                    perf_info["connection_pool_configured"] = True

        return perf_info

    def _categorize_property(self, prop_name: str) -> str:
        """Categorize a Hibernate property"""
        if "connection" in prop_name:
            return "connection"
        elif "dialect" in prop_name:
            return "dialect"
        elif "cache" in prop_name:
            return "cache"
        elif "transaction" in prop_name:
            return "transaction"
        else:
            return "other"

    def _detect_hibernate_version(self, root: Element) -> str:
        """Detect Hibernate version from DTD or other indicators"""
        # This is a simplified version - in practice, you'd check DOCTYPE
        return "5.x"  # Default assumption

    def _determine_file_type(self, root: Element) -> str:
        """Determine if this is a configuration or mapping file"""
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "hibernate-configuration":
            return "Configuration"
        elif root_tag == "hibernate-mapping":
            return "Mapping"
        else:
            return "Configuration"  # Default

    def _count_entities(self, root: Element) -> int:
        """Count number of entities in the file"""
        entity_elements = ["class", "subclass", "joined-subclass", "union-subclass"]
        count = 0

        for elem in root.iter():
            elem_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if elem_name in entity_elements:
                count += 1

        return count

    def _extract_database_summary(self, root: Element) -> Dict[str, Any]:
        """Extract database connection summary"""
        db_info = self._extract_database_info(root)
        return {
            "driver": db_info.get("driver"),
            "database_type": self._infer_database_type(db_info.get("driver", "")),
            "has_connection_pool": db_info.get("has_connection_pool", False),
            "show_sql": db_info.get("show_sql", False),
        }

    def _extract_entity_summary(self, root: Element) -> Dict[str, Any]:
        """Extract entity summary information"""
        entities = self._analyze_entities(root)
        return {
            "entity_count": entities["entity_count"],
            "table_names": entities["table_names"][:10],  # Limit to first 10
            "has_inheritance": len(entities["inheritance_strategies"]) > 0,
        }

    def _extract_configuration_summary(self, root: Element) -> Dict[str, Any]:
        """Extract configuration summary"""
        if self._find_element_by_local_name(root, "session-factory") is not None:
            session_factory = self._analyze_session_factory(root)
            return {
                "session_factory_configured": session_factory["present"],
                "property_count": session_factory["property_count"],
                "mapping_count": session_factory["mapping_count"],
            }
        else:
            return {
                "session_factory_configured": False,
                "property_count": 0,
                "mapping_count": 0,
            }

    def _infer_database_type(self, driver: str) -> str:
        """Infer database type from driver class"""
        if not driver:
            return "Unknown"

        driver_lower = driver.lower()
        if "mysql" in driver_lower:
            return "MySQL"
        elif "postgresql" in driver_lower or "postgres" in driver_lower:
            return "PostgreSQL"
        elif "oracle" in driver_lower:
            return "Oracle"
        elif "sqlserver" in driver_lower or "mssql" in driver_lower:
            return "SQL Server"
        elif "h2" in driver_lower:
            return "H2"
        elif "hsql" in driver_lower:
            return "HSQLDB"
        elif "derby" in driver_lower:
            return "Derby"
        else:
            return "Unknown"

    def _analyze_hibernate_elements(self, root: Element) -> Dict[str, Any]:
        """Generic analysis of Hibernate elements"""
        return {
            "file_type": self._determine_file_type(root),
            "version": self._detect_hibernate_version(root),
            "element_count": len(list(root.iter())),
        }

    def _analyze_security(self, root: Element) -> Dict[str, Any]:
        """Generic security analysis"""
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "hibernate-configuration":
            return self._analyze_configuration_security(root)
        else:
            return self._analyze_mapping_security(root)

    def _find_element_by_local_name(
        self, parent: Element, local_name: str
    ) -> Optional[Element]:
        """Find element by local name, ignoring namespace"""
        for elem in parent:
            elem_local_name = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if elem_local_name == local_name:
                return elem
        return None

    def _assess_hibernate_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess Hibernate configuration quality"""

        # Security quality
        security_score = 1.0
        if "security" in findings and findings["security"]["security_risks"]:
            risk_count = len(findings["security"]["security_risks"])
            security_score = max(0.0, 1.0 - (risk_count * 0.2))

        # Configuration quality
        config_score = 0.0
        if "session_factory" in findings and findings["session_factory"]["present"]:
            config_score += 0.4
        if "database_info" in findings and findings["database_info"]["driver"]:
            config_score += 0.3
        if "properties" in findings and findings["properties"]["property_count"] > 0:
            config_score += 0.3

        # Mapping quality
        mapping_score = 0.0
        if "entities" in findings:
            if findings["entities"]["entity_count"] > 0:
                mapping_score += 0.5
            if all(
                entity["id_present"]
                for entity in findings["entities"]["entity_details"]
            ):
                mapping_score += 0.3
            if findings["entities"]["entity_count"] > 0:
                mapping_score += 0.2
        else:
            mapping_score = 0.8  # Configuration files don't need mapping quality

        # Performance quality
        performance_score = 0.5  # Base score
        if "performance" in findings:
            if findings["performance"]["connection_pool_configured"]:
                performance_score += 0.2
            if findings["performance"]["batch_size"]:
                performance_score += 0.2
            if findings["performance"]["cache_settings"]:
                performance_score += 0.1

        performance_score = min(performance_score, 1.0)

        return {
            "security": security_score,
            "configuration": config_score,
            "mapping": mapping_score,
            "performance": performance_score,
            "overall": (
                security_score + config_score + mapping_score + performance_score
            )
            / 4,
        }
