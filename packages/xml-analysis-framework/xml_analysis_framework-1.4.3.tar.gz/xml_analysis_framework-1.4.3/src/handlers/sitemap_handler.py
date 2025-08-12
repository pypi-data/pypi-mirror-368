#!/usr/bin/env python3
"""
Sitemap Handler

Analyzes XML sitemap files for SEO optimization, URL structure analysis,
content indexing patterns, and website health monitoring.
"""

import sys
import os
from typing import Dict, List, Any, Tuple, TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element
else:
    Element = Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..base import XMLHandler, DocumentTypeInfo, SpecializedAnalysis  # noqa: E402


class SitemapHandler(XMLHandler):
    """Handler for XML sitemap files"""

    SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"

    def can_handle_xml(
        self, root: Element, namespaces: Dict[str, str]
    ) -> Tuple[bool, float]:
        # Check for sitemap namespace
        if "sitemaps.org/schemas/sitemap" in str(namespaces.values()):
            return True, 1.0

        # Check for urlset or sitemapindex root
        tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if tag in ["urlset", "sitemapindex"]:
            return True, 0.8

        return False, 0.0

    def detect_xml_type(
        self, root: Element, namespaces: Dict[str, str]
    ) -> DocumentTypeInfo:
        tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        is_index = tag == "sitemapindex"

        metadata = {
            "standard": "Sitemaps.org Protocol",
            "category": "seo_indexing",
            "sitemap_type": "index" if is_index else "urlset",
            "namespace_uri": self.SITEMAP_NAMESPACE,
            "element_count": len(list(root.iter())),
        }

        return DocumentTypeInfo(
            type_name="XML Sitemap" + (" Index" if is_index else ""),
            confidence=1.0,
            version="0.9",
            schema_uri=self.SITEMAP_NAMESPACE,
            metadata=metadata,
        )

    def analyze_xml(self, root: Element, file_path: str) -> SpecializedAnalysis:
        tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        is_index = tag == "sitemapindex"

        findings = {
            "sitemap_info": {
                "type": "index" if is_index else "urlset",
                "namespace": self._extract_namespace_info(root),
                "file_path": file_path,
            },
            "content_analysis": (
                self._analyze_sitemap_index(root)
                if is_index
                else self._analyze_url_sitemap(root)
            ),
            "seo_analysis": self._analyze_seo_aspects(root, is_index),
            "technical_analysis": self._analyze_technical_aspects(root, is_index),
            "quality_indicators": self._analyze_quality_indicators(root, is_index),
            "accessibility_analysis": self._analyze_accessibility(root, is_index),
            "performance_analysis": self._analyze_performance_aspects(root, is_index),
            "compliance_analysis": self._analyze_compliance(root, is_index),
            "security_analysis": self._analyze_security_aspects(root),
            "optimization_opportunities": self._identify_optimization_opportunities(
                root, is_index
            ),
        }

        recommendations = [
            "Validate all URLs for accessibility and response codes",
            "Check for outdated or broken links regularly",
            "Analyze URL patterns for SEO optimization opportunities",
            "Monitor change frequencies against actual content updates",
            "Ensure proper priority distribution across content types",
            "Validate sitemap size limits (50,000 URLs max)",
            "Review last modification dates for accuracy",
            "Optimize sitemap structure for search engine crawling",
            "Implement sitemap index for large sites (>50,000 URLs)",
        ]

        ai_use_cases = [
            "SEO health monitoring and optimization",
            "Content update pattern analysis and prediction",
            "Website structure visualization and mapping",
            "Broken link detection and automated fixing",
            "Content priority optimization based on analytics",
            "Crawl budget optimization analysis",
            "Duplicate content detection across URL patterns",
            "Sitemap performance monitoring and alerting",
            "Automated sitemap generation and maintenance",
            "SEO competitive analysis and benchmarking",
        ]

        # Calculate data inventory
        if is_index:
            data_inventory = {
                "sitemaps": findings["content_analysis"].get("sitemap_count", 0),
                "total_elements": len(list(root.iter())),
                "last_modified_entries": len(
                    [
                        s
                        for s in findings["content_analysis"].get("sitemap_details", [])
                        if s.get("lastmod")
                    ]
                ),
            }
        else:
            data_inventory = {
                "urls": findings["content_analysis"].get("url_count", 0),
                "priority_entries": sum(
                    findings["content_analysis"].get("priorities", {}).values()
                ),
                "changefreq_entries": sum(
                    findings["content_analysis"].get("change_frequencies", {}).values()
                ),
                "lastmod_entries": findings["content_analysis"]
                .get("last_modified", {})
                .get("count", 0),
                "unique_domains": len(
                    findings["content_analysis"]
                    .get("url_patterns", {})
                    .get("domains", [])
                ),
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
            quality_metrics=self._assess_sitemap_quality(findings),
        )

    def extract_xml_key_data(self, root: Element) -> Dict[str, Any]:
        tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        is_index = tag == "sitemapindex"

        return {
            "sitemap_metadata": {
                "type": "index" if is_index else "urlset",
                "namespace": self.SITEMAP_NAMESPACE,
                "total_entries": len(
                    root.findall(
                        f'.//{{{self.SITEMAP_NAMESPACE}}}{"sitemap" if is_index else "url"}'
                    )
                ),
            },
            "content_summary": self._extract_content_summary(root, is_index),
            "seo_summary": self._extract_seo_summary(root, is_index),
            "technical_summary": self._extract_technical_summary(root, is_index),
        }

    def _extract_namespace_info(self, root: Element) -> Dict[str, Any]:
        """Extract namespace information"""
        namespaces = {}
        for key, value in root.attrib.items():
            if key.startswith("xmlns"):
                prefix = key.split(":", 1)[1] if ":" in key else "default"
                namespaces[prefix] = value

        return {
            "declared_namespaces": namespaces,
            "sitemap_namespace": self.SITEMAP_NAMESPACE in str(namespaces.values()),
            "schema_version": "0.9",  # Standard sitemap version
        }

    def _analyze_url_sitemap(self, root: Element) -> Dict[str, Any]:
        """Analyze URL sitemap content"""
        urls = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}url")

        findings = {
            "url_count": len(urls),
            "url_details": self._extract_url_details(
                urls[:1000]
            ),  # First 1000 for performance
            "priorities": self._analyze_priorities(urls),
            "change_frequencies": self._analyze_changefreqs(urls),
            "last_modified": self._analyze_lastmod(urls),
            "url_patterns": self._analyze_url_patterns(urls),
            "size_analysis": self._analyze_sitemap_size(root, urls),
        }

        return findings

    def _analyze_sitemap_index(self, root: Element) -> Dict[str, Any]:
        """Analyze sitemap index content"""
        sitemaps = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}sitemap")

        findings = {
            "sitemap_count": len(sitemaps),
            "sitemap_details": self._extract_sitemap_details(sitemaps),
            "last_modified": self._analyze_sitemap_dates(sitemaps),
            "size_distribution": self._analyze_index_size_distribution(sitemaps),
        }

        return findings

    def _analyze_seo_aspects(self, root: Element, is_index: bool) -> Dict[str, Any]:
        """Analyze SEO-related aspects"""
        seo_analysis = {
            "priority_distribution": {},
            "changefreq_distribution": {},
            "content_freshness": {},
            "url_structure_seo": {},
            "crawl_optimization": {},
        }

        if not is_index:
            urls = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}url")

            # Priority distribution analysis
            priorities = self._analyze_priorities(urls)
            total_urls = len(urls)
            seo_analysis["priority_distribution"] = {
                "distribution": priorities,
                "average_priority": self._calculate_average_priority(urls),
                "high_priority_count": sum(
                    v for k, v in priorities.items() if float(k) >= 0.8
                ),
                "low_priority_count": sum(
                    v for k, v in priorities.items() if float(k) <= 0.3
                ),
            }

            # Change frequency analysis
            changefreqs = self._analyze_changefreqs(urls)
            seo_analysis["changefreq_distribution"] = {
                "distribution": changefreqs,
                "most_common": (
                    max(changefreqs.items(), key=lambda x: x[1])[0]
                    if changefreqs
                    else None
                ),
                "update_pattern_consistency": self._analyze_update_patterns(urls),
            }

            # Content freshness analysis
            lastmod_data = self._analyze_lastmod(urls)
            seo_analysis["content_freshness"] = {
                "urls_with_lastmod": lastmod_data.get("count", 0),
                "freshness_percentage": (
                    (lastmod_data.get("count", 0) / total_urls * 100)
                    if total_urls > 0
                    else 0
                ),
                "date_range": {
                    "oldest": lastmod_data.get("oldest"),
                    "newest": lastmod_data.get("latest"),
                },
            }

            # URL structure SEO analysis
            url_patterns = self._analyze_url_patterns(urls)
            seo_analysis["url_structure_seo"] = {
                "domain_consistency": len(url_patterns.get("domains", [])) == 1,
                "depth_distribution": url_patterns.get("depth_levels", {}),
                "seo_friendly_structure": self._assess_url_seo_friendliness(urls),
            }

        return seo_analysis

    def _analyze_technical_aspects(
        self, root: Element, is_index: bool
    ) -> Dict[str, Any]:
        """Analyze technical aspects of the sitemap"""
        technical = {
            "file_size": self._estimate_file_size(root),
            "compression_recommended": False,
            "namespace_compliance": True,
            "schema_validation": {},
            "encoding_analysis": {},
        }

        # Check if compression is recommended (>10KB estimated size)
        technical["compression_recommended"] = technical["file_size"] > 10000

        # Validate namespace usage
        technical["namespace_compliance"] = self._validate_namespace_usage(root)

        # Schema validation
        technical["schema_validation"] = self._validate_schema_compliance(
            root, is_index
        )

        return technical

    def _analyze_quality_indicators(
        self, root: Element, is_index: bool
    ) -> Dict[str, Any]:
        """Analyze quality indicators"""
        quality = {
            "completeness_score": 0.0,
            "consistency_score": 0.0,
            "best_practices_score": 0.0,
            "recommendations": [],
        }

        if not is_index:
            urls = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}url")
            total_urls = len(urls)

            if total_urls > 0:
                # Completeness score
                urls_with_priority = sum(
                    1
                    for url in urls
                    if url.find(f".//{{{self.SITEMAP_NAMESPACE}}}priority") is not None
                )
                urls_with_changefreq = sum(
                    1
                    for url in urls
                    if url.find(f".//{{{self.SITEMAP_NAMESPACE}}}changefreq")
                    is not None
                )
                urls_with_lastmod = sum(
                    1
                    for url in urls
                    if url.find(f".//{{{self.SITEMAP_NAMESPACE}}}lastmod") is not None
                )

                quality["completeness_score"] = (
                    (urls_with_priority / total_urls * 0.3)
                    + (urls_with_changefreq / total_urls * 0.3)
                    + (urls_with_lastmod / total_urls * 0.4)
                )

                # Consistency score
                quality["consistency_score"] = self._calculate_consistency_score(urls)

                # Best practices score
                quality["best_practices_score"] = self._calculate_best_practices_score(
                    urls, total_urls
                )

        # Generate recommendations
        if quality["completeness_score"] < 0.7:
            quality["recommendations"].append(
                "Add missing lastmod, priority, or changefreq elements"
            )
        if quality["consistency_score"] < 0.8:
            quality["recommendations"].append(
                "Improve consistency in priority and changefreq values"
            )

        return quality

    def _analyze_accessibility(self, root: Element, is_index: bool) -> Dict[str, Any]:
        """Analyze accessibility of URLs in sitemap"""
        accessibility = {
            "protocol_analysis": {},
            "url_validity": {},
            "potential_issues": [],
        }

        if not is_index:
            urls = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}url")

            # Protocol analysis
            protocols = {}
            for url in urls[:1000]:  # Analyze first 1000
                loc_elem = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc")
                if loc_elem is not None and loc_elem.text:
                    protocol = urlparse(loc_elem.text).scheme
                    protocols[protocol] = protocols.get(protocol, 0) + 1

            accessibility["protocol_analysis"] = {
                "protocols_used": protocols,
                "https_percentage": (
                    (protocols.get("https", 0) / sum(protocols.values()) * 100)
                    if protocols
                    else 0
                ),
                "mixed_protocols": len(protocols) > 1,
            }

            # URL validity checks
            accessibility["url_validity"] = self._check_url_validity(
                urls[:100]
            )  # Check first 100

            # Identify potential issues
            if protocols.get("http", 0) > 0:
                accessibility["potential_issues"].append("Contains non-HTTPS URLs")
            if accessibility["url_validity"]["invalid_urls"] > 0:
                accessibility["potential_issues"].append(
                    "Contains potentially invalid URLs"
                )

        return accessibility

    def _analyze_performance_aspects(
        self, root: Element, is_index: bool
    ) -> Dict[str, Any]:
        """Analyze performance-related aspects"""
        performance = {
            "size_optimization": {},
            "crawl_efficiency": {},
            "recommendations": [],
        }

        total_elements = len(list(root.iter()))

        # Size optimization
        performance["size_optimization"] = {
            "total_elements": total_elements,
            "estimated_size": self._estimate_file_size(root),
            "compression_savings": self._estimate_compression_savings(root),
            "size_limit_compliance": total_elements <= 50000,  # Standard sitemap limit
        }

        if not is_index:
            urls = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}url")

            # Crawl efficiency
            performance["crawl_efficiency"] = {
                "url_density": len(urls) / total_elements,
                "priority_optimization": self._analyze_priority_optimization(urls),
                "changefreq_accuracy": self._analyze_changefreq_accuracy(urls),
            }

        # Generate recommendations
        if not performance["size_optimization"]["size_limit_compliance"]:
            performance["recommendations"].append(
                "Split sitemap - exceeds 50,000 URL limit"
            )
        if (
            performance["size_optimization"]["estimated_size"] > 50 * 1024 * 1024
        ):  # 50MB
            performance["recommendations"].append(
                "Sitemap file size exceeds 50MB limit"
            )

        return performance

    def _analyze_compliance(self, root: Element, is_index: bool) -> Dict[str, Any]:
        """Analyze compliance with sitemap protocol"""
        compliance = {
            "protocol_version": "0.9",
            "namespace_compliance": True,
            "required_elements": {},
            "optional_elements": {},
            "violations": [],
        }

        # Check namespace compliance
        compliance["namespace_compliance"] = self._validate_namespace_usage(root)

        if not is_index:
            urls = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}url")

            # Check required elements
            urls_with_loc = sum(
                1
                for url in urls
                if url.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc") is not None
            )
            compliance["required_elements"] = {
                "loc_present": urls_with_loc,
                "loc_compliance": urls_with_loc == len(urls),
            }

            # Check optional elements
            compliance["optional_elements"] = {
                "lastmod_usage": sum(
                    1
                    for url in urls
                    if url.find(f".//{{{self.SITEMAP_NAMESPACE}}}lastmod") is not None
                ),
                "changefreq_usage": sum(
                    1
                    for url in urls
                    if url.find(f".//{{{self.SITEMAP_NAMESPACE}}}changefreq")
                    is not None
                ),
                "priority_usage": sum(
                    1
                    for url in urls
                    if url.find(f".//{{{self.SITEMAP_NAMESPACE}}}priority") is not None
                ),
            }

            # Check for violations
            if not compliance["required_elements"]["loc_compliance"]:
                compliance["violations"].append(
                    "Some URLs missing required <loc> element"
                )

        return compliance

    def _analyze_security_aspects(self, root: Element) -> Dict[str, Any]:
        """Analyze security aspects"""
        security = {
            "exposed_information": [],
            "url_security": {},
            "recommendations": [],
        }

        # Check for potentially sensitive information in URLs
        urls = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}url")
        for url in urls[:100]:  # Check first 100
            loc_elem = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc")
            if loc_elem is not None and loc_elem.text:
                url_text = loc_elem.text.lower()
                if any(
                    pattern in url_text
                    for pattern in ["admin", "private", "test", "staging", "dev"]
                ):
                    security["exposed_information"].append(
                        "Potentially sensitive URLs detected"
                    )
                    break

        # URL security analysis
        security["url_security"] = {
            "https_usage": self._count_https_urls(urls),
            "total_urls": len(urls),
        }

        # Generate recommendations
        if security["exposed_information"]:
            security["recommendations"].append(
                "Review URLs for sensitive information exposure"
            )

        https_percentage = (
            (
                security["url_security"]["https_usage"]
                / security["url_security"]["total_urls"]
                * 100
            )
            if security["url_security"]["total_urls"] > 0
            else 0
        )
        if https_percentage < 100:
            security["recommendations"].append("Consider migrating all URLs to HTTPS")

        return security

    def _identify_optimization_opportunities(
        self, root: Element, is_index: bool
    ) -> Dict[str, Any]:
        """Identify optimization opportunities"""
        opportunities = {
            "seo_opportunities": [],
            "technical_opportunities": [],
            "maintenance_opportunities": [],
        }

        if not is_index:
            urls = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}url")
            total_urls = len(urls)

            # SEO opportunities
            priorities = self._analyze_priorities(urls)
            if not priorities:
                opportunities["seo_opportunities"].append(
                    "Add priority values to guide search engine crawling"
                )

            changefreqs = self._analyze_changefreqs(urls)
            if not changefreqs:
                opportunities["seo_opportunities"].append(
                    "Add changefreq values to optimize crawl frequency"
                )

            lastmod_data = self._analyze_lastmod(urls)
            if lastmod_data.get("count", 0) < total_urls * 0.5:
                opportunities["seo_opportunities"].append(
                    "Add lastmod dates to improve crawl efficiency"
                )

            # Technical opportunities
            if total_urls > 10000:
                opportunities["technical_opportunities"].append(
                    "Consider splitting into multiple sitemaps for better performance"
                )

            # Maintenance opportunities
            if lastmod_data.get("count", 0) > 0:
                opportunities["maintenance_opportunities"].append(
                    "Implement automated lastmod date updates"
                )

        return opportunities

    def _extract_url_details(self, urls: List[Element]) -> List[Dict[str, Any]]:
        """Extract detailed information for URLs"""
        url_details = []

        for url in urls:
            url_data = {}

            loc = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc")
            if loc is not None and loc.text:
                url_data["loc"] = loc.text

                # Parse URL components
                parsed = urlparse(loc.text)
                url_data["domain"] = parsed.netloc
                url_data["path"] = parsed.path
                url_data["scheme"] = parsed.scheme
                url_data["depth"] = len([p for p in parsed.path.split("/") if p])

            lastmod = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}lastmod")
            if lastmod is not None and lastmod.text:
                url_data["lastmod"] = lastmod.text

            changefreq = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}changefreq")
            if changefreq is not None and changefreq.text:
                url_data["changefreq"] = changefreq.text

            priority = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}priority")
            if priority is not None and priority.text:
                url_data["priority"] = float(priority.text)

            url_details.append(url_data)

        return url_details

    def _extract_sitemap_details(self, sitemaps: List[Element]) -> List[Dict[str, Any]]:
        """Extract detailed information for sitemaps in index"""
        sitemap_details = []

        for sitemap in sitemaps:
            sitemap_data = {}

            loc = sitemap.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc")
            if loc is not None and loc.text:
                sitemap_data["loc"] = loc.text

            lastmod = sitemap.find(f".//{{{self.SITEMAP_NAMESPACE}}}lastmod")
            if lastmod is not None and lastmod.text:
                sitemap_data["lastmod"] = lastmod.text

            sitemap_details.append(sitemap_data)

        return sitemap_details

    def _analyze_priorities(self, urls: List[Element]) -> Dict[str, int]:
        """Analyze priority distribution"""
        priorities = {}

        for url in urls:
            priority = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}priority")
            if priority is not None and priority.text:
                p_value = priority.text
                priorities[p_value] = priorities.get(p_value, 0) + 1

        return priorities

    def _analyze_changefreqs(self, urls: List[Element]) -> Dict[str, int]:
        """Analyze change frequency distribution"""
        frequencies = {}

        for url in urls:
            changefreq = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}changefreq")
            if changefreq is not None and changefreq.text:
                freq = changefreq.text
                frequencies[freq] = frequencies.get(freq, 0) + 1

        return frequencies

    def _analyze_lastmod(self, urls: List[Element]) -> Dict[str, Any]:
        """Analyze last modification dates"""
        dates = []

        for url in urls:
            lastmod = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}lastmod")
            if lastmod is not None and lastmod.text:
                dates.append(lastmod.text)

        if dates:
            return {
                "count": len(dates),
                "latest": max(dates),
                "oldest": min(dates),
                "coverage_percentage": len(dates) / len(urls) * 100,
            }

        return {"count": 0}

    def _analyze_url_patterns(self, urls: List[Element]) -> Dict[str, Any]:
        """Analyze URL patterns and structure"""
        patterns = {
            "domains": set(),
            "extensions": {},
            "depth_levels": {},
            "path_patterns": {},
        }

        for url in urls[:1000]:  # Analyze first 1000 URLs for performance
            loc = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc")
            if loc is not None and loc.text:
                parsed = urlparse(loc.text)

                # Extract domain
                patterns["domains"].add(parsed.netloc)

                # Count depth
                path_parts = [p for p in parsed.path.split("/") if p]
                depth = len(path_parts)
                patterns["depth_levels"][depth] = (
                    patterns["depth_levels"].get(depth, 0) + 1
                )

                # Analyze extensions
                if "." in parsed.path:
                    ext = parsed.path.split(".")[-1].lower()
                    if len(ext) <= 4:  # Reasonable extension length
                        patterns["extensions"][ext] = (
                            patterns["extensions"].get(ext, 0) + 1
                        )

                # Analyze path patterns
                if path_parts:
                    first_segment = path_parts[0]
                    patterns["path_patterns"][first_segment] = (
                        patterns["path_patterns"].get(first_segment, 0) + 1
                    )

        patterns["domains"] = list(patterns["domains"])
        return patterns

    def _analyze_sitemap_dates(self, sitemaps: List[Element]) -> Dict[str, Any]:
        """Analyze sitemap modification dates"""
        dates = []

        for sitemap in sitemaps:
            lastmod = sitemap.find(f".//{{{self.SITEMAP_NAMESPACE}}}lastmod")
            if lastmod is not None and lastmod.text:
                dates.append(lastmod.text)

        if dates:
            return {"count": len(dates), "latest": max(dates), "oldest": min(dates)}

        return {"count": 0}

    def _analyze_sitemap_size(
        self, root: Element, urls: List[Element]
    ) -> Dict[str, Any]:
        """Analyze sitemap size characteristics"""
        return {
            "url_count": len(urls),
            "total_elements": len(list(root.iter())),
            "estimated_file_size": self._estimate_file_size(root),
            "size_limit_compliance": len(urls) <= 50000,
            "compression_recommended": self._estimate_file_size(root) > 10000,
        }

    def _analyze_index_size_distribution(
        self, sitemaps: List[Element]
    ) -> Dict[str, Any]:
        """Analyze size distribution in sitemap index"""
        return {
            "sitemap_count": len(sitemaps),
            "estimated_total_size": len(sitemaps) * 1000,  # Rough estimate
            "index_efficiency": min(len(sitemaps) / 1000, 1.0),  # Efficiency score
        }

    def _calculate_average_priority(self, urls: List[Element]) -> float:
        """Calculate average priority value"""
        priorities = []
        for url in urls:
            priority = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}priority")
            if priority is not None and priority.text:
                try:
                    priorities.append(float(priority.text))
                except ValueError:
                    continue

        return sum(priorities) / len(priorities) if priorities else 0.5

    def _analyze_update_patterns(self, urls: List[Element]) -> float:
        """Analyze consistency of update patterns"""
        # Simplified consistency score based on changefreq distribution
        changefreqs = self._analyze_changefreqs(urls)
        if not changefreqs:
            return 0.0

        _ = sum(changefreqs.values())  # Total for potential future analysis
        # More consistent if fewer different frequencies are used
        return 1.0 - (len(changefreqs) - 1) / 6  # 6 is max reasonable changefreq types

    def _assess_url_seo_friendliness(self, urls: List[Element]) -> Dict[str, Any]:
        """Assess SEO friendliness of URL structure"""
        seo_analysis = {
            "readable_urls": 0,
            "short_urls": 0,
            "parameterized_urls": 0,
            "total_analyzed": 0,
        }

        for url in urls[:100]:  # Analyze first 100
            loc = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc")
            if loc is not None and loc.text:
                url_text = loc.text
                seo_analysis["total_analyzed"] += 1

                # Check if URL is readable (no excessive parameters)
                if "?" not in url_text or url_text.count("&") <= 2:
                    seo_analysis["readable_urls"] += 1

                # Check URL length
                if len(url_text) <= 100:
                    seo_analysis["short_urls"] += 1

                # Count parameterized URLs
                if "?" in url_text:
                    seo_analysis["parameterized_urls"] += 1

        return seo_analysis

    def _estimate_file_size(self, root: Element) -> int:
        """Estimate file size in bytes"""
        # Rough estimation based on element count and average element size
        element_count = len(list(root.iter()))
        return element_count * 150  # Average 150 bytes per element

    def _validate_namespace_usage(self, root: Element) -> bool:
        """Validate proper namespace usage"""
        return self.SITEMAP_NAMESPACE in root.tag or "xmlns" in root.attrib

    def _validate_schema_compliance(
        self, root: Element, is_index: bool
    ) -> Dict[str, Any]:
        """Validate schema compliance"""
        compliance = {
            "required_elements_present": True,
            "valid_element_structure": True,
            "namespace_correct": self._validate_namespace_usage(root),
        }

        expected_child = "sitemap" if is_index else "url"
        children = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}{expected_child}")

        compliance["required_elements_present"] = len(children) > 0

        return compliance

    def _estimate_compression_savings(self, root: Element) -> Dict[str, Any]:
        """Estimate compression savings"""
        estimated_size = self._estimate_file_size(root)
        return {
            "uncompressed_size": estimated_size,
            "estimated_compressed_size": int(
                estimated_size * 0.1
            ),  # XML compresses well
            "estimated_savings": int(estimated_size * 0.9),
        }

    def _analyze_priority_optimization(self, urls: List[Element]) -> Dict[str, Any]:
        """Analyze priority optimization"""
        priorities = self._analyze_priorities(urls)
        return {
            "distribution": priorities,
            "optimization_score": (
                len(priorities) / 11 if priorities else 0
            ),  # 0.0-1.0 range
            "needs_optimization": len(set(priorities.keys())) <= 2,
        }

    def _analyze_changefreq_accuracy(self, urls: List[Element]) -> Dict[str, Any]:
        """Analyze changefreq accuracy"""
        changefreqs = self._analyze_changefreqs(urls)
        return {
            "distribution": changefreqs,
            "diversity_score": min(
                len(changefreqs) / 6, 1.0
            ),  # Max 6 standard frequencies
            "most_common": (
                max(changefreqs.items(), key=lambda x: x[1])[0] if changefreqs else None
            ),
        }

    def _calculate_consistency_score(self, urls: List[Element]) -> float:
        """Calculate consistency score"""
        # Check consistency of priority values and changefreq values
        priorities = self._analyze_priorities(urls)
        changefreqs = self._analyze_changefreqs(urls)

        # Simple consistency score based on distribution
        priority_consistency = 1.0 - (len(priorities) - 1) / 10 if priorities else 0.5
        changefreq_consistency = (
            1.0 - (len(changefreqs) - 1) / 6 if changefreqs else 0.5
        )

        return (priority_consistency + changefreq_consistency) / 2

    def _calculate_best_practices_score(
        self, urls: List[Element], total_urls: int
    ) -> float:
        """Calculate best practices compliance score"""
        score = 0.0

        # Check if sitemap size is reasonable
        if total_urls <= 50000:
            score += 0.3

        # Check if URLs have proper elements
        urls_with_priority = sum(
            1
            for url in urls
            if url.find(f".//{{{self.SITEMAP_NAMESPACE}}}priority") is not None
        )
        if urls_with_priority / total_urls > 0.8:
            score += 0.3

        # Check HTTPS usage
        https_count = self._count_https_urls(urls)
        if https_count / total_urls > 0.9:
            score += 0.4

        return score

    def _check_url_validity(self, urls: List[Element]) -> Dict[str, Any]:
        """Check URL validity"""
        validity = {"valid_urls": 0, "invalid_urls": 0, "issues": []}

        for url in urls:
            loc = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc")
            if loc is not None and loc.text:
                url_text = loc.text
                parsed = urlparse(url_text)

                if parsed.scheme and parsed.netloc:
                    validity["valid_urls"] += 1
                else:
                    validity["invalid_urls"] += 1
                    validity["issues"].append(
                        f"Invalid URL structure: {url_text[:50]}..."
                    )

        return validity

    def _count_https_urls(self, urls: List[Element]) -> int:
        """Count HTTPS URLs"""
        https_count = 0
        for url in urls:
            loc = url.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc")
            if loc is not None and loc.text:
                if loc.text.startswith("https://"):
                    https_count += 1
        return https_count

    def _extract_content_summary(self, root: Element, is_index: bool) -> Dict[str, Any]:
        """Extract content summary"""
        if is_index:
            sitemaps = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}sitemap")
            return {
                "type": "sitemap_index",
                "sitemap_count": len(sitemaps),
                "has_lastmod": sum(
                    1
                    for s in sitemaps
                    if s.find(f".//{{{self.SITEMAP_NAMESPACE}}}lastmod") is not None
                ),
            }
        else:
            urls = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}url")
            return {
                "type": "url_sitemap",
                "url_count": len(urls),
                "unique_domains": len(
                    set(
                        urlparse(
                            url.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc").text
                        ).netloc
                        for url in urls[:1000]
                        if url.find(f".//{{{self.SITEMAP_NAMESPACE}}}loc") is not None
                    )
                ),
            }

    def _extract_seo_summary(self, root: Element, is_index: bool) -> Dict[str, Any]:
        """Extract SEO summary"""
        if is_index:
            return {
                "sitemap_organization": "hierarchical",
                "crawl_optimization": "index_based",
            }
        else:
            urls = root.findall(f".//{{{self.SITEMAP_NAMESPACE}}}url")
            priorities = self._analyze_priorities(urls)
            changefreqs = self._analyze_changefreqs(urls)

            return {
                "priority_coverage": len(priorities) > 0,
                "changefreq_coverage": len(changefreqs) > 0,
                "https_adoption": (
                    self._count_https_urls(urls) / len(urls) if urls else 0
                ),
                "average_priority": self._calculate_average_priority(urls),
            }

    def _extract_technical_summary(
        self, root: Element, is_index: bool
    ) -> Dict[str, Any]:
        """Extract technical summary"""
        total_elements = len(list(root.iter()))

        return {
            "namespace": self.SITEMAP_NAMESPACE,
            "total_elements": total_elements,
            "estimated_size": self._estimate_file_size(root),
            "compression_recommended": self._estimate_file_size(root) > 10000,
            "schema_compliant": self._validate_namespace_usage(root),
        }

    def _assess_sitemap_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        """Assess overall sitemap quality"""

        # SEO quality
        seo_analysis = findings.get("seo_analysis", {})
        seo_score = 0.0

        priority_dist = seo_analysis.get("priority_distribution", {})
        if priority_dist.get("distribution"):
            seo_score += 0.3

        changefreq_dist = seo_analysis.get("changefreq_distribution", {})
        if changefreq_dist.get("distribution"):
            seo_score += 0.3

        freshness = seo_analysis.get("content_freshness", {})
        if freshness.get("freshness_percentage", 0) > 50:
            seo_score += 0.4

        # Technical quality
        technical = findings.get("technical_analysis", {})
        technical_score = 0.0

        if technical.get("namespace_compliance", False):
            technical_score += 0.4

        if technical.get("file_size", 0) < 50 * 1024 * 1024:  # Under 50MB
            technical_score += 0.3

        schema_validation = technical.get("schema_validation", {})
        if schema_validation.get("namespace_correct", False):
            technical_score += 0.3

        # Compliance quality
        compliance = findings.get("compliance_analysis", {})
        compliance_score = 0.0

        if compliance.get("namespace_compliance", False):
            compliance_score += 0.5

        required_elements = compliance.get("required_elements", {})
        if required_elements.get("loc_compliance", False):
            compliance_score += 0.5

        # Performance quality
        performance = findings.get("performance_analysis", {})
        performance_score = 0.0

        size_opt = performance.get("size_optimization", {})
        if size_opt.get("size_limit_compliance", False):
            performance_score += 0.5

        if len(performance.get("recommendations", [])) == 0:
            performance_score += 0.5

        return {
            "seo_optimization": seo_score,
            "technical_quality": technical_score,
            "compliance": compliance_score,
            "performance": performance_score,
            "overall": (
                seo_score + technical_score + compliance_score + performance_score
            )
            / 4,
        }
