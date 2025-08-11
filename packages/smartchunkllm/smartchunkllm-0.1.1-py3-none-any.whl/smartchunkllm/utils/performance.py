"""Performance monitoring and profiling utilities for SmartChunkLLM."""

import time
import functools
import threading
import statistics
from typing import Dict, List, Optional, Callable, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
from collections import defaultdict, deque
import cProfile
import pstats
import io
import sys
import os

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import line_profiler
    LINE_PROFILER_AVAILABLE = True
except ImportError:
    LINE_PROFILER_AVAILABLE = False

try:
    import memory_profiler
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False

from .logging import get_logger
from .memory import get_memory_info


@dataclass
class PerformanceMetric:
    """Performance metric data."""
    name: str
    timestamp: datetime
    duration: float
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_delta_mb: float = 0.0
    io_read_mb: float = 0.0
    io_write_mb: float = 0.0
    context_switches: int = 0
    thread_count: int = 0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'name': self.name,
            'timestamp': self.timestamp.isoformat(),
            'duration': self.duration,
            'cpu_percent': self.cpu_percent,
            'memory_mb': self.memory_mb,
            'memory_delta_mb': self.memory_delta_mb,
            'io_read_mb': self.io_read_mb,
            'io_write_mb': self.io_write_mb,
            'context_switches': self.context_switches,
            'thread_count': self.thread_count,
            'success': self.success,
            'error': self.error,
            'metadata': self.metadata
        }


@dataclass
class PerformanceStats:
    """Performance statistics."""
    name: str
    count: int
    total_duration: float
    avg_duration: float
    min_duration: float
    max_duration: float
    median_duration: float
    std_duration: float
    success_rate: float
    avg_cpu_percent: float
    avg_memory_mb: float
    total_memory_delta_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'name': self.name,
            'count': self.count,
            'total_duration': self.total_duration,
            'avg_duration': self.avg_duration,
            'min_duration': self.min_duration,
            'max_duration': self.max_duration,
            'median_duration': self.median_duration,
            'std_duration': self.std_duration,
            'success_rate': self.success_rate,
            'avg_cpu_percent': self.avg_cpu_percent,
            'avg_memory_mb': self.avg_memory_mb,
            'total_memory_delta_mb': self.total_memory_delta_mb
        }


