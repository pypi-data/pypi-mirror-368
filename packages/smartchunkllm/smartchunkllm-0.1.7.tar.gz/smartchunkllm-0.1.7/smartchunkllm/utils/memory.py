"""Memory monitoring and management utilities for SmartChunkLLM."""

import os
import gc
import sys
import psutil
import threading
import time
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
from collections import defaultdict, deque
import tracemalloc
import weakref

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from .logging import get_logger


@dataclass
class MemorySnapshot:
    """Memory usage snapshot."""
    timestamp: datetime
    process_memory_mb: float
    system_memory_percent: float
    available_memory_mb: float
    virtual_memory_mb: float
    resident_memory_mb: float
    shared_memory_mb: float = 0.0
    gpu_memory_mb: float = 0.0
    gpu_memory_percent: float = 0.0
    python_objects: int = 0
    gc_collections: Dict[int, int] = field(default_factory=dict)
    top_objects: List[Tuple[str, int]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'timestamp': self.timestamp.isoformat(),
            'process_memory_mb': self.process_memory_mb,
            'system_memory_percent': self.system_memory_percent,
            'available_memory_mb': self.available_memory_mb,
            'virtual_memory_mb': self.virtual_memory_mb,
            'resident_memory_mb': self.resident_memory_mb,
            'shared_memory_mb': self.shared_memory_mb,
            'gpu_memory_mb': self.gpu_memory_mb,
            'gpu_memory_percent': self.gpu_memory_percent,
            'python_objects': self.python_objects,
            'gc_collections': self.gc_collections,
            'top_objects': self.top_objects
        }


@dataclass
class MemoryAlert:
    """Memory usage alert."""
    timestamp: datetime
    alert_type: str
    message: str
    memory_mb: float
    threshold_mb: float
    severity: str = 'warning'  # info, warning, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'timestamp': self.timestamp.isoformat(),
            'alert_type': self.alert_type,
            'message': self.message,
            'memory_mb': self.memory_mb,
            'threshold_mb': self.threshold_mb,
            'severity': self.severity
        }


