#!/usr/bin/env python3
"""
Simple XML Document Analyzer

Usage: python analyze.py <filename>

Analyzes XML documents and provides structured output for LLM processing.
Automatically detects document type and generates appropriate analysis.
"""

import sys
import json
import time
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from core.schema_analyzer import XMLSchemaAnalyzer
except ImportError as e:
    print(f"Error: Could not import analyzer modules: {e}")
    print("Make sure the src/ directory contains the required files.")
    sys.exit(1)

def format_size(bytes_size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def analyze_file(file_path):
    """Analyze XML file and return structured results"""
    
    file_path = Path(file_path)
    
    # Basic file validation
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    
    if not file_path.is_file():
        return {"error": f"Path is not a file: {file_path}"}
    
    file_size = file_path.stat().st_size
    
    # Check if it's XML
    if file_path.suffix.lower() != '.xml':
        return {"error": f"Not an XML file: {file_path.suffix}"}
    
    print(f"📄 Analyzing: {file_path.name}")
    print(f"📊 Size: {format_size(file_size)}")
    print("⏳ Processing...")
    
    start_time = time.time()
    
    try:
        # Use the analyzer
        analyzer = XMLSchemaAnalyzer()
        schema = analyzer.analyze_file(str(file_path))
        
        # Generate LLM description
        llm_description = analyzer.generate_llm_description(schema)
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "file_info": {
                "name": file_path.name,
                "size_bytes": file_size,
                "size_formatted": format_size(file_size)
            },
            "schema": {
                "document_type": schema.root_element,
                "total_elements": schema.total_elements,
                "unique_elements": len(schema.elements),
                "max_depth": schema.max_depth,
                "namespaces": schema.namespaces
            },
            "analysis": llm_description,
            "processing_time": processing_time
        }
        
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "processing_time": time.time() - start_time
        }

def print_results(results):
    """Print analysis results in a clean format"""
    
    if "error" in results:
        print(f"❌ {results['error']}")
        return
    
    print("✅ Analysis Complete!")
    print("=" * 60)
    
    # File information
    info = results["file_info"]
    print(f"📄 File: {info['name']}")
    print(f"📊 Size: {info['size_formatted']}")
    
    # Schema summary
    schema = results["schema"]
    print(f"\n📋 Document Structure:")
    print(f"   Root Element: {schema['document_type']}")
    print(f"   Total Elements: {schema['total_elements']:,}")
    print(f"   Unique Elements: {schema['unique_elements']}")
    print(f"   Max Depth: {schema['max_depth']}")
    print(f"   Namespaces: {len(schema['namespaces'])}")
    
    # Processing info
    print(f"\n⏱️  Processed in {results['processing_time']:.2f} seconds")
    
    # Detailed analysis
    print(f"\n🔍 Detailed Analysis:")
    print("-" * 40)
    print(results["analysis"])

def save_results(results, output_file):
    """Save results to JSON file"""
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {output_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")

def main():
    """Main entry point"""
    
    if len(sys.argv) != 2:
        print("Usage: python analyze.py <xml_file>")
        print("\nExample:")
        print("  python analyze.py sample_data/node2.example.com-STIG-20250710162433.xml")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Analyze the file
    results = analyze_file(input_file)
    
    # Print results
    print_results(results)
    
    # Save results if successful
    if results.get("success"):
        output_file = Path(input_file).stem + "_analysis.json"
        save_results(results, output_file)
    
    # Return appropriate exit code
    sys.exit(0 if results.get("success") else 1)

if __name__ == "__main__":
    main()
