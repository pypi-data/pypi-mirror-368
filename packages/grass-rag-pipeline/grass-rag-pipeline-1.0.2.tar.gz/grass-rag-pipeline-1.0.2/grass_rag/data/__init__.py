"""
Data components for GRASS RAG pipeline
"""

import os
import json
from pathlib import Path

# Get package data directory
DATA_DIR = Path(__file__).parent

def load_templates():
    """Load template definitions from JSON file"""
    template_path = DATA_DIR / "templates.json"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_datasets_dir():
    """Get path to datasets directory"""
    return DATA_DIR / "datasets"

__all__ = ['load_templates', 'get_datasets_dir', 'DATA_DIR']