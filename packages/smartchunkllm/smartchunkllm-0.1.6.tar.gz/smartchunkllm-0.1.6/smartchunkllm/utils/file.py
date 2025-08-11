"""File management utilities for SmartChunkLLM."""

import os
import json
import yaml
import pickle
import hashlib
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Iterator
from datetime import datetime
import mimetypes
import zipfile
import tarfile

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

from ..core.exceptions import (
    FileNotFoundError as SmartChunkFileNotFoundError,
    InvalidFormatError,
    DataError
)


class FileManager:
    """File management utility class."""
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.temp_dir = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def cleanup(self):
        """Clean up temporary files and directories."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            self.temp_dir = None
    
    def get_temp_dir(self) -> Path:
        """Get or create temporary directory."""
        if not self.temp_dir:
            self.temp_dir = Path(tempfile.mkdtemp(prefix='smartchunk_'))
        return self.temp_dir
    
    def ensure_dir(self, path: Union[str, Path]) -> Path:
        """Ensure directory exists.
        
        Args:
            path: Directory path
        
        Returns:
            Path object
        """
        path = Path(path)
        if not path.is_absolute():
            path = self.base_path / path
        
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def resolve_path(self, path: Union[str, Path]) -> Path:
        """Resolve path relative to base path.
        
        Args:
            path: File or directory path
        
        Returns:
            Resolved path
        """
        path = Path(path)
        if not path.is_absolute():
            path = self.base_path / path
        return path.resolve()
    
    def exists(self, path: Union[str, Path]) -> bool:
        """Check if file or directory exists.
        
        Args:
            path: File or directory path
        
        Returns:
            True if exists
        """
        return self.resolve_path(path).exists()
    
    def is_file(self, path: Union[str, Path]) -> bool:
        """Check if path is a file.
        
        Args:
            path: Path to check
        
        Returns:
            True if is file
        """
        return self.resolve_path(path).is_file()
    
    def is_dir(self, path: Union[str, Path]) -> bool:
        """Check if path is a directory.
        
        Args:
            path: Path to check
        
        Returns:
            True if is directory
        """
        return self.resolve_path(path).is_dir()
    
    def get_size(self, path: Union[str, Path]) -> int:
        """Get file or directory size in bytes.
        
        Args:
            path: File or directory path
        
        Returns:
            Size in bytes
        """
        path = self.resolve_path(path)
        
        if not path.exists():
            raise SmartChunkFileNotFoundError(f"Path not found: {path}")
        
        if path.is_file():
            return path.stat().st_size
        
        # Directory size
        total_size = 0
        for file_path in path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        return total_size
    
    def get_modification_time(self, path: Union[str, Path]) -> datetime:
        """Get file modification time.
        
        Args:
            path: File path
        
        Returns:
            Modification time
        """
        path = self.resolve_path(path)
        
        if not path.exists():
            raise SmartChunkFileNotFoundError(f"File not found: {path}")
        
        return datetime.fromtimestamp(path.stat().st_mtime)
    
    def get_file_hash(self, path: Union[str, Path], algorithm: str = 'md5') -> str:
        """Calculate file hash.
        
        Args:
            path: File path
            algorithm: Hash algorithm ('md5', 'sha1', 'sha256')
        
        Returns:
            File hash
        """
        path = self.resolve_path(path)
        
        if not path.is_file():
            raise SmartChunkFileNotFoundError(f"File not found: {path}")
        
        hash_obj = hashlib.new(algorithm)
        
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    def get_mime_type(self, path: Union[str, Path]) -> Optional[str]:
        """Get file MIME type.
        
        Args:
            path: File path
        
        Returns:
            MIME type or None
        """
        path = self.resolve_path(path)
        
        if not path.is_file():
            return None
        
        if MAGIC_AVAILABLE:
            try:
                return magic.from_file(str(path), mime=True)
            except Exception:
                pass
        
        # Fallback to mimetypes
        mime_type, _ = mimetypes.guess_type(str(path))
        return mime_type
    
    def list_files(self, directory: Union[str, Path], 
                   pattern: str = '*', 
                   recursive: bool = False,
                   include_dirs: bool = False) -> List[Path]:
        """List files in directory.
        
        Args:
            directory: Directory path
            pattern: File pattern (glob)
            recursive: Search recursively
            include_dirs: Include directories in results
        
        Returns:
            List of file paths
        """
        directory = self.resolve_path(directory)
        
        if not directory.is_dir():
            raise SmartChunkFileNotFoundError(f"Directory not found: {directory}")
        
        if recursive:
            paths = directory.rglob(pattern)
        else:
            paths = directory.glob(pattern)
        
        results = []
        for path in paths:
            if include_dirs or path.is_file():
                results.append(path)
        
        return sorted(results)
    
    def copy_file(self, src: Union[str, Path], 
                  dst: Union[str, Path], 
                  overwrite: bool = False) -> Path:
        """Copy file.
        
        Args:
            src: Source file path
            dst: Destination file path
            overwrite: Overwrite if destination exists
        
        Returns:
            Destination path
        """
        src = self.resolve_path(src)
        dst = self.resolve_path(dst)
        
        if not src.is_file():
            raise SmartChunkFileNotFoundError(f"Source file not found: {src}")
        
        if dst.exists() and not overwrite:
            raise DataError(f"Destination already exists: {dst}")
        
        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(src, dst)
        return dst
    
    def move_file(self, src: Union[str, Path], 
                  dst: Union[str, Path], 
                  overwrite: bool = False) -> Path:
        """Move file.
        
        Args:
            src: Source file path
            dst: Destination file path
            overwrite: Overwrite if destination exists
        
        Returns:
            Destination path
        """
        src = self.resolve_path(src)
        dst = self.resolve_path(dst)
        
        if not src.exists():
            raise SmartChunkFileNotFoundError(f"Source not found: {src}")
        
        if dst.exists() and not overwrite:
            raise DataError(f"Destination already exists: {dst}")
        
        # Ensure destination directory exists
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(src), str(dst))
        return dst
    
    def delete_file(self, path: Union[str, Path], 
                    missing_ok: bool = False) -> bool:
        """Delete file or directory.
        
        Args:
            path: File or directory path
            missing_ok: Don't raise error if file doesn't exist
        
        Returns:
            True if deleted, False if didn't exist
        """
        path = self.resolve_path(path)
        
        if not path.exists():
            if missing_ok:
                return False
            raise SmartChunkFileNotFoundError(f"Path not found: {path}")
        
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
        
        return True
    
    def read_text(self, path: Union[str, Path], 
                  encoding: str = 'utf-8') -> str:
        """Read text file.
        
        Args:
            path: File path
            encoding: Text encoding
        
        Returns:
            File content
        """
        path = self.resolve_path(path)
        
        if not path.is_file():
            raise SmartChunkFileNotFoundError(f"File not found: {path}")
        
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError as e:
            raise InvalidFormatError(f"Cannot decode file {path}: {e}")
    
    def write_text(self, path: Union[str, Path], 
                   content: str, 
                   encoding: str = 'utf-8',
                   overwrite: bool = True) -> Path:
        """Write text file.
        
        Args:
            path: File path
            content: Text content
            encoding: Text encoding
            overwrite: Overwrite if file exists
        
        Returns:
            File path
        """
        path = self.resolve_path(path)
        
        if path.exists() and not overwrite:
            raise DataError(f"File already exists: {path}")
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(content, encoding=encoding)
        return path
    
    def read_binary(self, path: Union[str, Path]) -> bytes:
        """Read binary file.
        
        Args:
            path: File path
        
        Returns:
            File content
        """
        path = self.resolve_path(path)
        
        if not path.is_file():
            raise SmartChunkFileNotFoundError(f"File not found: {path}")
        
        return path.read_bytes()
    
    def write_binary(self, path: Union[str, Path], 
                     content: bytes,
                     overwrite: bool = True) -> Path:
        """Write binary file.
        
        Args:
            path: File path
            content: Binary content
            overwrite: Overwrite if file exists
        
        Returns:
            File path
        """
        path = self.resolve_path(path)
        
        if path.exists() and not overwrite:
            raise DataError(f"File already exists: {path}")
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_bytes(content)
        return path
    
    def read_json(self, path: Union[str, Path]) -> Any:
        """Read JSON file.
        
        Args:
            path: File path
        
        Returns:
            Parsed JSON data
        """
        content = self.read_text(path)
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise InvalidFormatError(f"Invalid JSON in {path}: {e}")
    
    def write_json(self, path: Union[str, Path], 
                   data: Any,
                   indent: int = 2,
                   overwrite: bool = True) -> Path:
        """Write JSON file.
        
        Args:
            path: File path
            data: Data to serialize
            indent: JSON indentation
            overwrite: Overwrite if file exists
        
        Returns:
            File path
        """
        try:
            content = json.dumps(data, indent=indent, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            raise InvalidFormatError(f"Cannot serialize data to JSON: {e}")
        
        return self.write_text(path, content, overwrite=overwrite)
    
    def read_yaml(self, path: Union[str, Path]) -> Any:
        """Read YAML file.
        
        Args:
            path: File path
        
        Returns:
            Parsed YAML data
        """
        content = self.read_text(path)
        
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise InvalidFormatError(f"Invalid YAML in {path}: {e}")
    
    def write_yaml(self, path: Union[str, Path], 
                   data: Any,
                   overwrite: bool = True) -> Path:
        """Write YAML file.
        
        Args:
            path: File path
            data: Data to serialize
            overwrite: Overwrite if file exists
        
        Returns:
            File path
        """
        try:
            content = yaml.dump(data, default_flow_style=False, 
                              allow_unicode=True, indent=2)
        except yaml.YAMLError as e:
            raise InvalidFormatError(f"Cannot serialize data to YAML: {e}")
        
        return self.write_text(path, content, overwrite=overwrite)
    
    def read_pickle(self, path: Union[str, Path]) -> Any:
        """Read pickle file.
        
        Args:
            path: File path
        
        Returns:
            Unpickled data
        """
        content = self.read_binary(path)
        
        try:
            return pickle.loads(content)
        except (pickle.PickleError, EOFError) as e:
            raise InvalidFormatError(f"Invalid pickle file {path}: {e}")
    
    def write_pickle(self, path: Union[str, Path], 
                     data: Any,
                     overwrite: bool = True) -> Path:
        """Write pickle file.
        
        Args:
            path: File path
            data: Data to pickle
            overwrite: Overwrite if file exists
        
        Returns:
            File path
        """
        try:
            content = pickle.dumps(data)
        except pickle.PickleError as e:
            raise InvalidFormatError(f"Cannot pickle data: {e}")
        
        return self.write_binary(path, content, overwrite=overwrite)
    
    def create_archive(self, source_path: Union[str, Path], 
                      archive_path: Union[str, Path],
                      format: str = 'zip',
                      compression: Optional[str] = None) -> Path:
        """Create archive from directory or files.
        
        Args:
            source_path: Source directory or file
            archive_path: Archive file path
            format: Archive format ('zip', 'tar', 'tar.gz', 'tar.bz2')
            compression: Compression level
        
        Returns:
            Archive file path
        """
        source_path = self.resolve_path(source_path)
        archive_path = self.resolve_path(archive_path)
        
        if not source_path.exists():
            raise SmartChunkFileNotFoundError(f"Source not found: {source_path}")
        
        # Ensure archive directory exists
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'zip':
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                if source_path.is_file():
                    zf.write(source_path, source_path.name)
                else:
                    for file_path in source_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source_path)
                            zf.write(file_path, arcname)
        
        elif format.startswith('tar'):
            mode = 'w'
            if format == 'tar.gz':
                mode = 'w:gz'
            elif format == 'tar.bz2':
                mode = 'w:bz2'
            
            with tarfile.open(archive_path, mode) as tf:
                if source_path.is_file():
                    tf.add(source_path, source_path.name)
                else:
                    tf.add(source_path, source_path.name)
        
        else:
            raise InvalidFormatError(f"Unsupported archive format: {format}")
        
        return archive_path
    
    def extract_archive(self, archive_path: Union[str, Path], 
                       extract_path: Union[str, Path],
                       overwrite: bool = False) -> Path:
        """Extract archive.
        
        Args:
            archive_path: Archive file path
            extract_path: Extraction directory
            overwrite: Overwrite existing files
        
        Returns:
            Extraction directory path
        """
        archive_path = self.resolve_path(archive_path)
        extract_path = self.resolve_path(extract_path)
        
        if not archive_path.is_file():
            raise SmartChunkFileNotFoundError(f"Archive not found: {archive_path}")
        
        if extract_path.exists() and not overwrite:
            raise DataError(f"Extract path already exists: {extract_path}")
        
        # Ensure extract directory exists
        extract_path.mkdir(parents=True, exist_ok=True)
        
        # Detect archive format
        if archive_path.suffix.lower() == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(extract_path)
        
        elif archive_path.suffix.lower() in ['.tar', '.gz', '.bz2'] or '.tar.' in archive_path.name.lower():
            with tarfile.open(archive_path, 'r:*') as tf:
                tf.extractall(extract_path)
        
        else:
            raise InvalidFormatError(f"Unsupported archive format: {archive_path.suffix}")
        
        return extract_path


class FileWatcher:
    """File system watcher."""
    
    def __init__(self, path: Union[str, Path], 
                 recursive: bool = True):
        if not WATCHDOG_AVAILABLE:
            raise ImportError("watchdog package is required for file watching")
        
        self.path = Path(path)
        self.recursive = recursive
        self.observer = Observer()
        self.handlers = []
    
    def add_handler(self, handler: FileSystemEventHandler):
        """Add event handler.
        
        Args:
            handler: Event handler
        """
        self.handlers.append(handler)
        self.observer.schedule(handler, str(self.path), recursive=self.recursive)
    
    def start(self):
        """Start watching."""
        self.observer.start()
    
    def stop(self):
        """Stop watching."""
        self.observer.stop()
        self.observer.join()
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def safe_filename(filename: str, replacement: str = '_') -> str:
    """Create safe filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        replacement: Replacement character for invalid chars
    
    Returns:
        Safe filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename
    
    for char in invalid_chars:
        safe_name = safe_name.replace(char, replacement)
    
    # Remove control characters
    safe_name = ''.join(char for char in safe_name if ord(char) >= 32)
    
    # Limit length
    if len(safe_name) > 255:
        name, ext = os.path.splitext(safe_name)
        max_name_len = 255 - len(ext)
        safe_name = name[:max_name_len] + ext
    
    # Ensure not empty
    if not safe_name.strip():
        safe_name = 'unnamed'
    
    return safe_name.strip()


