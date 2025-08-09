#!/usr/bin/env python3
"""
Basic usage examples for GRASS GIS RAG Pipeline
Demonstrates core functionality and common use cases
"""

from grass_rag import GrassRAG
from grass_rag.core.models import RAGConfig


def basic_query_example():
    """Example of basic query functionality"""
    print("🌱 Basic Query Example")
    print("=" * 50)
    
    # Initialize with default configuration
    rag = GrassRAG()
    
    # Ask a simple question
    response = rag.ask("How do I calculate slope from a DEM?")
    
    print(f"Question: How do I calculate slope from a DEM?")
    print(f"Answer: {response.answer}")
    print(f"Confidence: {response.confidence:.3f}")
    print(f"Response Time: {response.response_time_ms:.1f}ms")
    print(f"Source: {response.source_type}")
    print()


def custom_configuration_example():
    """Example of custom configuration"""
    print("🌱 Custom Configuration Example")
    print("=" * 50)
    
    # Create custom configuration
    config = {
        "cache_size": 500,
        "max_response_time": 3.0,
        "template_threshold": 0.9
    }
    
    # Initialize with custom config
    rag = GrassRAG(config)
    
    # Test the configuration
    response = rag.ask("Import raster data into GRASS GIS")
    
    print(f"Custom config: cache_size=500, max_response_time=3.0s")
    print(f"Question: Import raster data into GRASS GIS")
    print(f"Answer: {response.answer}")
    print(f"Response Time: {response.response_time_ms:.1f}ms")
    print()


def batch_processing_example():
    """Example of batch query processing"""
    print("🌱 Batch Processing Example")
    print("=" * 50)
    
    rag = GrassRAG()
    
    # Multiple questions to process
    questions = [
        "Calculate slope from elevation data",
        "Create buffer zones around points",
        "Export vector data to shapefile",
        "Perform watershed analysis",
        "Generate contour lines"
    ]
    
    # Process all questions
    responses = rag.ask_batch(questions)
    
    print(f"Processed {len(questions)} questions:")
    for i, (question, response) in enumerate(zip(questions, responses), 1):
        print(f"\n{i}. {question}")
        print(f"   Answer: {response.answer[:100]}...")
        print(f"   Confidence: {response.confidence:.3f}")
        print(f"   Time: {response.response_time_ms:.1f}ms")


def configuration_management_example():
    """Example of runtime configuration management"""
    print("🌱 Configuration Management Example")
    print("=" * 50)
    
    rag = GrassRAG()
    
    # Test with default settings
    response1 = rag.ask("vector overlay analysis")
    print(f"Default config - Response time: {response1.response_time_ms:.1f}ms")
    
    # Update configuration at runtime
    rag.configure(cache_size=2000, template_threshold=0.7)
    
    # Test with updated settings
    response2 = rag.ask("vector overlay analysis")
    print(f"Updated config - Response time: {response2.response_time_ms:.1f}ms")
    print()


def error_handling_example():
    """Example of error handling"""
    print("🌱 Error Handling Example")
    print("=" * 50)
    
    rag = GrassRAG()
    
    # Test various edge cases
    test_cases = [
        "",  # Empty query
        "   ",  # Whitespace only
        "a" * 500,  # Very long query
        "!@#$%^&*()",  # Special characters
        "How do I perform advanced quantum GIS analysis?"  # Out of domain
    ]
    
    for i, query in enumerate(test_cases, 1):
        try:
            if not query.strip():
                print(f"{i}. Empty/whitespace query: Skipped")
                continue
                
            response = rag.ask(query)
            print(f"{i}. Query: {query[:50]}...")
            print(f"   Handled gracefully: {response.confidence:.3f} confidence")
            
        except Exception as e:
            print(f"{i}. Query failed: {e}")
    
    print()


def performance_monitoring_example():
    """Example of performance monitoring"""
    print("🌱 Performance Monitoring Example")
    print("=" * 50)
    
    rag = GrassRAG()
    
    # Generate some queries for statistics
    test_queries = [
        "calculate slope",
        "import raster",
        "export data",
        "create buffer",
        "vector overlay"
    ]
    
    for query in test_queries:
        rag.ask(query)
    
    # Get performance report
    report = rag._pipeline.get_performance_report()
    
    if "performance_summary" in report:
        summary = report["performance_summary"]
        print(f"Total queries: {summary['total_queries']}")
        print(f"Average quality: {summary['avg_quality_score']:.3f}")
        print(f"Average response time: {summary['avg_response_time']:.3f}s")
        print(f"Template hit rate: {summary['template_hit_rate']:.1f}%")
        print(f"Cache hit rate: {summary['cache_hit_rate']:.1f}%")
    
    # Get cache statistics
    cache_stats = rag._pipeline.get_cache_stats()
    print(f"\nCache statistics:")
    print(f"L1 cache size: {cache_stats['l1_size']}")
    print(f"L2 cache size: {cache_stats['l2_size']}")
    print(f"Hit rate: {cache_stats['hit_rate']:.1f}%")
    print()


def advanced_features_example():
    """Example of advanced features"""
    print("🌱 Advanced Features Example")
    print("=" * 50)
    
    rag = GrassRAG()
    
    # Test different types of GRASS GIS operations
    operations = {
        "Terrain Analysis": "Calculate slope and aspect from DEM",
        "Data Management": "Import and export raster data",
        "Vector Operations": "Create buffer zones and overlay analysis",
        "Hydrological Analysis": "Perform watershed delineation",
        "Interpolation": "Interpolate surface from point data"
    }
    
    for category, query in operations.items():
        response = rag.ask(query)
        print(f"{category}:")
        print(f"  Query: {query}")
        print(f"  Source: {response.source_type}")
        print(f"  Quality: {response.confidence:.3f}")
        print(f"  Speed: {response.response_time_ms:.1f}ms")
        print()


def main():
    """Run all examples"""
    print("🌱 GRASS GIS RAG Pipeline - Usage Examples")
    print("=" * 60)
    print()
    
    try:
        basic_query_example()
        custom_configuration_example()
        batch_processing_example()
        configuration_management_example()
        error_handling_example()
        performance_monitoring_example()
        advanced_features_example()
        
        print("✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()