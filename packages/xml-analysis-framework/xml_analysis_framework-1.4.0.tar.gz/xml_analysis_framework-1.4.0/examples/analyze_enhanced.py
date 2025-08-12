#!/usr/bin/env python3
"""
Enhanced XML Analysis Example

Demonstrates the full capabilities of the XML analysis framework including:
- Document type detection
- Specialized handler analysis
- Chunking strategies
- AI/ML preparation features
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.analyzer import XMLDocumentAnalyzer


def analyze_xml_file(file_path: str):
    """Perform enhanced analysis on an XML file"""
    print(f"\n{'='*80}")
    print(f"ENHANCED XML ANALYSIS: {Path(file_path).name}")
    print(f"{'='*80}\n")
    
    # Initialize analyzer
    analyzer = XMLDocumentAnalyzer()
    
    # Perform analysis
    print("1. ANALYZING DOCUMENT...")
    result = analyzer.analyze_document(file_path)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    # Display document type and handler
    print(f"\n2. DOCUMENT TYPE DETECTION:")
    print(f"   Type: {result['document_type'].type_name}")
    print(f"   Confidence: {result['document_type'].confidence:.2f}")
    print(f"   Handler: {result['handler_used']}")
    
    # Display schema information
    if 'schema_analysis' in result:
        schema = result['schema_analysis']
        print(f"\n3. SCHEMA INFORMATION:")
        print(f"   Root Element: {schema.get('root_element', 'N/A')}")
        print(f"   Total Elements: {schema.get('total_elements', 0):,}")
        print(f"   Max Depth: {schema.get('max_depth', 0)}")
        print(f"   Unique Element Types: {len(schema.get('elements', {}))}")
        
        # Show namespaces if any
        if schema.get('namespaces'):
            print(f"   Namespaces:")
            for prefix, uri in schema['namespaces'].items():
                print(f"      {prefix}: {uri}")
    
    # Display specialized analysis
    if 'specialized_analysis' in result:
        analysis = result['specialized_analysis']
        print(f"\n4. SPECIALIZED ANALYSIS:")
        
        # Key findings
        if analysis.get('key_findings'):
            print("   Key Findings:")
            for key, value in analysis['key_findings'].items():
                if isinstance(value, dict):
                    print(f"      {key}:")
                    for k, v in value.items():
                        print(f"         {k}: {v}")
                else:
                    print(f"      {key}: {value}")
        
        # AI use cases
        if analysis.get('ai_use_cases'):
            print("\n   AI/ML Use Cases:")
            for use_case in analysis['ai_use_cases']:
                print(f"      • {use_case}")
        
        # Data inventory
        if analysis.get('data_inventory'):
            print("\n   Data Inventory:")
            for data_type, count in analysis['data_inventory'].items():
                print(f"      {data_type}: {count}")
        
        # Quality metrics
        if analysis.get('quality_metrics'):
            print("\n   Quality Metrics:")
            for metric, value in analysis['quality_metrics'].items():
                print(f"      {metric}: {value}")
    
    # Note: Chunking functionality is available but requires further implementation
    print(f"\n5. CHUNKING ANALYSIS:")
    print("   Note: Chunking strategies are available in src/core/chunking.py")
    print("   Methods include: hierarchical, sliding window, content-aware")
    print("   See ChunkingOrchestrator for implementation details")
    
    print(f"\n{'='*80}\n")
    
    return result


def main():
    """Main function to demonstrate enhanced analysis"""
    
    # Example files to analyze
    sample_files = [
        "sample_data/test_files/small/scap/ios-sample-1.0.xccdf.xml",
        "sample_data/test_files/small/ant/ant-ivy-build.xml",
        "sample_data/test_files/small/kml/mapbox-example.kml",
        "sample_data/test_files_synthetic/small/pom/spring-boot-example-pom.xml",
        "sample_data/test_files_synthetic/small/rss/sample-feed.xml",
        "sample_data/test_files_synthetic/small/servicenow/incident_export.xml",
        "sample_data/test_files_synthetic/medium/servicenow/full_export.xml"
    ]
    
    print("XML ANALYSIS FRAMEWORK - Enhanced Analysis Demo")
    print("=" * 80)
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Analyze each sample file
    for sample_file in sample_files:
        file_path = project_root / sample_file
        
        if file_path.exists():
            analyze_xml_file(str(file_path))
        else:
            print(f"\nWarning: Sample file not found: {sample_file}")
    
    # Allow user to specify a file
    if len(sys.argv) > 1:
        user_file = sys.argv[1]
        print(f"\nAnalyzing user-specified file: {user_file}")
        analyze_xml_file(user_file)


if __name__ == "__main__":
    main()