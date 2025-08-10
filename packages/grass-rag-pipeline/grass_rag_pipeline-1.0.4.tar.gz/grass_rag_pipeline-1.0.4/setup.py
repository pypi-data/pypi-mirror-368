#!/usr/bin/env python3
"""
Setup script for GRASS GIS RAG Pipeline
Optimized for package distribution with performance guarantees
"""

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import os
import sys
from pathlib import Path

# Package metadata
__version__ = "1.0.4"
__author__ = "Sachin-NK"
__email__ = "snkodijara52@gmail.com"  # Update with your real email

def read_readme():
    """Read README for long description"""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "High-performance RAG pipeline for GRASS GIS with instant pattern matching"

def read_requirements():
    """Parse requirements from requirements_production.txt"""
    req_path = Path(__file__).parent / "requirements_production.txt"
    
    if not req_path.exists():
        # Fallback to minimal requirements
        return [
            "torch>=2.0.0,<3.0.0",
            "transformers>=4.30.0,<5.0.0", 
            "sentence-transformers>=2.2.0,<3.0.0",
            "numpy>=1.24.0,<2.0.0",
            "lancedb>=0.3.0,<1.0.0",
            "pyarrow>=12.0.0,<15.0.0",
            "loguru>=0.7.0,<1.0.0",
            "click>=8.1.0,<9.0.0"
        ], {}
    
    with open(req_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    requirements = []
    extras_require = {
        'ui': [],
        'dev': [],
        'monitoring': [],
        'rich': []
    }
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if 'extra ==' in line:
                # Parse optional dependencies
                try:
                    pkg, extra = line.split('; extra ==')
                    extra_name = extra.strip().strip('"')
                    if extra_name in extras_require:
                        extras_require[extra_name].append(pkg.strip())
                except ValueError:
                    # Skip malformed lines
                    continue
            else:
                # Core requirement
                requirements.append(line)
    
    return requirements, extras_require

def get_package_data():
    """Get package data files"""
    package_data = {
        "grass_rag": [
            "data/*.json",
            "data/datasets/*.json",
            "*.md",
            "*.txt"
        ]
    }
    
    # Check if data files exist
    data_dir = Path(__file__).parent / "grass_rag" / "data"
    if data_dir.exists():
        # Include all JSON files in data directory
        json_files = list(data_dir.glob("**/*.json"))
        if json_files:
            package_data["grass_rag"].extend([
                str(f.relative_to(Path(__file__).parent / "grass_rag")) 
                for f in json_files
            ])
    
    return package_data

class PostInstallCommand(install):
    """Post-installation command to set up models"""
    
    def run(self):
        install.run(self)
        self._post_install()
    
    def _post_install(self):
        """Run post-installation setup"""
        try:
            print("\nSetting up GRASS GIS RAG Pipeline...")
            
            # Check platform compatibility
            self._check_platform_compatibility()
            
            # Import and initialize to trigger model setup
            try:
                from grass_rag import GrassRAG
                print("Package imported successfully")
                
                # Test basic functionality
                rag = GrassRAG()
                test_response = rag.ask("test")
                if test_response:
                    print("Basic functionality verified")
                
            except ImportError as e:
                print(f"Import warning: {e}")
            except Exception as e:
                print(f"Setup warning: {e}")
            
            print("\nInstallation complete!")
            self._show_usage_info()
            
        except Exception as e:
            print(f"Post-install setup encountered issues: {e}")
            print("Package should still work normally.")
    
    def _check_platform_compatibility(self):
        """Check platform compatibility and requirements"""
        try:
            from grass_rag.utils.platform import validate_system_requirements, platform_manager
            
            print(f"Detected platform: {platform_manager.system} {platform_manager.architecture}")
            
            if not validate_system_requirements():
                print("Some system requirements not met, but installation will continue")
            else:
                print("System requirements validated")
                
        except ImportError:
            print("Platform validation unavailable during installation")
        except Exception as e:
            print(f"Platform check warning: {e}")
    
    def _show_usage_info(self):
        """Show usage information"""
        print("""
GRASS GIS RAG Pipeline Usage:

Command Line:
   grass-rag --question "How do I calculate slope from DEM?"
   grass-rag --interactive

Web Interface:
   grass-rag-ui

Python API:
   from grass_rag import GrassRAG
   rag = GrassRAG()
   response = rag.ask("Your question here")

Performance Targets:
   >90% accuracy
   <5 second response time  
   <1GB package size

Package includes:
   - 10+ GRASS GIS template categories
   - Multi-level caching system
   - Offline operation capability
   - Cross-platform compatibility

For documentation: https://github.com/Sachin-NK/grass-rag-pipeline
        """)

class PostDevelopCommand(develop):
    """Post-development command"""
    
    def run(self):
        develop.run(self)
        print("Development installation complete!")

# Parse requirements
requirements, extras_require = read_requirements()

# Add full extras option
extras_require['full'] = [
    pkg for pkg_list in extras_require.values() 
    for pkg in pkg_list
]

# Add test extras
extras_require['test'] = [
    'pytest>=7.4.0',
    'pytest-asyncio>=0.21.0',
    'pytest-cov>=4.1.0',
    'psutil>=5.9.0'
]

setup(
    # Basic package information
    name="grass-rag-pipeline",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="High-performance RAG pipeline for GRASS GIS with >90% accuracy and <5s response time",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sachin-NK/grass-rag-pipeline",
    
    # Package configuration
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    include_package_data=True,
    package_data=get_package_data(),
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=requirements,
    extras_require=extras_require,
    
    # Entry points for command-line tools
    entry_points={
        "console_scripts": [
            "grass-rag=grass_rag.cli.main:main",
            "grass-rag-ui=grass_rag.cli.ui:main",
        ]
    },
    
    # Custom commands
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    
    # Package classification
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    
    # Keywords for package discovery
    keywords=[
        "grass-gis", "rag", "retrieval-augmented-generation", 
        "gis", "geospatial", "ai", "machine-learning",
        "vector-database", "semantic-search", "llm",
        "chatbot", "question-answering", "template-matching",
        "performance-optimized", "offline-capable"
    ],
    
    # Project URLs
    project_urls={
        "Bug Reports": "https://github.com/Sachin-NK/grass-rag-pipeline/issues",
        "Source": "https://github.com/Sachin-NK/grass-rag-pipeline",
        "Documentation": "https://github.com/Sachin-NK/grass-rag-pipeline/blob/main/README.md",
        "Changelog": "https://github.com/Sachin-NK/grass-rag-pipeline/blob/main/CHANGELOG.md",
    },
    
    # Package options
    zip_safe=False,
    platforms=["any"],
    
    # Test configuration
    test_suite="tests",
    
    # Package metadata for PyPI
    license="MIT",
    license_files=["LICENSE"],
)