class PerformanceMonitor:
    """Performance monitoring system."""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self.metrics = deque(maxlen=max_metrics)
        self.logger = get_logger('performance_monitor')
        self._lock = threading.Lock()
        
        # Process handle for system metrics
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()
        else:
            self.process = None
    
    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics.
        
        Returns:
            System metrics dictionary
        """
        metrics = {}
        
        if self.process:
            try:
                # CPU usage
                metrics['cpu_percent'] = self.process.cpu_percent()
                
                # Memory usage
                memory_info = self.process.memory_info()
                metrics['memory_mb'] = memory_info.rss / 1024 / 1024
                
                # I/O counters
                try:
                    io_counters = self.process.io_counters()
                    metrics['io_read_mb'] = io_counters.read_bytes / 1024 / 1024
                    metrics['io_write_mb'] = io_counters.write_bytes / 1024 / 1024
                except (AttributeError, psutil.AccessDenied):
                    metrics['io_read_mb'] = 0.0
                    metrics['io_write_mb'] = 0.0
                
                # Context switches
                try:
                    ctx_switches = self.process.num_ctx_switches()
                    metrics['context_switches'] = ctx_switches.voluntary + ctx_switches.involuntary
                except (AttributeError, psutil.AccessDenied):
                    metrics['context_switches'] = 0
                
                # Thread count
                metrics['thread_count'] = self.process.num_threads()
                
            except psutil.NoSuchProcess:
                # Process might have ended
                pass
        
        return metrics
    
    @contextmanager
    def measure(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """Context manager to measure performance.
        
        Args:
            name: Measurement name
            metadata: Additional metadata
        
        Yields:
            Performance metric (will be populated after completion)
        """
        start_time = time.time()
        start_metrics = self._get_system_metrics()
        start_memory = get_memory_info().get('process_memory_mb', 0.0)
        
        metric = PerformanceMetric(
            name=name,
            timestamp=datetime.now(),
            duration=0.0,
            metadata=metadata or {}
        )
        
        try:
            yield metric
            metric.success = True
            
        except Exception as e:
            metric.success = False
            metric.error = str(e)
            raise
            
        finally:
            end_time = time.time()
            end_metrics = self._get_system_metrics()
            end_memory = get_memory_info().get('process_memory_mb', 0.0)
            
            # Calculate metrics
            metric.duration = end_time - start_time
            metric.cpu_percent = end_metrics.get('cpu_percent', 0.0)
            metric.memory_mb = end_metrics.get('memory_mb', 0.0)
            metric.memory_delta_mb = end_memory - start_memory
            metric.io_read_mb = end_metrics.get('io_read_mb', 0.0) - start_metrics.get('io_read_mb', 0.0)
            metric.io_write_mb = end_metrics.get('io_write_mb', 0.0) - start_metrics.get('io_write_mb', 0.0)
            metric.context_switches = end_metrics.get('context_switches', 0) - start_metrics.get('context_switches', 0)
            metric.thread_count = end_metrics.get('thread_count', 0)
            
            # Store metric
            with self._lock:
                self.metrics.append(metric)
            
            # Log performance
            self.logger.debug(
                f"Performance: {name} completed in {metric.duration:.3f}s "
                f"(CPU: {metric.cpu_percent:.1f}%, Memory: {metric.memory_delta_mb:+.1f}MB)"
            )
    
    def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric.
        
        Args:
            metric: Performance metric
        """
        with self._lock:
            self.metrics.append(metric)
    
    def get_metrics(self, 
                   name: Optional[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   success_only: bool = False) -> List[PerformanceMetric]:
        """Get performance metrics.
        
        Args:
            name: Filter by metric name
            start_time: Start time filter
            end_time: End time filter
            success_only: Only return successful metrics
        
        Returns:
            List of performance metrics
        """
        with self._lock:
            metrics = list(self.metrics)
        
        # Apply filters
        if name:
            metrics = [m for m in metrics if m.name == name]
        if start_time:
            metrics = [m for m in metrics if m.timestamp >= start_time]
        if end_time:
            metrics = [m for m in metrics if m.timestamp <= end_time]
        if success_only:
            metrics = [m for m in metrics if m.success]
        
        return metrics
    
    def get_stats(self, name: Optional[str] = None) -> Dict[str, PerformanceStats]:
        """Get performance statistics.
        
        Args:
            name: Filter by metric name
        
        Returns:
            Dictionary of performance statistics by name
        """
        metrics = self.get_metrics(name=name)
        
        # Group by name
        grouped = defaultdict(list)
        for metric in metrics:
            grouped[metric.name].append(metric)
        
        stats = {}
        for metric_name, metric_list in grouped.items():
            if not metric_list:
                continue
            
            durations = [m.duration for m in metric_list]
            successes = [m.success for m in metric_list]
            cpu_percents = [m.cpu_percent for m in metric_list if m.cpu_percent > 0]
            memory_mbs = [m.memory_mb for m in metric_list if m.memory_mb > 0]
            memory_deltas = [m.memory_delta_mb for m in metric_list]
            
            stats[metric_name] = PerformanceStats(
                name=metric_name,
                count=len(metric_list),
                total_duration=sum(durations),
                avg_duration=statistics.mean(durations),
                min_duration=min(durations),
                max_duration=max(durations),
                median_duration=statistics.median(durations),
                std_duration=statistics.stdev(durations) if len(durations) > 1 else 0.0,
                success_rate=sum(successes) / len(successes),
                avg_cpu_percent=statistics.mean(cpu_percents) if cpu_percents else 0.0,
                avg_memory_mb=statistics.mean(memory_mbs) if memory_mbs else 0.0,
                total_memory_delta_mb=sum(memory_deltas)
            )
        
        return stats
    
    def clear_metrics(self):
        """Clear all metrics."""
        with self._lock:
            self.metrics.clear()
        self.logger.info("Performance metrics cleared")
    
    def export_metrics(self, filepath: str, format: str = 'json'):
        """Export metrics to file.
        
        Args:
            filepath: Output file path
            format: Export format ('json', 'csv')
        """
        import json
        
        metrics_data = [m.to_dict() for m in self.metrics]
        
        if format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump(metrics_data, f, indent=2, default=str)
        
        elif format.lower() == 'csv':
            import csv
            
            if metrics_data:
                with open(filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=metrics_data[0].keys())
                    writer.writeheader()
                    writer.writerows(metrics_data)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self.logger.info(f"Exported {len(metrics_data)} metrics to {filepath}")


class Timer:
    """Simple timer utility."""
    
    def __init__(self, name: str = 'Timer'):
        self.name = name
        self.start_time = None
        self.end_time = None
        self.logger = get_logger('timer')
    
    def start(self):
        """Start timer."""
        self.start_time = time.time()
        self.logger.debug(f"{self.name} started")
    
    def stop(self) -> float:
        """Stop timer and return duration.
        
        Returns:
            Duration in seconds
        """
        if self.start_time is None:
            raise ValueError("Timer not started")
        
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        self.logger.debug(f"{self.name} completed in {duration:.3f}s")
        return duration
    
    def elapsed(self) -> float:
        """Get elapsed time without stopping.
        
        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            raise ValueError("Timer not started")
        
        return time.time() - self.start_time
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class Profiler:
    """Code profiler wrapper."""
    
    def __init__(self, name: str = 'Profile'):
        self.name = name
        self.profiler = None
        self.logger = get_logger('profiler')
    
    def start(self):
        """Start profiling."""
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        self.logger.debug(f"Profiling started: {self.name}")
    
    def stop(self) -> str:
        """Stop profiling and return results.
        
        Returns:
            Profiling results as string
        """
        if self.profiler is None:
            raise ValueError("Profiler not started")
        
        self.profiler.disable()
        
        # Get results
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats()
        
        results = s.getvalue()
        self.logger.debug(f"Profiling completed: {self.name}")
        
        return results
    
    def save_results(self, filepath: str):
        """Save profiling results to file.
        
        Args:
            filepath: Output file path
        """
        if self.profiler is None:
            raise ValueError("Profiler not started")
        
        self.profiler.dump_stats(filepath)
        self.logger.info(f"Profiling results saved to {filepath}")
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def time_function(func: Optional[Callable] = None, *, 
                 name: Optional[str] = None,
                 monitor: Optional[PerformanceMonitor] = None,
                 log_result: bool = True):
    """Decorator to time function execution.
    
    Args:
        func: Function to decorate
        name: Custom name for timing
        monitor: Performance monitor to use
        log_result: Whether to log the result
    
    Returns:
        Decorated function or decorator
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            func_name = name or f"{f.__module__}.{f.__qualname__}"
            
            if monitor:
                with monitor.measure(func_name) as metric:
                    result = f(*args, **kwargs)
                    if log_result:
                        logger = get_logger('timer')
                        logger.info(
                            f"Function {func_name} completed in {metric.duration:.3f}s"
                        )
                return result
            else:
                with Timer(func_name):
                    return f(*args, **kwargs)
        
        return wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)


