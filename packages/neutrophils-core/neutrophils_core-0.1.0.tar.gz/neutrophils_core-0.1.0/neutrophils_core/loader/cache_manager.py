#!/usr/bin/env python3
"""
Intelligent caching system for ImageDataGenerator2D
Implements LRU cache with memory limits and smart prefetching.
"""

import os
import time
import threading
import weakref
from collections import OrderedDict
from typing import Optional, Tuple, Any, Dict
import numpy as np
import psutil
import SimpleITK as sitk
from concurrent.futures import ThreadPoolExecutor, Future
import logging

class ImageCache:
    """Thread-safe LRU cache for images with memory management"""
    
    def __init__(self, max_memory_mb: int = 1024, max_items: int = 1000):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_items = max_items
        
        self._cache: OrderedDict[str, Dict] = OrderedDict()
        self._memory_usage = 0
        self._lock = threading.RLock()
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'memory_pressure_evictions': 0
        }
        
        # Prefetch thread pool
        self._prefetch_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="ImageCache-Prefetch")
        self._prefetch_futures: Dict[str, Future] = {}
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Optional[np.ndarray]:
        """Get image from cache, returns None if not found"""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                entry = self._cache.pop(key)
                self._cache[key] = entry
                self._stats['hits'] += 1
                entry['access_time'] = time.time()
                entry['access_count'] += 1
                return entry['data'].copy()  # Return copy to prevent modification
            else:
                self._stats['misses'] += 1
                return None
    
    def put(self, key: str, data: np.ndarray, metadata: Optional[Dict] = None) -> None:
        """Store image in cache"""
        data_size = data.nbytes
        
        with self._lock:
            # Check if we need to make space
            while (self._memory_usage + data_size > self.max_memory_bytes or 
                   len(self._cache) >= self.max_items) and self._cache:
                self._evict_lru()
            
            # Add new entry
            entry = {
                'data': data.copy(),
                'size': data_size,
                'access_time': time.time(),
                'access_count': 1,
                'metadata': metadata or {}
            }
            
            self._cache[key] = entry
            self._memory_usage += data_size
    
    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self._cache:
            return
        
        key, entry = self._cache.popitem(last=False)  # Remove oldest
        self._memory_usage -= entry['size']
        self._stats['evictions'] += 1
        
        # Check if this was due to memory pressure
        if self._memory_usage > self.max_memory_bytes * 0.8:
            self._stats['memory_pressure_evictions'] += 1
    
    def prefetch(self, key: str, image_path: str, load_func) -> None:
        """Prefetch image asynchronously"""
        if key in self._cache or key in self._prefetch_futures:
            return
        
        future = self._prefetch_executor.submit(self._prefetch_worker, key, image_path, load_func)
        self._prefetch_futures[key] = future
    
    def _prefetch_worker(self, key: str, image_path: str, load_func) -> None:
        """Worker function for prefetching"""
        try:
            data = load_func(image_path)
            self.put(key, data, {'prefetched': True})
            self.logger.debug(f"Prefetched: {key}")
        except Exception as e:
            self.logger.warning(f"Failed to prefetch {key}: {e}")
        finally:
            # Clean up future reference
            with self._lock:
                self._prefetch_futures.pop(key, None)
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self._lock:
            hit_rate = self._stats['hits'] / (self._stats['hits'] + self._stats['misses']) if (self._stats['hits'] + self._stats['misses']) > 0 else 0
            return {
                **self._stats,
                'hit_rate': hit_rate,
                'current_items': len(self._cache),
                'memory_usage_mb': self._memory_usage / 1024 / 1024,
                'memory_usage_percent': (self._memory_usage / self.max_memory_bytes) * 100
            }
    
    def clear(self) -> None:
        """Clear all cached items"""
        with self._lock:
            self._cache.clear()
            self._memory_usage = 0
            
            # Cancel pending prefetch operations
            for future in self._prefetch_futures.values():
                future.cancel()
            self._prefetch_futures.clear()
    
    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, '_prefetch_executor'):
            self._prefetch_executor.shutdown(wait=False)

