"""
Streamlit web interface for GRASS RAG pipeline
Provides interactive web-based access to the chatbot
"""

import streamlit as st
import time
import json
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from .. import GrassRAG
from ..core.models import RAGConfig


def main():
    """Main Streamlit app entry point"""
    st.set_page_config(
        page_title="GRASS GIS RAG Assistant",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if "rag" not in st.session_state:
        st.session_state.rag = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "config" not in st.session_state:
        st.session_state.config = {}
    
    # Sidebar configuration
    with st.sidebar:
        st.title("🌱 GRASS RAG")
        st.markdown("AI-powered GRASS GIS assistance")
        
        # Configuration section
        st.header("⚙️ Configuration")
        
        cache_size = st.slider("Cache Size", 100, 5000, 1000, 100)
        max_response_time = st.slider("Max Response Time (s)", 1.0, 10.0, 5.0, 0.5)
        template_threshold = st.slider("Template Threshold", 0.1, 1.0, 0.8, 0.1)
        
        enable_gpu = st.checkbox("Enable GPU", value=False)
        enable_metrics = st.checkbox("Show Metrics", value=True)
        
        # Apply configuration
        config = {
            "cache_size": cache_size,
            "max_response_time": max_response_time,
            "template_threshold": template_threshold,
            "enable_gpu": enable_gpu,
            "enable_metrics": enable_metrics
        }
        
        if st.button("Apply Configuration"):
            st.session_state.config = config
            st.session_state.rag = None  # Force reinitialization
            st.success("Configuration applied!")
        
        # Statistics section
        st.header("📊 Statistics")
        if st.session_state.rag:
            show_statistics()
        
        # Quick actions
        st.header("🚀 Quick Actions")
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
        
        if st.button("Clear Cache"):
            if st.session_state.rag:
                st.session_state.rag.clear_cache()
                st.success("Cache cleared!")
    
    # Main content area
    st.title("🌱 GRASS GIS RAG Assistant")
    st.markdown("Ask questions about GRASS GIS and get AI-powered assistance!")
    
    # Initialize RAG pipeline
    if st.session_state.rag is None:
        with st.spinner("Initializing GRASS RAG Pipeline..."):
            try:
                st.session_state.rag = GrassRAG(st.session_state.config)
                st.success("✅ Pipeline initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize pipeline: {e}")
                return
    
    # Chat interface
    chat_interface()
    
    # Batch processing interface
    st.header("📦 Batch Processing")
    batch_interface()
    
    # Performance monitoring
    if st.session_state.config.get("enable_metrics", True):
        st.header("📈 Performance Monitoring")
        performance_monitoring()


def chat_interface():
    """Main chat interface"""
    st.header("💬 Chat Interface")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for i, (query, response) in enumerate(st.session_state.chat_history):
            # User message
            st.markdown(f"**🧑 You:** {query}")
            
            # Assistant response
            with st.expander(f"🌱 Assistant Response {i+1}", expanded=True):
                st.markdown(response.answer)
                
                # Show metrics if enabled
                if st.session_state.config.get("enable_metrics", True):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Confidence", f"{response.confidence:.3f}")
                    with col2:
                        st.metric("Response Time", f"{response.response_time_ms:.0f}ms")
                    with col3:
                        st.metric("Source Type", response.source_type)
                    with col4:
                        st.metric("Sources", len(response.sources))
            
            st.divider()
    
    # Query input
    with st.form("query_form"):
        query = st.text_area(
            "Ask a question about GRASS GIS:",
            placeholder="How do I calculate slope from a DEM?",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit = st.form_submit_button("🚀 Ask", use_container_width=True)
        with col2:
            if st.form_submit_button("🧹 Clear History", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
    
    if submit and query.strip():
        with st.spinner("Processing your question..."):
            try:
                start_time = time.time()
                response = st.session_state.rag.ask(query.strip())
                processing_time = time.time() - start_time
                
                # Add to chat history
                st.session_state.chat_history.append((query.strip(), response))
                
                # Show success message
                st.success(f"✅ Response generated in {processing_time:.2f}s")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error processing query: {e}")


def batch_interface():
    """Batch processing interface"""
    st.markdown("Process multiple queries at once")
    
    # Input methods
    input_method = st.radio(
        "Input Method:",
        ["Text Area", "File Upload"],
        horizontal=True
    )
    
    queries = []
    
    if input_method == "Text Area":
        query_text = st.text_area(
            "Enter queries (one per line):",
            placeholder="How do I import raster data?\nCalculate slope from DEM\nCreate buffer zones",
            height=150
        )
        if query_text:
            queries = [q.strip() for q in query_text.split('\n') if q.strip()]
    
    else:  # File Upload
        uploaded_file = st.file_uploader(
            "Upload text file with queries (one per line)",
            type=['txt']
        )
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            queries = [q.strip() for q in content.split('\n') if q.strip()]
    
    if queries:
        st.info(f"Found {len(queries)} queries to process")
        
        if st.button("🚀 Process Batch"):
            process_batch_queries(queries)


def process_batch_queries(queries: List[str]):
    """Process batch queries and display results"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    results = []
    total_time = 0
    
    for i, query in enumerate(queries):
        status_text.text(f"Processing query {i+1}/{len(queries)}: {query[:50]}...")
        progress_bar.progress((i + 1) / len(queries))
        
        try:
            start_time = time.time()
            response = st.session_state.rag.ask(query)
            query_time = time.time() - start_time
            total_time += query_time
            
            results.append({
                "query": query,
                "response": response,
                "success": True,
                "time": query_time
            })
        
        except Exception as e:
            results.append({
                "query": query,
                "error": str(e),
                "success": False,
                "time": 0
            })
    
    status_text.text("✅ Batch processing complete!")
    
    # Display results
    with results_container:
        st.subheader("📊 Batch Results")
        
        # Summary metrics
        successful = sum(1 for r in results if r["success"])
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", len(queries))
        with col2:
            st.metric("Successful", successful)
        with col3:
            st.metric("Failed", len(queries) - successful)
        with col4:
            st.metric("Total Time", f"{total_time:.2f}s")
        
        # Individual results
        for i, result in enumerate(results):
            with st.expander(f"Query {i+1}: {result['query'][:50]}..."):
                if result["success"]:
                    st.markdown(f"**Response:** {result['response'].answer}")
                    st.info(f"Confidence: {result['response'].confidence:.3f} | Time: {result['time']:.3f}s")
                else:
                    st.error(f"Error: {result['error']}")


def show_statistics():
    """Show pipeline statistics in sidebar"""
    try:
        report = st.session_state.rag._pipeline.get_performance_report()
        
        if "performance_summary" in report:
            summary = report["performance_summary"]
            
            st.metric("Total Queries", summary["total_queries"])
            st.metric("Avg Quality", f"{summary['avg_quality_score']:.3f}")
            st.metric("Avg Response Time", f"{summary['avg_response_time']:.3f}s")
            st.metric("Template Hit Rate", f"{summary['template_hit_rate']:.1f}%")
            st.metric("Cache Hit Rate", f"{summary['cache_hit_rate']:.1f}%")
        
        # Cache stats
        cache_stats = st.session_state.rag._pipeline.get_cache_stats()
        st.metric("Cache Hit Rate", f"{cache_stats['hit_rate']:.1f}%")
    
    except Exception as e:
        st.error(f"Error getting statistics: {e}")


def performance_monitoring():
    """Performance monitoring dashboard"""
    try:
        report = st.session_state.rag._pipeline.get_performance_report()
        
        if "performance_summary" not in report:
            st.info("No performance data available yet. Ask some questions first!")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Quality metrics
            st.subheader("🎯 Quality Metrics")
            
            quality_data = report.get("quality_analysis", {})
            if quality_data:
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = report["performance_summary"]["avg_quality_score"],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Average Quality Score"},
                    delta = {'reference': 0.9},
                    gauge = {
                        'axis': {'range': [None, 1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 0.5], 'color': "lightgray"},
                            {'range': [0.5, 0.9], 'color': "yellow"},
                            {'range': [0.9, 1], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 0.9
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Speed metrics
            st.subheader("⚡ Speed Metrics")
            
            speed_data = report.get("speed_analysis", {})
            if speed_data:
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = report["performance_summary"]["avg_response_time"],
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Average Response Time (s)"},
                    delta = {'reference': 5.0},
                    gauge = {
                        'axis': {'range': [0, 10]},
                        'bar': {'color': "darkgreen"},
                        'steps': [
                            {'range': [0, 1], 'color': "green"},
                            {'range': [1, 5], 'color': "yellow"},
                            {'range': [5, 10], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 5.0
                        }
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        # Cache performance
        st.subheader("💾 Cache Performance")
        cache_stats = st.session_state.rag._pipeline.get_cache_stats()
        
        cache_df = pd.DataFrame({
            'Cache Level': ['L1 Cache', 'L2 Cache', 'Misses'],
            'Count': [cache_stats['l1_hits'], cache_stats['l2_hits'], cache_stats['misses']],
            'Percentage': [
                cache_stats['l1_hit_rate'],
                cache_stats['l2_hit_rate'],
                100 - cache_stats['hit_rate']
            ]
        })
        
        fig = px.pie(cache_df, values='Count', names='Cache Level', 
                     title="Cache Hit Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Template usage
        st.subheader("📋 Template Usage")
        template_stats = st.session_state.rag._pipeline.get_template_stats()
        
        if template_stats.get("categories"):
            categories_df = pd.DataFrame(
                list(template_stats["categories"].items()),
                columns=['Category', 'Count']
            )
            
            fig = px.bar(categories_df, x='Category', y='Count',
                        title="Templates by Category")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error displaying performance metrics: {e}")


if __name__ == "__main__":
    main()