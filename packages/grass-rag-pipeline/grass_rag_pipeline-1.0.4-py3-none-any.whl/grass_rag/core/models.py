"""
Data models and structures for GRASS RAG pipeline
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import time
import os


@dataclass
class RAGResponse:
    """Response from RAG pipeline query"""
    
    answer: str
    confidence: float
    response_time_ms: float
    source_type: str  # "template", "rag", "fallback"
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate response data after initialization"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        if self.response_time_ms < 0:
            raise ValueError(f"Response time cannot be negative, got {self.response_time_ms}")
        
        if self.source_type not in ["template", "rag", "fallback", "cache", "enhanced_fallback"]:
            raise ValueError(f"Invalid source_type: {self.source_type}")
    
    @property
    def response_time_seconds(self) -> float:
        """Get response time in seconds"""
        return self.response_time_ms / 1000.0
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if response has high confidence (>= 0.9)"""
        return self.confidence >= 0.9
    
    @property
    def is_fast_response(self) -> bool:
        """Check if response was fast (< 1 second)"""
        return self.response_time_seconds < 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "answer": self.answer,
            "confidence": self.confidence,
            "response_time_ms": self.response_time_ms,
            "source_type": self.source_type,
            "sources": self.sources,
            "metadata": self.metadata
        }


@dataclass
class RAGConfig:
    """Configuration for RAG pipeline"""
    
    # Storage paths
    model_cache_dir: str = field(default_factory=lambda: os.path.expanduser("~/.grass_rag/models"))
    data_cache_dir: str = field(default_factory=lambda: os.path.expanduser("~/.grass_rag/data"))
    
    # Performance settings
    max_response_time: float = 5.0
    template_threshold: float = 0.8
    cache_size: int = 1000
    
    # Model settings
    enable_gpu: bool = False
    batch_size: int = 8
    top_k_results: int = 3
    
    # Logging and monitoring
    log_level: str = "INFO"
    enable_metrics: bool = True
    
    # Template system
    enable_templates: bool = True
    template_quality_threshold: float = 0.9

    # Cost / footprint optimization settings
    minimal_mode: bool = False              # If True, never load or download heavy models
    allow_download: bool = True             # If False, skip any network/model download attempts
    defer_model_loading: bool = True        # If True, load models lazily on first real need
    templates_only_fallback: bool = True    # If True and models unavailable, rely on templates + enhanced fallback
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.max_response_time <= 0:
            raise ValueError("max_response_time must be positive")
        
        if not 0.0 <= self.template_threshold <= 1.0:
            raise ValueError("template_threshold must be between 0.0 and 1.0")
        
        if self.cache_size < 0:
            raise ValueError("cache_size cannot be negative")
        
        if self.top_k_results <= 0:
            raise ValueError("top_k_results must be positive")
        
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            raise ValueError(f"Invalid log_level: {self.log_level}")

        # Enforce relationships
        if self.minimal_mode:
            # Override related flags for safety
            self.allow_download = False
            self.defer_model_loading = True
        if not self.allow_download:
            self.defer_model_loading = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "model_cache_dir": self.model_cache_dir,
            "data_cache_dir": self.data_cache_dir,
            "max_response_time": self.max_response_time,
            "template_threshold": self.template_threshold,
            "cache_size": self.cache_size,
            "enable_gpu": self.enable_gpu,
            "batch_size": self.batch_size,
            "top_k_results": self.top_k_results,
            "log_level": self.log_level,
            "enable_metrics": self.enable_metrics,
            "enable_templates": self.enable_templates,
            "template_quality_threshold": self.template_quality_threshold,
            "minimal_mode": self.minimal_mode,
            "allow_download": self.allow_download,
            "defer_model_loading": self.defer_model_loading,
            "templates_only_fallback": self.templates_only_fallback
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'RAGConfig':
        """Create config from dictionary"""
        return cls(**config_dict)