def get_unique_filename(path: Union[str, Path], 
                       suffix_format: str = '_{:03d}') -> Path:
    """Get unique filename by adding suffix if file exists.
    
    Args:
        path: Original file path
        suffix_format: Format for suffix (should contain one integer placeholder)
    
    Returns:
        Unique file path
    """
    path = Path(path)
    
    if not path.exists():
        return path
    
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    
    counter = 1
    while True:
        new_name = f"{stem}{suffix_format.format(counter)}{suffix}"
        new_path = parent / new_name
        
        if not new_path.exists():
            return new_path
        
        counter += 1
        
        # Prevent infinite loop
        if counter > 9999:
            raise DataError(f"Cannot create unique filename for {path}")


def find_files_by_extension(directory: Union[str, Path], 
                           extensions: Union[str, List[str]],
                           recursive: bool = True) -> List[Path]:
    """Find files by extension.
    
    Args:
        directory: Directory to search
        extensions: File extension(s) to search for
        recursive: Search recursively
    
    Returns:
        List of matching files
    """
    directory = Path(directory)
    
    if isinstance(extensions, str):
        extensions = [extensions]
    
    # Normalize extensions
    extensions = [ext.lower().lstrip('.') for ext in extensions]
    
    files = []
    
    if recursive:
        pattern = '**/*'
    else:
        pattern = '*'
    
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            file_ext = file_path.suffix.lower().lstrip('.')
            if file_ext in extensions:
                files.append(file_path)
    
    return sorted(files)


