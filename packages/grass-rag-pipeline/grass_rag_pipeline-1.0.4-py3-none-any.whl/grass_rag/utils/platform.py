"""
Cross-platform compatibility utilities for GRASS RAG pipeline
Handles OS-specific paths, configurations, and system detection
"""

import os
import sys
import platform
from pathlib import Path
from typing import Dict, Optional, Tuple
from loguru import logger


class PlatformManager:
    """Manages cross-platform compatibility and system detection"""
    
    def __init__(self):
        """Initialize platform manager with system detection"""
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.python_version = sys.version_info
        
        # Platform-specific configurations
        self.platform_configs = {
            'windows': {
                'cache_base': os.path.expandvars('%APPDATA%'),
                'temp_base': os.path.expandvars('%TEMP%'),
                'path_separator': ';',
                'executable_extension': '.exe',
                'library_extension': '.dll'
            },
            'darwin': {  # macOS
                'cache_base': os.path.expanduser('~/Library/Caches'),
                'temp_base': '/tmp',
                'path_separator': ':',
                'executable_extension': '',
                'library_extension': '.dylib'
            },
            'linux': {
                'cache_base': os.path.expanduser('~/.cache'),
                'temp_base': '/tmp',
                'path_separator': ':',
                'executable_extension': '',
                'library_extension': '.so'
            }
        }
        
        logger.info(f"Platform detected: {self.system} {self.architecture}")
    
    def get_cache_directory(self, app_name: str = "grass_rag") -> Path:
        """
        Get platform-appropriate cache directory
        
        Args:
            app_name: Application name for cache subdirectory
            
        Returns:
            Path to cache directory
        """
        if self.system in self.platform_configs:
            base_dir = self.platform_configs[self.system]['cache_base']
        else:
            # Fallback for unknown systems
            base_dir = os.path.expanduser('~/.cache')
        
        cache_dir = Path(base_dir) / app_name
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        return cache_dir
    
    def get_data_directory(self, app_name: str = "grass_rag") -> Path:
        """
        Get platform-appropriate data directory
        
        Args:
            app_name: Application name for data subdirectory
            
        Returns:
            Path to data directory
        """
        if self.system == 'windows':
            base_dir = os.path.expandvars('%LOCALAPPDATA%')
        elif self.system == 'darwin':
            base_dir = os.path.expanduser('~/Library/Application Support')
        else:  # Linux and others
            base_dir = os.path.expanduser('~/.local/share')
        
        data_dir = Path(base_dir) / app_name
        data_dir.mkdir(parents=True, exist_ok=True)
        
        return data_dir
    
    def get_temp_directory(self, app_name: str = "grass_rag") -> Path:
        """
        Get platform-appropriate temporary directory
        
        Args:
            app_name: Application name for temp subdirectory
            
        Returns:
            Path to temporary directory
        """
        if self.system in self.platform_configs:
            base_dir = self.platform_configs[self.system]['temp_base']
        else:
            base_dir = '/tmp'
        
        temp_dir = Path(base_dir) / app_name
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        return temp_dir
    
    def get_config_directory(self, app_name: str = "grass_rag") -> Path:
        """
        Get platform-appropriate configuration directory
        
        Args:
            app_name: Application name for config subdirectory
            
        Returns:
            Path to configuration directory
        """
        if self.system == 'windows':
            base_dir = os.path.expandvars('%APPDATA%')
        elif self.system == 'darwin':
            base_dir = os.path.expanduser('~/Library/Preferences')
        else:  # Linux and others
            base_dir = os.path.expanduser('~/.config')
        
        config_dir = Path(base_dir) / app_name
        config_dir.mkdir(parents=True, exist_ok=True)
        
        return config_dir
    
    def check_python_compatibility(self, min_version: Tuple[int, int] = (3, 8)) -> bool:
        """
        Check if current Python version meets minimum requirements
        
        Args:
            min_version: Minimum required Python version tuple
            
        Returns:
            True if Python version is compatible
        """
        current_version = (self.python_version.major, self.python_version.minor)
        compatible = current_version >= min_version
        
        if not compatible:
            logger.error(f"Python {current_version[0]}.{current_version[1]} detected, "
                        f"minimum required: {min_version[0]}.{min_version[1]}")
        
        return compatible
    
    def get_system_info(self) -> Dict[str, str]:
        """
        Get comprehensive system information
        
        Returns:
            Dictionary with system information
        """
        return {
            'system': self.system,
            'architecture': self.architecture,
            'python_version': f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}",
            'platform': platform.platform(),
            'processor': platform.processor(),
            'machine': platform.machine(),
            'node': platform.node(),
            'release': platform.release(),
            'version': platform.version()
        }
    
    def check_disk_space(self, path: Path, required_gb: float = 1.0) -> bool:
        """
        Check if sufficient disk space is available
        
        Args:
            path: Path to check disk space for
            required_gb: Required space in GB
            
        Returns:
            True if sufficient space is available
        """
        try:
            import shutil
            
            # Ensure path exists
            path.mkdir(parents=True, exist_ok=True)
            
            # Get disk usage
            total, used, free = shutil.disk_usage(path)
            free_gb = free / (1024**3)
            
            sufficient = free_gb >= required_gb
            
            if not sufficient:
                logger.warning(f"Insufficient disk space: {free_gb:.1f}GB available, "
                             f"{required_gb:.1f}GB required")
            
            return sufficient
        
        except Exception as e:
            logger.error(f"Failed to check disk space: {e}")
            return True  # Assume sufficient if check fails
    
    def get_executable_name(self, base_name: str) -> str:
        """
        Get platform-appropriate executable name
        
        Args:
            base_name: Base executable name
            
        Returns:
            Executable name with platform-specific extension
        """
        if self.system in self.platform_configs:
            extension = self.platform_configs[self.system]['executable_extension']
            return f"{base_name}{extension}"
        
        return base_name
    
    def normalize_path(self, path: str) -> Path:
        """
        Normalize path for current platform
        
        Args:
            path: Path string to normalize
            
        Returns:
            Normalized Path object
        """
        # Convert to Path object and resolve
        normalized = Path(path).expanduser().resolve()
        
        # Ensure parent directories exist
        if not normalized.exists() and normalized.suffix:
            # It's a file, create parent directories
            normalized.parent.mkdir(parents=True, exist_ok=True)
        elif not normalized.exists():
            # It's a directory, create it
            normalized.mkdir(parents=True, exist_ok=True)
        
        return normalized
    
    def get_path_separator(self) -> str:
        """Get platform-appropriate path separator for PATH variable"""
        if self.system in self.platform_configs:
            return self.platform_configs[self.system]['path_separator']
        return ':'
    
    def is_admin(self) -> bool:
        """
        Check if running with administrator/root privileges
        
        Returns:
            True if running with elevated privileges
        """
        try:
            if self.system == 'windows':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    def get_memory_info(self) -> Dict[str, float]:
        """
        Get system memory information
        
        Returns:
            Dictionary with memory info in GB
        """
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            
            return {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent_used': memory.percent
            }
        
        except ImportError:
            logger.warning("psutil not available, cannot get memory info")
            return {}
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return {}
    
    def validate_environment(self) -> Dict[str, bool]:
        """
        Validate system environment for GRASS RAG pipeline
        
        Returns:
            Dictionary with validation results
        """
        results = {
            'python_compatible': self.check_python_compatibility(),
            'sufficient_disk_space': self.check_disk_space(self.get_cache_directory(), 1.0),
            'cache_dir_writable': True,
            'data_dir_writable': True,
            'temp_dir_writable': True
        }
        
        # Test directory writability
        try:
            test_file = self.get_cache_directory() / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
        except Exception:
            results['cache_dir_writable'] = False
        
        try:
            test_file = self.get_data_directory() / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
        except Exception:
            results['data_dir_writable'] = False
        
        try:
            test_file = self.get_temp_directory() / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
        except Exception:
            results['temp_dir_writable'] = False
        
        return results


