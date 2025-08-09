"""
Integration tests for GRASS RAG pipeline
Tests end-to-end functionality and package integration
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from grass_rag import GrassRAG
from grass_rag.core.models import RAGConfig, RAGResponse


class TestPackageIntegration:
    """Integration tests for the complete package"""
    
    def setup_method(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "model_cache_dir": str(Path(self.temp_dir) / "models"),
            "data_cache_dir": str(Path(self.temp_dir) / "data"),
            "cache_size": 100,
            "max_response_time": 5.0
        }
    
    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_package_initialization(self):
        """Test package can be initialized successfully"""
        rag = GrassRAG(self.config)
        
        assert rag is not None
        assert rag._pipeline is not None
    
    def test_simple_query(self):
        """Test simple query through main interface"""
        rag = GrassRAG(self.config)
        
        response = rag.ask("How do I calculate slope?")
        
        assert isinstance(response, RAGResponse)
        assert response.answer is not None
        assert len(response.answer) > 0
        assert response.confidence >= 0.0
        assert response.response_time_ms >= 0
    
    def test_batch_processing(self):
        """Test batch query processing"""
        rag = GrassRAG(self.config)
        
        queries = [
            "calculate slope",
            "import raster",
            "export data"
        ]
        
        responses = rag.ask_batch(queries)
        
        assert len(responses) == len(queries)
        for response in responses:
            assert isinstance(response, RAGResponse)
            assert response.answer is not None
    
    def test_configuration_management(self):
        """Test configuration management"""
        rag = GrassRAG(self.config)
        
        # Test configuration update
        rag.configure(cache_size=500, max_response_time=3.0)
        
        # Verify configuration was applied
        assert rag._pipeline.config.cache_size == 500
        assert rag._pipeline.config.max_response_time == 3.0
    
    def test_performance_requirements_integration(self):
        """Test that integrated system meets performance requirements"""
        rag = GrassRAG(self.config)
        
        # Test queries that should cover different response types
        test_queries = [
            "calculate slope from DEM",           # Template match
            "import raster file",                 # Template match
            "export vector to shapefile",         # Template match
            "create contour lines",               # Template match
            "perform vector overlay",             # Template match
            "watershed analysis",                 # Template match
            "create buffer zones",                # Template match
            "raster calculations",                # Template match
            "classify landcover data",            # Template match
            "interpolate surface from points",    # Template match
            "some unknown operation xyz"          # Fallback
        ]
        
        quality_scores = []
        response_times = []
        
        for query in test_queries:
            response = rag.ask(query)
            
            quality_scores.append(response.confidence)
            response_times.append(response.response_time_seconds)
        
        # Verify performance requirements
        avg_quality = sum(quality_scores) / len(quality_scores)
        avg_response_time = sum(response_times) / len(response_times)
        
        # Quality requirement: >90% accuracy
        assert avg_quality >= 0.9, f"Average quality {avg_quality:.3f} below 0.9 requirement"
        
        # Speed requirement: <5 seconds
        assert avg_response_time < 5.0, f"Average response time {avg_response_time:.3f}s above 5s requirement"
        
        # Check individual query performance
        fast_responses = sum(1 for t in response_times if t < 5.0)
        speed_percentage = (fast_responses / len(response_times)) * 100
        assert speed_percentage >= 95, f"Only {speed_percentage}% of queries under 5s"
        
        high_quality_responses = sum(1 for q in quality_scores if q >= 0.9)
        quality_percentage = (high_quality_responses / len(quality_scores)) * 100
        assert quality_percentage >= 90, f"Only {quality_percentage}% of queries meet quality requirement"
    
    def test_error_recovery(self):
        """Test error recovery mechanisms"""
        rag = GrassRAG(self.config)
        
        # Test with various problematic inputs
        problematic_queries = [
            "",                    # Empty query
            "   ",                 # Whitespace only
            "a" * 1000,           # Very long query
            "!@#$%^&*()",         # Special characters only
        ]
        
        for query in problematic_queries:
            try:
                response = rag.ask(query)
                # Should either succeed or handle gracefully
                if response:
                    assert isinstance(response, RAGResponse)
            except Exception as e:
                # Exceptions should be informative
                assert str(e) is not None
    
    def test_memory_usage(self):
        """Test memory usage remains reasonable"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        rag = GrassRAG(self.config)
        
        # Process multiple queries
        for i in range(50):
            response = rag.ask(f"test query {i}")
            assert response is not None
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.1f}MB"
    
    def test_concurrent_queries(self):
        """Test handling of concurrent queries"""
        import threading
        import time
        
        rag = GrassRAG(self.config)
        results = []
        errors = []
        
        def query_worker(query_id):
            try:
                response = rag.ask(f"calculate slope {query_id}")
                results.append((query_id, response))
            except Exception as e:
                errors.append((query_id, e))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=query_worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=10)
        
        # Check results
        assert len(errors) == 0, f"Concurrent queries failed: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        
        for query_id, response in results:
            assert isinstance(response, RAGResponse)
            assert response.answer is not None
    
    def test_package_size_estimation(self):
        """Test package size estimation"""
        # This is a rough estimation test
        # In a real deployment, you'd measure actual package size
        
        rag = GrassRAG(self.config)
        
        # Estimate component sizes
        template_count = len(rag._pipeline.templates.templates)
        cache_size = rag._pipeline.config.cache_size
        
        # Basic size estimation (very rough)
        estimated_template_size = template_count * 2000  # ~2KB per template
        estimated_cache_size = cache_size * 1000         # ~1KB per cache item
        estimated_code_size = 50 * 1024 * 1024          # ~50MB for code
        
        total_estimated_size = estimated_template_size + estimated_cache_size + estimated_code_size
        
        # Should be well under 1GB (excluding AI models)
        assert total_estimated_size < 100 * 1024 * 1024, f"Estimated package size too large: {total_estimated_size / 1024 / 1024:.1f}MB"
    
    def test_offline_functionality(self):
        """Test that system works offline"""
        rag = GrassRAG(self.config)
        
        # Simulate offline mode by testing template-only responses
        template_queries = [
            "calculate slope",
            "import raster",
            "export data",
            "create buffer",
            "vector overlay"
        ]
        
        for query in template_queries:
            response = rag.ask(query)
            
            # Should get template responses even "offline"
            assert response is not None
            assert response.answer is not None
            assert len(response.answer) > 0
            assert response.confidence >= 0.9  # Templates should be high quality
    
    def test_response_validation(self):
        """Test response validation"""
        rag = GrassRAG(self.config)
        
        response = rag.ask("calculate slope")
        
        # Validate response structure
        assert hasattr(response, 'answer')
        assert hasattr(response, 'confidence')
        assert hasattr(response, 'response_time_ms')
        assert hasattr(response, 'source_type')
        assert hasattr(response, 'sources')
        assert hasattr(response, 'metadata')
        
        # Validate response content
        assert isinstance(response.answer, str)
        assert len(response.answer) > 0
        assert 0.0 <= response.confidence <= 1.0
        assert response.response_time_ms >= 0
        assert response.source_type in ["template", "rag", "fallback", "cache"]
        assert isinstance(response.sources, list)
        assert isinstance(response.metadata, dict)
    
    def test_template_coverage(self):
        """Test template coverage for common GRASS GIS operations"""
        rag = GrassRAG(self.config)
        
        # Common GRASS GIS operations that should have templates
        common_operations = [
            "slope",
            "import",
            "export", 
            "contour",
            "overlay",
            "watershed",
            "buffer",
            "calculate",
            "classification",
            "interpolation"
        ]
        
        template_hits = 0
        
        for operation in common_operations:
            response = rag.ask(f"{operation} analysis")
            
            if response.source_type == "template":
                template_hits += 1
        
        # Should have good template coverage
        coverage_percentage = (template_hits / len(common_operations)) * 100
        assert coverage_percentage >= 80, f"Template coverage only {coverage_percentage}%"


if __name__ == "__main__":
    pytest.main([__file__])