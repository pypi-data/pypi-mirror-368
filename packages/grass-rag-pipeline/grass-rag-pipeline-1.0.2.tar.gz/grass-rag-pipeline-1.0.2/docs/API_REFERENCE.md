# GRASS GIS RAG Pipeline - API Reference

## Overview

The GRASS GIS RAG Pipeline provides a high-performance, template-optimized system for answering GRASS GIS questions with >90% accuracy and <5 second response times.

## Core Classes

### GrassRAG

Main interface for the GRASS GIS RAG Pipeline.

```python
from grass_rag import GrassRAG

# Initialize with default configuration
rag = GrassRAG()

# Initialize with custom configuration
config = {"cache_size": 2000, "max_response_time": 3.0}
rag = GrassRAG(config)
```

#### Methods

##### `ask(question: str) -> RAGResponse`

Ask a question about GRASS GIS.

**Parameters:**
- `question` (str): Natural language question about GRASS GIS

**Returns:**
- `RAGResponse`: Response object with answer, confidence, and metadata

**Example:**
```python
response = rag.ask("How do I calculate slope from a DEM?")
print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence}")
print(f"Response Time: {response.response_time_ms}ms")
```

##### `ask_batch(questions: List[str]) -> List[RAGResponse]`

Process multiple questions in batch.

**Parameters:**
- `questions` (List[str]): List of questions to process

**Returns:**
- `List[RAGResponse]`: List of response objects

**Example:**
```python
questions = [
    "Calculate slope from DEM",
    "Import raster data",
    "Create buffer zones"
]
responses = rag.ask_batch(questions)
for response in responses:
    print(f"Answer: {response.answer}")
```

##### `configure(**kwargs) -> None`

Update pipeline configuration at runtime.

**Parameters:**
- `**kwargs`: Configuration parameters to update

**Example:**
```python
rag.configure(cache_size=5000, template_threshold=0.9)
```

---

### RAGResponse

Response object containing answer and metadata.

#### Attributes

- `answer` (str): The generated answer
- `confidence` (float): Confidence score (0.0-1.0)
- `response_time_ms` (float): Response time in milliseconds
- `source_type` (str): Source of response ("template", "rag", "fallback", "cache")
- `sources` (List[Dict]): Source information and metadata
- `metadata` (Dict): Additional response metadata

#### Properties

##### `response_time_seconds -> float`

Get response time in seconds.

```python
response = rag.ask("test question")
print(f"Response time: {response.response_time_seconds:.3f}s")
```

##### `is_high_confidence -> bool`

Check if response has high confidence (≥0.9).

```python
if response.is_high_confidence:
    print("High quality response!")
```

##### `is_fast_response -> bool`

Check if response was fast (<1 second).

```python
if response.is_fast_response:
    print("Fast response!")
```

#### Methods

##### `to_dict() -> Dict[str, Any]`

Convert response to dictionary format.

```python
response_dict = response.to_dict()
import json
print(json.dumps(response_dict, indent=2))
```

---

### RAGConfig

Configuration object for the RAG pipeline.

#### Parameters

- `model_cache_dir` (str): Directory for model cache (default: ~/.grass_rag/models)
- `data_cache_dir` (str): Directory for data cache (default: ~/.grass_rag/data)
- `cache_size` (int): Maximum cache size (default: 1000)
- `max_response_time` (float): Maximum response time in seconds (default: 5.0)
- `template_threshold` (float): Template matching threshold (default: 0.8)
- `enable_gpu` (bool): Enable GPU acceleration (default: False)
- `batch_size` (int): Batch processing size (default: 8)
- `top_k_results` (int): Number of top results to consider (default: 3)
- `log_level` (str): Logging level (default: "INFO")
- `enable_metrics` (bool): Enable metrics collection (default: True)

**Example:**
```python
from grass_rag.core.models import RAGConfig

config = RAGConfig(
    cache_size=2000,
    max_response_time=3.0,
    template_threshold=0.9,
    enable_metrics=True
)

rag = GrassRAG(config.to_dict())
```

---

## Utility Classes

### ModelDownloadManager

Manages downloading and caching of AI models.

```python
from grass_rag.utils.download import ModelDownloadManager

manager = ModelDownloadManager(cache_dir="./models")
success = manager.download_models()
paths = manager.get_model_paths()
```

#### Methods

##### `download_models(force_redownload: bool = False) -> bool`

Download all required models.

##### `verify_models() -> bool`

Verify all models are present and valid.

##### `get_model_paths() -> Dict[str, str]`

Get paths to all cached models.

##### `cleanup_old_models() -> None`

Remove old or corrupted model files.

---

### PlatformManager

Handles cross-platform compatibility.

```python
from grass_rag.utils.platform import platform_manager

cache_dir = platform_manager.get_cache_directory()
system_info = platform_manager.get_system_info()
```

#### Methods

##### `get_cache_directory(app_name: str = "grass_rag") -> Path`

Get platform-appropriate cache directory.

##### `get_data_directory(app_name: str = "grass_rag") -> Path`

Get platform-appropriate data directory.

##### `check_python_compatibility(min_version: Tuple[int, int] = (3, 8)) -> bool`

Check Python version compatibility.

##### `validate_environment() -> Dict[str, bool]`

Validate system environment for the pipeline.

---

### ResponseValidator

Validates responses and handles errors.

```python
from grass_rag.utils.validation import ResponseValidator

validator = ResponseValidator()
is_valid = validator.validate_response(response)
sanitized = validator.sanitize_query(query)
```

#### Methods

##### `validate_response(response: RAGResponse) -> bool`

