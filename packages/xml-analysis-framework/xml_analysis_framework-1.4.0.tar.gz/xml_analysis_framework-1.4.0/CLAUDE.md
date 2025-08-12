# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Core Commands

### New Simple API (v1.2.3+)
```python
# Import the framework with the new user-friendly API
import xml_analysis_framework as xaf

# Simple one-line analysis with specialized handlers
result = xaf.analyze("file.xml")
print(f"Document: {result['document_type'].type_name}")

# Basic schema analysis
schema = xaf.analyze_schema("file.xml")
print(f"Elements: {schema.total_elements}")

# Smart chunking for AI/ML processing
chunks = xaf.chunk("file.xml", strategy="auto")
print(f"Created {len(chunks)} chunks")

# Different chunking strategies
hierarchical_chunks = xaf.chunk("file.xml", strategy="hierarchical")
sliding_chunks = xaf.chunk("file.xml", strategy="sliding_window")
content_chunks = xaf.chunk("file.xml", strategy="content_aware")
```

### Advanced API (for customization)
```python
# Direct class access for advanced usage
from xml_analysis_framework import XMLDocumentAnalyzer, ChunkingOrchestrator

# Custom analyzer with specific settings
analyzer = XMLDocumentAnalyzer(max_file_size_mb=1000)
result = analyzer.analyze_document("file.xml")

# Custom chunking
orchestrator = ChunkingOrchestrator(max_file_size_mb=500)
chunks = orchestrator.chunk_document("file.xml", analysis, strategy="hierarchical")
```

### Development and Testing (Local)
```bash
# Run basic XML analysis (development mode)
python analyze.py sample_data/node2.example.com-STIG-20250710162433.xml

# Run enhanced analysis with specialized handlers (development mode)
python analyze_enhanced.py sample_data/node2.example.com-STIG-20250710162433.xml

# Run framework demonstration (development mode)
python demo_xml_framework.py

# Test framework imports and basic functionality
python test_framework.py

# Quick testing
python quick_test.py
```

### No Build/Lint Commands
This project uses only Python standard library (3.7+) with no external dependencies. No build, lint, or specific test runner commands are configured.

## Architecture Overview

This is an XML document analysis framework designed to prepare XML data for AI/ML processing. The architecture follows a modular handler-based pattern:

### Core Components

1. **Core Analysis Engine** (`src/xml_schema_analyzer_fixed.py`)
   - Fixed version that handles large XML files efficiently
   - Uses iterative parsing to avoid stack overflow on deeply nested documents
   - Generates structured schema information and LLM-ready descriptions

2. **Specialized Handler System** (`src/xml_specialized_handlers.py`)
   - Abstract `XMLHandler` base class for document-specific analysis
   - Pluggable architecture for different XML document types
   - Returns `SpecializedAnalysis` with AI use cases, quality metrics, and structured data

3. **Extended Handlers** (`src/additional_xml_handlers.py`)
   - Additional handlers for enterprise formats
   - Modular handler collection in `src/handlers/` directory

4. **Chunking Strategies** (`src/xml-chunking-strategy.py`)
   - Multiple chunking algorithms: hierarchical, sliding window, content-aware
   - Token-aware chunking for LLM processing
   - Automatic strategy selection based on document type

### Handler Architecture Pattern

All XML handlers follow this pattern:
```python
class CustomHandler(XMLHandler):
    def can_handle(self, root, namespaces) -> Tuple[bool, float]:
        # Detection logic returning (can_handle, confidence_score)
        
    def detect_type(self, root, namespaces) -> DocumentTypeInfo:
        # Returns document type metadata
        
    def analyze(self, root, file_path) -> SpecializedAnalysis:
        # Returns structured analysis with AI use cases
        
    def extract_key_data(self, root) -> Dict[str, Any]:
        # Extracts document-specific structured data
```

### Supported Document Types

The framework handles these XML formats with specialized analysis:
- **SCAP Security Reports**: Vulnerability analysis, compliance scoring
- **RSS/Atom Feeds**: Content extraction, trend analysis preparation  
- **Maven POM**: Dependency analysis, security scanning
- **Log4j Configuration**: Security checks, configuration analysis
- **Spring Framework**: Bean analysis, dependency graphs
- **DocBook Documentation**: Structure analysis, content extraction
- **XML Sitemaps**: SEO analysis, URL pattern detection
- **WSDL/XSD**: Schema analysis, service definitions
- **Generic XML**: Pattern detection, schema inference

### Entry Points

- `analyze.py`: Basic analysis using core engine only
- `analyze_enhanced.py`: Full analysis with all specialized handlers and chunking
- `demo_xml_framework.py`: Comprehensive demonstration of all features

### File Organization

```
xml_files/
├── src/                          # Core framework code
│   ├── xml_schema_analyzer_fixed.py    # Core analysis engine
│   ├── xml_specialized_handlers.py     # Handler framework
│   ├── additional_xml_handlers.py      # Extended handlers
│   ├── xml-chunking-strategy.py        # Chunking algorithms
│   └── handlers/                       # Modular handler collection
├── sample_data/                  # Test XML files organized by type/size
├── analyze.py                    # Basic analyzer entry point
├── analyze_enhanced.py           # Enhanced analyzer entry point
└── demo_xml_framework.py         # Framework demonstration
```

## Development Patterns

### Adding New Handlers
1. Create handler class inheriting from `XMLHandler` 
2. Implement required methods: `can_handle()`, `detect_type()`, `analyze()`, `extract_key_data()`
3. Register in `XMLDocumentAnalyzer.__init__()` handlers list
4. Follow the confidence scoring pattern for document type detection

### Testing XML Files
The `sample_data/` directory contains organized test files:
- `sample_data/test_files/`: Real-world examples organized by size (small/medium/large) and type
- `sample_data/test_files_synthetic/`: Generated examples for testing edge cases
- Use `collect_test_files.py` to gather additional test cases

### Integration Points
- All handlers produce standardized `SpecializedAnalysis` output
- Chunking strategies are document-type aware
- Framework designed for easy LLM integration with token-aware processing
- JSON output format optimized for AI/ML pipelines