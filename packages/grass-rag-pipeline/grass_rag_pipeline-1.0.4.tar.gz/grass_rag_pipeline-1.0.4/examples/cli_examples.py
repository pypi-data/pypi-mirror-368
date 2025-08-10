#!/usr/bin/env python3
"""
Command-line interface examples for GRASS GIS RAG Pipeline
Demonstrates CLI usage patterns and automation scripts
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and display results"""
    print(f"\n🔧 {description}")
    print(f"Command: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print("Output:")
                print(result.stdout)
        else:
            print("❌ Failed!")
            if result.stderr:
                print("Error:")
                print(result.stderr)
    
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out")
    except Exception as e:
        print(f"❌ Error running command: {e}")


def basic_cli_examples():
    """Basic CLI usage examples"""
    print("🌱 Basic CLI Examples")
    print("=" * 50)
    
    # Help command
    run_command(
        "grass-rag --help",
        "Display help information"
    )
    
    # Simple query
    run_command(
        'grass-rag --question "How do I calculate slope from DEM?"',
        "Ask a simple question"
    )
    
    # Verbose output
    run_command(
        'grass-rag --question "Import raster data" --verbose',
        "Query with verbose output"
    )
    
    # JSON output format
    run_command(
        'grass-rag --question "Create buffer zones" --format json',
        "Query with JSON output"
    )


def configuration_examples():
    """Configuration examples"""
    print("\n🌱 Configuration Examples")
    print("=" * 50)
    
    # Custom cache size
    run_command(
        'grass-rag --cache-size 2000 --question "Vector overlay analysis"',
        "Custom cache size"
    )
    
    # Custom response time limit
    run_command(
        'grass-rag --max-response-time 3.0 --question "Watershed analysis"',
        "Custom response time limit"
    )
    
    # Multiple config options
    run_command(
        'grass-rag --config cache_size=1500 --config template_threshold=0.9 --question "Contour lines"',
        "Multiple configuration options"
    )


def performance_examples():
    """Performance monitoring examples"""
    print("\n🌱 Performance Examples")
    print("=" * 50)
    
    # Show statistics
    run_command(
        "grass-rag --stats",
        "Display pipeline statistics"
    )
    
    # Benchmark mode
    run_command(
        'grass-rag --question "Interpolate surface" --benchmark',
        "Query with performance metrics"
    )


def interactive_mode_example():
    """Interactive mode example"""
    print("\n🌱 Interactive Mode Example")
    print("=" * 50)
    
    print("""
To start interactive mode, run:
    grass-rag --interactive

Interactive commands:
    > How do I calculate slope from DEM?
    > help
    > stats
    > config show
    > config cache_size=2000
    > clear
    > exit

Example session:
    🌱 > How do I import raster data?
    📝 Answer: Use r.import command to import raster data...
    
    🌱 > stats
    📊 Session Statistics:
       Queries processed: 1
       Average time: 0.05s
       Average confidence: 0.95
    
    🌱 > exit
    👋 Goodbye!
    """)


def batch_processing_example():
    """Batch processing example"""
    print("\n🌱 Batch Processing Example")
    print("=" * 50)
    
    # Create example batch file
    batch_file = Path("example_queries.txt")
    
    queries = [
        "How do I calculate slope from DEM?",
        "Import raster data into GRASS GIS",
        "Create buffer zones around points",
        "Export vector data to shapefile",
        "Perform watershed analysis"
    ]
    
    try:
        with open(batch_file, 'w') as f:
            f.write('\n'.join(queries))
        
        print(f"Created batch file: {batch_file}")
        print("Contents:")
        for i, query in enumerate(queries, 1):
            print(f"  {i}. {query}")
        
        print("\nTo process batch file:")
        print(f"    cat {batch_file} | while read line; do")
        print('        grass-rag --question "$line"')
        print("    done")
        
        # Clean up
        batch_file.unlink()
        
    except Exception as e:
        print(f"Error creating batch file: {e}")


def automation_script_example():
    """Automation script example"""
    print("\n🌱 Automation Script Example")
    print("=" * 50)
    
    script_content = '''#!/bin/bash
# GRASS GIS RAG Pipeline Automation Script

# Configuration
CACHE_SIZE=2000
MAX_RESPONSE_TIME=5.0
OUTPUT_DIR="./rag_outputs"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Common GRASS GIS questions
questions=(
    "How do I calculate slope from DEM?"
    "Import raster data into GRASS GIS"
    "Create buffer zones around points"
    "Export vector data to shapefile"
    "Perform watershed analysis"
    "Generate contour lines from elevation"
    "Vector overlay analysis"
    "Raster map algebra calculations"
    "Classify raster data"
    "Interpolate surface from points"
)

echo "🌱 Running GRASS GIS RAG Pipeline Automation"
echo "Processing ${#questions[@]} questions..."

# Process each question
for i in "${!questions[@]}"; do
    question="${questions[$i]}"
    output_file="$OUTPUT_DIR/query_$((i+1)).json"
    
    echo "Processing: $question"
    
    grass-rag \\
        --question "$question" \\
        --cache-size "$CACHE_SIZE" \\
        --max-response-time "$MAX_RESPONSE_TIME" \\
        --format json \\
        --quiet > "$output_file"
    
    if [ $? -eq 0 ]; then
        echo "✅ Saved to $output_file"
    else
        echo "❌ Failed to process question"
    fi
done

echo "🎉 Automation complete! Results in $OUTPUT_DIR"

# Generate summary report
echo "📊 Generating summary report..."
python3 -c "
import json
import glob
import statistics

files = glob.glob('$OUTPUT_DIR/*.json')
confidences = []
response_times = []

for file in files:
    try:
        with open(file, 'r') as f:
            data = json.load(f)
            confidences.append(data['confidence'])
            response_times.append(data['response_time_ms'])
    except:
        continue

if confidences:
    print(f'Average confidence: {statistics.mean(confidences):.3f}')
    print(f'Average response time: {statistics.mean(response_times):.1f}ms')
    print(f'High quality responses (≥0.9): {sum(1 for c in confidences if c >= 0.9)}/{len(confidences)}')
"
'''
    
    print("Example automation script (save as 'rag_automation.sh'):")
    print(script_content)


def web_interface_example():
    """Web interface example"""
    print("\n🌱 Web Interface Example")
    print("=" * 50)
    
    print("""
To start the web interface:
    grass-rag-ui

This will start a Streamlit web application with:

📊 Features:
- Interactive chat interface
- Real-time response metrics
- Batch query processing
- Configuration panel
- Performance monitoring
- Cache management

🌐 Access:
- Local: http://localhost:8501
- Network: http://your-ip:8501

💡 Usage Tips:
- Use the sidebar to adjust configuration
- Monitor performance metrics in real-time
- Process multiple queries with batch interface
- Clear cache when needed for testing
- Export results in various formats
    """)


def troubleshooting_examples():
    """Troubleshooting examples"""
    print("\n🌱 Troubleshooting Examples")
    print("=" * 50)
    
    print("""
Common Issues and Solutions:

1. Command not found: grass-rag
   Solution: Ensure package is installed and Python scripts directory is in PATH
   
   # Check installation
   pip show grass-rag-pipeline
   
   # Reinstall if needed
   pip install --upgrade grass-rag-pipeline

2. Permission denied errors
   Solution: Install with user flag or check directory permissions
   
   # User installation
   pip install --user grass-rag-pipeline
   
   # Check permissions
   grass-rag --question "test" --verbose

3. Slow response times
   Solution: Check system resources and configuration
   
   # Monitor performance
   grass-rag --stats
   
   # Adjust cache size
   grass-rag --cache-size 5000 --question "test"

4. Low quality responses
   Solution: Check template threshold and model availability
   
   # Lower template threshold
   grass-rag --config template_threshold=0.7 --question "test"
   
   # Verbose output for debugging
   grass-rag --question "test" --verbose

5. Memory issues
   Solution: Reduce cache size and batch processing
   
   # Smaller cache
   grass-rag --cache-size 500 --question "test"
   
   # Process queries individually instead of batch
    """)


def main():
    """Run all CLI examples"""
    print("🌱 GRASS GIS RAG Pipeline - CLI Examples")
    print("=" * 60)
    
    basic_cli_examples()
    configuration_examples()
    performance_examples()
    interactive_mode_example()
    batch_processing_example()
    automation_script_example()
    web_interface_example()
    troubleshooting_examples()
    
    print("\n✅ All CLI examples documented!")
    print("\n💡 Try running these commands to explore the functionality:")
    print("   grass-rag --help")
    print("   grass-rag --interactive")
    print("   grass-rag-ui")


if __name__ == "__main__":
    main()