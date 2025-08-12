"""
XML Handlers Registry

Centralized registry for all XML document handlers.
This module provides a single import point for all handlers and maintains
the handler registry used by the main analyzer.
"""

from typing import Dict, List, Any

# Core handlers (moved from main files) - only import what exists
from .scap_handler import SCAPHandler
from .rss_handler import RSSHandler
from .maven_pom_handler import MavenPOMHandler
from .spring_config_handler import SpringConfigHandler
from .generic_xml_handler import GenericXMLHandler

# New handlers
from .ant_build_handler import AntBuildHandler
from .soap_envelope_handler import SOAPEnvelopeHandler
from .saml_handler import SAMLHandler
from .hibernate_handler import HibernateHandler
from .ivy_handler import IvyHandler

# Migrated handlers
from .log4j_config_handler import Log4jConfigHandler
from .svg_handler import SVGHandler
from .docbook_handler import DocBookHandler
from .sitemap_handler import SitemapHandler
from .kml_handler import KMLHandler
from .gpx_handler import GPXHandler
from .xhtml_handler import XHTMLHandler
from .wadl_handler import WADLHandler
from .struts_config_handler import StrutsConfigHandler
from .graphml_handler import GraphMLHandler
from .xliff_handler import XLIFFHandler

# Technical documentation
from .s1000d_handler import S1000DHandler

# IT Service Management
from .servicenow_handler import ServiceNowHandler

# Existing handlers (already in individual files)
from .bpmn_handler import BPMNHandler
from .enterprise_config_handler import EnterpriseConfigHandler
from .openapi_xml_handler import OpenAPIXMLHandler
from .properties_xml_handler import PropertiesXMLHandler
from .test_report_handler import TestReportHandler
from .wsdl_handler import WSDLHandler
from .xsd_handler import XSDSchemaHandler

# Registry of all available handlers (order matters - most specific first)
ALL_HANDLERS = [
    # Security and compliance
    SCAPHandler,
    SAMLHandler,
    # Build tools and frameworks
    MavenPOMHandler,
    SpringConfigHandler,
    AntBuildHandler,
    IvyHandler,
    Log4jConfigHandler,
    StrutsConfigHandler,
    # Enterprise configuration
    EnterpriseConfigHandler,
    PropertiesXMLHandler,
    HibernateHandler,
    # IT Service Management
    ServiceNowHandler,
    # Business process and workflow
    BPMNHandler,
    # Web services and APIs
    WSDLHandler,
    OpenAPIXMLHandler,
    SOAPEnvelopeHandler,
    WADLHandler,
    # Content and documentation
    RSSHandler,
    DocBookHandler,
    S1000DHandler,
    SitemapHandler,
    # Web content
    XHTMLHandler,
    # Geographic and mapping
    KMLHandler,
    GPXHandler,
    # Graphics and media
    SVGHandler,
    # Network and graph data
    GraphMLHandler,
    # Translation/localization
    XLIFFHandler,
    # Testing
    TestReportHandler,
    # Schemas and definitions
    XSDSchemaHandler,
    # Fallback (always last)
    GenericXMLHandler,
]

# Categorized handlers for easier management
HANDLER_CATEGORIES = {
    "security": [SCAPHandler, SAMLHandler],
    "build_tools": [MavenPOMHandler, AntBuildHandler, IvyHandler],
    "frameworks": [SpringConfigHandler, Log4jConfigHandler, StrutsConfigHandler],
    "web_services": [WSDLHandler, OpenAPIXMLHandler, SOAPEnvelopeHandler, WADLHandler],
    "business_process": [BPMNHandler],
    "enterprise_config": [
        EnterpriseConfigHandler,
        PropertiesXMLHandler,
        HibernateHandler,
    ],
    "it_service_management": [ServiceNowHandler],
    "content": [RSSHandler, DocBookHandler, S1000DHandler, SitemapHandler],
    "web_content": [XHTMLHandler],
    "geographic": [KMLHandler, GPXHandler],
    "graphics": [SVGHandler],
    "network_data": [GraphMLHandler],
    "localization": [XLIFFHandler],
    "schemas": [XSDSchemaHandler],
    "testing": [TestReportHandler],
    "fallback": [GenericXMLHandler],
}

# Export handler classes and utilities
__all__ = [
    "ALL_HANDLERS",
    "HANDLER_CATEGORIES",
    "get_handlers_by_category",
    "get_handler_categories",
    "get_handler_info",
    "find_handler_by_name",
    "SCAPHandler",
    "RSSHandler",
    "MavenPOMHandler",
    "SpringConfigHandler",
    "AntBuildHandler",
    "SOAPEnvelopeHandler",
    "SAMLHandler",
    "HibernateHandler",
    "IvyHandler",
    "Log4jConfigHandler",
    "SVGHandler",
    "DocBookHandler",
    "SitemapHandler",
    "KMLHandler",
    "GPXHandler",
    "XHTMLHandler",
    "WADLHandler",
    "StrutsConfigHandler",
    "GraphMLHandler",
    "XLIFFHandler",
    "S1000DHandler",
    "GenericXMLHandler",
    "BPMNHandler",
    "EnterpriseConfigHandler",
    "OpenAPIXMLHandler",
    "PropertiesXMLHandler",
    "TestReportHandler",
    "WSDLHandler",
    "XSDSchemaHandler",
    "ServiceNowHandler",
]


# Handler Registry Utilities
def get_handlers_by_category(category: str) -> List:
    """Get all handlers in a specific category"""
    return HANDLER_CATEGORIES.get(category, [])


def get_handler_categories() -> List[str]:
    """Get list of all handler categories"""
    return list(HANDLER_CATEGORIES.keys())


def get_handler_info() -> Dict[str, Any]:
    """Get comprehensive information about the handler registry"""
    return {
        "total_handlers": len(ALL_HANDLERS),
        "categories": len(HANDLER_CATEGORIES),
        "handlers_by_category": {
            category: len(handlers) for category, handlers in HANDLER_CATEGORIES.items()
        },
        "handler_names": [handler.__name__ for handler in ALL_HANDLERS],
    }


def find_handler_by_name(name: str):
    """Find a handler class by name"""
    for handler in ALL_HANDLERS:
        if handler.__name__ == name or handler.__name__ == f"{name}Handler":
            return handler
    return None
