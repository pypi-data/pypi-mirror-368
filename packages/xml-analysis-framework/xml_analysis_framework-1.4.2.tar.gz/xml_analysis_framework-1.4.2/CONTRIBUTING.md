# Contributing to XML Analysis Framework

Thank you for your interest in contributing to the XML Analysis Framework! This document provides guidelines and information for contributors.

## 🎯 Project Vision

The XML Analysis Framework is designed to be a comprehensive, production-ready system for analyzing XML documents with AI/ML processing support. We aim to:

- Support enterprise XML formats with specialized handlers
- Maintain 100% success rate across diverse XML files
- Generate high-quality semantic chunks for AI applications
- Provide zero external dependencies (pure Python)
- Enable easy integration with vector stores and LLM systems

## 🚀 Getting Started

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/redhat-ai-americas/xml-analysis-framework.git
   cd xml-analysis-framework
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to verify setup:**
   ```bash
   python -m pytest tests/
   ```

### Project Structure

```
xml-analysis-framework/
├── src/                          # Main source code
│   ├── handlers/                 # Specialized XML handlers
│   ├── core/                     # Core analysis and chunking logic
│   └── utils/                    # Utility functions
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests for individual handlers
│   ├── integration/              # Integration tests
│   └── comprehensive/            # End-to-end tests
├── examples/                     # Usage examples and demos
├── sample_data/                  # Test XML files
└── docs/                         # Documentation
```

## 🛠️ Development Guidelines

### Code Style

- **Python Style**: Follow PEP 8 with these specifics:
  - Line length: 100 characters maximum
  - Use type hints for all public functions
  - Docstrings: Google style format

- **Formatting**: Use Black for code formatting:
  ```bash
  black src/ tests/ examples/
  ```

- **Linting**: Use flake8 for linting:
  ```bash
  flake8 src/ tests/ examples/
  ```

### Testing Requirements

All contributions must include appropriate tests:

- **Unit Tests**: Test individual handler methods
- **Integration Tests**: Test handler with real XML files
- **Regression Tests**: Ensure existing functionality isn't broken

**Running Tests:**
```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## 🚀 Using the Framework (v1.2.3+)

### Simple API for End Users
```python
import xml_analysis_framework as xaf

# One-line analysis with specialized handlers
result = xaf.analyze("document.xml")
print(f"Document: {result['document_type'].type_name}")

# Basic schema analysis
schema = xaf.analyze_schema("document.xml")
print(f"Elements: {schema.total_elements}")

# Smart chunking for AI/ML
chunks = xaf.chunk("document.xml", strategy="auto")
print(f"Created {len(chunks)} chunks")
```

### Advanced API for Contributors
```python
from xml_analysis_framework import XMLDocumentAnalyzer, ChunkingOrchestrator

# Custom configurations for testing/development
analyzer = XMLDocumentAnalyzer(max_file_size_mb=1000)
result = analyzer.analyze_document("test_file.xml")

# Test custom chunking strategies
orchestrator = ChunkingOrchestrator()
chunks = orchestrator.chunk_document("test_file.xml", result, strategy="hierarchical")
```

## 📝 Contributing Types

### 1. Adding New XML Handlers

We welcome handlers for new XML formats! Here's how to add one:

#### Handler Requirements
- Must extend the base `XMLHandler` interface
- Implement all required methods: `can_handle()`, `detect_type()`, `analyze()`, `extract_key_data()`
- Include comprehensive docstrings
- Handle edge cases gracefully
- Provide meaningful AI use case suggestions

#### Handler Template
```python
#!/usr/bin/env python3
"""
[Format Name] Handler

Handles [XML format description] documents.
Common file patterns: *.xml, *.specific_extension
"""

import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
from ..base import DocumentTypeInfo, SpecializedAnalysis, XMLHandler