def get_directory_tree(directory: Union[str, Path], 
                      max_depth: Optional[int] = None,
                      include_files: bool = True) -> Dict[str, Any]:
    """Get directory tree structure.
    
    Args:
        directory: Directory path
        max_depth: Maximum depth to traverse
        include_files: Include files in tree
    
    Returns:
        Directory tree structure
    """
    directory = Path(directory)
    
    if not directory.is_dir():
        raise SmartChunkFileNotFoundError(f"Directory not found: {directory}")
    
    def _build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
        if max_depth is not None and current_depth >= max_depth:
            return {}
        
        tree = {
            'name': path.name,
            'type': 'directory',
            'path': str(path),
            'children': {}
        }
        
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    tree['children'][item.name] = _build_tree(item, current_depth + 1)
                elif include_files and item.is_file():
                    tree['children'][item.name] = {
                        'name': item.name,
                        'type': 'file',
                        'path': str(item),
                        'size': item.stat().st_size
                    }
        except PermissionError:
            tree['error'] = 'Permission denied'
        
        return tree
    
    return _build_tree(directory)


def calculate_directory_size(directory: Union[str, Path]) -> Dict[str, int]:
    """Calculate directory size statistics.
    
    Args:
        directory: Directory path
    
    Returns:
        Size statistics
    """
    directory = Path(directory)
    
    if not directory.is_dir():
        raise SmartChunkFileNotFoundError(f"Directory not found: {directory}")
    
    total_size = 0
    file_count = 0
    dir_count = 0
    
    for item in directory.rglob('*'):
        if item.is_file():
            total_size += item.stat().st_size
            file_count += 1
        elif item.is_dir():
            dir_count += 1
    
    return {
        'total_size': total_size,
        'file_count': file_count,
        'directory_count': dir_count,
        'average_file_size': total_size // file_count if file_count > 0 else 0
    }


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
    
    Returns:
        Directory path
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(path: Union[str, Path]) -> int:
    """Get file size in bytes.
    
    Args:
        path: File path
    
    Returns:
        File size in bytes
    """
    path = Path(path)
    if not path.exists():
        raise SmartChunkFileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise DataError(f"Path is not a file: {path}")
    return path.stat().st_size


