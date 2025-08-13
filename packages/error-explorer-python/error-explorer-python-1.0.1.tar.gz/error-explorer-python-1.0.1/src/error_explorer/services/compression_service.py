"""Compression service for Error Explorer Python SDK."""

import base64
import gzip
import json
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from ..types import ErrorData


@dataclass
class CompressionConfig:
    """Configuration for compression service."""
    threshold: int = 1024  # Compress if payload is larger than 1KB
    level: int = 6  # Compression level (1-9)


@dataclass
class CompressionStats:
    """Statistics for compression operations."""
    total_compressions: int = 0
    total_decompressions: int = 0
    total_bytes_saved: int = 0
    average_compression_ratio: float = 0.0
    compression_time: float = 0.0  # Total time spent compressing in seconds


class CompressionService:
    """
    Compression service for reducing payload sizes.
    
    Features:
    - Gzip compression with configurable compression levels
    - Base64 encoding for safe transport
    - Automatic compression threshold
    - Compression statistics and monitoring
    - Support for single errors and batches
    """
    
    def __init__(self, config: Optional[CompressionConfig] = None):
        """Initialize compression service.
        
        Args:
            config: Compression configuration
        """
        self.config = config or CompressionConfig()
        self._stats = CompressionStats()
    
    def configure(self, config: CompressionConfig) -> None:
        """Update compression configuration.
        
        Args:
            config: New compression configuration
        """
        self.config = config
    
    def is_supported(self) -> bool:
        """Check if compression is supported.
        
        Returns:
            Always True for Python (gzip is built-in)
        """
        return True
    
    def should_compress(self, data: Union[ErrorData, List[ErrorData], Dict[str, Any], str]) -> bool:
        """Check if data should be compressed based on size threshold.
        
        Args:
            data: Data to check for compression
            
        Returns:
            True if data should be compressed
        """
        try:
            if isinstance(data, str):
                size = len(data.encode('utf-8'))
            else:
                # Convert to JSON string to measure size
                if hasattr(data, '__dict__'):
                    json_str = json.dumps(data.__dict__, default=str)
                elif isinstance(data, list):
                    json_data = []
                    for item in data:
                        if hasattr(item, '__dict__'):
                            json_data.append(item.__dict__)
                        else:
                            json_data.append(item)
                    json_str = json.dumps(json_data, default=str)
                else:
                    json_str = json.dumps(data, default=str)
                
                size = len(json_str.encode('utf-8'))
            
            return size >= self.config.threshold
        except Exception:
            return False
    
    def compress(self, data: Union[ErrorData, List[ErrorData], Dict[str, Any], str]) -> str:
        """Compress data using gzip and encode as base64.
        
        Args:
            data: Data to compress
            
        Returns:
            Base64-encoded compressed data
            
        Raises:
            Exception: If compression fails
        """
        start_time = time.time()
        
        try:
            # Convert data to JSON string if needed
            if isinstance(data, str):
                json_str = data
            else:
                if hasattr(data, '__dict__'):
                    json_str = json.dumps(data.__dict__, default=str)
                elif isinstance(data, list):
                    json_data = []
                    for item in data:
                        if hasattr(item, '__dict__'):
                            json_data.append(item.__dict__)
                        else:
                            json_data.append(item)
                    json_str = json.dumps(json_data, default=str)
                else:
                    json_str = json.dumps(data, default=str)
            
            # Get original size
            original_bytes = json_str.encode('utf-8')
            original_size = len(original_bytes)
            
            # Compress using gzip
            compressed_bytes = gzip.compress(original_bytes, compresslevel=self.config.level)
            compressed_size = len(compressed_bytes)
            
            # Encode as base64 for safe transport
            compressed_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
            
            # Update statistics
            compression_time = time.time() - start_time
            self._update_compression_stats(original_size, compressed_size, compression_time)
            
            return compressed_base64
            
        except Exception as e:
            raise Exception(f"Compression failed: {str(e)}")
    
    def decompress(self, compressed_data: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Decompress base64-encoded gzip data.
        
        Args:
            compressed_data: Base64-encoded compressed data
            
        Returns:
            Decompressed data
            
        Raises:
            Exception: If decompression fails
        """
        start_time = time.time()
        
        try:
            # Decode from base64
            compressed_bytes = base64.b64decode(compressed_data.encode('utf-8'))
            
            # Decompress using gzip
            decompressed_bytes = gzip.decompress(compressed_bytes)
            decompressed_str = decompressed_bytes.decode('utf-8')
            
            # Parse JSON
            decompressed_data = json.loads(decompressed_str)
            
            # Update statistics
            decompression_time = time.time() - start_time
            self._stats.total_decompressions += 1
            self._stats.compression_time += decompression_time
            
            return decompressed_data
            
        except Exception as e:
            raise Exception(f"Decompression failed: {str(e)}")
    
    def compress_string(self, data: str) -> str:
        """Simple string compression for compatibility.
        
        Args:
            data: String data to compress
            
        Returns:
            Compressed string representation
        """
        # For Python, we can use the same gzip compression
        return self.compress(data)
    
    def get_stats(self) -> CompressionStats:
        """Get compression statistics.
        
        Returns:
            Current compression statistics
        """
        return CompressionStats(
            total_compressions=self._stats.total_compressions,
            total_decompressions=self._stats.total_decompressions,
            total_bytes_saved=self._stats.total_bytes_saved,
            average_compression_ratio=self._stats.average_compression_ratio,
            compression_time=self._stats.compression_time
        )
    
    def reset_stats(self) -> None:
        """Reset compression statistics."""
        self._stats = CompressionStats()
    
    def _update_compression_stats(self, original_size: int, compressed_size: int, compression_time: float) -> None:
        """Update compression statistics.
        
        Args:
            original_size: Original data size in bytes
            compressed_size: Compressed data size in bytes
            compression_time: Time taken for compression
        """
        self._stats.total_compressions += 1
        self._stats.total_bytes_saved += max(0, original_size - compressed_size)
        self._stats.compression_time += compression_time
        
        # Update average compression ratio
        ratio = compressed_size / original_size if original_size > 0 else 1.0
        total_compressions = self._stats.total_compressions
        
        if total_compressions == 1:
            self._stats.average_compression_ratio = ratio
        else:
            current_avg = self._stats.average_compression_ratio
            self._stats.average_compression_ratio = ((current_avg * (total_compressions - 1)) + ratio) / total_compressions
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def get_compression_ratio(self, original_size: int, compressed_size: int) -> float:
        """Calculate compression ratio.
        
        Args:
            original_size: Original data size
            compressed_size: Compressed data size
            
        Returns:
            Compression ratio (compressed/original)
        """
        return compressed_size / original_size if original_size > 0 else 1.0
    
    def estimate_savings(self, data: Union[ErrorData, List[ErrorData], str]) -> Dict[str, Any]:
        """Estimate compression savings without actually compressing.
        
        Args:
            data: Data to analyze
            
        Returns:
            Dictionary with size estimates and potential savings
        """
        try:
            # Get original size
            if isinstance(data, str):
                original_size = len(data.encode('utf-8'))
            else:
                if hasattr(data, '__dict__'):
                    json_str = json.dumps(data.__dict__, default=str)
                elif isinstance(data, list):
                    json_data = []
                    for item in data:
                        if hasattr(item, '__dict__'):
                            json_data.append(item.__dict__)
                        else:
                            json_data.append(item)
                    json_str = json.dumps(json_data, default=str)
                else:
                    json_str = json.dumps(data, default=str)
                
                original_size = len(json_str.encode('utf-8'))
            
            # Rough estimation: gzip typically achieves 60-80% compression on JSON
            estimated_compressed_size = int(original_size * 0.7)  # Assume 30% savings
            estimated_savings = original_size - estimated_compressed_size
            
            return {
                "original_size": original_size,
                "estimated_compressed_size": estimated_compressed_size,
                "estimated_savings": estimated_savings,
                "estimated_ratio": self.get_compression_ratio(original_size, estimated_compressed_size),
                "should_compress": original_size >= self.config.threshold
            }
            
        except Exception:
            return {
                "original_size": 0,
                "estimated_compressed_size": 0,
                "estimated_savings": 0,
                "estimated_ratio": 1.0,
                "should_compress": False
            }