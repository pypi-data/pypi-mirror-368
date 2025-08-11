# from asyncio.unix_events import FastChildWatcher
# from pickletools import pybytes_or_str
from sqlalchemy import false
from cli.auth import get_authenticated_user
# from traceback import print_tb
import click
import requests
import json
import os
import sys
from typing import Optional
from pathlib import Path


# Backend API configuration
BACKEND_API_URL = "https://testgenie.fly.dev"

@click.group()
def online():
    """Online mode - Generate tests using online AI agents"""
    pass

def get_auth_token() -> Optional[str]:
    """Get authentication token from CLI config"""
    config_path = Path.home() / ".testgenie" / "config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('token')
        except:
            return None
    return None

def make_authenticated_request(endpoint: str, method: str = "GET", data: dict = None) -> Optional[dict]:
    """Make authenticated request to backend API"""
    token = get_auth_token()
    if not token:
        click.echo("❌ Not logged in. Please run 'test_genie login' first.")
        return None
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    #print("header:", headers)
    #print("data", data)
    
    url = f"{BACKEND_API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            click.echo(f"Unsupported method: {method}")
            return None
        
        if response.status_code == 401:
            click.echo("❌ Token expired. Please login again with 'test_genie login'")
            return None
        elif response.status_code != 200:
            click.echo(f"❌ API Error: {response.status_code} - {response.text}")
            return None
        
        return response.json()
    
    except requests.RequestException as e:
        click.echo(f"❌ Connection error: {e}")
        return None

def log_usage_to_backend(language: str, tokens_used: int = 0):
    """Log usage to backend for analytics"""
    data = {
        "language": language,
        "tokens_used": tokens_used,
    }
    #print("DATA: ", data)
    make_authenticated_request("/cli/usage", method="POST", data=data)

def read_file_content(file_path: str) -> str:
    """Read and return the content of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        click.echo(f"Error reading file {file_path}: {e}")
        sys.exit(1)

def detect_language(file_path: str) -> str:
    """Detect programming language from file extension"""
    ext = Path(file_path).suffix.lower()
    language_map = {
        '.py': 'python',
        '.cpp': 'cpp',
        '.c': 'c',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby'
    }
    return language_map.get(ext, 'unknown')


def save_test_file(file_path: str, test_content: str, language: str, framework: str, positive_cases: int, negative_cases: int, output_path: Optional[str] = None) -> str:
    """Save generated test cases to a file with proper naming and includes"""
    
    if output_path is None:
        # Generate output path based on input file - FIXED: Remove double dots
        input_path = Path(file_path)
        # Fix the double dot issue by properly handling the extension
        if input_path.suffix:
            output_path = input_path.parent / f"test_{input_path.stem}{input_path.suffix}"
        else:
            output_path = input_path.parent / f"test_{input_path.name}"
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Add imports and main execution based on language and framework
    if language == 'python':
        if framework == 'pytest':
            # For pytest, just add the test content
            import_statement = f"from {Path(file_path).stem} import *\n\n"
            full_content = import_statement + test_content
            test_execution = "\n# Run all test cases\n"
            for i in range(1, positive_cases + 1):
                test_execution += f"positive_test_case_{i}()\n"
            for i in range(1, negative_cases + 1):
                test_execution += f"negative_test_case_{i}()\n"
            test_execution += f"print('ALL TEST CASES PASSED!')"
            full_content = full_content + test_execution
        
        elif framework == 'unittest':
            # For unittest, add proper class structure
            import_statement = f"import unittest\nfrom {Path(file_path).stem} import *\n\n"
            class_start = "class TestSuite(unittest.TestCase):\n"
            class_end = "\n\nif __name__ == '__main__':\n    unittest.main()\n"
            
            # Indent the test content for unittest class
            indented_content = "\n".join("    " + line if line.strip() else line for line in test_content.split('\n'))
            full_content = import_statement + class_start + indented_content + class_end

    
    elif language == 'cpp':
        # FIXED: Include the original C++ file header
        original_file_name = Path(file_path).name
        includes = f"#include <iostream>\n#include <exception>\n#include \"{original_file_name}\"\n\n"
        
        if framework == 'gtest':
            # For gtest, add proper includes
            gtest_includes = f"#include <gtest/gtest.h>\n\n#include \"{original_file_name}\"\n\n"
            full_content = gtest_includes + test_content
        
        else:
            # Default format (your original)
            main_function = "\nint main() {\n    std::cout << \"Running all test cases...\\n\";\n"
            # FIXED: Call all test cases based on user input
            for i in range(1, positive_cases + 1):
                main_function += f"    positive_test_case_{i}();\n"
            for i in range(1, negative_cases + 1):
                main_function += f"    negative_test_case_{i}();\n"
            main_function += "    return 0;\n}\n"
            
            full_content = includes + test_content + main_function
    
    else:
        full_content = test_content
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return str(output_path)

def user_login():
    os.system("test-genie login")
    user = get_authenticated_user()
    if not user:
        return None
    return user