class MemoryMonitor:
    """Memory usage monitor."""
    
    def __init__(self, 
                 warning_threshold_mb: float = 1024,  # 1GB
                 critical_threshold_mb: float = 2048,  # 2GB
                 monitoring_interval: float = 5.0,  # seconds
                 max_snapshots: int = 1000,
                 enable_tracemalloc: bool = False):
        self.warning_threshold_mb = warning_threshold_mb
        self.critical_threshold_mb = critical_threshold_mb
        self.monitoring_interval = monitoring_interval
        self.max_snapshots = max_snapshots
        self.enable_tracemalloc = enable_tracemalloc
        
        self.logger = get_logger('memory_monitor')
        self.process = psutil.Process()
        self.snapshots = deque(maxlen=max_snapshots)
        self.alerts = deque(maxlen=100)
        self.callbacks = []
        
        self._monitoring = False
        self._monitor_thread = None
        self._lock = threading.Lock()
        
        # GPU monitoring
        self._gpu_available = self._check_gpu_availability()
        
        # Tracemalloc setup
        if self.enable_tracemalloc and not tracemalloc.is_tracing():
            tracemalloc.start()
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU monitoring is available.
        
        Returns:
            True if GPU monitoring is available
        """
        if TORCH_AVAILABLE and torch.cuda.is_available():
            return True
        
        try:
            import pynvml
            pynvml.nvmlInit()
            return True
        except ImportError:
            return False
    
    def _get_gpu_memory(self) -> Tuple[float, float]:
        """Get GPU memory usage.
        
        Returns:
            Tuple of (used_mb, total_mb)
        """
        if not self._gpu_available:
            return 0.0, 0.0
        
        try:
            if TORCH_AVAILABLE and torch.cuda.is_available():
                used = torch.cuda.memory_allocated() / 1024 / 1024
                total = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
                return used, total
        except Exception:
            pass
        
        try:
            import pynvml
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            used = info.used / 1024 / 1024
            total = info.total / 1024 / 1024
            return used, total
        except Exception:
            pass
        
        return 0.0, 0.0
    
    def _get_top_objects(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top memory consuming object types.
        
        Args:
            limit: Maximum number of object types to return
        
        Returns:
            List of (object_type, count) tuples
        """
        if not self.enable_tracemalloc or not tracemalloc.is_tracing():
            return []
        
        try:
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            
            # Group by object type
            type_counts = defaultdict(int)
            for stat in top_stats[:100]:  # Limit to top 100 for performance
                try:
                    # Try to get object type from traceback
                    frame = stat.traceback.format()[-1] if stat.traceback else ''
                    if 'object' in frame:
                        obj_type = frame.split('object')[0].split()[-1]
                        type_counts[obj_type] += stat.count
                except Exception:
                    continue
            
            return sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        except Exception:
            return []
    
    def take_snapshot(self) -> MemorySnapshot:
        """Take a memory usage snapshot.
        
        Returns:
            Memory snapshot
        """
        try:
            # Process memory info
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            # System memory info
            system_memory = psutil.virtual_memory()
            
            # GPU memory info
            gpu_used, gpu_total = self._get_gpu_memory()
            gpu_percent = (gpu_used / gpu_total * 100) if gpu_total > 0 else 0.0
            
            # Python object count
            python_objects = len(gc.get_objects())
            
            # GC statistics
            gc_stats = {i: gc.get_count()[i] for i in range(3)}
            
            # Top objects
            top_objects = self._get_top_objects()
            
            snapshot = MemorySnapshot(
                timestamp=datetime.now(),
                process_memory_mb=memory_info.rss / 1024 / 1024,
                system_memory_percent=memory_percent,
                available_memory_mb=system_memory.available / 1024 / 1024,
                virtual_memory_mb=memory_info.vms / 1024 / 1024,
                resident_memory_mb=memory_info.rss / 1024 / 1024,
                shared_memory_mb=getattr(memory_info, 'shared', 0) / 1024 / 1024,
                gpu_memory_mb=gpu_used,
                gpu_memory_percent=gpu_percent,
                python_objects=python_objects,
                gc_collections=gc_stats,
                top_objects=top_objects
            )
            
            with self._lock:
                self.snapshots.append(snapshot)
            
            # Check thresholds
            self._check_thresholds(snapshot)
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Failed to take memory snapshot: {e}")
            raise
    
    def _check_thresholds(self, snapshot: MemorySnapshot):
        """Check memory thresholds and generate alerts.
        
        Args:
            snapshot: Memory snapshot
        """
        memory_mb = snapshot.process_memory_mb
        
        if memory_mb > self.critical_threshold_mb:
            alert = MemoryAlert(
                timestamp=snapshot.timestamp,
                alert_type='memory_critical',
                message=f"Critical memory usage: {memory_mb:.1f}MB (threshold: {self.critical_threshold_mb}MB)",
                memory_mb=memory_mb,
                threshold_mb=self.critical_threshold_mb,
                severity='critical'
            )
            self._add_alert(alert)
            
        elif memory_mb > self.warning_threshold_mb:
            alert = MemoryAlert(
                timestamp=snapshot.timestamp,
                alert_type='memory_warning',
                message=f"High memory usage: {memory_mb:.1f}MB (threshold: {self.warning_threshold_mb}MB)",
                memory_mb=memory_mb,
                threshold_mb=self.warning_threshold_mb,
                severity='warning'
            )
            self._add_alert(alert)
        
        # GPU memory check
        if snapshot.gpu_memory_percent > 90:
            alert = MemoryAlert(
                timestamp=snapshot.timestamp,
                alert_type='gpu_memory_critical',
                message=f"Critical GPU memory usage: {snapshot.gpu_memory_percent:.1f}%",
                memory_mb=snapshot.gpu_memory_mb,
                threshold_mb=snapshot.gpu_memory_mb * 0.9,
                severity='critical'
            )
            self._add_alert(alert)
    
    def _add_alert(self, alert: MemoryAlert):
        """Add alert and notify callbacks.
        
        Args:
            alert: Memory alert
        """
        with self._lock:
            self.alerts.append(alert)
        
        # Log alert
        if alert.severity == 'critical':
            self.logger.critical(alert.message)
        elif alert.severity == 'warning':
            self.logger.warning(alert.message)
        else:
            self.logger.info(alert.message)
        
        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in memory alert callback: {e}")
    
    def add_callback(self, callback: Callable[[MemoryAlert], None]):
        """Add alert callback.
        
        Args:
            callback: Callback function
        """
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[MemoryAlert], None]):
        """Remove alert callback.
        
        Args:
            callback: Callback function
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start_monitoring(self):
        """Start continuous memory monitoring."""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info("Memory monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous memory monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        self.logger.info("Memory monitoring stopped")
    
    def _monitor_loop(self):
        """Monitoring loop."""
        while self._monitoring:
            try:
                self.take_snapshot()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Error in memory monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def get_snapshots(self, 
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None,
                     limit: Optional[int] = None) -> List[MemorySnapshot]:
        """Get memory snapshots.
        
        Args:
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of snapshots
        
        Returns:
            List of memory snapshots
        """
        with self._lock:
            snapshots = list(self.snapshots)
        
        # Apply time filters
        if start_time:
            snapshots = [s for s in snapshots if s.timestamp >= start_time]
        if end_time:
            snapshots = [s for s in snapshots if s.timestamp <= end_time]
        
        # Apply limit
        if limit:
            snapshots = snapshots[-limit:]
        
        return snapshots
    
    def get_alerts(self, 
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None,
                  severity: Optional[str] = None) -> List[MemoryAlert]:
        """Get memory alerts.
        
        Args:
            start_time: Start time filter
            end_time: End time filter
            severity: Severity filter
        
        Returns:
            List of memory alerts
        """
        with self._lock:
            alerts = list(self.alerts)
        
        # Apply filters
        if start_time:
            alerts = [a for a in alerts if a.timestamp >= start_time]
        if end_time:
            alerts = [a for a in alerts if a.timestamp <= end_time]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return alerts
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics.
        
        Returns:
            Memory statistics
        """
        snapshots = self.get_snapshots()
        if not snapshots:
            return {}
        
        memory_values = [s.process_memory_mb for s in snapshots]
        
        return {
            'current_memory_mb': memory_values[-1] if memory_values else 0,
            'peak_memory_mb': max(memory_values) if memory_values else 0,
            'average_memory_mb': sum(memory_values) / len(memory_values) if memory_values else 0,
            'min_memory_mb': min(memory_values) if memory_values else 0,
            'memory_growth_mb': memory_values[-1] - memory_values[0] if len(memory_values) > 1 else 0,
            'snapshot_count': len(snapshots),
            'alert_count': len(self.alerts),
            'monitoring_active': self._monitoring
        }
    
    def clear_history(self):
        """Clear monitoring history."""
        with self._lock:
            self.snapshots.clear()
            self.alerts.clear()
        self.logger.info("Memory monitoring history cleared")
    
    def force_gc(self) -> Dict[str, int]:
        """Force garbage collection.
        
        Returns:
            GC statistics
        """
        before_objects = len(gc.get_objects())
        collected = gc.collect()
        after_objects = len(gc.get_objects())
        
        stats = {
            'objects_before': before_objects,
            'objects_after': after_objects,
            'objects_collected': before_objects - after_objects,
            'gc_collected': collected
        }
        
        self.logger.info(f"Forced GC: collected {collected} objects, {stats['objects_collected']} objects freed")
        return stats