# Global platform manager instance
platform_manager = PlatformManager()


def get_platform_paths(app_name: str = "grass_rag") -> Dict[str, Path]:
    """
    Get all platform-appropriate paths for the application
    
    Args:
        app_name: Application name
        
    Returns:
        Dictionary with all relevant paths
    """
    return {
        'cache': platform_manager.get_cache_directory(app_name),
        'data': platform_manager.get_data_directory(app_name),
        'config': platform_manager.get_config_directory(app_name),
        'temp': platform_manager.get_temp_directory(app_name)
    }


def validate_system_requirements() -> bool:
    """
    Validate that system meets all requirements
    
    Returns:
        True if system is compatible
    """
    validation = platform_manager.validate_environment()
    
    all_valid = all(validation.values())
    
    if not all_valid:
        logger.error("System validation failed:")
        for check, result in validation.items():
            if not result:
                logger.error(f"  - {check}: FAILED")
    
    return all_valid


def get_installation_instructions() -> str:
    """
    Get platform-specific installation instructions
    
    Returns:
        Installation instructions as string
    """
    system = platform_manager.system
    
    instructions = {
        'windows': """
Windows Installation Instructions:

1. **Install Python 3.8+**
   - Download from https://python.org/downloads/
   - Ensure "Add Python to PATH" is checked during installation

2. **Install GRASS RAG Pipeline**
   ```cmd
   pip install grass-rag-pipeline
   ```

3. **Verify Installation**
   ```cmd
   grass-rag --help
   ```

4. **Run Web Interface**
   ```cmd
   grass-rag-ui
   ```

**Troubleshooting:**
- If command not found, add Python Scripts directory to PATH
- For permission issues, run Command Prompt as Administrator
- Ensure Windows Defender allows Python and pip
        """,
        
        'darwin': """
macOS Installation Instructions:

1. **Install Python 3.8+**
   ```bash
   # Using Homebrew (recommended)
   brew install python@3.11
   
   # Or download from https://python.org/downloads/
   ```

2. **Install GRASS RAG Pipeline**
   ```bash
   pip3 install grass-rag-pipeline
   ```

3. **Verify Installation**
   ```bash
   grass-rag --help
   ```

4. **Run Web Interface**
   ```bash
   grass-rag-ui
   ```

**Troubleshooting:**
- Use `pip3` instead of `pip` if needed
- For permission issues, use `--user` flag: `pip3 install --user grass-rag-pipeline`
- Ensure Xcode Command Line Tools are installed: `xcode-select --install`
        """,
        
        'linux': """
Linux Installation Instructions:

1. **Install Python 3.8+**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip
   
   # CentOS/RHEL/Fedora
   sudo yum install python3 python3-pip
   # or
   sudo dnf install python3 python3-pip
   ```

2. **Install GRASS RAG Pipeline**
   ```bash
   pip3 install grass-rag-pipeline
   ```

3. **Verify Installation**
   ```bash
   grass-rag --help
   ```

4. **Run Web Interface**
   ```bash
   grass-rag-ui
   ```

**Troubleshooting:**
- Use `pip3` instead of `pip` if needed
- For permission issues, use `--user` flag: `pip3 install --user grass-rag-pipeline`
- Ensure ~/.local/bin is in your PATH for user installations
- For system-wide installation, use `sudo pip3 install grass-rag-pipeline`
        """
    }
    
    return instructions.get(system, instructions['linux'])  # Default to Linux instructions