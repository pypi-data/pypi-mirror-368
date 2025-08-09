# GRASS GIS RAG Pipeline - Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### 1. Package Installation Fails

**Problem**: `pip install grass-rag-pipeline` fails with errors

**Solutions:**

```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# Install with user flag if permission issues
pip install --user grass-rag-pipeline

# Use virtual environment (recommended)
python -m venv grass_rag_env
source grass_rag_env/bin/activate  # Linux/macOS
# or
grass_rag_env\Scripts\activate     # Windows
pip install grass-rag-pipeline
```

#### 2. Command Not Found: grass-rag

**Problem**: `grass-rag: command not found` after installation

**Solutions:**

```bash
# Check if package is installed
pip show grass-rag-pipeline

# Find Python scripts directory
python -m site --user-base
# Add Scripts/bin directory to PATH

# Windows: Add to PATH
set PATH=%PATH%;%APPDATA%\Python\Python39\Scripts

# Linux/macOS: Add to ~/.bashrc or ~/.zshrc
export PATH=$PATH:~/.local/bin

# Alternative: Use python -m
python -m grass_rag.cli.main --help
```

#### 3. Python Version Compatibility

**Problem**: Package requires Python 3.8+ but older version installed

**Solutions:**

```bash
# Check Python version
python --version

# Install Python 3.8+ from python.org
# Or use pyenv (Linux/macOS)
pyenv install 3.11.0
pyenv global 3.11.0

# Or use conda
conda create -n grass_rag python=3.11
conda activate grass_rag
pip install grass-rag-pipeline
```

---

### Runtime Issues

#### 1. Slow Response Times

**Problem**: Queries take longer than expected (>5 seconds)

**Diagnosis:**
```python
from grass_rag import GrassRAG

rag = GrassRAG()
response = rag.ask("test query")
print(f"Response time: {response.response_time_ms}ms")
print(f"Source: {response.source_type}")

# Check performance report
report = rag._pipeline.get_performance_report()
print(f"Average time: {report['performance_summary']['avg_response_time']:.3f}s")
```

**Solutions:**

1. **Increase cache size:**
```python
rag.configure(cache_size=5000)
```

2. **Lower template threshold:**
```python
rag.configure(template_threshold=0.7)
```

3. **Check system resources:**
```bash
# Monitor memory and CPU usage
top  # Linux/macOS
# or
taskmgr  # Windows
```

4. **Clear cache if corrupted:**
```python
rag._pipeline.clear_cache()
```

#### 2. Low Quality Responses

**Problem**: Responses have low confidence scores (<0.9)

**Diagnosis:**
```python
response = rag.ask("your question")
print(f"Confidence: {response.confidence}")
print(f"Source type: {response.source_type}")
print(f"Sources: {response.sources}")
```

**Solutions:**

1. **Improve query specificity:**
```python
# Instead of: "How to analyze data?"
# Use: "How to calculate slope from DEM in GRASS GIS?"
```

2. **Check template coverage:**
```python
template_stats = rag._pipeline.get_template_stats()
print(f"Total templates: {template_stats['total_templates']}")
```

3. **Adjust template threshold:**
```python
# Lower threshold for broader matches
rag.configure(template_threshold=0.6)
```

#### 3. Memory Issues

**Problem**: High memory usage or out-of-memory errors

**Diagnosis:**
```python
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f"Memory usage: {memory_mb:.1f}MB")
```

**Solutions:**

1. **Reduce cache size:**
```python
rag.configure(cache_size=500)
```

2. **Process queries individually:**
```python
# Instead of batch processing
for question in questions:
    response = rag.ask(question)
    # Process response immediately
```

3. **Clear cache periodically:**
```python
# Clear cache every N queries
query_count = 0
for question in questions:
    response = rag.ask(question)
    query_count += 1
    if query_count % 100 == 0:
        rag._pipeline.clear_cache()
```

#### 4. Model Download Issues

**Problem**: Models fail to download or are corrupted

