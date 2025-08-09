"""
Response validation and error handling utilities
"""

import time
from typing import Any, Dict, List, Optional
from loguru import logger
from ..core.models import RAGResponse, RAGConfig, Template


class ResponseValidator:
    """Validates RAG responses and handles errors gracefully"""
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """
        Initialize response validator
        
        Args:
            config: RAG configuration for validation parameters
        """
        self.config = config or RAGConfig()
    
    def validate_response(self, response: RAGResponse) -> bool:
        """
        Validate RAG response completeness and quality
        
        Args:
            response: RAG response to validate
            
        Returns:
            True if response is valid
        """
        try:
            # Check required fields
            if not response.answer or not response.answer.strip():
                logger.warning("Response validation failed: empty answer")
                return False
            
            if not isinstance(response.confidence, (int, float)):
                logger.warning("Response validation failed: invalid confidence type")
                return False
            
            if not 0.0 <= response.confidence <= 1.0:
                logger.warning(f"Response validation failed: confidence out of range: {response.confidence}")
                return False
            
            if not isinstance(response.response_time_ms, (int, float)):
                logger.warning("Response validation failed: invalid response time type")
                return False
            
            if response.response_time_ms < 0:
                logger.warning(f"Response validation failed: negative response time: {response.response_time_ms}")
                return False
            
            if response.source_type not in ["template", "rag", "fallback", "cache", "enhanced_fallback"]:
                logger.warning(f"Response validation failed: invalid source type: {response.source_type}")
                return False
            
            # Check response time against configuration
            if response.response_time_seconds > self.config.max_response_time:
                logger.warning(f"Response time exceeded limit: {response.response_time_seconds}s > {self.config.max_response_time}s")
                # Don't fail validation, just warn
            
            return True
        
        except Exception as e:
            logger.error(f"Response validation error: {e}")
            return False
    
    def validate_query(self, query: str) -> bool:
        """
        Validate input query
        
        Args:
            query: User query to validate
            
        Returns:
            True if query is valid
        """
        try:
            if not query or not isinstance(query, str):
                return False
            
            if not query.strip():
                return False
            
            # Check query length (reasonable limits)
            if len(query) > 1000:
                logger.warning(f"Query too long: {len(query)} characters")
                return False
            
            if len(query.strip()) < 3:
                logger.warning(f"Query too short: '{query.strip()}'")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Query validation error: {e}")
            return False
    
    def sanitize_query(self, query: str) -> str:
        """
        Sanitize and normalize query input
        
        Args:
            query: Raw query input
            
        Returns:
            Sanitized query string
        """
        try:
            if not isinstance(query, str):
                query = str(query)
            
            # Basic sanitization
            query = query.strip()
            
            # Remove excessive whitespace
            import re
            query = re.sub(r'\s+', ' ', query)
            
            # Remove potentially problematic characters
            query = re.sub(r'[^\w\s\-\.\?\!,;:]', '', query)
            
            return query
        
        except Exception as e:
            logger.error(f"Query sanitization error: {e}")
            return ""
    
    def create_error_response(self, error_type: str, error_message: str, query: str = "") -> RAGResponse:
        """
        Create standardized error response
        
        Args:
            error_type: Type of error (timeout, validation, etc.)
            error_message: Human-readable error message
            query: Original query that caused the error
            
        Returns:
            RAGResponse with error information
        """
        error_responses = {
            "timeout": "The query took too long to process. Please try a simpler question or try again later.",
            "validation": "The query format is invalid. Please check your input and try again.",
            "model_error": "There was an issue with the AI models. Please try again later.",
            "network_error": "Network connectivity issues prevented processing. Please check your connection.",
            "storage_error": "Insufficient storage space for model data. Please free up disk space.",
            "unknown": "An unexpected error occurred. Please try again."
        }
        
        base_message = error_responses.get(error_type, error_responses["unknown"])
        full_message = f"{base_message}\n\nError details: {error_message}"
        
        return RAGResponse(
            answer=full_message,
            confidence=0.0,
            response_time_ms=0.0,
            source_type="error",
            sources=[{
                "type": "error",
                "error_type": error_type,
                "error_message": error_message,
                "query": query
            }],
            metadata={
                "error": True,
                "error_type": error_type,
                "error_message": error_message
            }
        )


