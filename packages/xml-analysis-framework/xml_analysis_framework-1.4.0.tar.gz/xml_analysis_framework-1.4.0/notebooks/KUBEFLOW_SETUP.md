# Kubeflow Pipeline Setup for XML Analysis Framework

This guide shows how to deploy the XML Analysis Framework as a production Kubeflow pipeline.

## 🏗️ **Architecture Overview**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Data Ingestion │───▶│ Vector Population│───▶│   Graph & RAG   │
│                 │    │                  │    │                 │
│ • XML Analysis  │    │ • Embeddings     │    │ • Graph Prep    │
│ • Chunking      │    │ • LanceDB        │    │ • RAG System    │
│ • Metadata      │    │ • Vector Index   │    │ • Final Summary │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 **Quick Start**

### **Prerequisites**
1. **Kubeflow Cluster**: Running Kubeflow Pipelines
2. **Python Environment**: Python 3.8+ with kubeflow-pipelines SDK
3. **Cluster Access**: kubectl configured for your cluster

### **Installation**
```bash
# Install Kubeflow Pipelines SDK
pip install kfp>=2.0.0

# Install additional dependencies
pip install xml-analysis-framework==1.2.12
```

### **Deploy Pipeline**
```bash
# Compile pipeline
python kubeflow_pipeline.py

# Deploy and run
python deploy_kubeflow.py
```

## 📦 **Pipeline Components**

### **Component 1: Data Ingestion**
- **Resources**: 1 CPU, 2Gi Memory
- **Dependencies**: xml-analysis-framework, pandas
- **Outputs**: 
  - Document analyses (JSON)
  - Vector-ready chunks (JSON)  
  - Pipeline metadata (JSON)

### **Component 2: Vector Population**
- **Resources**: 2 CPU, 4Gi Memory
- **Dependencies**: lancedb, sentence-transformers, pyarrow
- **Outputs**:
  - Vector database (LanceDB)
  - Enriched chunks with embeddings (JSON)

### **Component 3: Graph & RAG**
- **Resources**: 1 CPU, 2Gi Memory
- **Dependencies**: pandas
- **Outputs**:
  - Graph relationship data (JSON)
  - Final pipeline summary (JSON)

## 🔧 **Configuration**

### **Environment Variables**
```bash
export KUBEFLOW_ENDPOINT="http://your-kubeflow-host:8080"
export KUBEFLOW_NAMESPACE="your-namespace"
```

### **Custom Configuration**
Edit `deploy_kubeflow.py` to customize:
- Pipeline parameters
- Resource requirements
- Container images
- Persistent volume mounts

## 📊 **Production Considerations**

### **Data Volumes**
For production, mount persistent volumes for:
- **Input Data**: XML documents to process
- **Vector Database**: LanceDB persistence
- **Output Artifacts**: Results and logs

```python
# Example volume mount configuration
@component(base_image="python:3.11-slim")
def data_ingestion_component(
    input_data_path: str = "/data/xml_files"  # Mounted volume
):
    # Process files from mounted volume
    xml_files = Path(input_data_path).glob("*.xml")
```

### **Container Images**
Build custom images with pre-installed dependencies:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install \\
    xml-analysis-framework==1.2.12 \\
    lancedb>=0.4.0 \\
    sentence-transformers>=2.2.0 \\
    pyarrow>=10.0.0

WORKDIR /app
```

### **Resource Scaling**
Adjust resources based on workload:

```python
# High-volume processing
data_ingestion_task.set_cpu_request("4").set_memory_request("8Gi")
vector_population_task.set_cpu_request("8").set_memory_request("16Gi")
```

### **Monitoring & Logging**
- Use Kubeflow's built-in monitoring
- Add custom metrics with pipeline decorators
- Configure log aggregation

## 🔍 **Troubleshooting**

### **Common Issues**

1. **Container Image Pull Failures**
   ```bash
   # Check image availability
   kubectl describe pod <pod-name>
   ```

2. **Resource Constraints**
   ```bash
   # Check resource limits
   kubectl describe nodes
   ```

3. **Permission Issues**
   ```bash
   # Check service account permissions
   kubectl get serviceaccounts
   ```

### **Debug Mode**
Enable verbose logging:
```python
# Add to component decorator
@component(base_image="...", debugging=True)
```

## 🎯 **Advanced Features**

### **Parallel Processing**
Process multiple documents in parallel:

```python
@component
def parallel_data_ingestion(file_list: list):
    # Use multiprocessing for concurrent analysis
    from multiprocessing import Pool
    
    with Pool(processes=4) as pool:
        results = pool.map(analyze_document, file_list)
    
    return results
```

### **Conditional Execution**
Skip components based on conditions:

```python
@pipeline
def conditional_xml_pipeline():
    data_task = data_ingestion_component()
    
    # Only run vector processing if we have chunks
    with dsl.Condition(data_task.outputs['total_chunks'] > 0):
        vector_task = vector_population_component(...)
```

### **Hyperparameter Tuning**
Use Katib for model optimization:

```python
# Define parameter space for embedding models
from kubeflow.katib import ApiClient

# Optimize embedding model selection
embedding_models = ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "distilbert-base-nli-stsb-mean-tokens"]
```

## 📈 **Performance Optimization**

### **Caching**
Enable pipeline caching for faster reruns:
```python
@pipeline
def xml_analysis_pipeline():
    # Enable caching for expensive operations
    data_task = data_ingestion_component().set_caching_options(True)
```

### **GPU Acceleration**
For large-scale embedding generation:
```python
vector_population_task.set_gpu_limit(1).add_node_selector_constraint('accelerator', 'nvidia-tesla-k80')
```

## 🔗 **Integration Examples**

### **Slack Notifications**
```python
@component
def notify_completion(status: str):
    import requests
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    requests.post(webhook_url, json={"text": f"Pipeline {status}"})
```

### **S3 Output Storage**
```python
@component
def save_to_s3(data: Input[Dataset]):
    import boto3
    s3 = boto3.client('s3')
    s3.upload_file(data.path, 'my-bucket', 'pipeline-results.json')
```

## 📚 **Resources**

- [Kubeflow Pipelines Documentation](https://www.kubeflow.org/docs/components/pipelines/)
- [KFP SDK Reference](https://kubeflow-pipelines.readthedocs.io/)
- [XML Analysis Framework Docs](../README.md)

## 🎉 **Next Steps**

1. **Deploy to Production**: Set up persistent volumes and proper RBAC
2. **Scale Horizontally**: Add parallel processing for large document collections
3. **Add Monitoring**: Integrate with Prometheus/Grafana
4. **Automate Triggers**: Set up event-driven pipeline execution
5. **Model Management**: Add MLflow integration for model versioning

---

**Happy pipelining! 🚀**