**Diagnosis:**
```python
from grass_rag.utils.download import ModelDownloadManager

manager = ModelDownloadManager()
print("Verifying models...")
if not manager.verify_models():
    print("Models missing or corrupted")
    
status = manager.get_download_status()
print(f"Download status: {status}")
```

**Solutions:**

1. **Force redownload:**
```python
manager.download_models(force_redownload=True)
```

2. **Check disk space:**
```python
from grass_rag.utils.platform import platform_manager

cache_dir = platform_manager.get_cache_directory()
has_space = platform_manager.check_disk_space(cache_dir, 1.0)  # 1GB
print(f"Sufficient disk space: {has_space}")
```

3. **Clean up corrupted models:**
```python
manager.cleanup_old_models()
```

4. **Check network connectivity:**
```bash
# Test internet connection
ping google.com

# Check firewall/proxy settings
curl -I https://huggingface.co
```

---

### Platform-Specific Issues

#### Windows Issues

**1. Path Issues:**
```cmd
# Use forward slashes or raw strings
python -c "from grass_rag import GrassRAG; print('OK')"

# Check PATH environment variable
echo %PATH%
```

**2. Permission Issues:**
```cmd
# Run Command Prompt as Administrator
# Or use user installation
pip install --user grass-rag-pipeline
```

**3. Antivirus Interference:**
- Add Python installation directory to antivirus exclusions
- Add grass_rag cache directory to exclusions

#### macOS Issues

**1. Xcode Command Line Tools:**
```bash
# Install if missing
xcode-select --install
```

**2. Homebrew Python:**
```bash
# Use Homebrew Python
brew install python@3.11
pip3 install grass-rag-pipeline
```

**3. Permission Issues:**
```bash
# Use user installation
pip3 install --user grass-rag-pipeline

# Or fix permissions
sudo chown -R $(whoami) /usr/local/lib/python3.*/site-packages
```

#### Linux Issues

**1. Missing Dependencies:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-dev python3-pip build-essential

# CentOS/RHEL/Fedora
sudo yum install python3-devel python3-pip gcc
# or
sudo dnf install python3-devel python3-pip gcc
```

**2. Permission Issues:**
```bash
# Use user installation
pip3 install --user grass-rag-pipeline

# Add to PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

---

### Performance Optimization

#### 1. System Requirements Check

```python
from grass_rag.utils.platform import validate_system_requirements

if validate_system_requirements():
    print("✅ System meets all requirements")
else:
    print("❌ System requirements not met")
```

#### 2. Optimize Configuration

```python
# For speed-optimized setup
speed_config = {
    "cache_size": 5000,
    "template_threshold": 0.7,
    "max_response_time": 2.0
}

# For quality-optimized setup
quality_config = {
    "template_threshold": 0.9,
    "top_k_results": 5,
    "enable_metrics": True
}

# For memory-constrained setup
memory_config = {
    "cache_size": 200,
    "batch_size": 2,
    "enable_gpu": False
}
```

#### 3. Monitor Performance

```python
import time

def benchmark_queries(rag, queries, iterations=3):
    """Benchmark query performance"""
    results = []
    
    for query in queries:
        times = []
        confidences = []
        
        for _ in range(iterations):
            start = time.time()
            response = rag.ask(query)
            end = time.time()
            
            times.append(end - start)
            confidences.append(response.confidence)
        
        avg_time = sum(times) / len(times)
        avg_confidence = sum(confidences) / len(confidences)
        
        results.append({
            'query': query,
            'avg_time': avg_time,
            'avg_confidence': avg_confidence
        })
    
    return results

# Run benchmark
test_queries = [
    "calculate slope from DEM",
    "import raster data",
    "create buffer zones"
]

results = benchmark_queries(rag, test_queries)
for result in results:
    print(f"Query: {result['query']}")
    print(f"  Time: {result['avg_time']:.3f}s")
    print(f"  Quality: {result['avg_confidence']:.3f}")
```

---

### Debugging Tools

#### 1. Enable Verbose Logging

