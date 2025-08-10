"""
Multi-level caching system for GRASS RAG pipeline
Provides L1 (preloaded) and L2 (dynamic LRU) cache levels
"""

import time
import hashlib
import json
from typing import Dict, List, Any, Optional
from collections import OrderedDict
from loguru import logger


class MultiLevelCache:
    """
    Multi-level caching system for optimized response times
    
    L1 Cache: Preloaded common queries (instant response)
    L2 Cache: Dynamic LRU cache with TTL support
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize multi-level cache
        
        Args:
            max_size: Maximum number of items in L2 cache
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        
        # L1 Cache: Preloaded common queries
        self.l1_cache: Dict[str, Dict[str, Any]] = {}
        
        # L2 Cache: Dynamic LRU cache with TTL
        self.l2_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        
        # Statistics
        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "total_requests": 0,
            "evictions": 0
        }
        
        # Initialize with preloaded queries
        self._preload_common_queries()
        
        logger.info(f"MultiLevelCache initialized: L1={len(self.l1_cache)}, L2_max={max_size}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache (checks L1 then L2)
        
        Args:
            key: Cache key (usually the query string)
            
        Returns:
            Cached value or None if not found
        """
        self.stats["total_requests"] += 1
        cache_key = self._generate_key(key)
        
        # Check L1 cache first (preloaded queries)
        if cache_key in self.l1_cache:
            self.stats["l1_hits"] += 1
            logger.debug(f"L1 cache hit: {key[:30]}...")
            return self.l1_cache[cache_key]["value"]
        
        # Check L2 cache (dynamic cache)
        if cache_key in self.l2_cache:
            item = self.l2_cache[cache_key]
            
            # Check TTL
            if self._is_expired(item):
                del self.l2_cache[cache_key]
                self.stats["misses"] += 1
                return None
            
            # Move to end (LRU)
            self.l2_cache.move_to_end(cache_key)
            self.stats["l2_hits"] += 1
            logger.debug(f"L2 cache hit: {key[:30]}...")
            return item["value"]
        
        # Cache miss
        self.stats["misses"] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set item in L2 cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        cache_key = self._generate_key(key)
        
        # Don't cache if already in L1
        if cache_key in self.l1_cache:
            return
        
        if ttl is None:
            ttl = self.default_ttl
        
        # Create cache item
        cache_item = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl
        }
        
        # Add to L2 cache
        self.l2_cache[cache_key] = cache_item
        
        # Enforce size limit
        while len(self.l2_cache) > self.max_size:
            oldest_key = next(iter(self.l2_cache))
            del self.l2_cache[oldest_key]
            self.stats["evictions"] += 1
        
        logger.debug(f"Cached: {key[:30]}... (TTL: {ttl}s)")
    
    def clear(self, level: Optional[str] = None) -> None:
        """
        Clear cache
        
        Args:
            level: Cache level to clear ("l1", "l2", or None for both)
        """
        if level is None or level == "l1":
            # Don't clear L1 as it contains preloaded queries
            pass
        
        if level is None or level == "l2":
            self.l2_cache.clear()
            logger.info("L2 cache cleared")
        
        if level is None:
            logger.info("All caches cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_hits = self.stats["l1_hits"] + self.stats["l2_hits"]
        hit_rate = (total_hits / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0
        
        return {
            "l1_size": len(self.l1_cache),
            "l2_size": len(self.l2_cache),
            "l2_max_size": self.max_size,
            "l1_hits": self.stats["l1_hits"],
            "l2_hits": self.stats["l2_hits"],
            "total_hits": total_hits,
            "misses": self.stats["misses"],
            "total_requests": self.stats["total_requests"],
            "hit_rate": hit_rate,
            "l1_hit_rate": (self.stats["l1_hits"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0,
            "l2_hit_rate": (self.stats["l2_hits"] / self.stats["total_requests"] * 100) if self.stats["total_requests"] > 0 else 0,
            "evictions": self.stats["evictions"]
        }
    
    def cleanup_expired(self) -> int:
        """
        Remove expired items from L2 cache
        
        Returns:
            Number of items removed
        """
        expired_keys = []
        
        for key, item in self.l2_cache.items():
            if self._is_expired(item):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.l2_cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache items")
        
        return len(expired_keys)
    
    def _preload_common_queries(self) -> None:
        """Pre-populate L1 cache with most common GRASS GIS queries"""
        common_queries = {
            "calculate slope": {
                "value": {
                    "answer": "Use r.slope.aspect command to calculate slope from DEM",
                    "sources": [{"type": "preloaded", "category": "terrain"}],
                    "quality_score": 0.95
                }
            },
            "import raster": {
                "value": {
                    "answer": "Use r.import command to import raster data",
                    "sources": [{"type": "preloaded", "category": "data_import"}],
                    "quality_score": 0.92
                }
            },
            "export data": {
                "value": {
                    "answer": "Use r.out.gdal for raster or v.out.ogr for vector export",
                    "sources": [{"type": "preloaded", "category": "data_export"}],
                    "quality_score": 0.93
                }
            },
            "create buffer": {
                "value": {
                    "answer": "Use v.buffer command to create buffer zones around features",
                    "sources": [{"type": "preloaded", "category": "vector_analysis"}],
                    "quality_score": 0.90
                }
            },
            "watershed analysis": {
                "value": {
                    "answer": "Use r.watershed command for hydrological analysis",
                    "sources": [{"type": "preloaded", "category": "hydrology"}],
                    "quality_score": 0.96
                }
            },
            "contour lines": {
                "value": {
                    "answer": "Use r.contour command to generate contour lines from elevation",
                    "sources": [{"type": "preloaded", "category": "terrain"}],
                    "quality_score": 0.94
                }
            },
            "vector overlay": {
                "value": {
                    "answer": "Use v.overlay command for spatial overlay operations",
                    "sources": [{"type": "preloaded", "category": "vector_analysis"}],
                    "quality_score": 0.91
                }
            },
            "raster calculator": {
                "value": {
                    "answer": "Use r.mapcalc command for raster algebra and calculations",
                    "sources": [{"type": "preloaded", "category": "raster_analysis"}],
                    "quality_score": 0.93
                }
            },
            "interpolation": {
                "value": {
                    "answer": "Use v.surf.idw or v.surf.rst for surface interpolation",
                    "sources": [{"type": "preloaded", "category": "interpolation"}],
                    "quality_score": 0.92
                }
            },
            "classify raster": {
                "value": {
                    "answer": "Use r.reclass command to reclassify raster values",
                    "sources": [{"type": "preloaded", "category": "raster_analysis"}],
                    "quality_score": 0.91
                }
            }
        }
        
        for query, data in common_queries.items():
            cache_key = self._generate_key(query)
            self.l1_cache[cache_key] = data
        
        logger.info(f"Preloaded {len(common_queries)} common queries into L1 cache")
    
    def _generate_key(self, key: str) -> str:
        """Generate consistent cache key from input"""
        # Normalize the key
        normalized = key.lower().strip()
        
        # Generate hash for consistent key
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _is_expired(self, item: Dict[str, Any]) -> bool:
        """Check if cache item has expired"""
        if "timestamp" not in item or "ttl" not in item:
            return True
        
        age = time.time() - item["timestamp"]
        return age > item["ttl"]
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information for debugging"""
        l2_items = []
        current_time = time.time()
        
        for key, item in list(self.l2_cache.items()):
            age = current_time - item.get("timestamp", 0)
            ttl = item.get("ttl", 0)
            
            l2_items.append({
                "key_hash": key,
                "age_seconds": age,
                "ttl_seconds": ttl,
                "expired": self._is_expired(item)
            })
        
        return {
            "l1_cache": {
                "size": len(self.l1_cache),
                "keys": list(self.l1_cache.keys())[:10]  # First 10 keys for debugging
            },
            "l2_cache": {
                "size": len(self.l2_cache),
                "max_size": self.max_size,
                "items": l2_items[:10]  # First 10 items for debugging
            },
            "statistics": self.get_stats()
        }