# XML Analysis Framework

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Success Rate](https://img.shields.io/badge/Tests-100%25%20Success-brightgreen.svg)](./test_results)
[![Handlers](https://img.shields.io/badge/Specialized%20Handlers-29-blue.svg)](./src/handlers)
[![AI Ready](https://img.shields.io/badge/AI%20Ready-✓-green.svg)](./AI_INTEGRATION_ARCHITECTURE.md)

A production-ready XML document analysis and preprocessing framework with **29 specialized handlers** designed for AI/ML data pipelines. Transform any XML document into structured, AI-ready data and optimized chunks with **100% success rate** across 71 diverse test files.

## 🚀 Quick Start

### Simple API - Get Started in Seconds

```python
import xml_analysis_framework as xaf

# 🎯 One-line analysis with specialized handlers
result = xaf.analyze("path/to/file.xml")
print(f"Document type: {result['document_type'].type_name}")
print(f"Handler used: {result['handler_used']}")

# 📊 Basic schema analysis  
schema = xaf.analyze_schema("path/to/file.xml")
print(f"Elements: {schema.total_elements}, Depth: {schema.max_depth}")

# ✂️ Smart chunking for AI/ML
chunks = xaf.chunk("path/to/file.xml", strategy="auto")
print(f"Created {len(chunks)} optimized chunks")

# 💾 Save chunks to JSON
import json

# Convert chunks to JSON-serializable format
chunks_data = [
    {
        "chunk_id": chunk.chunk_id,
        "content": chunk.content,
        "element_path": chunk.element_path,
        "start_line": chunk.start_line,
        "end_line": chunk.end_line,
        "elements_included": chunk.elements_included,
        "metadata": chunk.metadata,
        "token_estimate": chunk.token_estimate
    }
    for chunk in chunks
]

# Write to file
with open("chunks_output.json", "w") as f:
    json.dump(chunks_data, f, indent=2)
```

### Advanced Usage

```python
import xml_analysis_framework as xaf

# Enhanced analysis with full results
analysis = xaf.analyze_enhanced("document.xml")

print(f"Type: {analysis.type_name} (confidence: {analysis.confidence:.2f})")
print(f"AI use cases: {len(analysis.ai_use_cases)}")
if analysis.quality_metrics:
    print(f"Quality score: {analysis.quality_metrics.get('completeness_score')}")
else:
    print("Quality metrics: Not available")

# Different chunking strategies
hierarchical_chunks = xaf.chunk("document.xml", strategy="hierarchical")
sliding_chunks = xaf.chunk("document.xml", strategy="sliding_window") 
content_chunks = xaf.chunk("document.xml", strategy="content_aware")

# Process chunks
for chunk in hierarchical_chunks:
    print(f"Chunk {chunk.chunk_id}: {len(chunk.content)} chars")
    print(f"Path: {chunk.element_path}, Elements: {len(chunk.elements_included)}")

# 💾 Save different chunking strategies to separate files
import json

# Helper function to convert chunk to dict
def chunk_to_dict(chunk):
    return {
        "chunk_id": chunk.chunk_id,
        "content": chunk.content,
        "element_path": chunk.element_path,
        "start_line": chunk.start_line,
        "end_line": chunk.end_line,
        "elements_included": chunk.elements_included,
        "metadata": chunk.metadata,
        "token_estimate": chunk.token_estimate
    }

# Save each strategy's results
strategies = {
    "hierarchical": hierarchical_chunks,
    "sliding_window": sliding_chunks,
    "content_aware": content_chunks
}

for strategy_name, chunks in strategies.items():
    chunks_data = [chunk_to_dict(chunk) for chunk in chunks]
    
    with open(f"chunks_{strategy_name}.json", "w") as f:
        json.dump({
            "strategy": strategy_name,
            "total_chunks": len(chunks_data),
            "chunks": chunks_data
        }, f, indent=2)
    
    print(f"Saved {len(chunks_data)} chunks to chunks_{strategy_name}.json")
```

### Expert Usage - Direct Class Access

```python
# For advanced customization, use the classes directly
from xml_analysis_framework import XMLDocumentAnalyzer, ChunkingOrchestrator

analyzer = XMLDocumentAnalyzer(max_file_size_mb=500)
orchestrator = ChunkingOrchestrator(max_file_size_mb=1000)

# Custom analysis
result = analyzer.analyze_document("file.xml")

# Custom chunking with config (result works directly now!)
from xml_analysis_framework.core.chunking import ChunkingConfig
config = ChunkingConfig(
    max_chunk_size=2000,
    min_chunk_size=300,
    overlap_size=150,
    preserve_hierarchy=True
)
chunks = orchestrator.chunk_document("file.xml", result, strategy="auto", config=config)

# 💾 Save with analysis metadata
import json
from datetime import datetime

output_data = {
    "metadata": {
        "file": "file.xml",
        "processed_at": datetime.now().isoformat(),
        "document_type": result.type_name,
        "confidence": result.confidence,
        "handler_used": result.handler_used,
        "chunking_config": {
            "strategy": "auto",
            "max_chunk_size": config.max_chunk_size,
            "min_chunk_size": config.min_chunk_size,
            "overlap_size": config.overlap_size,
            "preserve_hierarchy": config.preserve_hierarchy
        }
    },
    "analysis": {
        "ai_use_cases": result.ai_use_cases,
        "key_findings": result.key_findings,
        "quality_metrics": result.quality_metrics
    },
    "chunks": [
        {
            "chunk_id": chunk.chunk_id,
            "content": chunk.content,
            "element_path": chunk.element_path,
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "elements_included": chunk.elements_included,
            "metadata": chunk.metadata,
            "token_estimate": chunk.token_estimate
        }
        for chunk in chunks
    ]
}

with open("analysis_and_chunks.json", "w") as f:
    json.dump(output_data, f, indent=2)

print(f"Saved complete analysis with {len(chunks)} chunks to analysis_and_chunks.json")
```

## 🎯 Key Features

### 1. **🧠 29 Specialized XML Handlers**

Automatically detects and analyzes different XML document types:

- **Security & Compliance**: SCAP, SAML, SOAP
- **DevOps & Build**: Maven POM, Ant, Ivy, Spring, Log4j
- **Content & Documentation**: RSS/Atom, DocBook, XHTML, SVG
- **Enterprise Systems**: ServiceNow, Hibernate, Struts configurations
- **Data & APIs**: GPX, KML, GraphML, WADL/WSDL, XML Schemas

### 2. **⚡ Intelligent Chunking Strategies**

- **Hierarchical**: Preserves document structure and relationships
- **Sliding Window**: Fixed-size chunks with configurable overlap
- **Content-Aware**: Groups related content based on semantic meaning
- **Auto-Selection**: Automatically chooses best strategy based on document type

### 3. **🤖 AI/ML Ready Output**

- **Token-Optimized**: Chunks sized for LLM context windows
- **Rich Metadata**: Each chunk includes context, line numbers, and relationships
- **JSON Export**: Easy integration with vector stores and AI pipelines
- **Quality Metrics**: Automated assessment of data completeness and structure

### 4. **🔒 Enterprise Security**

- **Safe XML Parsing**: Uses defusedxml to prevent XXE attacks
- **File Size Limits**: Configurable limits to prevent resource exhaustion
- **Minimal Dependencies**: Only defusedxml + Python standard library

## 📋 Supported Document Types

| Category | Document Types | Common Use Cases |
| -------- | -------------- | ---------------- |
| **Security & Compliance** | SCAP, SAML, SOAP | Vulnerability scanning, authentication, web services |
| **Build & Configuration** | Maven POM, Ant, Spring, Log4j | Dependency management, build automation, app config |
| **Enterprise Systems** | ServiceNow, Hibernate, Struts | IT service management, ORM mapping, web frameworks |
| **Content & Media** | RSS/Atom, DocBook, XHTML, SVG | Feeds, documentation, web content, graphics |
| **Geospatial** | GPX, KML, GraphML | GPS tracking, maps, network graphs |
| **APIs & Services** | WADL, WSDL, OpenAPI | REST APIs, SOAP services, API documentation |
| **Data Exchange** | XLIFF, XML Sitemap, Generic XML | Translations, SEO, custom formats |


## 🔒 Security

### XML Security Protection

This framework uses **defusedxml** to protect against common XML security vulnerabilities:

- **XXE (XML External Entity) attacks**: Prevents reading local files or making network requests
- **Billion Laughs attack**: Prevents exponential entity expansion DoS attacks
- **DTD retrieval**: Blocks external DTD fetching to prevent data exfiltration

#### Security Features

```python
import xml_analysis_framework as xaf

# Safe parsing - malicious XML will be rejected automatically
try:
    result = xaf.analyze("potentially_malicious.xml")
except Exception as e:
    print(f"Security threat detected: {e}")

# The framework automatically protects against:
# - XXE attacks
# - Billion laughs / exponential entity expansion
# - External DTD retrieval
```

#### Best Practices

1. **Always use the framework's parsers** - Never use `xml.etree.ElementTree` directly
2. **Validate file sizes** - Set reasonable limits for your use case
3. **Sanitize file paths** - Ensure input paths are properly validated
4. **Monitor for security exceptions** - Log and alert on security-blocked parsing attempts

### File Size Limits

The framework includes built-in file size limits to prevent memory exhaustion:

```python
import xml_analysis_framework as xaf
from xml_analysis_framework import XMLDocumentAnalyzer, ChunkingOrchestrator

# Default limits are reasonable for most use cases
# But you can customize them:

# Create analyzer with custom 50MB limit
analyzer = XMLDocumentAnalyzer(max_file_size_mb=50.0)
result = analyzer.analyze_document("large_file.xml")

# Create chunking orchestrator with 100MB limit  
orchestrator = ChunkingOrchestrator(max_file_size_mb=100.0)
chunks = orchestrator.chunk_document("large_file.xml", result)

# For simple API, defaults are used automatically
try:
    result = xaf.analyze("very_large_file.xml")
except ValueError as e:
    print(f"File too large: {e}")
```

## 🔧 Installation

```bash
# Install from PyPI (recommended)
pip install xml-analysis-framework

# Install from source
git clone https://github.com/redhat-ai-americas/xml-analysis-framework.git
cd xml-analysis-framework
pip install -e .

# Or install development dependencies
pip install -e .[dev]
```

### Dependencies

- **defusedxml** (0.7.1+): For secure XML parsing protection
- Python standard library (3.8+) for all other functionality


## 🧪 Testing

The framework includes comprehensive tests for all handlers and features:

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/           # Unit tests for handlers
python -m pytest tests/integration/    # Integration tests
python -m pytest tests/comprehensive/  # Full system tests
```


## 🤖 AI/ML Integration

### AI Processing Pipeline

```
XML Documents → Analysis Framework → Structured Output → AI/ML Systems

1. Document Analysis (29 specialized handlers)
2. Smart Chunking (token-optimized)
3. JSON Export (with metadata)
4. Integration with:
   - Vector databases (semantic search)
   - LLMs (document Q&A, analysis)
   - Graph databases (relationship mapping)
   - ML pipelines (feature extraction)
```

### Common AI Use Cases

- **Security Intelligence**: Analyze SCAP reports, detect vulnerabilities, compliance monitoring
- **DevOps Automation**: Dependency analysis, configuration validation, build optimization  
- **Enterprise Search**: Semantic search across technical documentation and configurations
- **Knowledge Extraction**: Extract structured data from XML for ML training datasets


## 🚀 Extending the Framework

### Adding New Handlers

```python
from xml_analysis_framework.base import XMLHandler, SpecializedAnalysis, DocumentTypeInfo

class CustomHandler(XMLHandler):
    def can_handle_xml(self, root, namespaces):
        # Check if this handler can process the document
        if root.tag == 'custom-format':
            return True, 1.0  # (can_handle, confidence)
        return False, 0.0
  
    def detect_xml_type(self, root, namespaces):
        return DocumentTypeInfo(
            type_name="Custom Format",
            confidence=1.0,
            version="1.0"
        )
  
    def analyze_xml(self, root, file_path):
        return SpecializedAnalysis(
            type_name="Custom Format",
            confidence=1.0,
            key_findings={"custom_data": "value"},
            ai_use_cases=["Custom AI application"],
            structured_data={"extracted": "data"},
            file_path=file_path,
            handler_used="CustomHandler"
        )
    
    def extract_xml_key_data(self, root):
        # Extract key data specific to your format
        return {"key": "value"}
```

### Custom Chunking Strategies

```python
from xml_analysis_framework.core.chunking import XMLChunkingStrategy, XMLChunk
import xml.etree.ElementTree as ET

class CustomChunking(XMLChunkingStrategy):
    def chunk_document(self, file_path, specialized_analysis=None):
        chunks = []
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Custom chunking logic
        for i, element in enumerate(root):
            chunk = XMLChunk(
                chunk_id=f"custom_{i}",
                content=ET.tostring(element, encoding='unicode'),
                element_path=f"/{element.tag}",
                start_line=1,
                end_line=10,
                parent_context=None,
                metadata={"custom": True},
                token_estimate=100,
                elements_included=[element.tag]
            )
            chunks.append(chunk)
        
        return chunks

# Use with the framework
import xml_analysis_framework as xaf
from xml_analysis_framework import ChunkingOrchestrator

orchestrator = ChunkingOrchestrator()
# The orchestrator will use your custom strategy when needed
```


## 🤝 Contributing

We welcome contributions! Whether you're adding new XML handlers, improving chunking algorithms, or enhancing AI integrations, your contributions help make XML analysis more accessible and powerful.

**Priority contribution areas:**

- 🎯 New XML format handlers (ERP, CRM, healthcare, government)
- ⚡ Enhanced chunking algorithms and strategies
- 🚀 Performance optimizations for large files
- 🤖 Advanced AI/ML integration examples
- 📝 Documentation and usage examples

**👉 See [CONTRIBUTING.md](CONTRIBUTING.md) for complete guidelines, development setup, and submission process.**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Designed as part of the **AI Building Blocks** initiative
- Built for the modern AI/ML ecosystem
- Community-driven XML format support
