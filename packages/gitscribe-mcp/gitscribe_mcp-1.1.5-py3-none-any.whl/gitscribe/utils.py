"""
Utility functions and helpers for GitScribe.
"""

import os
import re
import logging
import hashlib
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('gitscribe.log')
        ]
    )


def normalize_url(url: str, base_url: str = None) -> str:
    """Normalize URL by resolving relative paths."""
    if base_url:
        return urljoin(base_url, url)
    return url


def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def clean_text(text: str) -> str:
    """Clean and normalize text content."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\-\.\,\;\:\!\?\(\)\[\]\"\'\/]', '', text)
    
    return text.strip()


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        return urlparse(url).netloc
    except:
        return ""


def generate_content_hash(content: str) -> str:
    """Generate SHA-256 hash of content."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """Split text into overlapping chunks."""
    if not text or chunk_size <= 0:
        return []
    
    chunks = []
    words = text.split()
    
    if len(words) <= chunk_size:
        return [{
            'text': text,
            'start': 0,
            'end': len(text),
            'word_count': len(words)
        }]
    
    start_idx = 0
    chunk_id = 0
    
    while start_idx < len(words):
        end_idx = min(start_idx + chunk_size, len(words))
        chunk_words = words[start_idx:end_idx]
        chunk_text = ' '.join(chunk_words)
        
        chunks.append({
            'id': chunk_id,
            'text': chunk_text,
            'start_word': start_idx,
            'end_word': end_idx,
            'word_count': len(chunk_words),
            'char_count': len(chunk_text)
        })
        
        # Move start index forward, accounting for overlap
        start_idx = max(start_idx + chunk_size - overlap, start_idx + 1)
        chunk_id += 1
        
        # Break if we're at the end
        if end_idx >= len(words):
            break
    
    return chunks


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage."""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove excessive dots and spaces
    filename = re.sub(r'\.+', '.', filename)
    filename = re.sub(r'\s+', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename.strip('._')


def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if necessary."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}")
        return False


def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase."""
    return Path(filename).suffix.lower().lstrip('.')


def is_text_file(content: bytes, filename: str = "") -> bool:
    """Check if content represents a text file."""
    # Check file extension
    text_extensions = {
        'txt', 'md', 'markdown', 'rst', 'html', 'htm', 'xml', 'json', 'yaml', 'yml',
        'py', 'js', 'ts', 'java', 'cpp', 'c', 'h', 'go', 'rs', 'rb', 'php', 'css',
        'scss', 'less', 'sql', 'sh', 'bat', 'ps1', 'r', 'jl', 'scala', 'kt'
    }
    
    if filename:
        ext = get_file_extension(filename)
        if ext in text_extensions:
            return True
    
    # Check content for binary indicators
    try:
        # Try to decode as UTF-8
        content.decode('utf-8')
        
        # Check for null bytes (common in binary files)
        if b'\x00' in content[:1024]:
            return False
        
        # Check for high ratio of non-printable characters
        printable_chars = sum(1 for b in content[:1024] if 32 <= b <= 126 or b in [9, 10, 13])
        if len(content) > 0 and printable_chars / min(len(content), 1024) < 0.7:
            return False
        
        return True
    except UnicodeDecodeError:
        return False


def rate_limit_delay(last_request_time: float, min_delay: float) -> None:
    """Apply rate limiting delay."""
    elapsed = time.time() - last_request_time
    if elapsed < min_delay:
        time.sleep(min_delay - elapsed)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def extract_title_from_content(content: str, filename: str = "") -> str:
    """Extract title from content or use filename."""
    if not content:
        return filename or "Untitled"
    
    lines = content.strip().split('\n')
    
    # Try to find title in various formats
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if not line:
            continue
        
        # Markdown heading
        if line.startswith('#'):
            return line.lstrip('#').strip()
        
        # HTML title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', line, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        
        # reStructuredText title (line followed by ===)
        if len(lines) > lines.index(line) + 1:
            next_line = lines[lines.index(line) + 1].strip()
            if next_line and all(c in '=-~^"' for c in next_line):
                return line
        
        # If it's the first non-empty line and looks like a title
        if line and len(line) < 100 and not line.endswith('.'):
            return line
    
    # Fallback to filename
    return filename or "Untitled"


def validate_config(config: Dict) -> List[str]:
    """Validate configuration settings."""
    errors = []
    
    required_fields = ['server_name', 'server_version']
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate numeric fields
    numeric_fields = {
        'max_depth': (1, 10),
        'max_pages': (1, 10000),
        'timeout': (1, 300),
        'chunk_size': (100, 10000),
        'chunk_overlap': (0, 1000)
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        if field in config:
            try:
                value = int(config[field])
                if not (min_val <= value <= max_val):
                    errors.append(f"{field} must be between {min_val} and {max_val}")
            except (ValueError, TypeError):
                errors.append(f"{field} must be a valid integer")
    
    return errors


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Recursively merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def safe_get_nested(data: Dict, keys: List[str], default: Any = None) -> Any:
    """Safely get nested dictionary value."""
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return default
    return data


class ProgressTracker:
    """Simple progress tracker for long-running operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, increment: int = 1):
        """Update progress."""
        self.current += increment
        if self.current % 10 == 0 or self.current == self.total:
            self._log_progress()
    
    def _log_progress(self):
        """Log current progress."""
        if self.total > 0:
            percentage = (self.current / self.total) * 100
            elapsed = time.time() - self.start_time
            
            if self.current > 0 and elapsed > 0:
                rate = self.current / elapsed
                eta = (self.total - self.current) / rate if rate > 0 else 0
                logger.info(
                    f"{self.description}: {self.current}/{self.total} "
                    f"({percentage:.1f}%) - ETA: {eta:.1f}s"
                )


class Cache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self, default_ttl: int = 3600):
        self.cache = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            value, expiry = self.cache[key]
            if time.time() < expiry:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache."""
        if ttl is None:
            ttl = self.default_ttl
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
    
    def size(self) -> int:
        """Get cache size."""
        return len(self.cache)