Validate response completeness and quality.

##### `validate_query(query: str) -> bool`

Validate input query format.

##### `sanitize_query(query: str) -> str`

Sanitize and normalize query input.

##### `create_error_response(error_type: str, error_message: str, query: str = "") -> RAGResponse`

Create standardized error response.

---

## Performance Monitoring

### Getting Performance Reports

```python
# Get comprehensive performance report
report = rag._pipeline.get_performance_report()

print(f"Total queries: {report['performance_summary']['total_queries']}")
print(f"Average quality: {report['performance_summary']['avg_quality_score']:.3f}")
print(f"Average response time: {report['performance_summary']['avg_response_time']:.3f}s")
```

### Cache Statistics

```python
# Get cache performance statistics
cache_stats = rag._pipeline.get_cache_stats()

print(f"Cache hit rate: {cache_stats['hit_rate']:.1f}%")
print(f"L1 cache size: {cache_stats['l1_size']}")
print(f"L2 cache size: {cache_stats['l2_size']}")
```

### Template Statistics

```python
# Get template system statistics
template_stats = rag._pipeline.get_template_stats()

print(f"Total templates: {template_stats['total_templates']}")
print(f"Average quality: {template_stats['avg_quality_score']:.3f}")
```

---

## Error Handling

### Exception Types

The pipeline defines several custom exceptions:

- `InsufficientStorageError`: Raised when insufficient disk space
- `NetworkError`: Raised for network connectivity issues
- `ModelNotFoundError`: Raised when required models are missing

### Error Recovery

```python
try:
    response = rag.ask("your question")
except Exception as e:
    print(f"Error: {e}")
    # Pipeline includes automatic error recovery
    # Most errors result in fallback responses rather than exceptions
```

### Graceful Degradation

The pipeline is designed for graceful degradation:

1. **Template Fallback**: If AI models fail, uses template responses
2. **Enhanced Fallback**: If templates don't match, provides structured guidance
3. **Offline Mode**: Works without network connectivity
4. **Error Responses**: Converts errors to helpful response objects

---

## Configuration Examples

### Basic Configuration

```python
# Minimal configuration
rag = GrassRAG({
    "cache_size": 1000,
    "max_response_time": 5.0
})
```

### Performance Optimization

```python
# Optimized for speed
rag = GrassRAG({
    "cache_size": 5000,
    "template_threshold": 0.7,
    "max_response_time": 2.0
})
```

### Quality Optimization

```python
# Optimized for quality
rag = GrassRAG({
    "template_threshold": 0.9,
    "top_k_results": 5,
    "enable_metrics": True
})
```

### Memory Constrained

```python
# For limited memory environments
rag = GrassRAG({
    "cache_size": 100,
    "batch_size": 4,
    "enable_gpu": False
})
```

---

## Best Practices

### Query Optimization

1. **Use specific keywords**: "slope calculation" vs "terrain analysis"
2. **Include context**: "GRASS GIS slope from DEM" vs "slope"
3. **Be concise**: Avoid overly long questions
4. **Use standard terminology**: GRASS GIS command names and concepts

### Performance Tips

1. **Warm up cache**: Run common queries first
2. **Batch processing**: Use `ask_batch()` for multiple queries
3. **Monitor metrics**: Check response times and quality scores
4. **Adjust thresholds**: Lower template_threshold for broader matches

### Error Handling

1. **Validate inputs**: Check query format before processing
2. **Handle timeouts**: Set appropriate max_response_time
3. **Monitor quality**: Check confidence scores
4. **Use fallbacks**: Implement backup strategies for critical applications

---

## Integration Examples

### Web Application Integration

```python
from flask import Flask, request, jsonify
from grass_rag import GrassRAG

app = Flask(__name__)
rag = GrassRAG()

@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json.get('question')
    response = rag.ask(question)
    return jsonify(response.to_dict())
```

### Batch Processing Script

```python
import csv
from grass_rag import GrassRAG

rag = GrassRAG()

# Process questions from CSV
with open('questions.csv', 'r') as f:
    reader = csv.reader(f)
    questions = [row[0] for row in reader]

responses = rag.ask_batch(questions)

# Save results
with open('results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Question', 'Answer', 'Confidence', 'Response_Time'])
    
    for question, response in zip(questions, responses):
        writer.writerow([
            question,
            response.answer,
            response.confidence,
            response.response_time_ms
        ])
```

### Monitoring Integration

```python
import time
import logging
from grass_rag import GrassRAG

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rag = GrassRAG()

def monitored_query(question):
    start_time = time.time()
    response = rag.ask(question)
    end_time = time.time()
    
    # Log metrics
    logger.info(f"Query: {question[:50]}...")
    logger.info(f"Confidence: {response.confidence:.3f}")
    logger.info(f"Response time: {end_time - start_time:.3f}s")
    logger.info(f"Source: {response.source_type}")
    
    return response
```

---

## Version Compatibility

- **Python**: 3.8+
- **Operating Systems**: Windows, macOS, Linux
- **Memory**: Minimum 2GB RAM recommended
- **Storage**: ~1GB for models and cache
- **Network**: Optional (for model downloads only)

---

## Support and Troubleshooting

For issues and questions:

1. Check the troubleshooting guide in the documentation
2. Review the examples in the `examples/` directory
3. Enable verbose logging for debugging
4. Check system requirements and compatibility

Common solutions:
- Clear cache: `rag._pipeline.clear_cache()`
- Reset statistics: `rag._pipeline.reset_stats()`
- Validate environment: Use platform utilities
- Update configuration: Adjust thresholds and limits