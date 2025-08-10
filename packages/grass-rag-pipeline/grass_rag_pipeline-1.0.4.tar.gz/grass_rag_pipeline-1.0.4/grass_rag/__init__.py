"""
GRASS GIS RAG Pipeline - Python Package
High-performance RAG pipeline for GRASS GIS with instant pattern matching
"""

from typing import Optional, Dict, List

__version__ = "1.0.4"

__author__ = "Sachin-NK"

class GrassRAG:
    """
    Main interface for GRASS GIS RAG Pipeline
    
    Simple, developer-friendly API for querying GRASS GIS knowledge
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize GRASS RAG pipeline
        
        Args:
            config: Optional configuration dictionary
        """
        # Import here to avoid circular imports
        from .core.pipeline import OptimizedRAGPipeline
        self._pipeline = OptimizedRAGPipeline(config)
    
    def ask(self, question: str):
        """
        Ask a question about GRASS GIS
        
        Args:
            question: Natural language question about GRASS GIS
            
        Returns:
            RAGResponse with answer, confidence, and metadata
        """
        from .core.models import RAGResponse
        
        answer, sources, metrics = self._pipeline.query(question)
        
        return RAGResponse(
            answer=answer,
            confidence=metrics.get('quality_score', 0.0),
            response_time_ms=metrics.get('total_time', 0.0) * 1000,
            source_type=metrics.get('method', 'unknown'),
            sources=sources,
            metadata=metrics
        )
    
    def ask_batch(self, questions: List[str]):
        """
        Process multiple questions in batch
        
        Args:
            questions: List of questions to process
            
        Returns:
            List of RAGResponse objects
        """
        return [self.ask(q) for q in questions]
    
    def configure(self, **kwargs) -> None:
        """
        Update pipeline configuration
        
        Args:
            **kwargs: Configuration parameters
        """
        self._pipeline.configure(**kwargs)

# Convenience imports
try:
    from .core.pipeline import OptimizedRAGPipeline as RAGPipeline  # backward friendly alias
except Exception:
    RAGPipeline = None  # type: ignore

__all__ = [
    'GrassRAG',
    'RAGPipeline'
]