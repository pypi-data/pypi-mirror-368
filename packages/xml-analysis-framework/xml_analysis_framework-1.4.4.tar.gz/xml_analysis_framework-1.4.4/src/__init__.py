"""
XML Analysis Framework

An XML document analysis and preprocessing framework designed for AI/ML data pipelines.
Features specialized handlers for different document types and generates structured,
AI-ready data and optimized chunks.

Simple Usage:
    import xml_analysis_framework as xaf
    
    # Basic analysis
    result = xaf.analyze("file.xml")
    
    # Enhanced analysis with specialized handlers
    result = xaf.analyze_enhanced("file.xml") 
    
    # Schema analysis
    schema = xaf.analyze_schema("file.xml")
    
    # Chunking
    chunks = xaf.chunk("file.xml")
    chunks = xaf.chunk("file.xml", strategy="hierarchical")
"""

__version__ = "1.4.4"
__author__ = "AI Building Blocks"

# Import core functionality for easy access
from .core.analyzer import XMLDocumentAnalyzer
from .core.schema_analyzer import XMLSchemaAnalyzer
from .core.chunking import ChunkingOrchestrator, XMLChunkingStrategy
from .unified_interface import UnifiedAnalysisResult

# Create singleton instances for convenience
_enhanced_analyzer = None
_schema_analyzer = None
_chunking_orchestrator = None

def _get_enhanced_analyzer():
    """Get or create enhanced analyzer instance"""
    global _enhanced_analyzer
    if _enhanced_analyzer is None:
        _enhanced_analyzer = XMLDocumentAnalyzer()
    return _enhanced_analyzer

def _get_schema_analyzer():
    """Get or create schema analyzer instance"""
    global _schema_analyzer
    if _schema_analyzer is None:
        _schema_analyzer = XMLSchemaAnalyzer()
    return _schema_analyzer

def _get_chunking_orchestrator():
    """Get or create chunking orchestrator instance"""
    global _chunking_orchestrator
    if _chunking_orchestrator is None:
        _chunking_orchestrator = ChunkingOrchestrator()
    return _chunking_orchestrator

# Public API Functions
def analyze_enhanced(file_path: str, **kwargs):
    """
    Analyze XML document with specialized handlers.
    
    Args:
        file_path: Path to XML file
        **kwargs: Additional arguments passed to analyzer
        
    Returns:
        SpecializedAnalysis object containing analysis results with document type detection,
        specialized analysis, and structured data extraction
    """
    analyzer = _get_enhanced_analyzer()
    return analyzer.analyze_document(file_path, **kwargs)

def analyze_unified(file_path: str, **kwargs) -> UnifiedAnalysisResult:
    """
    Analyze XML document and return unified result format.
    
    This provides a consistent interface across all analysis frameworks.
    
    Args:
        file_path: Path to XML file
        **kwargs: Additional arguments passed to analyzer
        
    Returns:
        UnifiedAnalysisResult with consistent interface (dict-like access, standard properties)
    """
    analyzer = _get_enhanced_analyzer()
    return analyzer.analyze_unified(file_path)

def analyze_schema(file_path: str, **kwargs):
    """
    Perform basic XML schema analysis.
    
    Args:
        file_path: Path to XML file
        **kwargs: Additional arguments passed to analyzer
        
    Returns:
        SchemaAnalysisResult with structure information
    """
    analyzer = _get_schema_analyzer()
    return analyzer.analyze_file(file_path, **kwargs)

def chunk(file_path: str, strategy: str = "auto", **kwargs):
    """
    Chunk XML document for AI/ML processing.
    
    Args:
        file_path: Path to XML file
        strategy: Chunking strategy ("auto", "hierarchical", "sliding_window", "content_aware")
        **kwargs: Additional arguments passed to chunking orchestrator
        
    Returns:
        List of document chunks optimized for AI processing
    """
    # Get enhanced analysis first for better chunking
    analysis_result = analyze_enhanced(file_path)
    
    # SpecializedAnalysis now works directly with chunk_document!
    orchestrator = _get_chunking_orchestrator()
    return orchestrator.chunk_document(file_path, analysis_result, strategy=strategy, **kwargs)

# Convenience alias - analyze() defaults to enhanced analysis
def analyze(file_path: str, **kwargs):
    """
    Analyze XML document (alias for analyze_enhanced).
    
    Args:
        file_path: Path to XML file
        **kwargs: Additional arguments passed to analyzer
        
    Returns:
        SpecializedAnalysis object containing enhanced analysis results
    """
    return analyze_enhanced(file_path, **kwargs)

# Export main classes for advanced usage
__all__ = [
    # Main API functions
    "analyze",
    "analyze_enhanced", 
    "analyze_unified",
    "analyze_schema",
    "chunk",
    
    # Core classes for advanced usage
    "XMLDocumentAnalyzer",
    "XMLSchemaAnalyzer", 
    "ChunkingOrchestrator",
    "XMLChunkingStrategy",
    "UnifiedAnalysisResult",
    
    # Package metadata
    "__version__",
    "__author__",
]