```python
import logging
from loguru import logger

# Enable debug logging
logger.remove()
logger.add(sys.stderr, level="DEBUG")

# Or use Python logging
logging.basicConfig(level=logging.DEBUG)
```

#### 2. Inspect Pipeline State

```python
# Check pipeline configuration
print(f"Config: {rag._pipeline.config.to_dict()}")

# Check cache statistics
cache_stats = rag._pipeline.get_cache_stats()
print(f"Cache stats: {cache_stats}")

# Check template statistics
template_stats = rag._pipeline.get_template_stats()
print(f"Template stats: {template_stats}")
```

#### 3. Test Individual Components

```python
# Test template matching
from grass_rag.core.templates import AdvancedQualityTemplates

templates = AdvancedQualityTemplates()
match = templates.match_template("calculate slope", threshold=0.8)
print(f"Template match: {match}")

# Test cache functionality
from grass_rag.core.cache import MultiLevelCache

cache = MultiLevelCache(max_size=100)
cache.set("test", {"answer": "test response"})
result = cache.get("test")
print(f"Cache result: {result}")
```

---

### Error Messages and Solutions

#### "InsufficientStorageError"

**Error**: Not enough disk space for models

**Solution**:
```bash
# Check disk space
df -h  # Linux/macOS
dir   # Windows

# Free up space or change cache directory
export GRASS_RAG_CACHE_DIR="/path/to/larger/disk"
```

#### "NetworkError"

**Error**: Failed to download models

**Solution**:
```bash
# Check internet connection
ping google.com

# Check proxy settings
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# Manual download if needed
wget https://huggingface.co/model-files
```

#### "ModelNotFoundError"

**Error**: Required models not available

**Solution**:
```python
from grass_rag.utils.download import ModelDownloadManager

manager = ModelDownloadManager()
manager.download_models(force_redownload=True)
```

#### "ValidationError"

**Error**: Query validation failed

**Solution**:
```python
from grass_rag.utils.validation import ResponseValidator

validator = ResponseValidator()
sanitized_query = validator.sanitize_query(your_query)
is_valid = validator.validate_query(sanitized_query)
```

---

### Getting Help

#### 1. Enable Detailed Error Reporting

```python
import traceback

try:
    response = rag.ask("your question")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
```

#### 2. Collect System Information

```python
from grass_rag.utils.platform import platform_manager

system_info = platform_manager.get_system_info()
print("System Information:")
for key, value in system_info.items():
    print(f"  {key}: {value}")

# Check environment validation
validation = platform_manager.validate_environment()
print("\nEnvironment Validation:")
for check, result in validation.items():
    status = "✅" if result else "❌"
    print(f"  {check}: {status}")
```

#### 3. Generate Diagnostic Report

```python
def generate_diagnostic_report(rag):
    """Generate comprehensive diagnostic report"""
    report = {
        "system_info": platform_manager.get_system_info(),
        "environment_validation": platform_manager.validate_environment(),
        "pipeline_config": rag._pipeline.config.to_dict(),
        "performance_report": rag._pipeline.get_performance_report(),
        "cache_stats": rag._pipeline.get_cache_stats(),
        "template_stats": rag._pipeline.get_template_stats()
    }
    
    return report

# Generate and save report
diagnostic = generate_diagnostic_report(rag)
import json
with open("diagnostic_report.json", "w") as f:
    json.dump(diagnostic, f, indent=2, default=str)

print("Diagnostic report saved to diagnostic_report.json")
```

---

### Performance Benchmarks

Expected performance on different systems:

#### Minimum System (2GB RAM, HDD)
- Response time: 1-3 seconds
- Quality: >90% for template matches
- Cache hit rate: >80%

#### Recommended System (8GB RAM, SSD)
- Response time: 0.1-1 seconds
- Quality: >92% overall
- Cache hit rate: >90%

#### High-end System (16GB+ RAM, NVMe SSD)
- Response time: 0.05-0.5 seconds
- Quality: >95% overall
- Cache hit rate: >95%

If your system doesn't meet these benchmarks, review the optimization suggestions above.