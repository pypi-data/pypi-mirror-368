# XML Analysis Framework - Notebooks

This directory contains Jupyter notebooks demonstrating various use cases and integrations for the XML Analysis Framework. These notebooks provide hands-on examples for testing, development, and production deployment scenarios.

## 📁 Notebook Overview

### 1. [Testing Documentation Examples](01_testing_documentation_examples.ipynb)
**Purpose**: Validate all documentation examples work correctly
- Tests all README code examples interactively
- Verifies Simple, Advanced, and Expert API usage
- Demonstrates JSON export functionality
- Uses synthetic test data for safe experimentation

**Use when**: 
- Testing framework functionality
- Validating documentation accuracy
- Learning the API
- Troubleshooting issues

### 2. [Agentic Workflow Example](02_agentic_workflow_example.ipynb)
**Purpose**: Shows integration with AI agent frameworks like LangChain
- Demonstrates intelligent document analysis
- Shows how to create AI-powered document Q&A
- Provides templates for LangChain integration
- Includes simulated agent workflows

**Use when**:
- Building AI agents that process XML documents
- Creating conversational interfaces for document analysis
- Implementing intelligent document routing
- Developing AI-powered insights systems

### 3. [Pipeline Data Ingestion](03_pipeline_data_ingestion.ipynb) 
**Purpose**: First stage of a production pipeline
- Batch processes multiple XML documents
- Creates structured analysis results
- Prepares data for vector database ingestion
- Generates processing metadata and summaries

**Use when**:
- Processing large document collections
- Setting up production data pipelines
- Batch analyzing enterprise document stores
- Preparing data for AI/ML workflows

### 4. [Vector Database Population](04_pipeline_vector_population.ipynb)
**Purpose**: Second stage - creates searchable vector database
- Generates embeddings using local sentence transformers
- Populates LanceDB with document chunks
- Creates search indexes for similarity queries
- Prepares graph relationship data

**Use when**:
- Building semantic search systems
- Creating document similarity engines
- Preparing for RAG (Retrieval Augmented Generation)
- Setting up vector-based recommendation systems

### 5. [Graph Database & RAG System](05_pipeline_graph_rag.ipynb)
**Purpose**: Final stage - unified knowledge system
- Populates Memgraph with document relationships
- Creates hybrid vector + graph search
- Demonstrates intelligent Q&A system
- Generates insights and recommendations

**Use when**:
- Building comprehensive knowledge systems
- Creating intelligent document discovery
- Implementing advanced RAG workflows
- Developing relationship-aware search

## 🏗️ Elyra Pipeline Integration

Notebooks 3-5 are designed to work as an **Elyra pipeline** for production workflows:

```
Data Ingestion → Vector Population → Graph & RAG
     (3)              (4)               (5)
```

### Pipeline Benefits:
- **Scalable**: Each stage can be scaled independently
- **Modular**: Stages can be modified or replaced
- **Resumable**: Pipeline can restart from any stage
- **Auditable**: Each stage produces detailed logs and metadata

### Running the Pipeline:

#### Option A: Individual Notebooks
Run each notebook in sequence:
1. Execute notebook 3 with your XML files
2. Execute notebook 4 to create vector database
3. Execute notebook 5 for graph and RAG functionality

#### Option B: Elyra Pipeline (Recommended)
1. Import notebooks into Elyra
2. Create pipeline connecting: `03 → 04 → 05`
3. Configure data paths and parameters
4. Execute complete pipeline with monitoring

## 🗂️ Data Directory

The `data/` subdirectory contains synthetic test files:
- `mapbox-example.kml` - Geographic data example
- `build.xml` - Apache Ant build configuration
- `spring-boot-example-pom.xml` - Maven project file
- `ivy.xml` - Ivy dependency management
- Additional synthetic XML files for testing

**Note**: All test files are synthetic and safe for experimentation.

## 🚀 Getting Started

### Prerequisites
1. **Python Environment**: Python 3.8+ with virtual environment
2. **Jupyter**: `pip install jupyter notebook` or `pip install jupyterlab`
3. **Framework**: `pip install xml-analysis-framework`
4. **API Keys**: OpenAI API key for notebooks 2-5 (see Environment Setup below)

### Quick Start
1. **Clone/Download** this notebooks directory
2. **Set up environment variables** (see Environment Setup below)
3. **Start Jupyter**: `jupyter notebook` or `jupyter lab`
4. **Begin with Notebook 1** to test basic functionality
5. **Progress to Notebook 2** for AI agent examples
6. **Use Notebooks 3-5** for production pipeline workflows

