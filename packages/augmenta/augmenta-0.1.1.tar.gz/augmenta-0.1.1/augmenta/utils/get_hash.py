"""Utility functions and classes for the Augmenta package."""

import json
import hashlib
from pathlib import Path
from typing import Union

# logging
import logging
import logfire
logging.basicConfig(handlers=[logfire.LogfireLoggingHandler()])
logger = logging.getLogger(__name__)

def get_hash(data: Union[dict, Path, str], chunk_size: int = 8192) -> str:
    """Generate a deterministic hash of data or file contents."""
    hasher = hashlib.sha256()
    
    if isinstance(data, dict):
        hasher.update(json.dumps(data, sort_keys=True).encode('utf-8'))
    elif isinstance(data, (str, Path)):
        filepath = Path(data)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
            
        with open(filepath, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
    else:
        raise TypeError("Data must be a dictionary, Path, or string filepath")
        
    return hasher.hexdigest()
