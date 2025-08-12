#!/usr/bin/env python3
"""
Enhanced XML Analyzer with Specialized Handlers

This is an updated version of analyze.py that integrates the specialized handler system
for more intelligent XML document analysis.
"""

import sys
import json
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.core.analyzer import XMLDocumentAnalyzer
    from src.core.schema_analyzer import XMLSchemaAnalyzer
    from src.core.chunking import ChunkingOrchestrator
except ImportError as e:
    print(f"Error: Could not import required modules: {e}")
    print("Make sure you're running from the project root directory.")
    sys.exit(1)

def format_size(bytes_size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def analyze_file_enhanced(file_path):
    """Enhanced analysis using specialized handlers"""
    
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
        # Use specialized analyzer first
        specialized_analyzer = XMLDocumentAnalyzer()
        specialized_result = specialized_analyzer.analyze_document(str(file_path))
        
        # Also run basic schema analysis for compatibility
        basic_analyzer = XMLSchemaAnalyzer()
        schema = basic_analyzer.analyze_file(str(file_path))
        llm_description = basic_analyzer.generate_llm_description(schema)
        
        # Check if we should chunk the document
        should_chunk = file_size > 1024 * 1024  # Chunk if larger than 1MB
        chunks = []
        
        if should_chunk:
            print("📦 Large file detected, applying chunking strategy...")
            chunker = XMLChunkingStrategy()
            chunks = chunker.chunk_document(
                str(file_path),
                specialized_result
            )
            print(f"✂️  Created {len(chunks)} chunks")
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "file_info": {
                "name": file_path.name,
                "size_bytes": file_size,
                "size_formatted": format_size(file_size)
            },
            "basic_schema": {
                "document_type": schema.root_element,
                "total_elements": schema.total_elements,
                "unique_elements": len(schema.elements),
                "max_depth": schema.max_depth,
                "namespaces": schema.namespaces
            },
            "specialized_analysis": {
                "document_type": specialized_result.get("document_type"),
                "handler": specialized_result.get("handler_used"),
                "confidence": specialized_result.get("confidence"),
                "analysis": specialized_result.get("analysis")
            },
            "chunking": {
                "was_chunked": should_chunk,
                "chunk_count": len(chunks),
                "chunks_summary": [
                    {
                        "id": chunk.chunk_id,
                        "tokens": chunk.token_estimate,
                        "path": chunk.element_path
                    } for chunk in chunks[:5]  # First 5 chunks as summary
                ] if chunks else []
            },
            "llm_description": llm_description,
            "processing_time": processing_time
        }
        
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "processing_time": time.time() - start_time
        }

def print_enhanced_results(results):
    """Print enhanced analysis results"""
    
    if "error" in results:
        print(f"❌ {results['error']}")
        return
    
    print("✅ Analysis Complete!")
    print("=" * 60)
    
    # File information
    info = results["file_info"]
    print(f"📄 File: {info['name']}")
    print(f"📊 Size: {info['size_formatted']}")
    
    # Basic schema summary
    schema = results["basic_schema"]
    print(f"\n📋 Basic Structure:")
    print(f"   Root Element: {schema['document_type']}")
    print(f"   Total Elements: {schema['total_elements']:,}")
    print(f"   Unique Elements: {schema['unique_elements']}")
    print(f"   Max Depth: {schema['max_depth']}")
    print(f"   Namespaces: {len(schema['namespaces'])}")
    
    # Specialized analysis
    specialized = results["specialized_analysis"]
    if specialized["document_type"]:
        print(f"\n🎯 Document Type Detection:")
        print(f"   Type: {specialized['document_type'].get('type_name', 'Unknown')}")
        print(f"   Confidence: {specialized['confidence']:.1%}")
        print(f"   Handler: {specialized['handler']}")
        
        analysis = specialized["analysis"]
        if analysis:
            print(f"\n🔍 Specialized Analysis:")
            
            # Key findings
            if analysis.get("key_findings"):
                print("   Key Findings:")
                for key, value in list(analysis["key_findings"].items())[:5]:
                    print(f"     - {key}: {value}")
            
            # AI use cases
            if analysis.get("ai_use_cases"):
                print("   Potential AI Use Cases:")
                for use_case in analysis["ai_use_cases"][:3]:
                    print(f"     - {use_case}")
            
            # Data quality
            if analysis.get("quality_metrics"):
                print("   Data Quality:")
                for metric, score in analysis["quality_metrics"].items():
                    print(f"     - {metric}: {score:.1%}")
    
    # Chunking information
    chunking = results["chunking"]
    if chunking["was_chunked"]:
        print(f"\n📦 Document Chunking:")
        print(f"   Chunks Created: {chunking['chunk_count']}")
        if chunking["chunks_summary"]:
            print("   Sample Chunks:")
            for chunk in chunking["chunks_summary"]:
                print(f"     - {chunk['id']}: ~{chunk['tokens']} tokens")
    
    # Processing info
    print(f"\n⏱️  Processed in {results['processing_time']:.2f} seconds")

def save_enhanced_results(results, output_file):
    """Save enhanced results to JSON file"""
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {output_file}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")

def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Enhanced XML Analyzer")
        print("====================")
        print("\nUsage: python analyze_enhanced.py <xml_file> [options]")
        print("\nOptions:")
        print("  --basic     Use only basic analysis (no specialized handlers)")
        print("  --no-chunk  Disable chunking for large files")
        print("\nExamples:")
        print("  python analyze_enhanced.py sample_data/node2.example.com-STIG-20250710162433.xml")
        print("  python analyze_enhanced.py my_file.xml --basic")
        sys.exit(1)
    
    input_file = sys.argv[1]
    use_basic = "--basic" in sys.argv
    
    if use_basic:
        # Import and use the original analyze_file function
        from basic_analysis import analyze_file, print_results, save_results
        results = analyze_file(input_file)
        print_results(results)
        
        if results.get("success"):
            output_file = Path(input_file).stem + "_analysis.json"
            save_results(results, output_file)
    else:
        # Use enhanced analysis
        results = analyze_file_enhanced(input_file)
        print_enhanced_results(results)
        
        if results.get("success"):
            output_file = Path(input_file).stem + "_enhanced_analysis.json"
            save_enhanced_results(results, output_file)
    
    # Return appropriate exit code
    sys.exit(0 if results.get("success") else 1)

if __name__ == "__main__":
    main()
