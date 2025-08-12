#!/usr/bin/env python3
"""
JUnit/TestNG Test Report Handler

Analyzes JUnit and TestNG XML test report files to extract
test execution results, failure patterns, and test metrics.
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


class TestReportHandler(XMLHandler):
    """Handler for JUnit and TestNG test report XML files"""

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # JUnit report indicators
        if root_tag in ["testsuites", "testsuite"]:
            # Check for JUnit-specific attributes
            if root.get("tests") is not None or root.get("failures") is not None:
                return True, 1.0

        # TestNG report indicators
        if root_tag == "testng-results":
            return True, 1.0

        # Check for test-related elements
        test_indicators = ["testcase", "test-method", "test", "suite"]
        found = sum(1 for ind in test_indicators if root.find(f".//{ind}") is not None)

        if found >= 2:
            return True, min(found * 0.3, 0.9)

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        # Determine test framework
        if root_tag == "testng-results":
            framework = "TestNG"
            version = root.get("version", "unknown")
        elif root_tag in ["testsuites", "testsuite"]:
            framework = "JUnit"
            # Try to detect JUnit version
            if root.find(".//properties") is not None:
                version = "4.x"  # JUnit 4 typically has properties
            else:
                version = "5.x"  # Assume JUnit 5 for newer reports
        else:
            framework = "Generic Test Report"
            version = "unknown"

        return DocumentTypeInfo(
            type_name=f"{framework} Test Report",
            confidence=0.95,
            version=version,
            metadata={
                "framework": framework,
                "category": "test_results",
                "report_type": "execution_report",
            },
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        framework = self._determine_framework(root)

        if framework == "TestNG":
            findings = self._analyze_testng(root)
        else:
            findings = self._analyze_junit(root)

        recommendations = [
            "Analyze failure patterns for flaky tests",
            "Track test execution time trends",
            "Identify slow-running test suites",
            "Generate test coverage reports",
            "Monitor test stability over time",
            "Prioritize test maintenance efforts",
        ]

        ai_use_cases = [
            "Flaky test detection",
            "Test failure prediction",
            "Test execution optimization",
            "Root cause analysis for failures",
            "Test suite optimization",
            "Test quality metrics",
            "Regression test selection",
            "Test impact analysis",
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
                "total_tests": findings["summary"]["total"],
                "passed_tests": findings["summary"]["passed"],
                "failed_tests": findings["summary"]["failed"],
                "skipped_tests": findings["summary"]["skipped"],
                "test_suites": len(findings.get("suites", [])),
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_xml_key_data(root),
            quality_metrics=self._assess_test_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        framework = self._determine_framework(root)

        return {
            "test_summary": self._extract_test_summary(root, framework),
            "failed_tests": self._extract_failed_tests(root, framework),
            "slow_tests": self._extract_slow_tests(root, framework),
            "test_metrics": self._calculate_test_metrics(root, framework),
            "error_categories": self._categorize_errors(root, framework),
        }

    def _determine_framework(self, root: Element) -> str:
        """Determine which test framework generated the report"""
        root_tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

        if root_tag == "testng-results":
            return "TestNG"
        elif root_tag in ["testsuites", "testsuite"]:
            return "JUnit"
        else:
            return "Unknown"

    def _analyze_junit(self, root: Element) -> Dict[str, Any]:
        """Analyze JUnit test report"""
        findings = {
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "error": 0,
                "time": 0.0,
            },
            "suites": [],
            "failed_tests": [],
            "skipped_tests": [],
            "slow_tests": [],
            "execution_time": {},
        }

        # Handle both single testsuite and testsuites container
        if root.tag == "testsuites" or root.tag.endswith("}testsuites"):
            testsuites = root.findall(".//testsuite")
        else:
            testsuites = [root]

        for suite in testsuites:
            suite_info = {
                "name": suite.get("name"),
                "tests": int(suite.get("tests", 0)),
                "failures": int(suite.get("failures", 0)),
                "errors": int(suite.get("errors", 0)),
                "skipped": int(suite.get("skipped", 0)),
                "time": float(suite.get("time", 0)),
                "timestamp": suite.get("timestamp"),
                "testcases": [],
            }

            # Analyze test cases
            for testcase in suite.findall(".//testcase"):
                test_info = {
                    "name": testcase.get("name"),
                    "classname": testcase.get("classname"),
                    "time": float(testcase.get("time", 0)),
                    "status": "passed",  # Default
                }

                # Check for failures
                failure = testcase.find(".//failure")
                if failure is not None:
                    test_info["status"] = "failed"
                    test_info["failure"] = {
                        "message": failure.get("message"),
                        "type": failure.get("type"),
                        "text": failure.text[:500] if failure.text else None,
                    }
                    findings["failed_tests"].append(test_info)

                # Check for errors
                error = testcase.find(".//error")
                if error is not None:
                    test_info["status"] = "error"
                    test_info["error"] = {
                        "message": error.get("message"),
                        "type": error.get("type"),
                        "text": error.text[:500] if error.text else None,
                    }
                    findings["failed_tests"].append(test_info)

                # Check for skipped
                skipped = testcase.find(".//skipped")
                if skipped is not None:
                    test_info["status"] = "skipped"
                    test_info["skip_message"] = skipped.get("message")
                    findings["skipped_tests"].append(test_info)

                suite_info["testcases"].append(test_info)

                # Track slow tests
                if test_info["time"] > 1.0:  # Tests taking more than 1 second
                    findings["slow_tests"].append(
                        {
                            "name": test_info["name"],
                            "class": test_info["classname"],
                            "time": test_info["time"],
                        }
                    )

            findings["suites"].append(suite_info)

            # Update summary
            findings["summary"]["total"] += suite_info["tests"]
            findings["summary"]["failed"] += suite_info["failures"]
            findings["summary"]["error"] += suite_info["errors"]
            findings["summary"]["skipped"] += suite_info["skipped"]
            findings["summary"]["time"] += suite_info["time"]

        findings["summary"]["passed"] = (
            findings["summary"]["total"]
            - findings["summary"]["failed"]
            - findings["summary"]["error"]
            - findings["summary"]["skipped"]
        )

        # Sort slow tests by time
        findings["slow_tests"].sort(key=lambda x: x["time"], reverse=True)

        return findings

    def _analyze_testng(self, root: Element) -> Dict[str, Any]:
        """Analyze TestNG test report"""
        findings = {
            "summary": {
                "total": int(root.get("total", 0)),
                "passed": int(root.get("passed", 0)),
                "failed": int(root.get("failed", 0)),
                "skipped": int(root.get("skipped", 0)),
                "error": 0,  # TestNG doesn't separate errors
                "time": 0.0,
            },
            "suites": [],
            "failed_tests": [],
            "skipped_tests": [],
            "slow_tests": [],
            "test_groups": {},
        }

        # Analyze suites
        for suite in root.findall(".//suite"):
            suite_info = {
                "name": suite.get("name"),
                "duration": float(suite.get("duration-ms", 0))
                / 1000,  # Convert to seconds
                "started_at": suite.get("started-at"),
                "finished_at": suite.get("finished-at"),
                "tests": [],
            }

            # Analyze tests within suite
            for test in suite.findall(".//test"):
                test_info = {
                    "name": test.get("name"),
                    "duration": float(test.get("duration-ms", 0)) / 1000,
                    "test_methods": [],
                }

                # Analyze test methods
                for method in test.findall(".//test-method"):
                    method_info = {
                        "name": method.get("name"),
                        "signature": method.get("signature"),
                        "status": method.get("status"),
                        "duration": float(method.get("duration-ms", 0)) / 1000,
                        "started_at": method.get("started-at"),
                        "finished_at": method.get("finished-at"),
                    }

                    # Extract groups
                    groups = method.find(".//groups")
                    if groups is not None:
                        method_info["groups"] = [
                            g.get("name") for g in groups.findall(".//group")
                        ]
                        # Track group statistics
                        for group_name in method_info["groups"]:
                            if group_name not in findings["test_groups"]:
                                findings["test_groups"][group_name] = {
                                    "total": 0,
                                    "passed": 0,
                                    "failed": 0,
                                }
                            findings["test_groups"][group_name]["total"] += 1
                            if method_info["status"] == "PASS":
                                findings["test_groups"][group_name]["passed"] += 1
                            elif method_info["status"] == "FAIL":
                                findings["test_groups"][group_name]["failed"] += 1

                    # Track failures
                    if method_info["status"] == "FAIL":
                        exception = method.find(".//exception")
                        if exception is not None:
                            method_info["exception"] = {
                                "class": exception.get("class"),
                                "message": self._get_child_text(exception, "message"),
                                "stacktrace": self._get_child_text(
                                    exception, "full-stacktrace", ""
                                )[:500],
                            }
                        findings["failed_tests"].append(method_info)

                    # Track skipped
                    elif method_info["status"] == "SKIP":
                        findings["skipped_tests"].append(method_info)

                    # Track slow tests
                    if method_info["duration"] > 1.0:
                        findings["slow_tests"].append(
                            {
                                "name": method_info["name"],
                                "signature": method_info["signature"],
                                "time": method_info["duration"],
                            }
                        )

                    test_info["test_methods"].append(method_info)

                suite_info["tests"].append(test_info)
                findings["summary"]["time"] += test_info["duration"]

            findings["suites"].append(suite_info)

        # Sort slow tests
        findings["slow_tests"].sort(key=lambda x: x["time"], reverse=True)

        return findings

    def _extract_test_summary(self, root: Element, framework: str) -> Dict[str, Any]:
        """Extract test execution summary"""
        if framework == "TestNG":
            return {
                "total": int(root.get("total", 0)),
                "passed": int(root.get("passed", 0)),
                "failed": int(root.get("failed", 0)),
                "skipped": int(root.get("skipped", 0)),
                "duration_ms": sum(
                    float(s.get("duration-ms", 0)) for s in root.findall(".//suite")
                ),
            }
        else:  # JUnit
            summary = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "duration_seconds": 0.0,
            }

            for suite in root.findall(".//testsuite"):
                summary["total"] += int(suite.get("tests", 0))
                summary["failed"] += int(suite.get("failures", 0))
                summary["errors"] += int(suite.get("errors", 0))
                summary["skipped"] += int(suite.get("skipped", 0))
                summary["duration_seconds"] += float(suite.get("time", 0))

            summary["passed"] = (
                summary["total"]
                - summary["failed"]
                - summary["errors"]
                - summary["skipped"]
            )

            return summary

    def _extract_failed_tests(
        self, root: Element, framework: str
    ) -> List[Dict[str, Any]]:
        """Extract details of failed tests"""
        failed_tests = []

        if framework == "TestNG":
            for method in root.findall('.//test-method[@status="FAIL"]'):
                exception = method.find(".//exception")
                failed_tests.append(
                    {
                        "name": method.get("name"),
                        "signature": method.get("signature"),
                        "duration_ms": float(method.get("duration-ms", 0)),
                        "exception_class": (
                            exception.get("class") if exception is not None else None
                        ),
                        "message": (
                            self._get_child_text(exception, "message")
                            if exception is not None
                            else None
                        ),
                    }
                )
        else:  # JUnit
            for testcase in root.findall(".//testcase"):
                failure = testcase.find(".//failure")
                error = testcase.find(".//error")

                if failure is not None or error is not None:
                    fail_elem = failure if failure is not None else error
                    failed_tests.append(
                        {
                            "name": testcase.get("name"),
                            "classname": testcase.get("classname"),
                            "time": float(testcase.get("time", 0)),
                            "failure_type": fail_elem.get("type"),
                            "message": fail_elem.get("message"),
                            "text": fail_elem.text[:200] if fail_elem.text else None,
                        }
                    )

        return failed_tests[:50]  # Limit to first 50

    def _extract_slow_tests(
        self, root: Element, framework: str, threshold: float = 1.0
    ) -> List[Dict[str, Any]]:
        """Extract slow-running tests"""
        slow_tests = []

        if framework == "TestNG":
            for method in root.findall(".//test-method"):
                duration = (
                    float(method.get("duration-ms", 0)) / 1000
                )  # Convert to seconds
                if duration > threshold:
                    slow_tests.append(
                        {
                            "name": method.get("name"),
                            "signature": method.get("signature"),
                            "duration_seconds": duration,
                            "status": method.get("status"),
                        }
                    )
        else:  # JUnit
            for testcase in root.findall(".//testcase"):
                time = float(testcase.get("time", 0))
                if time > threshold:
                    slow_tests.append(
                        {
                            "name": testcase.get("name"),
                            "classname": testcase.get("classname"),
                            "duration_seconds": time,
                        }
                    )

        # Sort by duration descending
        slow_tests.sort(key=lambda x: x["duration_seconds"], reverse=True)

        return slow_tests[:20]  # Top 20 slowest

    def _calculate_test_metrics(self, root: Element, framework: str) -> Dict[str, Any]:
        """Calculate various test metrics"""
        metrics = {
            "success_rate": 0.0,
            "average_test_time": 0.0,
            "total_execution_time": 0.0,
            "test_distribution": {},
            "failure_rate_by_suite": {},
        }

        # Get summary stats
        summary = self._extract_test_summary(root, framework)

        # Calculate success rate
        if summary["total"] > 0:
            metrics["success_rate"] = summary["passed"] / summary["total"]

        # Calculate average test time
        if framework == "TestNG":
            test_count = 0
            total_time = 0
            for method in root.findall(".//test-method"):
                test_count += 1
                total_time += float(method.get("duration-ms", 0)) / 1000

            if test_count > 0:
                metrics["average_test_time"] = total_time / test_count
            metrics["total_execution_time"] = total_time
        else:  # JUnit
            test_count = summary["total"]
            total_time = summary["duration_seconds"]

            if test_count > 0:
                metrics["average_test_time"] = total_time / test_count
            metrics["total_execution_time"] = total_time

        # Test distribution by status
        metrics["test_distribution"] = {
            "passed": summary["passed"],
            "failed": summary.get("failed", 0),
            "skipped": summary.get("skipped", 0),
            "error": summary.get("errors", 0),
        }

        # Failure rate by suite
        if framework == "TestNG":
            for suite in root.findall(".//suite"):
                suite_name = suite.get("name")
                suite_stats = {"total": 0, "failed": 0}

                for method in suite.findall(".//test-method"):
                    suite_stats["total"] += 1
                    if method.get("status") == "FAIL":
                        suite_stats["failed"] += 1

                if suite_stats["total"] > 0:
                    metrics["failure_rate_by_suite"][suite_name] = (
                        suite_stats["failed"] / suite_stats["total"]
                    )
        else:  # JUnit
            for suite in root.findall(".//testsuite"):
                suite_name = suite.get("name")
                total = int(suite.get("tests", 0))
                failed = int(suite.get("failures", 0)) + int(suite.get("errors", 0))

                if total > 0:
                    metrics["failure_rate_by_suite"][suite_name] = failed / total

        return metrics

    def _categorize_errors(
        self, root: Element, framework: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize test failures by error type"""
        error_categories = {
            "assertion_errors": [],
            "null_pointer": [],
            "timeout": [],
            "setup_errors": [],
            "other": [],
        }

        if framework == "TestNG":
            for method in root.findall('.//test-method[@status="FAIL"]'):
                exception = method.find(".//exception")
                if exception is not None:
                    error_info = {
                        "test": method.get("name"),
                        "exception_class": exception.get("class"),
                        "message": self._get_child_text(exception, "message"),
                    }

                    self._categorize_single_error(error_info, error_categories)
        else:  # JUnit
            for testcase in root.findall(".//testcase"):
                failure = testcase.find(".//failure")
                error = testcase.find(".//error")

                if failure is not None or error is not None:
                    fail_elem = failure if failure is not None else error
                    error_info = {
                        "test": testcase.get("name"),
                        "class": testcase.get("classname"),
                        "exception_class": fail_elem.get("type"),
                        "message": fail_elem.get("message"),
                    }

                    self._categorize_single_error(error_info, error_categories)

        # Limit each category
        for category in error_categories:
            error_categories[category] = error_categories[category][:10]

        return error_categories

    def _categorize_single_error(
        self, error_info: Dict[str, Any], categories: Dict[str, List]
    ):
        """Categorize a single error"""
        exception_class = error_info.get("exception_class", "").lower()
        message = (error_info.get("message") or "").lower()

        if "assert" in exception_class or "assert" in message:
            categories["assertion_errors"].append(error_info)
        elif "nullpointer" in exception_class or "null pointer" in message:
            categories["null_pointer"].append(error_info)
        elif "timeout" in exception_class or "timeout" in message:
            categories["timeout"].append(error_info)
        elif (
            "setup" in message
            or "before" in exception_class
            or "after" in exception_class
        ):
            categories["setup_errors"].append(error_info)
        else:
            categories["other"].append(error_info)

    def _assess_test_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess test suite quality metrics"""
        # Test coverage (based on success rate)
        success_rate = 0.0
        if findings["summary"]["total"] > 0:
            success_rate = findings["summary"]["passed"] / findings["summary"]["total"]

        # Test stability (inverse of failure rate)
        stability = success_rate

        # Performance (based on slow tests)
        performance = 1.0
        if findings["summary"]["total"] > 0:
            slow_test_ratio = len(findings["slow_tests"]) / findings["summary"]["total"]
            performance = max(0, 1.0 - slow_test_ratio * 2)  # Penalize if >50% are slow

        # Test maintenance (based on skip rate)
        maintenance = 1.0
        if findings["summary"]["total"] > 0:
            skip_ratio = findings["summary"]["skipped"] / findings["summary"]["total"]
            maintenance = max(0, 1.0 - skip_ratio * 2)  # Penalize if >50% are skipped

        # Flakiness indicator (would need historical data for accurate measurement)
        # For now, use a simple heuristic based on error types
        flakiness_score = 0.8  # Default to good
        if "failed_tests" in findings:
            timeout_failures = sum(
                1
                for test in findings["failed_tests"]
                if "timeout" in str(test.get("failure", {}).get("type", "")).lower()
            )
            if timeout_failures > 2:
                flakiness_score = 0.4

        return {
            "success_rate": success_rate,
            "stability": stability,
            "performance": performance,
            "maintenance": maintenance,
            "flakiness": flakiness_score,
            "overall": (
                success_rate + stability + performance + maintenance + flakiness_score
            )
            / 5,
        }

    def _get_child_text(
        self, parent: Element, child_name: str, default: str = None
    ) -> Optional[str]:
        """Get text content of a child element"""
        if parent is None:
            return default

        child = parent.find(f".//{child_name}")
        return child.text if child is not None and child.text else default
