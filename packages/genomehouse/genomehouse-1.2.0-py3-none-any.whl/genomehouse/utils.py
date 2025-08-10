"""
Utility Functions for GenomeHouse
"""
import os
import gzip

def read_file(file_path):
    """Read a text file (supports .gz)."""
    if file_path.endswith('.gz'):
        with gzip.open(file_path, 'rt') as f:
            return f.read()
    else:
        with open(file_path, 'r') as f:
            return f.read()

def write_file(file_path, content):
    """Write content to a text file."""
    with open(file_path, 'w') as f:
        f.write(content)

def file_exists(file_path):
    """Check if a file exists."""
    return os.path.isfile(file_path)
