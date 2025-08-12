#!/usr/bin/env python3
"""
Quick test of the fixed XML analyzer
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.core.analyzer import XMLSchemaAnalyzer
    
    print("✅ Fixed analyzer imported successfully")
    
    # Test with a small XML sample
    test_xml = """<?xml version="1.0" encoding="UTF-8"?>
<test xmlns:ns="http://example.com">
    <item id="1">
        <name>Test Item</name>
        <value>123</value>
    </item>
    <item id="2">
        <name>Another Item</name>
        <value>456</value>
    </item>
</test>"""
    
    # Write test file
    test_file = "test_sample.xml"
    with open(test_file, 'w') as f:
        f.write(test_xml)
    
    # Test analysis
    analyzer = XMLSchemaAnalyzer()
    schema = analyzer.analyze_file(test_file)
    
    print(f"✅ Test analysis successful!")
    print(f"   Root element: {schema.root_element}")
    print(f"   Total elements: {schema.total_elements}")
    print(f"   Unique elements: {len(schema.elements)}")
    
    # Generate description
    description = analyzer.generate_llm_description(schema)
    print(f"✅ Description generated: {len(description)} characters")
    
    # Cleanup
    Path(test_file).unlink()
    
    print("\n🎉 Fixed analyzer is working correctly!")
    print("Ready to test with large files.")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