class YourFormatHandler(XMLHandler):
    """Handler for [Format Name] XML documents"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        """Check if this handler can process the XML document"""
        # Implementation here
        pass
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        """Detect and classify the document type"""
        # Implementation here
        pass
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        """Perform specialized analysis"""
        # Implementation here
        pass
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        """Extract key structured data"""
        # Implementation here
        pass
```

#### Steps to Add a Handler

1. **Create the handler file**: `src/handlers/your_format_handler.py`
2. **Write comprehensive tests**: `tests/unit/test_your_format_handler.py`
3. **Add test XML files**: `sample_data/test_files/[size]/your_format_example.xml`
4. **Register the handler**: Add import in `src/handlers/__init__.py`
5. **Update documentation**: Add handler to README and architecture docs

### 2. Improving Chunking Strategies

The framework supports multiple chunking strategies for different use cases:

- **Hierarchical**: Preserves XML structure and relationships
- **Content-Aware**: Focuses on semantic content boundaries
- **Sliding Window**: Fixed-size chunks with overlap
- **Auto**: Automatically selects best strategy

**Contributing Chunking Improvements:**
- Enhance existing strategies in `src/core/chunking.py`
- Add new chunking algorithms
- Improve chunk quality metrics
- Optimize chunk size distribution

### 3. Test Coverage Improvements

Help us maintain our 100% success rate:

- Add test cases for edge cases
- Contribute XML files from real-world scenarios
- Create synthetic test data for complex scenarios
- Improve test automation and CI/CD

### 4. Documentation Enhancements

- API documentation improvements
- Usage examples and tutorials
- Architecture diagrams and explanations
- Best practices guides

## 📋 Submission Process

### Pull Request Guidelines

1. **Fork and Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**:
   - Follow coding standards
   - Add comprehensive tests
   - Update documentation as needed

3. **Test Your Changes**:
   ```bash
   # Run full test suite
   python -m pytest tests/
   
   # Run linting
   flake8 src/ tests/
   black --check src/ tests/
   
   # Test with real XML files
   python demo_xml_framework.py
   ```

4. **Commit with Clear Messages**:
   ```bash
   git commit -m "Add ServiceNow incident XML handler
   
   - Implements specialized handler for ServiceNow incident exports
   - Includes field extraction and relationship mapping
   - Adds comprehensive test coverage with sample files
   - Generates AI use cases for incident analysis"
   ```

5. **Create Pull Request**:
   - Use descriptive title and detailed description
   - Reference any related issues
   - Include test results and examples

### Pull Request Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] New XML handler
- [ ] Bug fix
- [ ] Performance improvement
- [ ] Documentation update
- [ ] Test coverage improvement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] New test files added (if applicable)

## Sample XML Files
List any new test files added or existing files that benefit from this change.

## AI Use Cases
Describe potential AI/ML applications enabled by this contribution.

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Changes don't break existing functionality
```

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues for duplicates
2. Test with the latest version
3. Try to reproduce with minimal example

### Bug Report Template
```markdown
**Describe the Bug**
Clear description of the problem.

**XML File Details**
- File type/format: 
- File size:
- Sample content (sanitized):

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Error Messages**
Full error traceback if applicable.

**Environment**
- Python version:
- Operating system:
- Framework version:

**Reproduction Steps**
1. Step one
2. Step two
3. ...
```

## 💡 Feature Requests

We welcome suggestions for new features! Please include:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **XML Formats**: What formats would benefit?
- **AI Applications**: How would this enable AI/ML use cases?

## 🎖️ Recognition

Contributors are recognized in several ways:

- **README Credits**: Listed in the contributors section
- **Release Notes**: Contributions highlighted in release announcements
- **Handler Attribution**: Handler files include author information
- **Community Recognition**: Outstanding contributions featured in project updates

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community interaction
- **Documentation**: Check the `docs/` directory for detailed guides

## 📄 Code of Conduct

This project follows a professional and inclusive environment:

- Be respectful and constructive in all interactions
- Focus on the technical aspects of contributions
- Help create a welcoming space for contributors of all backgrounds
- Follow GitHub's Community Guidelines

## 🎯 Contribution Priorities

Current high-priority areas for contributions:

1. **Enterprise XML Handlers**: ERP, CRM, and business system formats
2. **Healthcare Standards**: HL7, CCDA, FHIR XML formats  
3. **Government/Compliance**: SCAP, XBRL, regulatory formats
4. **Performance Optimization**: Large file handling and memory efficiency
5. **AI Integration**: Enhanced semantic analysis and chunking strategies

---

Thank you for contributing to the XML Analysis Framework! Your contributions help make XML analysis more accessible and powerful for the AI/ML community.