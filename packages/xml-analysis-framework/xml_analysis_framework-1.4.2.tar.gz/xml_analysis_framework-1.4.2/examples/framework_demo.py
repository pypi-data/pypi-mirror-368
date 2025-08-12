#!/usr/bin/env python3
"""
XML Analysis Framework Demonstration

This script demonstrates the full capabilities of the XML analysis framework,
including specialized handlers, chunking strategies, and AI use case identification.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.analyzer import XMLSchemaAnalyzer, XMLDocumentAnalyzer
from src.core.chunking import ChunkingOrchestrator, ChunkingConfig

def print_separator(title: str = ""):
    """Print a nice separator line"""
    if title:
        print(f"\n{'='*20} {title} {'='*20}")
    else:
        print("="*60)

def demonstrate_specialized_handlers():
    """Demonstrate the specialized handler system"""
    print_separator("SPECIALIZED HANDLER DEMONSTRATION")
    
    # Example XML files to test
    test_files = [
        {
            "path": "sample_data/pom.xml",
            "content": """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>demo-app</artifactId>
    <version>1.0.0</version>
    <packaging>jar</packaging>
    
    <properties>
        <java.version>11</java.version>
        <spring.version>5.3.10</spring.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-core</artifactId>
            <version>${spring.version}</version>
        </dependency>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>"""
        },
        {
            "path": "sample_data/log4j2.xml",
            "content": """<?xml version="1.0" encoding="UTF-8"?>
<Configuration status="WARN" monitorInterval="30">
    <Appenders>
        <Console name="Console" target="SYSTEM_OUT">
            <PatternLayout pattern="%d{HH:mm:ss.SSS} [%t] %-5level %logger{36} - %msg%n"/>
        </Console>
        <RollingFile name="RollingFile" fileName="logs/app.log"
                     filePattern="logs/app-%d{MM-dd-yyyy}-%i.log.gz">
            <PatternLayout pattern="%d{ISO8601} [%t] %-5level %logger{36} - %msg%n"/>
            <Policies>
                <TimeBasedTriggeringPolicy/>
                <SizeBasedTriggeringPolicy size="10MB"/>
            </Policies>
        </RollingFile>
    </Appenders>
    <Loggers>
        <Logger name="com.example" level="DEBUG" additivity="false">
            <AppenderRef ref="Console"/>
            <AppenderRef ref="RollingFile"/>
        </Logger>
        <Root level="INFO">
            <AppenderRef ref="Console"/>
        </Root>
    </Loggers>
</Configuration>"""
        },
        {
            "path": "sample_data/rss_feed.xml",
            "content": """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Tech News Daily</title>
        <link>https://example.com/news</link>
        <description>Latest technology news and updates</description>
        <item>
            <title>AI Breakthrough in Natural Language Processing</title>
            <description>Researchers announce significant improvements in LLM capabilities</description>
            <link>https://example.com/news/ai-breakthrough</link>
            <pubDate>Mon, 23 Jul 2025 10:00:00 GMT</pubDate>
            <category>AI</category>
        </item>
        <item>
            <title>New Security Vulnerability Discovered</title>
            <description>Critical vulnerability affects millions of devices worldwide</description>
            <link>https://example.com/news/security-alert</link>
            <pubDate>Sun, 22 Jul 2025 15:30:00 GMT</pubDate>
            <category>Security</category>
        </item>
    </channel>
