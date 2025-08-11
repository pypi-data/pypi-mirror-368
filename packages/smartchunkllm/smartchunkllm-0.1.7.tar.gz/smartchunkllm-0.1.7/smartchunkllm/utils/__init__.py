"""Utility modules for SmartChunkLLM."""

from .text import (
    clean_text,
    normalize_text,
    extract_sentences,
    count_tokens,
    split_into_tokens,
    detect_language,
    is_turkish_text,
    remove_stopwords,
    stem_text,
    calculate_text_similarity,
    extract_keywords,
    TextProcessor
)

from .file import (
    ensure_directory,
    get_file_size,
    get_file_extension,
    is_pdf_file,
    create_temp_file,
    safe_file_write,
    backup_file,
    FileManager
)

from .validation import (
    validate_pdf_file,
    validate_text_input,
    validate_config,
    validate_chunk_size,
    validate_quality_threshold,
    InputValidator
)

from .logging import (
    setup_logging,
    get_logger,
    log_performance,
    log_error,
    LogManager
)

from .memory import (
    get_memory_usage,
    check_memory_limit,
    optimize_memory,
    MemoryMonitor
)

from .performance import (
    measure_time,
    profile_function,
    benchmark_operation,
    PerformanceMonitor
)

from .system import (
    get_system_info,
    check_dependencies,
    check_ollama_availability,
    check_gpu_availability,
    get_package_versions,
    check_environment,
    print_environment_report
)

__all__ = [
    # Text utilities
    'clean_text',
    'normalize_text', 
    'extract_sentences',
    'count_tokens',
    'split_into_tokens',
    'detect_language',
    'is_turkish_text',
    'remove_stopwords',
    'stem_text',
    'calculate_text_similarity',
    'extract_keywords',
    'TextProcessor',
    
    # File utilities
    'ensure_directory',
    'get_file_size',
    'get_file_extension',
    'is_pdf_file',
    'create_temp_file',
    'safe_file_write',
    'backup_file',
    'FileManager',
    
    # Validation utilities
    'validate_pdf_file',
    'validate_text_input',
    'validate_config',
    'validate_chunk_size',
    'validate_quality_threshold',
    'InputValidator',
    
    # Logging utilities
    'setup_logging',
    'get_logger',
    'log_performance',
    'log_error',
    'LogManager',
    
    # Memory utilities
    'get_memory_usage',
    'check_memory_limit',
    'optimize_memory',
    'MemoryMonitor',
    
    # Performance utilities
    'measure_time',
    'profile_function',
    'benchmark_operation',
    'PerformanceMonitor',
    
    # System utilities
    'get_system_info',
    'check_dependencies',
    'check_ollama_availability',
    'check_gpu_availability',
    'get_package_versions',
    'check_environment',
    'print_environment_report'
]