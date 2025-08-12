#!/usr/bin/env python3
"""
Log4j Configuration Handler

Analyzes Apache Log4j XML configuration files for log level optimization,
security configuration analysis, performance assessment, and compliance checking.
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


class Log4jConfigHandler(XMLHandler):
    """Handler for Log4j XML configuration files"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Log4j 1.x uses 'log4j:configuration'
        if root.tag == "log4j:configuration" or root.tag.endswith("}configuration"):
            if "log4j" in root.tag:
                return True, 1.0

        # Log4j 2.x uses 'Configuration'
        if root.tag == "Configuration":
            if (
                root.find(".//Appenders") is not None
                or root.find(".//Loggers") is not None
            ):
                return True, 0.9

            # Check for Log4j 2.x specific attributes
            if root.get("status") or root.get("monitorInterval"):
                return True, 0.8

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        version = "2.x" if root.tag == "Configuration" else "1.x"

        # Extract more detailed version information
        detailed_version = self._detect_detailed_version(root, namespaces)

        metadata = {
            "framework": "Apache Log4j",
            "category": "logging_configuration",
            "version_major": version,
            "appender_count": self._count_appenders(root),
            "logger_count": self._count_loggers(root),
            "has_security_issues": len(self._check_security_issues(root)) > 0,
        }

        return DocumentTypeInfo(
            type_name="Log4j Configuration",
            confidence=1.0,
            version=detailed_version or version,
            metadata=metadata,
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        is_v2 = root.tag == "Configuration"

        findings = {
            "log4j_info": {
                "version": "2.x" if is_v2 else "1.x",
                "detailed_version": self._detect_detailed_version(root, {}),
                "configuration_source": file_path,
            },
            "appenders": self._analyze_appenders(root, is_v2),
            "loggers": self._analyze_loggers(root, is_v2),
            "log_levels": self._extract_log_levels(root, is_v2),
            "patterns": self._analyze_patterns(root, is_v2),
            "filters": self._analyze_filters(root, is_v2),
            "security_concerns": self._check_security_issues(root),
            "performance": self._analyze_performance_settings(root, is_v2),
            "global_settings": self._extract_global_settings(root, is_v2),
        }

        recommendations = [
            "Review log levels for production appropriateness",
            "Check for sensitive data in log patterns",
            "Ensure file appenders have proper rotation",
            "Validate external appender destinations",
            "Check for JNDI lookup patterns (Log4Shell vulnerability)",
            "Optimize pattern layouts for performance",
            "Review async appender configurations",
            "Validate log file permissions and locations",
        ]

        ai_use_cases = [
            "Log level optimization and tuning",
            "Security configuration analysis and hardening",
            "Performance impact assessment and optimization",
            "Compliance checking for log retention policies",
            "Sensitive data detection in log patterns",
            "Log4Shell vulnerability assessment",
            "Log rotation and archival policy analysis",
            "Monitoring and alerting configuration review",
            "Centralized logging integration analysis",
        ]

        data_inventory = {
            "appenders": len(findings["appenders"]["appender_details"]),
            "loggers": len(findings["loggers"]["logger_details"]),
            "patterns": len(findings["patterns"]["pattern_details"]),
            "filters": len(findings["filters"]["filter_details"]),
            "security_issues": len(findings["security_concerns"]["security_risks"]),
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
            quality_metrics=self._assess_logging_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        is_v2 = root.tag == "Configuration"

        return {
            "configuration_metadata": {
                "version": "2.x" if is_v2 else "1.x",
                "monitoring_enabled": (
                    root.get("monitorInterval") is not None if is_v2 else False
                ),
                "status_level": root.get("status") if is_v2 else root.get("threshold"),
            },
            "appender_summary": self._extract_appender_summary(root, is_v2),
            "logger_summary": self._extract_logger_summary(root, is_v2),
            "security_summary": self._extract_security_summary(root),
        }

    def _detect_detailed_version(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Optional[str]:
        """Attempt to detect more detailed Log4j version"""
        # Check for version in attributes or comments
        if root.tag == "Configuration":
            # Log4j 2.x - check for version-specific features
            if root.find(".//AsyncRoot") is not None:
                return "2.6+"  # AsyncRoot introduced in 2.6
            elif root.find(".//ScriptFilter") is not None:
                return "2.4+"  # ScriptFilter introduced in 2.4
            else:
                return "2.x"
        else:
            return "1.x"

    def _count_appenders(self, root: Element) -> int:
        """Count number of appenders"""
        if root.tag == "Configuration":
            return len(root.findall(".//Appenders/*"))
        else:
            return len(root.findall(".//appender"))

    def _count_loggers(self, root: Element) -> int:
        """Count number of loggers"""
        if root.tag == "Configuration":
            return len(root.findall(".//Loggers/*"))
        else:
            return len(root.findall(".//logger")) + len(root.findall(".//root"))

    def _analyze_appenders(self, root: Element, is_v2: bool) -> Dict[str, Any]:
        """Analyze appender configurations"""
        appender_info = {
            "appender_count": 0,
            "appender_details": [],
            "appender_types": {},
            "file_appenders": [],
            "async_appenders": [],
            "external_appenders": [],
        }

        if is_v2:
            appenders_section = root.find(".//Appenders")
            if appenders_section is not None:
                for appender in appenders_section:
                    appender_detail = {
                        "name": appender.get("name"),
                        "type": appender.tag,
                        "target": self._extract_v2_target(appender),
                        "pattern": self._extract_pattern(appender),
                        "async": appender.tag == "AsyncAppender",
                        "filters": len(list(appender.iter("Filter"))),
                    }

                    appender_info["appender_details"].append(appender_detail)
                    appender_info["appender_count"] += 1

                    # Categorize appenders
                    appender_type = appender.tag
                    appender_info["appender_types"][appender_type] = (
                        appender_info["appender_types"].get(appender_type, 0) + 1
                    )

                    if appender_type in ["File", "RollingFile"]:
                        appender_info["file_appenders"].append(appender_detail)
                    elif appender_type == "AsyncAppender":
                        appender_info["async_appenders"].append(appender_detail)
                    elif appender_type in ["Socket", "JMS", "SMTP"]:
                        appender_info["external_appenders"].append(appender_detail)
        else:
            for appender in root.findall(".//appender"):
                class_name = appender.get("class", "")
                appender_detail = {
                    "name": appender.get("name"),
                    "class": class_name,
                    "type": self._extract_v1_type(class_name),
                    "target": self._extract_v1_target(appender),
                    "pattern": self._extract_pattern(appender),
                    "async": "AsyncAppender" in class_name,
                }

                appender_info["appender_details"].append(appender_detail)
                appender_info["appender_count"] += 1

                appender_type = appender_detail["type"]
                appender_info["appender_types"][appender_type] = (
                    appender_info["appender_types"].get(appender_type, 0) + 1
                )

                if "File" in appender_type:
                    appender_info["file_appenders"].append(appender_detail)
                elif "Async" in class_name:
                    appender_info["async_appenders"].append(appender_detail)
                elif any(ext in class_name for ext in ["Socket", "JMS", "SMTP"]):
                    appender_info["external_appenders"].append(appender_detail)

        return appender_info

    def _analyze_loggers(self, root: Element, is_v2: bool) -> Dict[str, Any]:
        """Analyze logger configurations"""
        logger_info = {
            "logger_count": 0,
            "logger_details": [],
            "root_logger": None,
            "package_loggers": [],
            "class_loggers": [],
            "level_distribution": {},
        }

        if is_v2:
            loggers_section = root.find(".//Loggers")
            if loggers_section is not None:
                for logger in loggers_section:
                    logger_name = logger.get(
                        "name", "ROOT" if logger.tag == "Root" else ""
                    )
                    logger_level = logger.get("level")

                    logger_detail = {
                        "name": logger_name,
                        "level": logger_level,
                        "additivity": logger.get("additivity", "true"),
                        "appender_refs": [
                            ref.get("ref") for ref in logger.findall(".//AppenderRef")
                        ],
                        "is_root": logger.tag == "Root",
                        "is_async": logger.tag == "AsyncRoot",
                    }

                    logger_info["logger_details"].append(logger_detail)
                    logger_info["logger_count"] += 1

                    # Categorize loggers
                    if logger_detail["is_root"]:
                        logger_info["root_logger"] = logger_detail
                    elif "." in logger_name:
                        logger_info["package_loggers"].append(logger_detail)
                    else:
                        logger_info["class_loggers"].append(logger_detail)

                    # Track level distribution
                    if logger_level:
                        logger_info["level_distribution"][logger_level] = (
                            logger_info["level_distribution"].get(logger_level, 0) + 1
                        )
        else:
            # Handle Log4j 1.x root logger
            root_logger = root.find(".//root")
            if root_logger is not None:
                level_elem = root_logger.find(".//level")
                logger_detail = {
                    "name": "ROOT",
                    "level": (
                        level_elem.get("value") if level_elem is not None else None
                    ),
                    "appender_refs": [
                        ref.get("ref") for ref in root_logger.findall(".//appender-ref")
                    ],
                    "is_root": True,
                    "is_async": False,
                }
                logger_info["root_logger"] = logger_detail
                logger_info["logger_details"].append(logger_detail)
                logger_info["logger_count"] += 1

            # Handle regular loggers
            for logger in root.findall(".//logger"):
                logger_name = logger.get("name", "")
                level_elem = logger.find(".//level")
                logger_level = (
                    level_elem.get("value") if level_elem is not None else None
                )

                logger_detail = {
                    "name": logger_name,
                    "level": logger_level,
                    "additivity": logger.get("additivity", "true"),
                    "appender_refs": [
                        ref.get("ref") for ref in logger.findall(".//appender-ref")
                    ],
                    "is_root": False,
                    "is_async": False,
                }

                logger_info["logger_details"].append(logger_detail)
                logger_info["logger_count"] += 1

                if "." in logger_name:
                    logger_info["package_loggers"].append(logger_detail)
                else:
                    logger_info["class_loggers"].append(logger_detail)

                if logger_level:
                    logger_info["level_distribution"][logger_level] = (
                        logger_info["level_distribution"].get(logger_level, 0) + 1
                    )

        return logger_info

    def _extract_log_levels(self, root: Element, is_v2: bool) -> Dict[str, Any]:
        """Extract and analyze log levels"""
        level_info = {
            "level_counts": {},
            "production_appropriate": True,
            "debug_loggers": [],
            "trace_loggers": [],
        }

        if is_v2:
            for elem in root.findall(".//*[@level]"):
                level = elem.get("level").upper()
                level_info["level_counts"][level] = (
                    level_info["level_counts"].get(level, 0) + 1
                )

                if level in ["DEBUG", "TRACE"]:
                    logger_name = elem.get("name", elem.tag)
                    if level == "DEBUG":
                        level_info["debug_loggers"].append(logger_name)
                    else:
                        level_info["trace_loggers"].append(logger_name)
        else:
            for level_elem in root.findall(".//level"):
                level = level_elem.get("value", "").upper()
                if level:
                    level_info["level_counts"][level] = (
                        level_info["level_counts"].get(level, 0) + 1
                    )

                    if level in ["DEBUG", "TRACE"]:
                        # Find parent logger by traversing up the tree
                        parent = None
                        for logger_elem in root.findall(".//logger"):
                            if level_elem in logger_elem.iter():
                                parent = logger_elem
                                break
                        if parent is None:
                            for root_elem in root.findall(".//root"):
                                if level_elem in root_elem.iter():
                                    parent = root_elem
                                    break

                        logger_name = (
                            parent.get("name", "ROOT")
                            if parent is not None
                            else "UNKNOWN"
                        )
                        if level == "DEBUG":
                            level_info["debug_loggers"].append(logger_name)
                        else:
                            level_info["trace_loggers"].append(logger_name)

        # Check if configuration is production appropriate
        debug_count = level_info["level_counts"].get("DEBUG", 0)
        trace_count = level_info["level_counts"].get("TRACE", 0)
        level_info["production_appropriate"] = debug_count + trace_count < 3

        return level_info

    def _analyze_patterns(self, root: Element, is_v2: bool) -> Dict[str, Any]:
        """Analyze log patterns for security and performance"""
        pattern_info = {
            "pattern_count": 0,
            "pattern_details": [],
            "potential_pii_exposure": [],
            "performance_concerns": [],
        }

        # Find all pattern layouts
        if is_v2:
            patterns = root.findall(".//PatternLayout")
        else:
            patterns = root.findall(
                './/layout[@class="org.apache.log4j.PatternLayout"]'
            )

        for pattern_elem in patterns:
            if is_v2:
                pattern_text = pattern_elem.get("pattern", "")
            else:
                param = pattern_elem.find('.//param[@name="ConversionPattern"]')
                pattern_text = param.get("value", "") if param is not None else ""

            if pattern_text:
                pattern_detail = {
                    "pattern": pattern_text,
                    "has_timestamp": "%d" in pattern_text or "%date" in pattern_text,
                    "has_level": "%p" in pattern_text or "%level" in pattern_text,
                    "has_logger": "%c" in pattern_text or "%logger" in pattern_text,
                    "has_message": "%m" in pattern_text or "%msg" in pattern_text,
                    "has_location": any(
                        loc in pattern_text for loc in ["%l", "%C", "%M", "%F", "%L"]
                    ),
                    "has_mdc": "%X" in pattern_text or "%mdc" in pattern_text,
                }

                pattern_info["pattern_details"].append(pattern_detail)
                pattern_info["pattern_count"] += 1

                # Check for potential PII exposure
                if any(
                    pii in pattern_text.lower()
                    for pii in ["user", "email", "ssn", "credit"]
                ):
                    pattern_info["potential_pii_exposure"].append(pattern_text)

                # Check for performance concerns
                if pattern_detail["has_location"]:
                    pattern_info["performance_concerns"].append(
                        "Location info can impact performance"
                    )

        return pattern_info

    def _analyze_filters(self, root: Element, is_v2: bool) -> Dict[str, Any]:
        """Analyze filter configurations"""
        filter_info = {"filter_count": 0, "filter_details": [], "filter_types": {}}

        if is_v2:
            filters = root.findall(".//Filter") + root.findall(".//Filters/*")
        else:
            filters = root.findall(".//filter")

        for filter_elem in filters:
            if is_v2:
                filter_type = filter_elem.tag
                filter_detail = {
                    "type": filter_type,
                    "level": filter_elem.get("level"),
                    "onMatch": filter_elem.get("onMatch"),
                    "onMismatch": filter_elem.get("onMismatch"),
                }
            else:
                filter_class = filter_elem.get("class", "")
                filter_detail = {
                    "class": filter_class,
                    "type": filter_class.split(".")[-1] if filter_class else "Unknown",
                }

            filter_info["filter_details"].append(filter_detail)
            filter_info["filter_count"] += 1

            filter_type = filter_detail.get("type", "Unknown")
            filter_info["filter_types"][filter_type] = (
                filter_info["filter_types"].get(filter_type, 0) + 1
            )

        return filter_info

    def _check_security_issues(self, root: Element) -> Dict[str, Any]:
        """Check for security issues including Log4Shell"""
        security_info = {
            "security_risks": [],
            "jndi_patterns": [],
            "external_connections": [],
            "log4shell_vulnerable": False,
            "sensitive_patterns": [],
        }

        # Check for JNDI lookup patterns (Log4Shell vulnerability)
        for elem in root.iter():
            if elem.text and "${jndi:" in elem.text:
                security_info["jndi_patterns"].append(elem.text)
                security_info["log4shell_vulnerable"] = True
                security_info["security_risks"].append(
                    "Potential JNDI lookup pattern detected (Log4Shell)"
                )

            # Check for other potential lookup patterns
            if elem.text:
                for pattern in ["${java:", "${script:", "${dns:", "${ldap:"]:
                    if pattern in elem.text:
                        security_info["security_risks"].append(
                            f"Potential {pattern} lookup pattern detected"
                        )

        # Check for external socket appenders
        for appender in root.findall(".//appender"):
            class_name = appender.get("class", "")
            if "SocketAppender" in class_name:
                host = None
                port = None

                for param in appender.findall(".//param"):
                    if param.get("name") == "RemoteHost":
                        host = param.get("value")
                    elif param.get("name") == "Port":
                        port = param.get("value")

                security_info["external_connections"].append(
                    {"type": "SocketAppender", "host": host, "port": port}
                )
                security_info["security_risks"].append(
                    "External socket appender detected"
                )

        # Check Log4j 2.x external appenders
        for appender in root.findall(".//Socket"):
            host = appender.get("host")
            port = appender.get("port")
            security_info["external_connections"].append(
                {"type": "Socket", "host": host, "port": port}
            )
            security_info["security_risks"].append("External socket appender detected")

        # Check for potentially sensitive information in patterns
        for pattern_elem in root.findall(".//PatternLayout"):
            pattern = pattern_elem.get("pattern", "")
            if any(
                sensitive in pattern.lower()
                for sensitive in ["password", "token", "key", "secret"]
            ):
                security_info["sensitive_patterns"].append(pattern)
                security_info["security_risks"].append(
                    "Pattern may expose sensitive information"
                )

        return security_info

    def _analyze_performance_settings(
        self, root: Element, is_v2: bool
    ) -> Dict[str, Any]:
        """Analyze performance-related settings"""
        perf_info = {
            "async_appenders": 0,
            "async_loggers": 0,
            "buffer_sizes": [],
            "location_info_used": False,
            "performance_risks": [],
        }

        if is_v2:
            # Count async appenders
            perf_info["async_appenders"] = len(root.findall(".//AsyncAppender"))

            # Count async loggers
            perf_info["async_loggers"] = len(root.findall(".//AsyncLogger")) + len(
                root.findall(".//AsyncRoot")
            )

            # Check for location info usage
            for pattern in root.findall(".//PatternLayout"):
                pattern_text = pattern.get("pattern", "")
                if any(loc in pattern_text for loc in ["%l", "%C", "%M", "%F", "%L"]):
                    perf_info["location_info_used"] = True
                    perf_info["performance_risks"].append(
                        "Location info in patterns can impact performance"
                    )
                    break
        else:
            # Check for async appenders in Log4j 1.x
            for appender in root.findall(".//appender"):
                if "AsyncAppender" in appender.get("class", ""):
                    perf_info["async_appenders"] += 1

        return perf_info

    def _extract_global_settings(self, root: Element, is_v2: bool) -> Dict[str, Any]:
        """Extract global configuration settings"""
        settings = {}

        if is_v2:
            settings["status"] = root.get("status", "ERROR")
            settings["monitorInterval"] = root.get("monitorInterval")
            settings["shutdownHook"] = root.get("shutdownHook", "true")
            settings["shutdownTimeout"] = root.get("shutdownTimeout")
        else:
            settings["threshold"] = root.get("threshold")
            settings["debug"] = root.get("debug", "false")

        return settings

    def _extract_v2_target(self, appender: Element) -> Optional[str]:
        """Extract target for Log4j 2.x appenders"""
        if appender.tag == "File":
            return appender.get("fileName")
        elif appender.tag == "RollingFile":
            return appender.get("fileName")
        elif appender.tag == "Console":
            return appender.get("target", "SYSTEM_OUT")
        elif appender.tag == "Socket":
            host = appender.get("host")
            port = appender.get("port")
            return f"{host}:{port}" if host and port else None
        return None

    def _extract_v1_target(self, appender: Element) -> Optional[str]:
        """Extract target for Log4j 1.x appenders"""
        for param in appender.findall(".//param"):
            param_name = param.get("name")
            if param_name in ["File", "Filename"]:
                return param.get("value")
            elif param_name == "Target":
                return param.get("value")
        return None

    def _extract_v1_type(self, class_name: str) -> str:
        """Extract appender type from Log4j 1.x class name"""
        if "ConsoleAppender" in class_name:
            return "Console"
        elif "FileAppender" in class_name:
            return "File"
        elif "RollingFileAppender" in class_name:
            return "RollingFile"
        elif "DailyRollingFileAppender" in class_name:
            return "DailyRollingFile"
        elif "SocketAppender" in class_name:
            return "Socket"
        elif "AsyncAppender" in class_name:
            return "Async"
        return "Other"

    def _extract_pattern(self, appender: Element) -> Optional[str]:
        """Extract pattern from appender layout"""
        # Log4j 2.x
        pattern_layout = appender.find(".//PatternLayout")
        if pattern_layout is not None:
            return pattern_layout.get("pattern")

        # Log4j 1.x
        layout = appender.find(".//layout")
        if layout is not None:
            param = layout.find('.//param[@name="ConversionPattern"]')
            if param is not None:
                return param.get("value")

        return None

    def _extract_appender_summary(self, root: Element, is_v2: bool) -> Dict[str, Any]:
        """Extract appender summary information"""
        appender_analysis = self._analyze_appenders(root, is_v2)
        return {
            "appender_count": appender_analysis["appender_count"],
            "appender_types": appender_analysis["appender_types"],
            "file_appenders": len(appender_analysis["file_appenders"]),
            "async_appenders": len(appender_analysis["async_appenders"]),
            "external_appenders": len(appender_analysis["external_appenders"]),
        }

    def _extract_logger_summary(self, root: Element, is_v2: bool) -> Dict[str, Any]:
        """Extract logger summary information"""
        logger_analysis = self._analyze_loggers(root, is_v2)
        return {
            "logger_count": logger_analysis["logger_count"],
            "has_root_logger": logger_analysis["root_logger"] is not None,
            "package_loggers": len(logger_analysis["package_loggers"]),
            "level_distribution": logger_analysis["level_distribution"],
        }

    def _extract_security_summary(self, root: Element) -> Dict[str, Any]:
        """Extract security summary information"""
        security_analysis = self._check_security_issues(root)
        return {
            "log4shell_vulnerable": security_analysis["log4shell_vulnerable"],
            "security_risk_count": len(security_analysis["security_risks"]),
            "external_connections": len(security_analysis["external_connections"]),
            "jndi_patterns_found": len(security_analysis["jndi_patterns"]),
        }

    def _assess_logging_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess logging configuration quality"""

        # Security quality
        security_score = 1.0
        if findings["security_concerns"]["security_risks"]:
            risk_count = len(findings["security_concerns"]["security_risks"])
            if findings["security_concerns"]["log4shell_vulnerable"]:
                security_score = 0.0  # Critical security issue
            else:
                security_score = max(0.0, 1.0 - (risk_count * 0.2))

        # Production readiness
        production_score = 0.0
        if findings["log_levels"]["production_appropriate"]:
            production_score += 0.4
        if findings["appenders"]["file_appenders"]:
            production_score += 0.3
        if not findings["performance"]["location_info_used"]:
            production_score += 0.3

        # Performance quality
        performance_score = 0.0
        if (
            findings["performance"]["async_appenders"] > 0
            or findings["performance"]["async_loggers"] > 0
        ):
            performance_score += 0.4
        if not findings["performance"]["location_info_used"]:
            performance_score += 0.3
        if len(findings["performance"]["performance_risks"]) == 0:
            performance_score += 0.3

        # Configuration completeness
        completeness_score = 0.0
        if findings["loggers"]["root_logger"] is not None:
            completeness_score += 0.4
        if findings["appenders"]["appender_count"] > 0:
            completeness_score += 0.3
        if findings["patterns"]["pattern_count"] > 0:
            completeness_score += 0.3

        return {
            "security": security_score,
            "production_ready": production_score,
            "performance": performance_score,
            "completeness": completeness_score,
            "overall": (
                security_score
                + production_score
                + performance_score
                + completeness_score
            )
            / 4,
        }