</rss>"""
        }
    ]
    
    # Create sample files
    sample_dir = Path("sample_data")
    sample_dir.mkdir(exist_ok=True)
    
    for test_file in test_files:
        file_path = Path(test_file["path"])
        file_path.parent.mkdir(exist_ok=True)
        file_path.write_text(test_file["content"])
    
    # Analyze each file
    analyzer = XMLDocumentAnalyzer()
    
    for test_file in test_files:
        print(f"\n📄 Analyzing: {test_file['path']}")
        print("-" * 40)
        
        result = analyzer.analyze_document(test_file["path"])
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        doc_type = result["document_type"]
        analysis = result["analysis"]
        
        print(f"✅ Document Type: {doc_type.type_name}")
        print(f"   Confidence: {doc_type.confidence:.1%}")
        print(f"   Handler: {result['handler_used']}")
        
        if analysis:
            print(f"\n🔍 Key Findings:")
            for key, value in list(analysis.key_findings.items())[:3]:
                print(f"   - {key}: {value}")
            
            print(f"\n🤖 AI Use Cases:")
            for use_case in analysis.ai_use_cases[:3]:
                print(f"   - {use_case}")
            
            print(f"\n📊 Data Quality:")
            for metric, score in analysis.quality_metrics.items():
                print(f"   - {metric}: {score:.1%}")

def demonstrate_chunking_strategies():
    """Demonstrate different chunking strategies"""
    print_separator("CHUNKING STRATEGY DEMONSTRATION")
    
    # Create a larger sample XML for chunking
    large_xml_path = Path("sample_data/large_document.xml")
    large_xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<documentation>
    <metadata>
        <title>System Administration Guide</title>
        <version>2.0</version>
        <date>2025-07-23</date>
    </metadata>
    <chapters>
        <chapter id="intro">
            <title>Introduction</title>
            <section>
                <title>Overview</title>
                <para>This guide provides comprehensive information about system administration tasks.</para>
                <para>It covers installation, configuration, maintenance, and troubleshooting.</para>
            </section>
            <section>
                <title>Prerequisites</title>
                <para>Before beginning, ensure you have the following:</para>
                <list>
                    <item>Administrative access to the system</item>
                    <item>Basic understanding of command line interfaces</item>
                    <item>Network connectivity for updates</item>
                </list>
            </section>
        </chapter>
        <chapter id="installation">
            <title>Installation</title>
            <section>
                <title>System Requirements</title>
                <para>The following are minimum system requirements:</para>
                <table>
                    <row><cell>CPU</cell><cell>2 cores @ 2.0 GHz</cell></row>
                    <row><cell>RAM</cell><cell>4 GB minimum, 8 GB recommended</cell></row>
                    <row><cell>Storage</cell><cell>20 GB available space</cell></row>
                </table>
            </section>
            <section>
                <title>Installation Steps</title>
                <para>Follow these steps to install the system:</para>
                <code language="bash">
# Download the installer
wget https://example.com/installer.sh

# Make it executable
chmod +x installer.sh

# Run the installer
sudo ./installer.sh
                </code>
            </section>
        </chapter>
        <chapter id="configuration">
            <title>Configuration</title>
            <section>
                <title>Basic Configuration</title>
                <para>After installation, configure the basic settings.</para>
                <para>Edit the main configuration file located at /etc/system/config.xml</para>
            </section>
            <section>
                <title>Advanced Options</title>
                <para>For advanced users, additional options are available.</para>
                <para>These include performance tuning, security hardening, and custom modules.</para>
            </section>
        </chapter>
    </chapters>
</documentation>"""
    
    large_xml_path.write_text(large_xml_content)
    
    # Analyze the document first
    analyzer = XMLDocumentAnalyzer()
    analysis_result = analyzer.analyze_document(str(large_xml_path))
    
    # Test different chunking strategies
    orchestrator = ChunkingOrchestrator()
    
    strategies = ['hierarchical', 'sliding_window', 'content_aware']
    
    for strategy in strategies:
        print(f"\n📦 Testing {strategy.upper()} chunking strategy")
        print("-" * 40)
        
        # Custom config for demonstration
        config = ChunkingConfig(
            max_chunk_size=500,  # Smaller chunks for demo
            min_chunk_size=100,
            overlap_size=50,
            preserve_hierarchy=True
        )
        
        chunks = orchestrator.chunk_document(
            str(large_xml_path),
            analysis_result,
            strategy=strategy,
            config=config
        )
        
        print(f"✂️  Created {len(chunks)} chunks")
        
        # Show first 2 chunks
        for i, chunk in enumerate(chunks[:2]):
            print(f"\n   Chunk {i+1}:")
            print(f"   - ID: {chunk.chunk_id}")
            print(f"   - Path: {chunk.element_path}")
            print(f"   - Tokens: ~{chunk.token_estimate}")
            print(f"   - Elements: {', '.join(chunk.elements_included[:3])}")
            print(f"   - Preview: {chunk.content[:80]}...")