@dataclass
class Template:
    """Template for instant GRASS GIS responses"""
    
    id: str
    keywords: List[str]
    response: str
    quality_score: float
    category: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Structured fields for richer answers
    prerequisites: List[str] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    command: str = ""
    notes: str = ""
    pitfalls: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate template data after initialization"""
        if not self.id:
            raise ValueError("Template ID cannot be empty")
        
        if not self.keywords:
            raise ValueError("Template must have at least one keyword")
        
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError(f"Quality score must be between 0.0 and 1.0, got {self.quality_score}")
        
        if not self.response.strip():
            raise ValueError("Template response cannot be empty")
    
    def matches_query(self, query: str, threshold: float = 0.8) -> bool:
        """Check if template matches query based on keywords"""
        query_lower = query.lower()
        
        # Calculate match score
        total_score = 0
        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                total_score += len(keyword)
        
        # Normalize by query length
        if len(query_lower) > 0:
            match_score = total_score / len(query_lower)
            return match_score >= threshold
        
        return False
    
    def get_match_score(self, query: str) -> float:
        """Get numerical match score for query"""
        query_lower = query.lower()
        
        total_score = 0
        matched_keywords = 0
        
        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                total_score += len(keyword)
                matched_keywords += 1
        
        if matched_keywords == 0:
            return 0.0
        
        # Combine keyword coverage and match strength
        keyword_coverage = matched_keywords / len(self.keywords)
        match_strength = total_score / len(query_lower) if len(query_lower) > 0 else 0
        
        return (keyword_coverage + match_strength) / 2
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary"""
        return {
            "id": self.id,
            "keywords": self.keywords,
            "response": self.response,
            "quality_score": self.quality_score,
            "category": self.category,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, template_dict: Dict[str, Any]) -> 'Template':
        """Create template from dictionary"""
        return cls(**template_dict)


@dataclass
class QueryMetrics:
    """Metrics for query processing"""
    
    query: str
    total_time: float
    template_time: float = 0.0
    embedding_time: float = 0.0
    search_time: float = 0.0
    generation_time: float = 0.0
    
    template_matched: bool = False
    cache_hit: bool = False
    
    quality_score: float = 0.0
    source_count: int = 0
    
    timestamp: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Validate metrics after initialization"""
        if self.total_time < 0:
            raise ValueError("total_time cannot be negative")
        
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError("quality_score must be between 0.0 and 1.0")
    
    @property
    def is_fast(self) -> bool:
        """Check if query was processed quickly (< 1s)"""
        return self.total_time < 1.0
    
    @property
    def is_high_quality(self) -> bool:
        """Check if query result has high quality (>= 0.9)"""
        return self.quality_score >= 0.9
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "query": self.query,
            "total_time": self.total_time,
            "template_time": self.template_time,
            "embedding_time": self.embedding_time,
            "search_time": self.search_time,
            "generation_time": self.generation_time,
            "template_matched": self.template_matched,
            "cache_hit": self.cache_hit,
            "quality_score": self.quality_score,
            "source_count": self.source_count,
            "timestamp": self.timestamp
        }


# Validation functions
def validate_response(response: RAGResponse) -> bool:
    """Validate RAG response"""
    try:
        # Check required fields
        if not response.answer or not response.answer.strip():
            return False
        
        if not isinstance(response.confidence, (int, float)):
            return False
        
        if not isinstance(response.response_time_ms, (int, float)):
            return False
        
        if response.source_type not in ["template", "rag", "fallback", "cache", "enhanced_fallback"]:
            return False
        
        return True
    
    except Exception:
        return False


def validate_config(config: RAGConfig) -> bool:
    """Validate RAG configuration"""
    try:
        # Check paths exist or can be created
        import os
        from pathlib import Path
        
        for path_attr in ["model_cache_dir", "data_cache_dir"]:
            path = getattr(config, path_attr)
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
            except Exception:
                return False
        
        # Check numeric ranges
        if config.max_response_time <= 0:
            return False
        
        if not 0.0 <= config.template_threshold <= 1.0:
            return False
        
        return True
    
    except Exception:
        return False


def validate_template(template: Template) -> bool:
    """Validate template"""
    try:
        if not template.id or not template.id.strip():
            return False
        
        if not template.keywords or len(template.keywords) == 0:
            return False
        
        if not template.response or not template.response.strip():
            return False
        
        if not 0.0 <= template.quality_score <= 1.0:
            return False
        
        return True
    
    except Exception:
        return False