def get_file_extension(path: Union[str, Path]) -> str:
    """Get file extension.
    
    Args:
        path: File path
    
    Returns:
        File extension (without dot)
    """
    path = Path(path)
    return path.suffix.lstrip('.')


def is_pdf_file(path: Union[str, Path]) -> bool:
    """Check if file is a PDF.
    
    Args:
        path: File path
    
    Returns:
        True if file is PDF
    """
    path = Path(path)
    if not path.exists() or not path.is_file():
        return False
    
    # Check extension
    if path.suffix.lower() != '.pdf':
        return False
    
    # Check magic bytes
    try:
        with open(path, 'rb') as f:
            header = f.read(4)
            return header == b'%PDF'
    except (IOError, OSError):
        return False


def create_temp_file(suffix: str = '', prefix: str = 'tmp', 
                    dir: Optional[Union[str, Path]] = None,
                    delete: bool = True) -> Path:
    """Create temporary file.
    
    Args:
        suffix: File suffix
        prefix: File prefix
        dir: Directory for temp file
        delete: Delete file when closed
    
    Returns:
        Temporary file path
    """
    import tempfile
    
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir)
    os.close(fd)  # Close file descriptor
    
    temp_path = Path(path)
    
    if delete:
        # Register for cleanup
        import atexit
        atexit.register(lambda: temp_path.unlink(missing_ok=True))
    
    return temp_path


def safe_file_write(path: Union[str, Path], content: Union[str, bytes],
                   encoding: str = 'utf-8', backup: bool = True) -> Path:
    """Safely write to file with backup.
    
    Args:
        path: File path
        content: Content to write
        encoding: Text encoding (for string content)
        backup: Create backup if file exists
    
    Returns:
        File path
    """
    path = Path(path)
    
    # Create backup if file exists
    if backup and path.exists():
        backup_path = path.with_suffix(path.suffix + '.bak')
        import shutil
        shutil.copy2(path, backup_path)
    
    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write content
    if isinstance(content, str):
        path.write_text(content, encoding=encoding)
    else:
        path.write_bytes(content)
    
    return path


def backup_file(path: Union[str, Path], backup_dir: Optional[Union[str, Path]] = None) -> Path:
    """Create backup of file.
    
    Args:
        path: File path to backup
        backup_dir: Directory for backup (default: same directory)
    
    Returns:
        Backup file path
    """
    import shutil
    from datetime import datetime
    
    path = Path(path)
    if not path.exists():
        raise SmartChunkFileNotFoundError(f"File not found: {path}")
    
    if backup_dir:
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}"
    else:
        backup_path = path.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}")
    
    shutil.copy2(path, backup_path)
    return backup_path