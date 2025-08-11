import os
import json
from typing import Dict, Any, Optional

def read_file_content(file_path: str) -> str:
    """Read file content and return as string"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"Error reading file {file_path}: {e}")

def write_file_content(file_path: str, content: str) -> None:
    """Write content to file"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"Error writing file {file_path}: {e}")

def detect_language(file_path: str) -> str:
    """Detect programming language from file extension"""
    ext = os.path.splitext(file_path)[1].lower()
    
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
    }
    
    return language_map.get(ext, 'unknown')

def detect_framework(file_path: str, language: str) -> str:
    """Detect testing framework based on file content and language"""
    if language == 'python':
        return 'pytest'  # Default for Python
    elif language in ['javascript', 'typescript']:
        return 'jest'  # Default for JS/TS
    else:
        return 'unknown' 