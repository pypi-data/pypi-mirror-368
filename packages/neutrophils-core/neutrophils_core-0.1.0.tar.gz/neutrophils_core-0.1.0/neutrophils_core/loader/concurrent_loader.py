#!/usr/bin/env python3
"""
Concurrent image loading utilities for improved I/O performance
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from typing import List, Tuple, Optional, Dict, Any, Callable
import numpy as np
import queue
import os
from dataclasses import dataclass
import logging

@dataclass
class LoadTask:
    """Represents an image loading task"""
    index: int
    image_path: str
    cache_key: Optional[str] = None
    metadata: Optional[Dict] = None
    priority: int = 0  # Lower numbers = higher priority

class ConcurrentImageLoader:
    """Concurrent image loader with thread pool management"""
    
    def __init__(self, max_workers: int = 4, queue_size: int = 32):
        self.max_workers = max_workers
        self.queue_size = queue_size
        
        # Thread pool for I/O operations
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="ImageLoader"
        )
        
        # Task queue with priority support
        self._task_queue = queue.PriorityQueue(maxsize=queue_size)
        self._results = {}
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'tasks_submitted': 0,
            'tasks_completed': 0,
            'total_load_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        self.logger = logging.getLogger(__name__)
    
    def load_batch_concurrent(self, 
                            image_paths: List[str], 
                            load_func: Callable[[str], np.ndarray],
                            cache_loader: Optional[Any] = None) -> List[np.ndarray]:
        """Load a batch of images concurrently"""
        
        start_time = time.time()
        
        # Create loading tasks
        tasks = []
        cached_results = {}
        
        for i, path in enumerate(image_paths):
            # Check cache first if available
            if cache_loader:
                cached_data = cache_loader.cache.get(path)
                if cached_data is not None:
                    cached_results[i] = cached_data
                    self._stats['cache_hits'] += 1
                    continue
            
            # Submit loading task
            future = self._executor.submit(self._load_single_image, i, path, load_func)
            tasks.append((i, future))
            self._stats['tasks_submitted'] += 1
            self._stats['cache_misses'] += 1
        
        # Collect results
        results = [None] * len(image_paths)
        
        # Add cached results
        for idx, data in cached_results.items():
            results[idx] = data
        
        # Collect concurrent loading results
        for idx, future in tasks:
            try:
                results[idx] = future.result(timeout=30)  # 30 second timeout
                self._stats['tasks_completed'] += 1
            except Exception as e:
                self.logger.error(f"Failed to load image at index {idx}: {e}")
                # Create a zero array as fallback
                results[idx] = np.zeros((96, 96, 1), dtype=np.float32)
        
        end_time = time.time()
        self._stats['total_load_time'] += (end_time - start_time)
        
        return results
    
    def _load_single_image(self, index: int, image_path: str, load_func: Callable) -> np.ndarray:
        """Load a single image (called by worker threads)"""
        try:
            return load_func(image_path)
        except Exception as e:
            self.logger.warning(f"Error loading {image_path}: {e}")
            # Return a default array on error
            return np.zeros((96, 96, 1), dtype=np.float32)
    
    def prefetch_batch(self, 
                      image_paths: List[str], 
                      load_func: Callable[[str], np.ndarray],
                      cache_loader: Optional[Any] = None) -> Dict[int, Future]:
        """Prefetch a batch of images asynchronously"""
        
        futures = {}
        
        for i, path in enumerate(image_paths):
            # Skip if already in cache
            if cache_loader and cache_loader.cache.get(path) is not None:
                continue
            
            # Submit prefetch task
            future = self._executor.submit(self._prefetch_single_image, path, load_func, cache_loader)
            futures[i] = future
        
        return futures
    
    def _prefetch_single_image(self, 
                              image_path: str, 
                              load_func: Callable,
                              cache_loader: Optional[Any] = None) -> bool:
        """Prefetch a single image"""
        try:
            data = load_func(image_path)
            
            # Store in cache if available
            if cache_loader:
                cache_loader.cache.put(image_path, data, {'prefetched': True})
            
            return True
        except Exception as e:
            self.logger.warning(f"Failed to prefetch {image_path}: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get loading statistics"""
        with self._lock:
            avg_load_time = (self._stats['total_load_time'] / max(1, self._stats['tasks_completed']))
            cache_hit_rate = (self._stats['cache_hits'] / 
                             max(1, self._stats['cache_hits'] + self._stats['cache_misses']))
            
            return {
                **self._stats,
                'avg_load_time_per_task': avg_load_time,
                'cache_hit_rate': cache_hit_rate,
                'pending_tasks': self._task_queue.qsize()
            }
    
    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the thread pool"""
        self._executor.shutdown(wait=wait)
    
    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)

class BatchProcessor:
    """Optimized batch processing with memory pooling and concurrent operations"""
    
    def __init__(self, 
                 batch_size: int,
                 image_size: Tuple[int, int] = (96, 96),
                 num_channels: int = 1,
                 max_workers: int = 4,
                 enable_memory_pool: bool = True):
        
        self.batch_size = batch_size
        self.image_size = image_size
        self.num_channels = num_channels
        self.max_workers = max_workers
        self.enable_memory_pool = enable_memory_pool
        
        # Concurrent loader
        self.loader = ConcurrentImageLoader(max_workers=max_workers)
        
        # Memory pool for batch arrays
        self._memory_pool = queue.Queue() if enable_memory_pool else None
        self._pool_size = 3  # Keep 3 arrays in pool
        
        # Pre-allocate arrays for memory pool
        if self.enable_memory_pool:
            for _ in range(self._pool_size):
                array = np.empty((batch_size, *image_size, num_channels), dtype=np.float32)
                self._memory_pool.put(array)
        
        self.logger = logging.getLogger(__name__)
    
    def get_batch_array(self) -> np.ndarray:
        """Get a batch array from memory pool or allocate new one"""
        if self.enable_memory_pool and not self._memory_pool.empty():
            try:
                return self._memory_pool.get_nowait()
            except queue.Empty:
                pass
        
        # Allocate new array if pool is empty
        return np.empty((self.batch_size, *self.image_size, self.num_channels), dtype=np.float32)
    
    def return_batch_array(self, array: np.ndarray) -> None:
        """Return batch array to memory pool"""
        if self.enable_memory_pool and self._memory_pool.qsize() < self._pool_size:
            try:
                self._memory_pool.put_nowait(array)
            except queue.Full:
                pass  # Pool is full, let array be garbage collected
    
    def process_batch_concurrent(self,
                                image_paths: List[str],
                                load_func: Callable[[str], np.ndarray],
                                process_func: Optional[Callable[[np.ndarray], np.ndarray]] = None,
                                cache_loader: Optional[Any] = None) -> np.ndarray:
        """Process a batch of images concurrently"""
        
        # Get batch array from pool
        batch_array = self.get_batch_array()
        
        try:
            # Load images concurrently
            loaded_images = self.loader.load_batch_concurrent(
                image_paths, load_func, cache_loader
            )
            
            # Process images and fill batch array
            for i, img in enumerate(loaded_images):
                if i >= self.batch_size:
                    break
                
                # Apply additional processing if specified
                if process_func:
                    img = process_func(img)
                
                # Ensure correct shape
                if img.shape[-1] != self.num_channels:
                    if self.num_channels == 1 and img.ndim == 3:
                        img = img[..., :1]
                    elif self.num_channels > 1 and img.ndim == 2:
                        img = np.expand_dims(img, axis=-1)
                        img = np.repeat(img, self.num_channels, axis=-1)
                
                # Resize if needed
                if img.shape[:2] != self.image_size:
                    # Simple resize - in practice you might want to use a better method
                    from skimage.transform import resize
                    img = resize(img, (*self.image_size, self.num_channels), 
                               anti_aliasing=True, preserve_range=True)
                
                batch_array[i] = img
            
            return batch_array.copy()  # Return copy to allow array reuse
            
        finally:
            # Return array to pool
            self.return_batch_array(batch_array)
    
    def get_stats(self) -> Dict:
        """Get processing statistics"""
        loader_stats = self.loader.get_stats()
        pool_stats = {
            'memory_pool_enabled': self.enable_memory_pool,
            'pool_size': self._memory_pool.qsize() if self.enable_memory_pool else 0,
            'max_pool_size': self._pool_size if self.enable_memory_pool else 0
        }
        
        return {**loader_stats, **pool_stats}
    
    def shutdown(self) -> None:
        """Shutdown the processor"""
        self.loader.shutdown()
    
    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, 'loader'):
            self.loader.shutdown()

# Async utilities for advanced use cases
class AsyncImageProcessor:
    """Async image processor for maximum concurrency"""
    
    def __init__(self, max_concurrent: int = 8):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def load_image_async(self, 
                              image_path: str,
                              load_func: Callable[[str], np.ndarray],
                              loop: Optional[asyncio.AbstractEventLoop] = None) -> np.ndarray:
        """Load image asynchronously"""
        if loop is None:
            loop = asyncio.get_event_loop()
        
        async with self._semaphore:
            # Run in thread pool to avoid blocking
            return await loop.run_in_executor(None, load_func, image_path)
    
    async def load_batch_async(self,
                              image_paths: List[str],
                              load_func: Callable[[str], np.ndarray]) -> List[np.ndarray]:
        """Load batch of images asynchronously"""
        tasks = [
            self.load_image_async(path, load_func)
            for path in image_paths
        ]
        
        return await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    # Example usage and testing
    import SimpleITK as sitk
    
    def dummy_load_func(path: str) -> np.ndarray:
        """Dummy load function for testing"""
        return np.random.random((96, 96, 1)).astype(np.float32)
    
    # Test concurrent loader
    loader = ConcurrentImageLoader(max_workers=4)
    
    test_paths = [f"test_{i}.nrrd" for i in range(10)]
    results = loader.load_batch_concurrent(test_paths, dummy_load_func)
    
    print(f"Loaded {len(results)} images")
    print("Loader stats:", loader.get_stats())
    
    # Test batch processor
    processor = BatchProcessor(batch_size=8, max_workers=4)
    
    batch_result = processor.process_batch_concurrent(
        test_paths[:8], dummy_load_func
    )
    
    print(f"Batch shape: {batch_result.shape}")
    print("Processor stats:", processor.get_stats())
    
    # Cleanup
    loader.shutdown()
    processor.shutdown()
    
    print("All tests passed!")