def profile_function(func: Optional[Callable] = None, *,
                    name: Optional[str] = None,
                    save_to: Optional[str] = None):
    """Decorator to profile function execution.
    
    Args:
        func: Function to decorate
        name: Custom name for profiling
        save_to: File path to save results
    
    Returns:
        Decorated function or decorator
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            func_name = name or f"{f.__module__}.{f.__qualname__}"
            
            with Profiler(func_name) as profiler:
                result = f(*args, **kwargs)
                
                if save_to:
                    profiler.save_results(save_to)
                
                return result
        
        return wrapper
    
    if func is None:
        return decorator
    else:
        return decorator(func)


class BenchmarkSuite:
    """Benchmark suite for performance testing."""
    
    def __init__(self, name: str = 'Benchmark'):
        self.name = name
        self.benchmarks = {}
        self.results = {}
        self.logger = get_logger('benchmark')
        self.monitor = PerformanceMonitor()
    
    def add_benchmark(self, name: str, func: Callable, *args, **kwargs):
        """Add a benchmark function.
        
        Args:
            name: Benchmark name
            func: Function to benchmark
            *args: Function arguments
            **kwargs: Function keyword arguments
        """
        self.benchmarks[name] = (func, args, kwargs)
    
    def run_benchmark(self, name: str, iterations: int = 1) -> PerformanceStats:
        """Run a specific benchmark.
        
        Args:
            name: Benchmark name
            iterations: Number of iterations
        
        Returns:
            Performance statistics
        """
        if name not in self.benchmarks:
            raise ValueError(f"Benchmark '{name}' not found")
        
        func, args, kwargs = self.benchmarks[name]
        
        self.logger.info(f"Running benchmark '{name}' ({iterations} iterations)")
        
        for i in range(iterations):
            with self.monitor.measure(f"{name}_iter_{i}"):
                func(*args, **kwargs)
        
        # Get statistics
        stats = self.monitor.get_stats(name=f"{name}_iter_0")
        if stats:
            benchmark_stats = list(stats.values())[0]
            self.results[name] = benchmark_stats
            
            self.logger.info(
                f"Benchmark '{name}' completed: "
                f"avg={benchmark_stats.avg_duration:.3f}s, "
                f"min={benchmark_stats.min_duration:.3f}s, "
                f"max={benchmark_stats.max_duration:.3f}s"
            )
            
            return benchmark_stats
        
        raise RuntimeError(f"No statistics available for benchmark '{name}'")
    
    def run_all(self, iterations: int = 1) -> Dict[str, PerformanceStats]:
        """Run all benchmarks.
        
        Args:
            iterations: Number of iterations per benchmark
        
        Returns:
            Dictionary of performance statistics
        """
        self.logger.info(f"Running all benchmarks in suite '{self.name}'")
        
        results = {}
        for name in self.benchmarks:
            try:
                results[name] = self.run_benchmark(name, iterations)
            except Exception as e:
                self.logger.error(f"Benchmark '{name}' failed: {e}")
        
        return results
    
    def compare_results(self, baseline: str, target: str) -> Dict[str, float]:
        """Compare two benchmark results.
        
        Args:
            baseline: Baseline benchmark name
            target: Target benchmark name
        
        Returns:
            Comparison metrics
        """
        if baseline not in self.results or target not in self.results:
            raise ValueError("Both benchmarks must be run first")
        
        baseline_stats = self.results[baseline]
        target_stats = self.results[target]
        
        return {
            'duration_ratio': target_stats.avg_duration / baseline_stats.avg_duration,
            'duration_improvement': (baseline_stats.avg_duration - target_stats.avg_duration) / baseline_stats.avg_duration,
            'memory_ratio': target_stats.avg_memory_mb / max(baseline_stats.avg_memory_mb, 0.001),
            'cpu_ratio': target_stats.avg_cpu_percent / max(baseline_stats.avg_cpu_percent, 0.001)
        }
    
    def export_results(self, filepath: str):
        """Export benchmark results.
        
        Args:
            filepath: Output file path
        """
        import json
        
        results_data = {
            'suite_name': self.name,
            'timestamp': datetime.now().isoformat(),
            'results': {name: stats.to_dict() for name, stats in self.results.items()}
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        self.logger.info(f"Benchmark results exported to {filepath}")


# Global performance monitor
_global_monitor = None


def get_global_monitor() -> PerformanceMonitor:
    """Get global performance monitor.
    
    Returns:
        Global performance monitor
    """
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


# Convenience functions
def measure_time(name: str, metadata: Optional[Dict[str, Any]] = None):
    """Measure execution time.
    
    Args:
        name: Measurement name
        metadata: Additional metadata
    
    Returns:
        Context manager
    """
    return get_global_monitor().measure(name, metadata)


def get_performance_stats(name: Optional[str] = None) -> Dict[str, PerformanceStats]:
    """Get performance statistics.
    
    Args:
        name: Filter by metric name
    
    Returns:
        Performance statistics
    """
    return get_global_monitor().get_stats(name)


def benchmark_operation(func: Callable, *args, iterations: int = 1, name: Optional[str] = None, **kwargs) -> PerformanceStats:
    """Benchmark a function or operation.
    
    Args:
        func: Function to benchmark
        *args: Function arguments
        iterations: Number of iterations to run
        name: Custom name for the benchmark
        **kwargs: Function keyword arguments
    
    Returns:
        Performance statistics
    """
    monitor = get_global_monitor()
    operation_name = name or f"{func.__name__}_benchmark"
    
    logger = get_logger('benchmark')
    logger.info(f"Benchmarking '{operation_name}' with {iterations} iterations")
    
    # Run the benchmark iterations
    for i in range(iterations):
        with monitor.measure(f"{operation_name}_iter_{i}"):
            func(*args, **kwargs)
    
    # Get and return statistics
    stats = monitor.get_stats(name=f"{operation_name}_iter_0")
    if stats:
        result = list(stats.values())[0]
        logger.info(
            f"Benchmark '{operation_name}' completed: "
            f"avg={result.avg_duration:.3f}s, "
            f"min={result.min_duration:.3f}s, "
            f"max={result.max_duration:.3f}s"
        )
        return result
    
    raise RuntimeError(f"No statistics available for benchmark '{operation_name}'")