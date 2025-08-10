"""
Command-line interface for GRASS RAG pipeline
Provides both single query and interactive shell modes
"""

import sys
import time
import argparse
from typing import Optional
from loguru import logger

from .. import GrassRAG
from ..core.models import RAGConfig
from ..utils.validation import ResponseValidator


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GRASS GIS RAG Chatbot - AI-powered GRASS GIS assistance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  grass-rag --question "How do I calculate slope from DEM?"
  grass-rag --interactive
  grass-rag --question "Import raster data" --verbose
  grass-rag --config cache_size=2000 --question "Buffer analysis"
        """
    )
    
    # Query options
    parser.add_argument(
        "--question", "-q",
        type=str,
        help="Question to ask about GRASS GIS"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start interactive shell mode"
    )
    
    # Configuration options
    parser.add_argument(
        "--config",
        type=str,
        action="append",
        help="Configuration options (key=value format)"
    )
    
    parser.add_argument(
        "--cache-size",
        type=int,
        default=1000,
        help="Cache size (default: 1000)"
    )
    
    parser.add_argument(
        "--max-response-time",
        type=float,
        default=5.0,
        help="Maximum response time in seconds (default: 5.0)"
    )
    
    # Output options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress non-essential output"
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    # Performance options
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Show detailed performance metrics"
    )

    # Cost optimization flags
    parser.add_argument(
        "--minimal-mode",
        action="store_true",
        help="Run in minimal mode (no model downloads, template + heuristic only)"
    )
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="Disable any model downloads (operate with existing cache only)"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show pipeline statistics"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    elif args.quiet:
        logger.remove()
        logger.add(sys.stderr, level="ERROR")
    
    # Parse configuration
    config = _parse_config(args)
    # Inject cost flags
    if args.minimal_mode:
        config["minimal_mode"] = True
    if args.no_download:
        config["allow_download"] = False
    
    try:
        # Initialize RAG pipeline
        if not args.quiet:
            print("🌱 Initializing GRASS GIS RAG Pipeline...")
        
        rag = GrassRAG(config)
        
        if not args.quiet:
            print("✅ Pipeline ready!")
        
        # Handle different modes
        if args.interactive:
            interactive_shell(rag, args)
        elif args.question:
            single_query(rag, args.question, args)
        elif args.stats:
            show_stats(rag, args)
        else:
            # No specific action, show help
            parser.print_help()
            return 1
        
        return 0
    
    except KeyboardInterrupt:
        if not args.quiet:
            print("\n👋 Goodbye!")
        return 0
    
    except Exception as e:
        logger.error(f"CLI error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def single_query(rag: GrassRAG, question: str, args) -> None:
    """Handle single query mode"""
    validator = ResponseValidator()
    
    # Validate and sanitize query
    if not validator.validate_query(question):
        print("❌ Invalid query format. Please check your input.")
        return
    
    question = validator.sanitize_query(question)
    
    if not args.quiet:
        print(f"\n🔍 Query: {question}")
        print("⏳ Processing...")
    
    # Execute query with timing
    start_time = time.time()
    
    try:
        response = rag.ask(question)
        
        # Validate response
        if not validator.validate_response(response):
            print("⚠️  Response validation failed")
        
        # Display results
        if args.format == "json":
            import json
            print(json.dumps(response.to_dict(), indent=2))
        else:
            _display_text_response(response, args)
    
    except Exception as e:
        logger.error(f"Query failed: {e}")
        print(f"❌ Error: {e}")


def interactive_shell(rag: GrassRAG, args) -> None:
    """Handle interactive shell mode"""
    validator = ResponseValidator()
    
    print("\n🌱 GRASS GIS RAG Interactive Shell")
    print("Type 'help' for commands, 'exit' to quit")
    print("-" * 50)
    
    session_stats = {
        "queries": 0,
        "total_time": 0.0,
        "avg_confidence": 0.0
    }
    
    while True:
        try:
            # Get user input
            question = input("\n🌱 > ").strip()
            
            if not question:
                continue
            
            # Handle special commands
            if question.lower() in ["exit", "quit", "q"]:
                break
            elif question.lower() == "help":
                _show_help()
                continue
            elif question.lower() == "stats":
                _show_session_stats(session_stats)
                continue
            elif question.lower() == "clear":
                rag.clear_cache()
                print("🧹 Cache cleared")
                continue
            elif question.lower().startswith("config"):
                _handle_config_command(question, rag)
                continue
            
            # Validate query
            if not validator.validate_query(question):
                print("❌ Invalid query format. Please try again.")
                continue
            
            question = validator.sanitize_query(question)
            
            # Process query
            print("⏳ Processing...")
            start_time = time.time()
            
            response = rag.ask(question)
            query_time = time.time() - start_time
            
            # Update session stats
            session_stats["queries"] += 1
            session_stats["total_time"] += query_time
            session_stats["avg_confidence"] = (
                (session_stats["avg_confidence"] * (session_stats["queries"] - 1) + response.confidence) 
                / session_stats["queries"]
            )
            
            # Display response
            _display_text_response(response, args)
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Interactive shell error: {e}")
            print(f"❌ Error: {e}")
    
    # Show session summary
    if session_stats["queries"] > 0:
        print(f"\n📊 Session Summary:")
        print(f"   Queries: {session_stats['queries']}")
        print(f"   Total time: {session_stats['total_time']:.2f}s")
        print(f"   Avg confidence: {session_stats['avg_confidence']:.3f}")
    
    print("👋 Goodbye!")


def show_stats(rag: GrassRAG, args) -> None:
    """Show pipeline statistics"""
    try:
        # Get performance report
        report = rag._pipeline.get_performance_report()
        
        print("\n📊 GRASS RAG Pipeline Statistics")
        print("=" * 50)
        
        if "performance_summary" in report:
            summary = report["performance_summary"]
            print(f"Total Queries: {summary['total_queries']}")
            print(f"Average Quality: {summary['avg_quality_score']:.3f}")
            print(f"Average Response Time: {summary['avg_response_time']:.3f}s")
            print(f"Template Hit Rate: {summary['template_hit_rate']:.1f}%")
            print(f"Cache Hit Rate: {summary['cache_hit_rate']:.1f}%")
        
        if "target_achievement" in report:
            targets = report["target_achievement"]
            print(f"\n🎯 Target Achievement:")
            print(f"Quality (≥0.9): {'✅' if targets['quality_achieved'] else '❌'}")
            print(f"Speed (<5s): {'✅' if targets['speed_achieved'] else '❌'}")
            print(f"Size (<1GB): {'✅' if targets['size_achievable'] else '❌'}")
        
        # Cache stats
        cache_stats = rag._pipeline.get_cache_stats()
        print(f"\n💾 Cache Statistics:")
        print(f"L1 Cache Size: {cache_stats['l1_size']}")
        print(f"L2 Cache Size: {cache_stats['l2_size']}/{cache_stats['l2_max_size']}")
        print(f"Hit Rate: {cache_stats['hit_rate']:.1f}%")
        
        # Template stats
        template_stats = rag._pipeline.get_template_stats()
        print(f"\n📋 Template Statistics:")
        print(f"Total Templates: {template_stats['total_templates']}")
        print(f"Average Quality: {template_stats['avg_quality_score']:.3f}")
        print(f"Categories: {len(template_stats['categories'])}")
    
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        print(f"❌ Error getting statistics: {e}")


def _parse_config(args) -> dict:
    """Parse configuration from command line arguments"""
    config = {
        "cache_size": args.cache_size,
        "max_response_time": args.max_response_time
    }
    
    # Parse additional config options
    if args.config:
        for config_str in args.config:
            try:
                key, value = config_str.split("=", 1)
                # Try to convert to appropriate type
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        if value.lower() in ["true", "false"]:
                            value = value.lower() == "true"
                
                config[key] = value
            except ValueError:
                logger.warning(f"Invalid config format: {config_str}")
    
    return config


def _display_text_response(response, args) -> None:
    """Display response in text format"""
    print(f"\n📝 Answer:")
    print(response.answer)
    
    if args.benchmark or args.verbose:
        print(f"\n📊 Metrics:")
        print(f"   Confidence: {response.confidence:.3f}")
        print(f"   Response Time: {response.response_time_ms:.1f}ms")
        print(f"   Source Type: {response.source_type}")
        
        if response.sources:
            print(f"   Sources: {len(response.sources)}")
            if args.verbose:
                for i, source in enumerate(response.sources[:3]):  # Show first 3
                    print(f"     {i+1}. {source.get('type', 'unknown')}")


def _show_help() -> None:
    """Show interactive shell help"""
    print("""