class MemoryProfiler:
    """Memory profiler for functions and code blocks."""
    
    def __init__(self, monitor: Optional[MemoryMonitor] = None):
        self.monitor = monitor or MemoryMonitor()
        self.logger = get_logger('memory_profiler')
        self.profiles = {}
    
    @contextmanager
    def profile(self, name: str):
        """Profile memory usage of a code block.
        
        Args:
            name: Profile name
        """
        start_snapshot = self.monitor.take_snapshot()
        start_time = time.time()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_snapshot = self.monitor.take_snapshot()
            
            duration = end_time - start_time
            memory_delta = end_snapshot.process_memory_mb - start_snapshot.process_memory_mb
            
            profile_data = {
                'name': name,
                'start_time': start_snapshot.timestamp,
                'end_time': end_snapshot.timestamp,
                'duration_seconds': duration,
                'memory_delta_mb': memory_delta,
                'start_memory_mb': start_snapshot.process_memory_mb,
                'end_memory_mb': end_snapshot.process_memory_mb,
                'peak_memory_mb': max(start_snapshot.process_memory_mb, end_snapshot.process_memory_mb)
            }
            
            self.profiles[name] = profile_data
            
            self.logger.info(
                f"Memory profile '{name}': {memory_delta:+.1f}MB delta, "
                f"{end_snapshot.process_memory_mb:.1f}MB final, {duration:.3f}s duration"
            )
    
    def profile_function(self, func):
        """Decorator to profile function memory usage.
        
        Args:
            func: Function to profile
        
        Returns:
            Decorated function
        """
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__qualname__}"
            with self.profile(func_name):
                return func(*args, **kwargs)
        return wrapper
    
    def get_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get all profiles.
        
        Returns:
            Dictionary of profiles
        """
        return self.profiles.copy()
    
    def clear_profiles(self):
        """Clear all profiles."""
        self.profiles.clear()
        self.logger.info("Memory profiles cleared")


class MemoryPool:
    """Simple memory pool for object reuse."""
    
    def __init__(self, factory: Callable[[], Any], max_size: int = 100):
        self.factory = factory
        self.max_size = max_size
        self.pool = deque(maxlen=max_size)
        self.created_count = 0
        self.reused_count = 0
        self._lock = threading.Lock()
    
    def get(self) -> Any:
        """Get object from pool.
        
        Returns:
            Object instance
        """
        with self._lock:
            if self.pool:
                self.reused_count += 1
                return self.pool.popleft()
            else:
                self.created_count += 1
                return self.factory()
    
    def put(self, obj: Any):
        """Return object to pool.
        
        Args:
            obj: Object to return
        """
        with self._lock:
            if len(self.pool) < self.max_size:
                # Reset object if it has a reset method
                if hasattr(obj, 'reset'):
                    obj.reset()
                self.pool.append(obj)
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics.
        
        Returns:
            Pool statistics
        """
        with self._lock:
            return {
                'pool_size': len(self.pool),
                'max_size': self.max_size,
                'created_count': self.created_count,
                'reused_count': self.reused_count,
                'reuse_ratio': self.reused_count / max(1, self.created_count + self.reused_count)
            }
    
    def clear(self):
        """Clear pool."""
        with self._lock:
            self.pool.clear()


