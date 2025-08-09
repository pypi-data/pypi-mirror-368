"""
Data compression utilities for GRASS RAG pipeline
Optimizes package size while maintaining data integrity
"""

import json
import gzip
import pickle
import lzma
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from loguru import logger


class DataCompressor:
    """Handles compression and decompression of package data"""
    
    def __init__(self):
        """Initialize data compressor"""
        self.compression_methods = {
            "json": self._compress_json,
            "pickle": self._compress_pickle,
            "gzip": self._compress_gzip,
            "lzma": self._compress_lzma
        }
        
        self.decompression_methods = {
            "json": self._decompress_json,
            "pickle": self._decompress_pickle,
            "gzip": self._decompress_gzip,
            "lzma": self._decompress_lzma
        }
    
    def compress_data(self, data: Any, method: str = "json", output_path: Optional[Path] = None) -> Union[bytes, str]:
        """
        Compress data using specified method
        
        Args:
            data: Data to compress
            method: Compression method ("json", "pickle", "gzip", "lzma")
            output_path: Optional path to save compressed data
            
        Returns:
            Compressed data as bytes or string
        """
        if method not in self.compression_methods:
            raise ValueError(f"Unsupported compression method: {method}")
        
        try:
            compressed_data = self.compression_methods[method](data)
            
            if output_path:
                self._save_compressed_data(compressed_data, output_path, method)
            
            logger.info(f"Data compressed using {method}")
            return compressed_data
        
        except Exception as e:
            logger.error(f"Compression failed with {method}: {e}")
            raise
    
    def decompress_data(self, compressed_data: Union[bytes, str], method: str = "json") -> Any:
        """
        Decompress data using specified method
        
        Args:
            compressed_data: Compressed data to decompress
            method: Compression method used
            
        Returns:
            Decompressed data
        """
        if method not in self.decompression_methods:
            raise ValueError(f"Unsupported decompression method: {method}")
        
        try:
            data = self.decompression_methods[method](compressed_data)
            logger.debug(f"Data decompressed using {method}")
            return data
        
        except Exception as e:
            logger.error(f"Decompression failed with {method}: {e}")
            raise
    
    def compress_file(self, input_path: Path, output_path: Path, method: str = "gzip") -> None:
        """
        Compress file using specified method
        
        Args:
            input_path: Path to input file
            output_path: Path to output compressed file
            method: Compression method
        """
        try:
            with open(input_path, 'rb') as f:
                data = f.read()
            
            compressed_data = self.compress_data(data, method)
            
            with open(output_path, 'wb') as f:
                if isinstance(compressed_data, str):
                    f.write(compressed_data.encode())
                else:
                    f.write(compressed_data)
            
            # Log compression ratio
            original_size = input_path.stat().st_size
            compressed_size = output_path.stat().st_size
            ratio = (1 - compressed_size / original_size) * 100
            
            logger.info(f"File compressed: {original_size} -> {compressed_size} bytes ({ratio:.1f}% reduction)")
        
        except Exception as e:
            logger.error(f"File compression failed: {e}")
            raise
    
    def decompress_file(self, input_path: Path, output_path: Path, method: str = "gzip") -> None:
        """
        Decompress file using specified method
        
        Args:
            input_path: Path to compressed file
            output_path: Path to output decompressed file
            method: Compression method used
        """
        try:
            with open(input_path, 'rb') as f:
                compressed_data = f.read()
            
            data = self.decompress_data(compressed_data, method)
            
            with open(output_path, 'wb') as f:
                if isinstance(data, str):
                    f.write(data.encode())
                else:
                    f.write(data)
            
            logger.info(f"File decompressed: {input_path} -> {output_path}")
        
        except Exception as e:
            logger.error(f"File decompression failed: {e}")
            raise
    
    def get_compression_ratio(self, original_data: Any, compressed_data: Union[bytes, str]) -> float:
        """
        Calculate compression ratio
        
        Args:
            original_data: Original uncompressed data
            compressed_data: Compressed data
            
        Returns:
            Compression ratio as percentage
        """
        try:
            if isinstance(original_data, str):
                original_size = len(original_data.encode())
            elif isinstance(original_data, bytes):
                original_size = len(original_data)
            else:
                original_size = len(str(original_data).encode())
            
            if isinstance(compressed_data, str):
                compressed_size = len(compressed_data.encode())
            else:
                compressed_size = len(compressed_data)
            
            if original_size == 0:
                return 0.0
            
            return (1 - compressed_size / original_size) * 100
        
        except Exception as e:
            logger.error(f"Failed to calculate compression ratio: {e}")
            return 0.0
    
    def _compress_json(self, data: Any) -> str:
        """Compress data using JSON with minimal formatting"""
        return json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    
    def _decompress_json(self, compressed_data: Union[bytes, str]) -> Any:
        """Decompress JSON data"""
        if isinstance(compressed_data, bytes):
            compressed_data = compressed_data.decode()
        return json.loads(compressed_data)
    
    def _compress_pickle(self, data: Any) -> bytes:
        """Compress data using pickle"""
        return pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
    
    def _decompress_pickle(self, compressed_data: bytes) -> Any:
        """Decompress pickle data"""
        return pickle.loads(compressed_data)
    
    def _compress_gzip(self, data: Any) -> bytes:
        """Compress data using gzip"""
        if isinstance(data, str):
            data = data.encode()
        elif not isinstance(data, bytes):
            data = str(data).encode()
        
        return gzip.compress(data)
    
    def _decompress_gzip(self, compressed_data: bytes) -> bytes:
        """Decompress gzip data"""
        return gzip.decompress(compressed_data)
    
    def _compress_lzma(self, data: Any) -> bytes:
        """Compress data using LZMA"""
        if isinstance(data, str):
            data = data.encode()
        elif not isinstance(data, bytes):
            data = str(data).encode()
        
        return lzma.compress(data)
    
    def _decompress_lzma(self, compressed_data: bytes) -> bytes:
        """Decompress LZMA data"""
        return lzma.decompress(compressed_data)
    
    def _save_compressed_data(self, compressed_data: Union[bytes, str], output_path: Path, method: str) -> None:
        """Save compressed data to file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        mode = 'wb' if isinstance(compressed_data, bytes) else 'w'
        encoding = None if isinstance(compressed_data, bytes) else 'utf-8'
        
        with open(output_path, mode, encoding=encoding) as f:
            f.write(compressed_data)


def optimize_package_data(data_dir: Path, output_dir: Path) -> Dict[str, Any]:
    """
    Optimize all package data for minimal size
    
    Args:
        data_dir: Directory containing original data
        output_dir: Directory for optimized data
        
    Returns:
        Optimization statistics
    """
    compressor = DataCompressor()
    stats = {
        "files_processed": 0,
        "original_size": 0,
        "compressed_size": 0,
        "compression_ratio": 0.0
    }
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process JSON files
    for json_file in data_dir.glob("**/*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Compress JSON with minimal formatting
            compressed_data = compressor.compress_data(data, method="json")
            
            # Save compressed version
            relative_path = json_file.relative_to(data_dir)
            output_path = output_dir / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(compressed_data)
            
            # Update statistics
            original_size = json_file.stat().st_size
            compressed_size = output_path.stat().st_size
            
            stats["files_processed"] += 1
            stats["original_size"] += original_size
            stats["compressed_size"] += compressed_size
            
            logger.info(f"Optimized {json_file.name}: {original_size} -> {compressed_size} bytes")
        
        except Exception as e:
            logger.error(f"Failed to optimize {json_file}: {e}")
    
    # Calculate overall compression ratio
    if stats["original_size"] > 0:
        stats["compression_ratio"] = (1 - stats["compressed_size"] / stats["original_size"]) * 100
    
    logger.info(f"Package data optimization complete:")
    logger.info(f"  Files processed: {stats['files_processed']}")
    logger.info(f"  Original size: {stats['original_size']} bytes")
    logger.info(f"  Compressed size: {stats['compressed_size']} bytes")
    logger.info(f"  Compression ratio: {stats['compression_ratio']:.1f}%")
    
    return stats