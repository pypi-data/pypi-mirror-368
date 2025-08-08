import time
import functools
from typing import Callable, Any, Dict

def benchmark_operation(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    start_time = time.perf_counter()
    start_process_time = time.process_time()
    
    result = func(*args, **kwargs)
    
    end_time = time.perf_counter()
    end_process_time = time.process_time()
    
    return {
        'result': result,
        'wall_time_ms': (end_time - start_time) * 1000,
        'cpu_time_ms': (end_process_time - start_process_time) * 1000
    }

def profile_memory(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024
            
            result = func(*args, **kwargs)
            
            memory_after = process.memory_info().rss / 1024 / 1024
            memory_delta = memory_after - memory_before
            
            print(f"Memory usage: {memory_delta:.2f} MB")
            
            return result
        except ImportError:
            return func(*args, **kwargs)
    
    return wrapper

def time_operation(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        execution_time = (end_time - start_time) * 1000
        print(f"{func.__name__} took {execution_time:.2f} ms")
        
        return result
    
    return wrapper

class PerformanceProfiler:
    def __init__(self):
        self.measurements = {}
    
    def measure(self, operation_name: str, func: Callable, *args, **kwargs) -> Any:
        benchmark_result = benchmark_operation(func, *args, **kwargs)
        
        self.measurements[operation_name] = {
            'wall_time_ms': benchmark_result['wall_time_ms'],
            'cpu_time_ms': benchmark_result['cpu_time_ms']
        }
        
        return benchmark_result['result']
    
    def get_summary(self) -> Dict[str, Any]:
        return self.measurements.copy()
    
    def clear(self):
        self.measurements.clear()