#!/usr/bin/env python3
"""
Test script to verify all documentation examples work correctly.
Run this before publishing to ensure examples are accurate.
"""

import sys
import json
from pathlib import Path

# Add src to path for local testing
sys.path.insert(0, 'src')

import xml_analysis_framework as xaf

def test_simple_api_example():
    """Test the Simple API example from README"""
    print("Testing Simple API example...")
    
    # Use the test file you mentioned
    test_file = "/Users/wjackson/Developer/AI-Building-Blocks/tests/mapbox-example.kml"
    
    # 🎯 One-line analysis with specialized handlers
    result = xaf.analyze(test_file)
    print(f"Document type: {result['document_type'].type_name}")
    print(f"Handler used: {result['handler_used']}")

    # 📊 Basic schema analysis  
    schema = xaf.analyze_schema(test_file)
    print(f"Elements: {schema.total_elements}, Depth: {schema.max_depth}")

    # ✂️ Smart chunking for AI/ML
    chunks = xaf.chunk(test_file, strategy="auto")
    print(f"Created {len(chunks)} optimized chunks")

    # Test the chunk attributes to see what's available
    if chunks:
        first_chunk = chunks[0]
        print(f"First chunk attributes: {dir(first_chunk)}")
        print(f"First chunk type: {type(first_chunk)}")
        print(f"Chunk ID: {first_chunk.chunk_id}")
        print(f"Content length: {len(first_chunk.content)}")
        print(f"Element path: {first_chunk.element_path}")
        print(f"Elements included: {first_chunk.elements_included}")

    # 💾 Save chunks to JSON - CORRECTED VERSION
    chunks_data = [
        {
            "chunk_id": chunk.chunk_id,
            "content": chunk.content,
            "element_path": chunk.element_path,  # Not chunk_type
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "elements_included": chunk.elements_included,
            "metadata": chunk.metadata,
            "token_estimate": chunk.token_estimate,
            "parent_context": chunk.parent_context
        }
        for chunk in chunks
    ]

    # Write to file
    with open("chunks_output.json", "w") as f:
        json.dump(chunks_data, f, indent=2)
    
    print(f"✅ Simple API example works! Saved {len(chunks_data)} chunks to chunks_output.json")
    return True

def test_advanced_api_example():
    """Test the Advanced API example from README"""
    print("\nTesting Advanced API example...")
    
    test_file = "/Users/wjackson/Developer/AI-Building-Blocks/tests/mapbox-example.kml"
    
    # Enhanced analysis with full results
    analysis = xaf.analyze_enhanced(test_file)

    print(f"Type: {analysis.type_name} (confidence: {analysis.confidence:.2f})")
    print(f"AI use cases: {len(analysis.ai_use_cases)}")
    if analysis.quality_metrics:
        print(f"Quality score: {analysis.quality_metrics.get('completeness_score', 'N/A')}")
    else:
        print("Quality metrics: Not available")

    # Different chunking strategies
    hierarchical_chunks = xaf.chunk(test_file, strategy="hierarchical")
    sliding_chunks = xaf.chunk(test_file, strategy="sliding_window") 
    content_chunks = xaf.chunk(test_file, strategy="content_aware")

    # Process chunks
    for chunk in hierarchical_chunks[:3]:  # Just first 3 to avoid spam
        print(f"Chunk {chunk.chunk_id}: {len(chunk.content)} chars")
        print(f"Element path: {chunk.element_path}, Elements: {len(chunk.elements_included)}")

    # 💾 Save different chunking strategies to separate files - CORRECTED VERSION
    # Helper function to convert chunk to dict
    def chunk_to_dict(chunk):
        return {
            "chunk_id": chunk.chunk_id,
            "content": chunk.content,
            "element_path": chunk.element_path,  # Not chunk_type
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "elements_included": chunk.elements_included,
            "metadata": chunk.metadata,
            "token_estimate": chunk.token_estimate,
            "parent_context": chunk.parent_context
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

    print("✅ Advanced API example works!")
    return True

def test_expert_api_example():
    """Test the Expert API example from README"""
    print("\nTesting Expert API example...")
    
    test_file = "/Users/wjackson/Developer/AI-Building-Blocks/tests/mapbox-example.kml"
    
    # For advanced customization, use the classes directly
    from xml_analysis_framework import XMLDocumentAnalyzer, ChunkingOrchestrator

    analyzer = XMLDocumentAnalyzer(max_file_size_mb=500)
    orchestrator = ChunkingOrchestrator(max_file_size_mb=1000)

    # Custom analysis
    result = analyzer.analyze_document(test_file)

    # Custom chunking with config (result works directly now!)
    from xml_analysis_framework.core.chunking import ChunkingConfig
    config = ChunkingConfig(
        max_chunk_size=2000,
        min_chunk_size=300,
        overlap_size=150,
        preserve_hierarchy=True
    )
    chunks = orchestrator.chunk_document(test_file, result, strategy="auto", config=config)

    # 💾 Save with analysis metadata - CORRECTED VERSION
    from datetime import datetime

    output_data = {
        "metadata": {
            "file": test_file,
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
                "element_path": chunk.element_path,  # Not chunk_type
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "elements_included": chunk.elements_included,
                "metadata": chunk.metadata,
                "token_estimate": chunk.token_estimate,
                "parent_context": chunk.parent_context
            }
            for chunk in chunks
        ]
    }

    with open("analysis_and_chunks.json", "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"Saved complete analysis with {len(chunks)} chunks to analysis_and_chunks.json")
    print("✅ Expert API example works!")
    return True

if __name__ == "__main__":
    print("Testing documentation examples...")
    print("=" * 50)
    
    try:
        test_simple_api_example()
        test_advanced_api_example() 
        test_expert_api_example()
        
        print("\n" + "=" * 50)
        print("🎉 All documentation examples work correctly!")
        
    except Exception as e:
        print(f"\n❌ Error in documentation examples: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)