def demonstrate_ai_use_cases():
    """Show how the analysis can be used for AI projects"""
    print_separator("AI USE CASE DEMONSTRATION")
    
    # Create a sample SCAP document
    scap_path = Path("sample_data/security_scan.xml")
    scap_content = """<?xml version="1.0" encoding="UTF-8"?>
<arf:asset-report-collection xmlns:arf="http://scap.nist.gov/schema/asset-reporting-format/1.1">
    <core:relationships xmlns:core="http://scap.nist.gov/schema/reporting-core/1.1">
        <core:relationship type="isAbout" subject="scan1">
            <core:ref>server-01</core:ref>
        </core:relationship>
    </core:relationships>
    <arf:reports>
        <arf:report id="scan1">
            <content>
                <rule-result idref="xccdf_rule_1" severity="high">
                    <result>fail</result>
                    <message>SSH root login is enabled</message>
                </rule-result>
                <rule-result idref="xccdf_rule_2" severity="medium">
                    <result>pass</result>
                    <message>Firewall is properly configured</message>
                </rule-result>
                <rule-result idref="xccdf_rule_3" severity="high">
                    <result>fail</result>
                    <message>System updates are not configured</message>
                </rule-result>
            </content>
        </arf:report>
    </arf:reports>
</arf:asset-report-collection>"""
    
    scap_path.write_text(scap_content)
    
    # Analyze the document
    analyzer = XMLDocumentAnalyzer()
    result = analyzer.analyze_document(str(scap_path))
    
    print("\n🎯 AI Project Planning Assistant")
    print("-" * 40)
    
    if result.get("analysis"):
        analysis = result["analysis"]
        doc_type = result["document_type"].type_name
        
        print(f"\n📄 Document Type: {doc_type}")
        print(f"\n🤖 Recommended AI Applications:")
        
        for i, use_case in enumerate(analysis.ai_use_cases, 1):
            print(f"\n{i}. {use_case}")
            
            # Provide specific guidance for each use case
            if "compliance" in use_case.lower():
                print("   📋 Implementation approach:")
                print("   - Extract rule violations and patterns")
                print("   - Train classifier on historical compliance data")
                print("   - Build automated remediation suggestions")
                
            elif "risk" in use_case.lower():
                print("   📋 Implementation approach:")
                print("   - Aggregate severity scores and failure patterns")
                print("   - Develop risk scoring model")
                print("   - Create predictive analytics dashboard")
                
            elif "recommendation" in use_case.lower():
                print("   📋 Implementation approach:")
                print("   - Map failures to remediation steps")
                print("   - Use NLP to generate human-readable fixes")
                print("   - Prioritize based on risk and effort")
        
        print(f"\n📊 Data Availability:")
        for data_type, count in analysis.data_inventory.items():
            print(f"   - {data_type}: {count}")
        
        print(f"\n✨ Quick Start Code:")
        print("""
# Load and process the analyzed data
from pathlib import Path
import json

# Load the analysis results
with open('security_scan_enhanced_analysis.json') as f:
    analysis = json.load(f)

# Extract structured data for ML
structured_data = analysis['specialized_analysis']['analysis']['structured_data']

# Example: Build a compliance classifier
failed_rules = [rule for rule in structured_data.get('scan_results', []) 
                if rule.get('result') == 'fail']

# Train your model on the extracted data
# model.train(failed_rules, remediation_labels)
""")

