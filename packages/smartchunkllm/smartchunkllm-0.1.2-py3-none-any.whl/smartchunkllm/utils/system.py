"""System information and dependency checking utilities."""

import sys
import platform
import importlib
import subprocess
from typing import Dict, Any, List, Optional
import warnings
warnings.filterwarnings('ignore')


def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information.
    
    Returns:
        Dictionary containing system information
    """
    info = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "node": platform.node()
    }
    
    # Add memory information if available
    try:
        import psutil
        memory = psutil.virtual_memory()
        info["total_memory"] = f"{memory.total / (1024**3):.1f} GB"
        info["available_memory"] = f"{memory.available / (1024**3):.1f} GB"
        info["memory_usage"] = f"{memory.percent}%"
    except ImportError:
        info["memory_info"] = "psutil not available"
    
    return info


def check_dependencies() -> Dict[str, bool]:
    """Check availability of key dependencies.
    
    Returns:
        Dictionary mapping dependency names to availability status
    """
    dependencies = {
        "numpy": _check_import("numpy"),
        "pandas": _check_import("pandas"),
        "scipy": _check_import("scipy"),
        "sklearn": _check_import("sklearn"),
        "transformers": _check_import("transformers"),
        "sentence_transformers": _check_import("sentence_transformers"),
        "torch": _check_import("torch"),
        "tensorflow": _check_import("tensorflow"),
        "openai": _check_import("openai"),
        "anthropic": _check_import("anthropic"),
        "requests": _check_import("requests"),
        "pdfplumber": _check_import("pdfplumber"),
        "PyPDF2": _check_import("PyPDF2"),
        "pymupdf": _check_import("fitz"),  # PyMuPDF imports as fitz
        "layoutparser": _check_import("layoutparser"),
        "hdbscan": _check_import("hdbscan"),
        "umap": _check_import("umap"),
        "spacy": _check_import("spacy"),
        "textstat": _check_import("textstat"),
        "zeyrek": _check_import("zeyrek"),
        "turkish_stemmer": _check_import("TurkishStemmer"),
        "psutil": _check_import("psutil"),
        "matplotlib": _check_import("matplotlib"),
        "seaborn": _check_import("seaborn"),
        "plotly": _check_import("plotly"),
        "streamlit": _check_import("streamlit"),
        "fastapi": _check_import("fastapi"),
        "uvicorn": _check_import("uvicorn"),
        "sqlalchemy": _check_import("sqlalchemy"),
        "redis": _check_import("redis"),
        "celery": _check_import("celery")
    }
    
    return dependencies


def _check_import(module_name: str) -> bool:
    """Check if a module can be imported.
    
    Args:
        module_name: Name of the module to check
        
    Returns:
        True if module can be imported, False otherwise
    """
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def check_ollama_availability() -> Dict[str, Any]:
    """Check if Ollama is available and running.
    
    Returns:
        Dictionary with Ollama status information
    """
    status = {
        "available": False,
        "running": False,
        "models": [],
        "version": None,
        "error": None
    }
    
    try:
        # Check if ollama command exists
        result = subprocess.run(
            ["ollama", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        
        if result.returncode == 0:
            status["available"] = True
            status["version"] = result.stdout.strip()
            
            # Check if Ollama is running by listing models
            models_result = subprocess.run(
                ["ollama", "list"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if models_result.returncode == 0:
                status["running"] = True
                # Parse model list
                lines = models_result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    for line in lines[1:]:
                        if line.strip():
                            model_name = line.split()[0]
                            status["models"].append(model_name)
            else:
                status["error"] = "Ollama not running or no models available"
        else:
            status["error"] = "Ollama command failed"
            
    except subprocess.TimeoutExpired:
        status["error"] = "Ollama command timed out"
    except FileNotFoundError:
        status["error"] = "Ollama not installed"
    except Exception as e:
        status["error"] = f"Error checking Ollama: {str(e)}"
    
    return status


def check_gpu_availability() -> Dict[str, Any]:
    """Check GPU availability for ML operations.
    
    Returns:
        Dictionary with GPU information
    """
    gpu_info = {
        "cuda_available": False,
        "mps_available": False,  # Apple Metal Performance Shaders
        "gpu_count": 0,
        "gpu_names": [],
        "memory_info": {}
    }
    
    # Check PyTorch CUDA
    try:
        import torch
        gpu_info["cuda_available"] = torch.cuda.is_available()
        if gpu_info["cuda_available"]:
            gpu_info["gpu_count"] = torch.cuda.device_count()
            for i in range(gpu_info["gpu_count"]):
                gpu_info["gpu_names"].append(torch.cuda.get_device_name(i))
                
        # Check MPS (Apple Silicon)
        if hasattr(torch.backends, 'mps'):
            gpu_info["mps_available"] = torch.backends.mps.is_available()
            
    except ImportError:
        pass
    
    # Check TensorFlow GPU
    try:
        import tensorflow as tf
        physical_devices = tf.config.list_physical_devices('GPU')
        if physical_devices and not gpu_info["cuda_available"]:
            gpu_info["gpu_count"] = len(physical_devices)
            gpu_info["gpu_names"] = [device.name for device in physical_devices]
    except ImportError:
        pass
    
    return gpu_info


def get_package_versions() -> Dict[str, str]:
    """Get versions of installed packages.
    
    Returns:
        Dictionary mapping package names to versions
    """
    versions = {}
    
    packages = [
        "numpy", "pandas", "scipy", "sklearn", "transformers",
        "sentence_transformers", "torch", "tensorflow", "openai",
        "anthropic", "requests", "pdfplumber", "PyPDF2", "pymupdf",
        "layoutparser", "hdbscan", "umap-learn", "spacy", "textstat"
    ]
    
    for package in packages:
        try:
            if package == "pymupdf":
                import fitz
                versions[package] = getattr(fitz, '__version__', 'unknown')
            elif package == "sklearn":
                import sklearn
                versions[package] = sklearn.__version__
            else:
                module = importlib.import_module(package)
                versions[package] = getattr(module, '__version__', 'unknown')
        except ImportError:
            versions[package] = "not installed"
        except Exception:
            versions[package] = "error"
    
    return versions


def check_environment() -> Dict[str, Any]:
    """Comprehensive environment check.
    
    Returns:
        Dictionary with complete environment information
    """
    return {
        "system_info": get_system_info(),
        "dependencies": check_dependencies(),
        "package_versions": get_package_versions(),
        "gpu_info": check_gpu_availability(),
        "ollama_status": check_ollama_availability()
    }


def print_environment_report():
    """Print a comprehensive environment report."""
    env_info = check_environment()
    
    print("🔍 SmartChunkLLM Environment Report")
    print("=" * 50)
    
    # System Information
    print("\n📊 System Information:")
    for key, value in env_info["system_info"].items():
        print(f"  {key}: {value}")
    
    # Dependencies
    print("\n📦 Dependencies:")
    deps = env_info["dependencies"]
    available = sum(1 for status in deps.values() if status)
    total = len(deps)
    print(f"  Available: {available}/{total}")
    
    for dep, status in deps.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {dep}")
    
    # GPU Information
    print("\n🎮 GPU Information:")
    gpu_info = env_info["gpu_info"]
    if gpu_info["cuda_available"] or gpu_info["mps_available"]:
        if gpu_info["cuda_available"]:
            print(f"  ✅ CUDA available ({gpu_info['gpu_count']} GPUs)")
            for name in gpu_info["gpu_names"]:
                print(f"    - {name}")
        if gpu_info["mps_available"]:
            print("  ✅ Apple MPS available")
    else:
        print("  ❌ No GPU acceleration available")
    
    # Ollama Status
    print("\n🦙 Ollama Status:")
    ollama = env_info["ollama_status"]
    if ollama["available"]:
        print(f"  ✅ Ollama available (version: {ollama['version']})")
        if ollama["running"]:
            print(f"  ✅ Ollama running ({len(ollama['models'])} models)")
            for model in ollama["models"]:
                print(f"    - {model}")
        else:
            print("  ⚠️ Ollama not running")
    else:
        print(f"  ❌ Ollama not available: {ollama['error']}")