class SmartImageLoader:
    """Smart image loader with caching and prefetching capabilities"""
    
    def __init__(self, cache_size_mb: int = 1024, enable_prefetch: bool = True):
        self.cache = ImageCache(max_memory_mb=cache_size_mb)
        self.enable_prefetch = enable_prefetch
        self.logger = logging.getLogger(__name__)
        
        # Load function cache for different file types
        self._load_functions = {
            '.nrrd': self._load_with_sitk,
            '.nii': self._load_with_sitk,
            '.nii.gz': self._load_with_sitk,
            '.mha': self._load_with_sitk,
            '.mhd': self._load_with_sitk,
        }
    
    def _load_with_sitk(self, image_path: str) -> np.ndarray:
        """Load image using SimpleITK"""
        img_sitk = sitk.ReadImage(image_path)
        return sitk.GetArrayFromImage(img_sitk)
    
    def _get_load_function(self, image_path: str):
        """Get appropriate load function based on file extension"""
        ext = ''.join(os.path.splitext(image_path)[-2:]).lower()
        return self._load_functions.get(ext, self._load_with_sitk)
    
    def load_image(self, image_path: str, cache_key: Optional[str] = None) -> np.ndarray:
        """Load image with caching"""
        if cache_key is None:
            cache_key = image_path
        
        # Try cache first
        cached_data = self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Load from disk
        load_func = self._get_load_function(image_path)
        data = load_func(image_path)
        
        # Store in cache
        self.cache.put(cache_key, data)
        
        return data
    
    def prefetch_batch(self, image_paths: list, cache_keys: Optional[list] = None) -> None:
        """Prefetch a batch of images"""
        if not self.enable_prefetch:
            return
        
        if cache_keys is None:
            cache_keys = image_paths
        
        for image_path, cache_key in zip(image_paths, cache_keys):
            load_func = self._get_load_function(image_path)
            self.cache.prefetch(cache_key, image_path, load_func)
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache.get_stats()
    
    def clear_cache(self) -> None:
        """Clear cache"""
        self.cache.clear()

class AdaptiveCacheManager:
    """Adaptive cache manager that adjusts cache size based on system resources"""
    
    def __init__(self, target_memory_percent: float = 0.3, min_cache_mb: int = 256, max_cache_mb: int = 4096):
        self.target_memory_percent = target_memory_percent
        self.min_cache_mb = min_cache_mb
        self.max_cache_mb = max_cache_mb
        
        self.loader = None
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        
        self._calculate_optimal_cache_size()
    
    def _calculate_optimal_cache_size(self) -> int:
        """Calculate optimal cache size based on available memory"""
        total_memory = psutil.virtual_memory().total
        target_cache_bytes = total_memory * self.target_memory_percent
        target_cache_mb = int(target_cache_bytes / 1024 / 1024)
        
        # Clamp to min/max bounds
        optimal_cache_mb = max(self.min_cache_mb, min(target_cache_mb, self.max_cache_mb))
        
        return optimal_cache_mb
    
    def get_loader(self) -> SmartImageLoader:
        """Get image loader with adaptive cache sizing"""
        if self.loader is None:
            cache_size = self._calculate_optimal_cache_size()
            self.loader = SmartImageLoader(cache_size_mb=cache_size)
            
            # Start monitoring thread
            self._start_monitoring()
        
        return self.loader
    
    def _start_monitoring(self) -> None:
        """Start memory monitoring thread"""
        if self._monitoring_thread is None or not self._monitoring_thread.is_alive():
            self._monitoring_thread = threading.Thread(
                target=self._monitor_memory,
                daemon=True,
                name="AdaptiveCacheMonitor"
            )
            self._monitoring_thread.start()
    
    def _monitor_memory(self) -> None:
        """Monitor memory usage and adjust cache if needed"""
        while not self._stop_monitoring.wait(30):  # Check every 30 seconds
            try:
                memory = psutil.virtual_memory()
                
                # If memory usage is high, consider reducing cache
                if memory.percent > 85:  # System memory usage > 85%
                    stats = self.loader.get_cache_stats()
                    if stats['memory_usage_mb'] > 100:  # Cache using > 100MB
                        # Clear some cache to free memory
                        current_items = stats['current_items']
                        items_to_clear = max(1, current_items // 4)  # Clear 25%
                        
                        # This is a simple implementation - could be more sophisticated
                        self.loader.clear_cache()
                        
                        logging.info(f"Cleared cache due to high memory usage: {memory.percent}%")
                
            except Exception as e:
                logging.warning(f"Error in memory monitoring: {e}")
    
    def stop_monitoring(self) -> None:
        """Stop memory monitoring"""
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=1)
    
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_monitoring()

# Global cache manager instance
_cache_manager = None

def get_global_cache_manager() -> AdaptiveCacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = AdaptiveCacheManager()
    return _cache_manager