🌱 GRASS RAG Interactive Shell Commands:

Basic Commands:
  help          - Show this help message
  exit, quit, q - Exit the shell
  stats         - Show session statistics
  clear         - Clear response cache

Configuration:
  config show   - Show current configuration
  config cache_size=N - Set cache size

Query Tips:
  - Ask specific questions about GRASS GIS
  - Use keywords like "slope", "import", "buffer"
  - Try "How do I..." or "What command..." formats

Examples:
  > How do I calculate slope from a DEM?
  > Import raster data into GRASS GIS
  > Create buffer zones around points
    """)


def _show_session_stats(stats: dict) -> None:
    """Show current session statistics"""
    print(f"\n📊 Session Statistics:")
    print(f"   Queries processed: {stats['queries']}")
    if stats['queries'] > 0:
        print(f"   Total time: {stats['total_time']:.2f}s")
        print(f"   Average time: {stats['total_time']/stats['queries']:.2f}s")
        print(f"   Average confidence: {stats['avg_confidence']:.3f}")


def _handle_config_command(command: str, rag: GrassRAG) -> None:
    """Handle configuration commands in interactive mode"""
    parts = command.split()
    
    if len(parts) == 1 or (len(parts) == 2 and parts[1] == "show"):
        # Show current config
        config = rag._pipeline.config
        print(f"\n⚙️  Current Configuration:")
        print(f"   Cache Size: {config.cache_size}")
        print(f"   Max Response Time: {config.max_response_time}s")
        print(f"   Template Threshold: {config.template_threshold}")
        print(f"   Enable GPU: {config.enable_gpu}")
    
    elif len(parts) == 2 and "=" in parts[1]:
        # Set configuration
        try:
            key, value = parts[1].split("=", 1)
            
            # Convert value to appropriate type
            if key in ["cache_size", "batch_size", "top_k_results"]:
                value = int(value)
            elif key in ["max_response_time", "template_threshold", "template_quality_threshold"]:
                value = float(value)
            elif key in ["enable_gpu", "enable_metrics", "enable_templates"]:
                value = value.lower() == "true"
            
            # Apply configuration
            rag.configure(**{key: value})
            print(f"✅ Configuration updated: {key} = {value}")
        
        except Exception as e:
            print(f"❌ Configuration error: {e}")
    
    else:
        print("❌ Invalid config command. Use 'config show' or 'config key=value'")


if __name__ == "__main__":
    sys.exit(main())