class ErrorRecoveryManager:
    """Manages error recovery strategies and fallback mechanisms"""
    
    def __init__(self):
        """Initialize error recovery manager"""
        self.recovery_strategies = {
            "timeout": self._handle_timeout,
            "model_error": self._handle_model_error,
            "network_error": self._handle_network_error,
            "storage_error": self._handle_storage_error,
            "validation_error": self._handle_validation_error
        }
        
        self.fallback_responses = self._load_fallback_responses()
    
    def recover_from_error(self, error_type: str, context: Dict[str, Any]) -> Optional[RAGResponse]:
        """
        Attempt to recover from error using appropriate strategy
        
        Args:
            error_type: Type of error to recover from
            context: Error context information
            
        Returns:
            Recovery response or None if recovery failed
        """
        try:
            if error_type in self.recovery_strategies:
                return self.recovery_strategies[error_type](context)
            else:
                return self._handle_unknown_error(context)
        
        except Exception as e:
            logger.error(f"Error recovery failed: {e}")
            return None
    
    def _handle_timeout(self, context: Dict[str, Any]) -> Optional[RAGResponse]:
        """Handle query timeout with partial results"""
        query = context.get("query", "")
        partial_results = context.get("partial_results", [])
        
        if partial_results:
            # Return partial results with timeout notice
            answer = f"""Query timed out, but here are some partial results:

{partial_results[0].get('content', 'No content available')}

For more complete results, try simplifying your query or breaking it into smaller parts."""
            
            return RAGResponse(
                answer=answer,
                confidence=0.5,
                response_time_ms=context.get("timeout_duration", 5000),
                source_type="timeout_partial",
                sources=partial_results,
                metadata={"timeout": True, "partial_results": True}
            )
        
        # No partial results, return generic timeout response
        return self._get_fallback_response("timeout", query)
    
    def _handle_model_error(self, context: Dict[str, Any]) -> Optional[RAGResponse]:
        """Handle model loading/processing errors"""
        query = context.get("query", "")
        
        # Try to provide a template-based response if possible
        if hasattr(context.get("pipeline"), "templates"):
            templates = context["pipeline"].templates
            template_match = templates.match_template(query, threshold=0.5)
            
            if template_match and template_match["matched"]:
                return RAGResponse(
                    answer=template_match["response"],
                    confidence=template_match["quality_score"] * 0.8,  # Reduced confidence
                    response_time_ms=100,
                    source_type="template_fallback",
                    sources=[{"type": "template_fallback", "template_id": template_match["template_id"]}],
                    metadata={"model_error_recovery": True}
                )
        
        return self._get_fallback_response("model_error", query)
    
    def _handle_network_error(self, context: Dict[str, Any]) -> Optional[RAGResponse]:
        """Handle network connectivity issues"""
        query = context.get("query", "")
        
        # Network errors shouldn't affect local processing
        # Return offline mode response
        answer = """Operating in offline mode due to network issues.

All processing is done locally, so this shouldn't affect functionality.
If you're experiencing issues, please check:

1. Model files are downloaded and cached locally
2. No external API calls are being made
3. Try restarting the application

For GRASS GIS help, try using more specific keywords in your query."""
        
        return RAGResponse(
            answer=answer,
            confidence=0.7,
            response_time_ms=50,
            source_type="offline_mode",
            sources=[{"type": "offline_recovery"}],
            metadata={"network_error_recovery": True, "offline_mode": True}
        )
    
    def _handle_storage_error(self, context: Dict[str, Any]) -> Optional[RAGResponse]:
        """Handle insufficient storage errors"""
        query = context.get("query", "")
        
        answer = """Insufficient storage space detected.

To resolve this issue:

1. **Free up disk space** (need ~1GB for models)
2. **Clear cache**: Use `rag.clear_cache()` 
3. **Check model directory**: ~/.grass_rag/models
4. **Restart application** after freeing space

**Temporary workaround:**
You can still get basic GRASS GIS help using template responses,
but full AI functionality requires model downloads."""
        
        return RAGResponse(
            answer=answer,
            confidence=0.6,
            response_time_ms=50,
            source_type="storage_error",
            sources=[{"type": "storage_recovery"}],
            metadata={"storage_error_recovery": True}
        )
    
    def _handle_validation_error(self, context: Dict[str, Any]) -> Optional[RAGResponse]:
        """Handle query validation errors"""
        query = context.get("query", "")
        error_details = context.get("error_details", "")
        
        answer = f"""Query validation failed: {error_details}

**Please check:**
1. Query is not empty
2. Query length is reasonable (< 1000 characters)
3. Query contains valid characters
4. Query is a proper question about GRASS GIS

**Example valid queries:**
- "How do I calculate slope from a DEM?"
- "Import raster data into GRASS GIS"
- "Create buffer zones around points"

Please rephrase your question and try again."""
        
        return RAGResponse(
            answer=answer,
            confidence=0.3,
            response_time_ms=10,
            source_type="validation_error",
            sources=[{"type": "validation_recovery"}],
            metadata={"validation_error_recovery": True}
        )
    
    def _handle_unknown_error(self, context: Dict[str, Any]) -> Optional[RAGResponse]:
        """Handle unknown errors with generic recovery"""
        query = context.get("query", "")
        
        return self._get_fallback_response("unknown", query)
    
    def _get_fallback_response(self, error_type: str, query: str) -> RAGResponse:
        """Get generic fallback response for error type"""
        fallback = self.fallback_responses.get(error_type, self.fallback_responses["default"])
        
        return RAGResponse(
            answer=fallback["answer"],
            confidence=fallback["confidence"],
            response_time_ms=fallback["response_time_ms"],
            source_type="error_fallback",
            sources=[{"type": "error_fallback", "error_type": error_type}],
            metadata={"error_fallback": True, "error_type": error_type}
        )
    
    def _load_fallback_responses(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined fallback responses for different error types"""
        return {
            "timeout": {
                "answer": """Query processing timed out. Here are some general GRASS GIS tips:

**Common commands:**
- `r.import` - Import raster data
- `v.import` - Import vector data  
- `r.info` - Get raster information
- `v.info` - Get vector information
- `g.region` - Set computational region

**For specific help:**
- Use `g.manual -k keyword` to search commands
- Visit: https://grass.osgeo.org/grass-stable/manuals/

Try rephrasing your question or breaking it into smaller parts.""",
                "confidence": 0.4,
                "response_time_ms": 5000
            },
            
            "model_error": {
                "answer": """AI models are temporarily unavailable. Here's basic GRASS GIS guidance:

**Getting Started:**
1. Set computational region: `g.region`
2. Import data: `r.import` (raster) or `v.import` (vector)
3. Analyze data using appropriate commands
4. Export results: `r.out.gdal` or `v.out.ogr`

**Command Structure:**
- Raster commands start with `r.`
- Vector commands start with `v.`
- General commands start with `g.`

**Documentation:** https://grass.osgeo.org/grass-stable/manuals/""",
                "confidence": 0.5,
                "response_time_ms": 100
            },
            
            "default": {
                "answer": """An error occurred while processing your query.

**Troubleshooting steps:**
1. Check your query format
2. Try a simpler question
3. Restart the application
4. Check system resources

**GRASS GIS Resources:**
- Official documentation: https://grass.osgeo.org/
- Command reference: https://grass.osgeo.org/grass-stable/manuals/
- Community support: https://grass.osgeo.org/support/

Please try again with a different question.""",
                "confidence": 0.3,
                "response_time_ms": 50
            }
        }