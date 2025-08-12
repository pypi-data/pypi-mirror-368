# Examples

This directory contains example usage scripts for the XML Analysis Framework.

## Available Examples

### Basic Analysis
- **basic_analysis.py** - Simple XML document analysis using core engine
- **enhanced_analysis.py** - Full analysis with specialized handlers and chunking
- **framework_demo.py** - Comprehensive demonstration of all framework features
- **quick_test.py** - Quick validation and testing script

### Demo Scripts
- **xml-demo-script.py** - Interactive demonstration script
- **xml_framework_demo_script.py** - Framework capabilities showcase

## Usage

```bash
# Basic analysis
python examples/basic_analysis.py sample_data/test_files/small/ant/build.xml

# Enhanced analysis with all handlers
python examples/enhanced_analysis.py sample_data/test_files/small/scap/security-report.xml

# Framework demonstration
python examples/framework_demo.py

# Quick test
python examples/quick_test.py
```

## Requirements

All examples use only Python standard library (3.8+) and defusedxml for secure parsing.