### Environment Setup

For notebooks that use AI features (notebooks 2-5), you'll need an OpenAI API key. You can set this up in two ways:

#### Option A: Using .env File (Recommended)
1. **Copy the example file**: `cp ../.env.example ../.env`
2. **Edit the .env file**: Add your actual OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```
3. **Install python-dotenv**: `pip install python-dotenv`
4. **Notebooks will automatically load**: The notebooks use `os.getenv('OPENAI_API_KEY')` to read from .env

#### Option B: System Environment Variable
Set the environment variable in your shell before starting Jupyter:
```bash
export OPENAI_API_KEY="your_actual_api_key_here"
jupyter notebook
```

**Security Note**: The .env file is in .gitignore and will never be committed to git. Always use environment variables for API keys in production.

### Advanced Setup (Full Pipeline)
For the complete pipeline experience:

```bash
# Install additional dependencies
pip install lancedb sentence-transformers pymgclient pandas python-dotenv

# Optional: Install Elyra for pipeline orchestration
pip install elyra

# Optional: Set up Memgraph for graph database
# (Pipeline works in simulation mode without it)
```

## 📊 Expected Outputs

### Testing Notebook (1):
- Verification that all documentation examples work
- JSON files with analysis results
- Confidence in framework functionality

### Agentic Workflow (2):
- Simulated AI agent conversations
- Vector database preparation examples
- LangChain integration templates

### Pipeline Notebooks (3-5):
- **Stage 1**: `pipeline_outputs/document_analyses.json`
- **Stage 2**: LanceDB vector database + embeddings
- **Stage 3**: Memgraph knowledge graph + RAG system
- **Final**: Comprehensive insights and recommendations

## 🔧 Customization

### Adding Your Data
1. **Replace test files** in `data/` with your XML documents
2. **Modify file paths** in notebooks as needed
3. **Adjust processing parameters** for your use case

### Extending the Pipeline
- **Add new stages** by creating additional notebooks
- **Modify vector models** for domain-specific embeddings
- **Customize graph schema** for your relationship types
- **Enhance RAG system** with domain-specific prompts

### Production Deployment
- **Use Elyra** for scalable pipeline orchestration
- **Deploy databases** (LanceDB, Memgraph) on infrastructure
- **Configure monitoring** and error handling
- **Set up automated scheduling** for batch processing

## 🤝 Integration Examples

### Document Management Systems
```python
# Process documents from SharePoint, Confluence, etc.
files = get_documents_from_cms()
for file in files:
    result = xaf.analyze(file)
    store_in_vector_db(result)
```

### Enterprise Search
```python
# Create searchable knowledge base
query = \"security configuration best practices\"
results = rag_system.unified_search(query)
return formatted_results(results)
```

### Compliance Monitoring
```python
# Analyze documents for compliance requirements
for doc in compliance_docs:
    analysis = xaf.analyze_enhanced(doc)
    check_compliance_rules(analysis)
```

## 📚 Additional Resources

- **Main Documentation**: [Framework README](../README.md)
- **API Reference**: [Framework Documentation](../docs/)
- **Contributing**: [Contribution Guidelines](../CONTRIBUTING.md)
- **Issues & Support**: [GitHub Issues](https://github.com/redhat-ai-americas/xml-analysis-framework/issues)

## ⚡ Performance Tips

1. **Batch Processing**: Use notebook 3 for multiple files
2. **Vector Models**: Choose appropriate embedding models for your domain
3. **Chunk Strategies**: Experiment with different chunking approaches
4. **Database Tuning**: Optimize vector and graph database configurations
5. **Pipeline Monitoring**: Use Elyra's monitoring for production workflows

## 🔒 Security Considerations

- **Test Data**: All included test files are synthetic and safe
- **API Keys**: 
  - Use .env files (automatically ignored by git) or system environment variables
  - Never hardcode API keys directly in notebooks or code
  - The provided .env.example shows the format but contains no real keys
- **Data Privacy**: Be mindful of sensitive data in document content
- **Database Security**: Secure vector and graph database connections
- **Access Control**: Implement appropriate authentication for production

---

**Happy analyzing! 🎉**

These notebooks demonstrate the power and flexibility of the XML Analysis Framework for building intelligent document processing systems. Start with the basics and work your way up to sophisticated AI-powered knowledge systems.