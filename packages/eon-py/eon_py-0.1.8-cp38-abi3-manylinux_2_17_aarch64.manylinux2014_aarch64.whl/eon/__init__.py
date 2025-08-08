"""
EON (Extensible Object Notation) - Python bindings

A human-friendly configuration format that's a superset of JSON.
"""

# Import the compiled Rust functions
from ._eon import loads as _loads, dumps as _dumps

__all__ = ['loads', 'dumps', 'load', 'dump']
__version__ = '0.1.0'

def loads(s, **kwargs):
    """
    Parse an EON string into a Python object.
    
    Args:
        s: EON formatted string to parse
        
    Returns:
        Python object (dict, list, str, int, float, bool, None)
        
    Raises:
        ValueError: If the EON string is invalid
    """
    return _loads(s)

def dumps(obj, indent=None, sort_keys=False):
    """
    Serialize a Python object to an EON formatted string.
    
    Args:
        obj: Python object to serialize
        indent: Number of spaces for indentation (None for compact output)
        sort_keys: Whether to sort dictionary keys
        
    Returns:
        EON formatted string
        
    Raises:
        ValueError: If the object cannot be serialized to EON
    """
    return _dumps(obj, indent=indent, sort_keys=sort_keys)

def load(fp, **kwargs):
    """
    Parse an EON document from a file-like object.
    
    Args:
        fp: File-like object with a read() method
        
    Returns:
        Python object
        
    Raises:
        ValueError: If the EON content is invalid
    """
    return loads(fp.read(), **kwargs)

def dump(obj, fp, **kwargs):
    """
    Serialize a Python object to an EON document in a file-like object.
    
    Args:
        obj: Python object to serialize
        fp: File-like object with a write() method
        **kwargs: Additional arguments passed to dumps()
    """
    fp.write(dumps(obj, **kwargs))