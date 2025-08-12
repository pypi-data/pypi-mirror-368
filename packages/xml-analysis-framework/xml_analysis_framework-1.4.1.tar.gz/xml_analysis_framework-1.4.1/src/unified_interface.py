"""Unified interface compatibility layer for xml-analysis-framework.

This module provides a consistent interface wrapper that can be copied to other frameworks.
It ensures all analysis results have the same access patterns regardless of the underlying
implementation.
"""

from typing import Dict, Any, Optional, List


class UnifiedAnalysisResult:
    """Wrapper to provide consistent interface for SpecializedAnalysis objects.
    
    This class provides:
    - Dictionary-style access: result['key']
    - Attribute access: result.key
    - Consistent method interface: result.to_dict()
    """
    
    def __init__(self, specialized_analysis):
        """Initialize with a SpecializedAnalysis object.
        
        Args:
            specialized_analysis: The raw analysis result from XMLDocumentAnalyzer
        """
        self._raw = specialized_analysis
        self._dict_cache = None
    
    @property
    def document_type(self) -> str:
        """Get the document type."""
        return getattr(self._raw, 'type_name', 'unknown')
    
    @property
    def confidence(self) -> float:
        """Get the confidence score."""
        return getattr(self._raw, 'confidence', 1.0)
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata dictionary."""
        return getattr(self._raw, 'metadata', {})
    
    @property
    def content(self) -> str:
        """Get extracted content."""
        return getattr(self._raw, 'content', '')
    
    @property
    def ai_opportunities(self) -> List[str]:
        """Get AI processing opportunities."""
        return getattr(self._raw, 'ai_opportunities', [])
    
    @property
    def framework(self) -> str:
        """Get the framework name."""
        return 'xml-analysis-framework'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for compatibility.
        
        Returns:
            Dict containing all standard fields
        """
        if self._dict_cache is None:
            # Build the standard dictionary representation
            self._dict_cache = {
                'document_type': self.document_type,
                'confidence': self.confidence,
                'metadata': self.metadata,
                'content': self.content,
                'ai_opportunities': self.ai_opportunities,
                'framework': self.framework,
                # Include raw analysis data
                'raw_analysis': self._raw
            }
            
            # Add any additional attributes from the raw object
            for attr in dir(self._raw):
                if not attr.startswith('_') and attr not in self._dict_cache:
                    try:
                        value = getattr(self._raw, attr)
                        # Only include serializable values
                        if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                            self._dict_cache[attr] = value
                    except:
                        pass
        
        return self._dict_cache
    
    def get(self, key: str, default=None):
        """Dict-like access with default value.
        
        Args:
            key: The key to look up
            default: Default value if key not found
            
        Returns:
            The value or default
        """
        return self.to_dict().get(key, default)
    
    def __getitem__(self, key: str):
        """Support result['key'] syntax.
        
        Args:
            key: The key to look up
            
        Returns:
            The value
            
        Raises:
            KeyError: If key not found
        """
        return self.to_dict()[key]
    
    def __contains__(self, key: str) -> bool:
        """Support 'key in result' syntax."""
        return key in self.to_dict()
    
    def keys(self):
        """Get dictionary keys."""
        return self.to_dict().keys()
    
    def values(self):
        """Get dictionary values."""
        return self.to_dict().values()
    
    def items(self):
        """Get dictionary items."""
        return self.to_dict().items()
    
    # Proxy all other attributes to the raw object
    def __getattr__(self, name):
        """Proxy attribute access to the raw object.
        
        This allows accessing any attributes from the original
        SpecializedAnalysis object that aren't explicitly defined here.
        """
        return getattr(self._raw, name)
    
    def __repr__(self):
        """String representation."""
        return f"UnifiedAnalysisResult(document_type='{self.document_type}', framework='{self.framework}')" 