def demonstrate_integration_workflow():
    """Show a complete workflow from analysis to LLM preparation"""
    print_separator("COMPLETE INTEGRATION WORKFLOW")
    
    print("\n🔄 Workflow: XML → Analysis → Chunks → LLM-Ready")
    print("-" * 40)
    
    # Use the existing STIG file
    stig_path = Path("sample_data/node2.example.com-STIG-20250710162433.xml")
    
    if not stig_path.exists():
        print("❌ STIG sample file not found. Using a smaller example.")
        # Create a simple example
        stig_path = Path("sample_data/mini_stig.xml")
        stig_path.write_text("""<?xml version="1.0"?>
<Benchmark id="xccdf_benchmark">
    <Group id="V-1234">
        <title>Security Configuration</title>
        <Rule id="rule_1234" severity="high">
            <title>Ensure secure settings</title>
            <description>This rule checks for secure configurations</description>
            <check system="http://oval.mitre.org/XMLSchema/oval-definitions-5">
                <check-content-ref href="#oval:check:1234"/>
            </check>
        </Rule>
    </Group>
</Benchmark>""")
    
    print(f"\n1️⃣ Step 1: Analyze Document")
    analyzer = XMLDocumentAnalyzer()
    analysis = analyzer.analyze_document(str(stig_path))
    
    print(f"   ✅ Document type: {analysis['document_type'].type_name}")
    print(f"   ✅ Handler confidence: {analysis['confidence']:.1%}")
    
    print(f"\n2️⃣ Step 2: Apply Intelligent Chunking")
    orchestrator = ChunkingOrchestrator()
    chunks = orchestrator.chunk_document(
        str(stig_path),
        analysis,
        strategy='auto'
    )
    
    print(f"   ✅ Created {len(chunks)} chunks")
    print(f"   ✅ Strategy selected: {orchestrator._select_strategy(analysis)}")
    
    print(f"\n3️⃣ Step 3: Prepare for LLM Processing")
    
    # Simulate LLM prompts for first chunk
    if chunks:
        chunk = chunks[0]
        prompt = f"""You are analyzing a {analysis['document_type'].type_name} document.

Document Context:
- Type: {analysis['document_type'].type_name}
- Total chunks: {len(chunks)}
- Current chunk: 1 of {len(chunks)}

Chunk Content:
{chunk.content[:500]}...

Based on this security compliance data, please:
1. Identify any high-severity findings
2. Suggest remediation steps
3. Assess overall security posture
"""
        
        print("   📝 Generated LLM Prompt Preview:")
        print("   " + "-" * 35)
        for line in prompt.split('\n')[:10]:
            print(f"   {line}")
        print("   ...")
    
    print(f"\n4️⃣ Step 4: Process Results")
    print("   ✅ Ready for LLM processing")
    print("   ✅ Chunks maintain context")
    print("   ✅ Specialized extraction completed")

def main():
    """Run all demonstrations"""
    print("\n🚀 XML ANALYSIS FRAMEWORK DEMONSTRATION")
    print("=====================================")
    
    # Create sample directory
    Path("sample_data").mkdir(exist_ok=True)
    
    try:
        # Run demonstrations
        demonstrate_specialized_handlers()
        demonstrate_chunking_strategies()
        demonstrate_ai_use_cases()
        demonstrate_integration_workflow()
        
        print_separator("DEMONSTRATION COMPLETE")
        print("\n✅ All demonstrations completed successfully!")
        print("\n📚 Next Steps:")
        print("1. Try with your own XML files: python analyze_enhanced.py your_file.xml")
        print("2. Create custom handlers for your specific XML formats")
        print("3. Integrate with your LLM pipeline for automated processing")
        print("4. Build AI applications using the extracted structured data")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