def get_memory_info() -> Dict[str, Any]:
    """Get current memory information.
    
    Returns:
        Memory information dictionary
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    system_memory = psutil.virtual_memory()
    
    info = {
        'process_memory_mb': memory_info.rss / 1024 / 1024,
        'process_memory_percent': process.memory_percent(),
        'virtual_memory_mb': memory_info.vms / 1024 / 1024,
        'system_total_mb': system_memory.total / 1024 / 1024,
        'system_available_mb': system_memory.available / 1024 / 1024,
        'system_used_percent': system_memory.percent,
        'python_objects': len(gc.get_objects())
    }
    
    # Add GPU info if available
    try:
        if TORCH_AVAILABLE and torch.cuda.is_available():
            info['gpu_memory_allocated_mb'] = torch.cuda.memory_allocated() / 1024 / 1024
            info['gpu_memory_cached_mb'] = torch.cuda.memory_reserved() / 1024 / 1024
            info['gpu_memory_total_mb'] = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
    except Exception:
        pass
    
    return info


def optimize_memory():
    """Optimize memory usage."""
    logger = get_logger('memory_optimizer')
    
    # Force garbage collection
    before_objects = len(gc.get_objects())
    collected = gc.collect()
    after_objects = len(gc.get_objects())
    
    logger.info(f"GC: collected {collected} objects, freed {before_objects - after_objects} objects")
    
    # Clear PyTorch cache if available
    if TORCH_AVAILABLE and torch.cuda.is_available():
        try:
            torch.cuda.empty_cache()
            logger.info("Cleared PyTorch CUDA cache")
        except Exception as e:
            logger.warning(f"Failed to clear PyTorch cache: {e}")
    
    # Clear NumPy cache if available
    if NUMPY_AVAILABLE:
        try:
            # NumPy doesn't have a direct cache clear, but we can suggest GC
            pass
        except Exception:
            pass


# Global memory monitor instance
_global_monitor = None


def get_global_monitor() -> MemoryMonitor:
    """Get global memory monitor instance.
    
    Returns:
        Global memory monitor
    """
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = MemoryMonitor()
    return _global_monitor


def start_global_monitoring():
    """Start global memory monitoring."""
    get_global_monitor().start_monitoring()


def stop_global_monitoring():
    """Stop global memory monitoring."""
    if _global_monitor:
        _global_monitor.stop_monitoring()


def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage information.
    
    Returns:
        Dictionary containing memory usage metrics in MB
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    system_memory = psutil.virtual_memory()
    
    usage = {
        'process_memory_mb': memory_info.rss / 1024 / 1024,
        'virtual_memory_mb': memory_info.vms / 1024 / 1024,
        'system_total_mb': system_memory.total / 1024 / 1024,
        'system_available_mb': system_memory.available / 1024 / 1024,
        'system_used_mb': (system_memory.total - system_memory.available) / 1024 / 1024,
        'system_used_percent': system_memory.percent
    }
    
    # Add GPU memory if available
    try:
        if TORCH_AVAILABLE and torch.cuda.is_available():
            usage['gpu_allocated_mb'] = torch.cuda.memory_allocated() / 1024 / 1024
            usage['gpu_cached_mb'] = torch.cuda.memory_reserved() / 1024 / 1024
    except Exception:
        pass
    
    return usage


def check_memory_limit(limit_mb: float = 1000.0) -> bool:
    """Check if current memory usage exceeds the specified limit.
    
    Args:
        limit_mb: Memory limit in megabytes
        
    Returns:
        True if memory usage is within limit, False otherwise
    """
    try:
        process = psutil.Process()
        current_memory_mb = process.memory_info().rss / 1024 / 1024
        return current_memory_mb <= limit_mb
    except Exception:
        # If we can't check memory, assume it's okay
        return True