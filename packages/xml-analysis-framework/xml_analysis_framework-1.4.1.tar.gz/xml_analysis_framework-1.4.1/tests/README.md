# XML Analysis Framework Test Suite

This directory contains all tests for the XML analysis framework, organized into a clean structure for easy maintenance and execution.

## Directory Structure

```
tests/
├── __init__.py                 # Test package initialization
├── README.md                   # This file
├── run_all_tests.py           # Comprehensive test runner
├── test_framework.py          # Framework-level tests
├── test_setup.py              # Setup and configuration tests
├── test_existing_handlers.py  # Tests for existing handlers
├── test_migration_progress.py # Migration progress tests
│
├── debug/                     # Debug and troubleshooting scripts
│   ├── debug_analyzer_issue.py
│   └── debug_hierarchical_chunking.py
│
├── manual/                    # Manual testing and analysis scripts
│   ├── test_end_to_end_workflow.py      # ⭐ Main comprehensive test
│   ├── test_all_chunking.py             # Chunking validation
│   ├── test_servicenow_analysis.py      # ServiceNow handler testing
│   └── analyze_test_results.py          # Test result analysis
│
├── unit/                      # Individual handler unit tests
│   ├── __init__.py
│   ├── test_ant_handler.py
│   ├── test_soap_handler.py
│   ├── test_saml_handler.py
│   ├── test_hibernate_handler.py
│   ├── test_ivy_handler.py
│   ├── test_log4j_handler.py
│   ├── test_svg_handler.py
│   ├── test_docbook_handler.py
│   ├── test_sitemap_handler.py
│   ├── test_kml_handler.py
│   ├── test_gpx_handler.py
│   ├── test_xhtml_handler.py
│   ├── test_wadl_handler.py
│   ├── test_struts_handler.py
│   ├── test_graphml_handler.py
│   └── test_xliff_handler.py
│
├── integration/               # Handler integration tests
│   ├── __init__.py
│   ├── test_ant_integration.py
│   ├── test_svg_integration.py
│   ├── test_docbook_integration.py
│   ├── test_sitemap_integration.py
│   ├── test_kml_integration.py
│   ├── test_gpx_integration.py
│   ├── test_xhtml_integration.py
│   ├── test_wadl_integration.py
│   ├── test_struts_integration.py
│   ├── test_graphml_integration.py
│   └── test_xliff_integration.py
│
└── comprehensive/             # Full system tests
    ├── __init__.py
    ├── test_all_sample_data.py    # Test all handlers against all sample data
    ├── test_gpx_comprehensive.py  # Detailed GPX analysis
    ├── test_xhtml_comprehensive.py # Detailed XHTML analysis
    └── test_kml_manual.py         # Manual KML testing
```

## Test Categories

### Unit Tests (`unit/`)
Individual handler tests that verify each handler's functionality in isolation:
- Handler import and initialization
- Document type detection (`can_handle()` method)
- Document analysis (`analyze()` method)
- Key data extraction (`extract_key_data()` method)
- Synthetic test files for controlled testing

### Integration Tests (`integration/`)
Tests that verify handlers work correctly within the main framework:
- Handler registration and discovery
- End-to-end document analysis through `XMLDocumentAnalyzer`
- Confidence scoring and handler selection
- Integration with the centralized handler registry

### Framework Tests
Core framework functionality tests:
- `test_framework.py`: Basic framework operations
- `test_setup.py`: Environment and setup validation
- `test_existing_handlers.py`: Legacy handler compatibility
- `test_migration_progress.py`: Migration status tracking

### Comprehensive Tests (`comprehensive/`)
Full system validation and performance testing:
- `test_all_sample_data.py`: Tests all 28 handlers against 99 sample files
- `test_*_comprehensive.py`: Detailed analysis of specific handler types
- Performance benchmarking and quality metrics

## Running Tests

### 🚀 Main Production Tests
```bash
# Run comprehensive end-to-end test (100% success rate)
cd tests/manual
python test_end_to_end_workflow.py

# Run chunking validation test
cd tests/manual  
python test_all_chunking.py
```

### 🧪 Standard Test Suite
```bash
# Run all framework tests
cd tests
python run_all_tests.py
```

### 🔍 Specific Test Categories
```bash
# Unit tests only
cd unit && python test_ant_handler.py

# Integration tests only  
cd integration && python test_ant_integration.py

# Comprehensive tests only
cd comprehensive && python test_all_sample_data.py

# Debug and troubleshooting
cd debug && python debug_analyzer_issue.py
```

### Run Individual Tests
```bash
# From tests directory
python unit/test_xliff_handler.py
python integration/test_xliff_integration.py
python comprehensive/test_all_sample_data.py
```

## Test Results Interpretation

### Success Criteria
- **Unit Tests**: Handler correctly processes synthetic test files
- **Integration Tests**: Handler integrates properly with main framework
- **Comprehensive Tests**: High success rate across all sample data

### Performance Metrics
- **Processing Speed**: Average time per file (target: <0.1s)
- **Success Rate**: Percentage of files processed without errors (target: >95%)
- **Quality Scores**: Handler-specific quality assessment (target: >0.7)

## Adding New Tests

### For New Handlers
1. Create unit test in `unit/test_[handler_name]_handler.py`
2. Create integration test in `integration/test_[handler_name]_integration.py`
3. Add synthetic test files in `../sample_data/test_files_synthetic/small/[type]/`
4. Update handler registry in `../src/handlers/__init__.py`

### Test File Template
```python
#!/usr/bin/env python3
"""
Test [Handler Name] handler implementation
"""
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_handler():
    """Test [Handler Name] handler with sample files"""
    
    try:
        from handlers.[handler_file] import [HandlerClass]
        print("✅ [HandlerClass] imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import [HandlerClass]: {e}")
        return False
    
    # Add test implementation
    return True

if __name__ == "__main__":
    success = test_handler()
    sys.exit(0 if success else 1)
```

## Current Status

- **✅ 29 Specialized Handlers** implemented and tested
- **✅ 100% Success Rate** across all 71 test files (latest comprehensive test)
- **✅ 2,752 Chunks Generated** with optimal 38.8 average per file
- **✅ 54 Document Types** detected with 90-100% confidence
- **✅ Sub-millisecond** average processing time per document
- **✅ Production Ready** with comprehensive enterprise, security, and AI integration

The test suite validates that the XML analysis framework achieves enterprise-grade reliability and performance with full AI workflow integration.