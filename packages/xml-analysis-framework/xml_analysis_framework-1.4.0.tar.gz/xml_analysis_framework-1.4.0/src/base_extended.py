#!/usr/bin/env python3
"""
Extended base classes for XML Analysis Framework using inheritance.
This shows how we could refactor to have SpecializedAnalysis extend DocumentTypeInfo.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class DocumentTypeInfo:
    """Basic document type information"""
    type_name: str
    confidence: float  # 0.0 to 1.0
    version: Optional[str] = None
    schema_uri: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class EnhancedAnalysis(DocumentTypeInfo):
    """
    Complete document analysis extending basic document type info.
    This combines DocumentTypeInfo + SpecializedAnalysis into one clean object.
    """
    # Inherited from DocumentTypeInfo:
    # - type_name: str
    # - confidence: float
    # - version: Optional[str]
    # - schema_uri: Optional[str] 
    # - metadata: Dict[str, Any]
    
    # Additional analysis fields:
    file_path: str = ""
    handler_used: str = ""
    namespaces: Dict[str, str] = field(default_factory=dict)
    key_findings: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    data_inventory: Dict[str, int] = field(default_factory=dict)
    ai_use_cases: List[str] = field(default_factory=list)
    structured_data: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    
    @classmethod
    def from_separate_objects(cls, 
                            doc_type: DocumentTypeInfo, 
                            analysis: 'SpecializedAnalysis',
                            file_path: str = "",
                            handler_used: str = "",
                            namespaces: Dict[str, str] = None) -> 'EnhancedAnalysis':
        """Create from existing DocumentTypeInfo and SpecializedAnalysis objects"""
        return cls(
            # From DocumentTypeInfo
            type_name=doc_type.type_name,
            confidence=doc_type.confidence,
            version=doc_type.version,
            schema_uri=doc_type.schema_uri,
            metadata=doc_type.metadata,
            # Additional fields
            file_path=file_path,
            handler_used=handler_used,
            namespaces=namespaces or {},
            # From SpecializedAnalysis
            key_findings=analysis.key_findings,
            recommendations=analysis.recommendations,
            data_inventory=analysis.data_inventory,
            ai_use_cases=analysis.ai_use_cases,
            structured_data=analysis.structured_data,
            quality_metrics=analysis.quality_metrics
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for backward compatibility"""
        return {
            'file_path': self.file_path,
            'document_type': DocumentTypeInfo(
                type_name=self.type_name,
                confidence=self.confidence,
                version=self.version,
                schema_uri=self.schema_uri,
                metadata=self.metadata
            ),
            'analysis': {
                'document_type': self.type_name,
                'key_findings': self.key_findings,
                'recommendations': self.recommendations,
                'data_inventory': self.data_inventory,
                'ai_use_cases': self.ai_use_cases,
                'structured_data': self.structured_data,
                'quality_metrics': self.quality_metrics
            },
            'handler_used': self.handler_used,
            'namespaces': self.namespaces,
            'confidence': self.confidence
        }


# Example of how this would work:
if __name__ == "__main__":
    # Create an EnhancedAnalysis object (what analyze_document would return)
    result = EnhancedAnalysis(
        # Document type info
        type_name="SCAP/XCCDF Document",
        confidence=0.9,
        version="1.2",
        # Analysis info
        file_path="/path/to/file.xml",
        handler_used="SCAPHandler",
        ai_use_cases=["Security compliance checking", "Vulnerability analysis"],
        key_findings={"rules": 150, "profiles": 3},
        quality_metrics={"completeness": 0.85}
    )
    
    # This object can be used anywhere DocumentTypeInfo is expected
    print(f"Type: {result.type_name} (confidence: {result.confidence})")
    
    # But also has all the analysis data
    print(f"AI use cases: {result.ai_use_cases}")
    print(f"Quality: {result.quality_metrics}")
    
    # Can be passed directly to chunk_document
    # No conversion needed!
    print(f"\nCan be used directly with chunk_document:")
    print(f"- Document type: {result.type_name}")
    print(f"- Confidence: {result.confidence}")
    print(f"- Has analysis data: {bool(result.ai_use_cases)}")