"""
Shared file utility functions for TestGenie
"""

import os
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional

def find_code_files(directory: str, extensions: List[str] = None) -> List[str]:
    """Find all code files in a directory"""
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']
    
    code_files = []
    for ext in extensions:
        pattern = os.path.join(directory, f"**/*{ext}")
        code_files.extend(glob.glob(pattern, recursive=True))
    
    return sorted(code_files)

def read_file_safe(file_path: str) -> Optional[str]:
    """Safely read a file, returning None if it fails"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (IOError, UnicodeDecodeError):
        return None

def write_file_safe(file_path: str, content: str) -> bool:
    """Safely write content to a file"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except IOError:
        return False

def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get information about a file"""
    try:
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'extension': Path(file_path).suffix,
            'name': Path(file_path).name,
            'directory': str(Path(file_path).parent)
        }
    except OSError:
        return {}

def is_test_file(file_path: str) -> bool:
    """Check if a file is a test file"""
    test_patterns = [
        'test_', '_test', 'Test', 'spec_', '_spec'
    ]
    
    filename = Path(file_path).name.lower()
    return any(pattern in filename for pattern in test_patterns)

def get_output_path(input_path: str, output_dir: str = None, suffix: str = "_test") -> str:
    """Generate an output path for test files"""
    input_path = Path(input_path)
    
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = input_path.parent
    
    # Create test filename
    stem = input_path.stem
    if not stem.endswith('_test'):
        stem = f"{stem}{suffix}"
    
    return str(output_path / f"{stem}{input_path.suffix}")

def create_test_directory(project_path: str) -> str:
    """Create a tests directory in the project"""
    project_path = Path(project_path)
    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    return str(tests_dir)

def get_project_structure(directory: str) -> Dict[str, Any]:
    """Get the structure of a project directory"""
    structure = {
        'code_files': [],
        'test_files': [],
        'directories': [],
        'total_files': 0
    }
    
    for root, dirs, files in os.walk(directory):
        # Skip common directories that shouldn't be processed
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv']]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, directory)
            
            if is_test_file(file_path):
                structure['test_files'].append(rel_path)
            else:
                structure['code_files'].append(rel_path)
            
            structure['total_files'] += 1
        
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(dir_path, directory)
            structure['directories'].append(rel_path)
    
    return structure 