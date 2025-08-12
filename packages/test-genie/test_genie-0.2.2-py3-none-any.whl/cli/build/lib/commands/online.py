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

# Your existing AI API configuration
MISTRAL_API_KEY = "d6wPM9KBGWVHWX6XdoZRCviMsOnOPueb"
CPP_AGENT_ID = "ag:106ab62c:20250728:cpp-test-genie:a96dbee7"
PYTHON_AGENT_ID = "ag:106ab62c:20250731:py-test-genie:8ab521b4"

# Backend API configuration
BACKEND_API_URL = "http://localhost:8000"

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

def get_python_test_prompt(code_content: str, framework: str, positive_cases: int = 2, negative_cases: int = 2) -> str:
    """Generate prompt for Python test case generation based on framework"""
    
    if framework == 'pytest':
        def get_all_positive_cases(count):
            s = ""
            for i in range(1, count + 1):
                s += f"""def positive_test_case_{i}():
                        \"\"\"Test positive case {i}\"\"\"
                        # TODO: Add your test logic here
                        assert True  # Replace with actual assertions
                    """
            return s

        def get_all_negative_cases(count):
            s = ""
            for i in range(1, count + 1):
                s += f"""def negative_test_case_{i}():
                        \"\"\"Test negative case {i}\"\"\"
                        # TODO: Add your test logic here
                        assert True  # Replace with actual assertions
                    """
            return s

        return (
            "You are an expert software tester. "
            f"Given the following code, generate {positive_cases} positive (valid input) and {negative_cases} negative (invalid or edge case input) test cases using pytest. "
            "Return only executable pytest code for these test cases, without any explanation or comments. "
            "Use proper pytest assertions and test naming conventions. "
            "Format your response as:\n"
            "# Positive Test Cases:\n"
            f"{get_all_positive_cases(positive_cases)}"
            "\n# Negative Test Cases:\n"
            f"{get_all_negative_cases(negative_cases)}"
            "\nGenerate actual test logic with proper assertions.\n"
            "\nIncase of any errors, raise appropriate exceptions with clear messages in all test cases. Respond only with the logical test cases itself.\n"
            "Code:\n"
            f"{code_content}"
        )
    
    elif framework == 'unittest':
        def get_all_positive_cases(count):
            s = ""
            for i in range(1, count + 1):
                s += f"""def test_positive_case_1{i}(self):
                        \"\"\"Test positive case {i}\"\"\"
                        # TODO: Add your test logic here
                        self.assertTrue(True)  # Replace with actual assertions
                    """
            return s

        def get_all_negative_cases(count):
            s = ""
            for i in range(1, count + 1):
                s += f"""def test_negative_case_1{i}(self):
                        \"\"\"Test negative case {i}\"\"\"
                        # TODO: Add your test logic here
                        self.assertTrue(True)  # Replace with actual assertions
                    """
            return s

        return (
            "You are an expert software tester. "
            f"Given the following code, generate {positive_cases} positive (valid input) and {negative_cases} negative (invalid or edge case input) unit test cases."
            "Return only executable python code for these test cases, without any explanation or comments. "
            "Use proper assertions and test naming conventions. "
            "Format your response as:\n"
            "# Positive Test Cases:\n"
            f"{get_all_positive_cases(positive_cases)}"
            "\n# Negative Test Cases:\n"
            f"{get_all_negative_cases(negative_cases)}"
            "\nGenerate actual test logic with proper assertions.\n"
            "\nIncase of any errors, raise appropriate exceptions with clear messages in all test cases. Respond only with the logical test cases itself.\n"
            "Code:\n"
            f"{code_content}"
        )
    
    else:
        # Default to your original format
        def get_all_positive_cases(count):
            s = ""
            for i in range(1, count + 1):
                s += f"def positive_test_case_{i}():\n  try:\n...\n     print('Passed Positive Test Case {i}')\n    except Exception as e:\n        print(f'Failed at positive test case {i}: e')\n..."
            return s

        def get_all_negative_cases(count):
            s = ""
            for i in range(1, count + 1):
                s += f"def negative_test_case_{i}():\n  try:\n...\n     print('Passed Negative Test Case {i}')\n  except Exception as e:\n        print(f'Failed at negative test case {i}: e')\n..."
            return s

        return (
            "You are an expert software tester. "
            f"Given the following code, generate {positive_cases} positive (valid input) and {negative_cases} negative (invalid or edge case input) test cases. "
            "Return only executable code for these test cases, without any explanation or comments. "
            "Format your response as:\n"
            "# Positive Test Cases:\n"
            f"{get_all_positive_cases(positive_cases)}"
            "\n# Negative Test Cases:\n"
            f"{get_all_negative_cases(negative_cases)}"
            "\nIncase of any errors, raise appropriate exceptions with clear messages in all test cases. Respond only with the logical test cases itself.\n"
            "Code:\n"
            f"{code_content}"
        )

def get_cpp_test_prompt(code_content: str, framework: str, positive_cases: int = 2, negative_cases: int = 2) -> str:
    """Generate prompt for C++ test case generation based on framework"""
    
    if framework == 'gtest':
        def get_all_positive_cases(count):
            s = ""
            for i in range(1, count + 1):
                s += f"""TEST(TestSuite, PositiveCase{i}) {{
                            // TODO: Add your test logic here
                            EXPECT_TRUE(true);  // Replace with actual assertions
                        }}
                    """
            return s

        def get_all_negative_cases(count):
            s = ""
            for i in range(1, count + 1):
                s += f"""TEST(TestSuite, NegativeCase{i}) {{
                            // TODO: Add your test logic here
                            EXPECT_TRUE(true);  // Replace with actual assertions
                        }}
                    """
            return s

        return (
            "You are an expert C++ software tester. "
            f"Given the following code, generate {positive_cases} positive (valid input) and {negative_cases} negative (invalid or edge case input) test cases using Google Test (gtest). "
            "Return only executable gtest code for these test cases, without any explanation or comments. "
            "Use proper gtest assertions and test naming conventions. "
            "Format your response as:\n"
            "// Positive Test Cases:\n"
            f"{get_all_positive_cases(positive_cases)}"
            "\n// Negative Test Cases:\n"
            f"{get_all_negative_cases(negative_cases)}"
            "\nIncase of any errors, raise appropriate exceptions with clear messages in all test cases. Respond only with the logical test cases itself.\n"
            "\nGenerate actual test logic with proper assertions.\n"
            "Code:\n"
            f"{code_content}"
        )
    
    else:
        # Default to your original format
        def get_all_positive_cases(count):
            s = ""
            for i in range(1, count + 1):
                s += f"""void positive_test_case_{i}() {{
                            try {{
                                // ...
                                std::cout << "Passed Positive Test Case {i}\\n";
                            }} catch (const std::exception& e) {{
                                std::cout << "Failed at positive test case {i}: " << e.what() << "\\n";
                            }}
                        }}
                    """
            return s

        def get_all_negative_cases(count):
            s = ""
            for i in range(1, count + 1):
                s += f"""void negative_test_case_{i}() {{
                            try {{
                                // ...
                                std::cout << "Passed Negative Test Case {i}\\n";
                            }} catch (const std::exception& e) {{
                                std::cout << "Failed at negative test case {i}: " << e.what() << "\\n";
                            }}
                        }}
                    """
            return s

        return (
            "You are an expert C++ software tester. "
            "Only write test case functions as specified below. Do not write any other functions or logical code. "
            f"\nGiven the following code, generate {positive_cases} positive (valid input) and {negative_cases} negative (invalid or edge case input) test cases. "
            "Return only executable C++ test cases, without any explanation or comments. "
            "Format your response as:\n"
            "// Positive Test Cases\n"
            f"{get_all_positive_cases(positive_cases)}"
            "\n// Negative Test Cases\n"
            f"{get_all_negative_cases(negative_cases)}"
            "\nHandle all exceptions with clear messages.\nRespond only with the logical test cases itself.\n"
            "Code:\n"
            f"{code_content}"
        )

def get_response_from_python_agent(prompt: str, agent_id: Optional[str] = None) -> Optional[str]:
    """Get response from Mistral AI agent using your existing implementation"""
    
    url = "https://api.mistral.ai/v1/agents/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "agent_id": agent_id or PYTHON_AGENT_ID,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "n": 1,
        "max_tokens": 2048,
        "prompt_mode": "reasoning",  # Use reasoning mode for better results
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            click.echo(f"Error: {response.status_code} - {response.text}")
            return None
        else:
            response_json = response.json()
            output = response_json["choices"][0]["message"]["content"]
            return output
    except Exception as e:
        click.echo(f"Error calling Mistral API: {e}")
        return None

def get_response_from_cpp_agent(prompt: str, agent_id: Optional[str] = None) -> Optional[str]:
    """Get response from Mistral AI agent using your existing implementation"""
    
    url = "https://api.mistral.ai/v1/agents/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "agent_id": agent_id or CPP_AGENT_ID,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "n": 1,
        "max_tokens": 2048,
        "prompt_mode": "reasoning",  # Use reasoning mode for better results
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            click.echo(f"Error: {response.status_code} - {response.text}")
            return None
        else:
            response_json = response.json()
            output = response_json["choices"][0]["message"]["content"]
            return output
    except Exception as e:
        click.echo(f"Error calling Mistral API: {e}")
        return None


def generate_test_cases(file_path: str, language: str, framework: str, positive_cases: int = 2, negative_cases: int = 2) -> Optional[str]:
    """Generate test cases using AI based on language and framework"""
    
    # Read the source code
    code_content = read_file_content(file_path)
    
    if language == 'python':
        if framework == 'gtest':
            return "PYTHON DOES NOT SUPPORT GTEST FRAMEWORK"
        # Use agent completion for C++
        prompt = get_python_test_prompt(code_content, framework, positive_cases, negative_cases)
        suffix = f"# The above are the {positive_cases} positive and {negative_cases} negative test cases for the provided code."
        # print(prompt)
        # print(suffix)
        full_prompt = prompt + "\n" + suffix
        return get_response_from_python_agent(full_prompt, PYTHON_AGENT_ID)
    
    elif language == 'cpp':
        if framework == 'pytest':
            return "NOT SUPPORTED!"
        # Use agent completion for C++
        prompt = get_cpp_test_prompt(code_content, framework, positive_cases, negative_cases)
        suffix = f"// The above are the {positive_cases} positive and {negative_cases} negative test cases for the provided code."
        full_prompt = prompt + "\n" + suffix
        return get_response_from_cpp_agent(full_prompt, CPP_AGENT_ID)
    
    # else:
    #     print("NOT SUPPORTED!")
    #     return "NOT SUPPORTED!"
        # Generic approach for other languages
        # prompt = f"""You are an expert software tester. Generate {positive_cases} positive and {negative_cases} negative test cases for the following {language} code using {framework}.
        
        # Code:
        # {code_content}
        
        # Generate only executable test cases without explanations."""
        
        # return get_response_from_mistral_agent(prompt)

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
    os.system("python cli/main.py login")
    user = get_authenticated_user()
    if not user:
        return None
    return user

"""
@online.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--framework', '-f', default="unittest", help='Testing framework (pytest, unittest, gtest)')
@click.option('--language', '-l', default=None, help='Programming language (auto-detected if not specified)')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--positive', '-p', default=2, help='Number of positive test cases (0-8)')
@click.option('--negative', '-n', default=2, help='Number of negative test cases (0-8)')
def path(file_path, framework, language, output, positive, negative):
    Generate test cases for a file using AI agents

    user = get_authenticated_user()
    if user:
        click.echo(f"Welcome back {user.get('username', 'Unknown')}")
        # click.echo(f"🆔 User ID: {user.get('plabn', 'Unknown')}")
        # click.echo("🔑 Token: [HIDDEN]")
    else:
        click.echo("❌ Not logged in or token is invalid!") 
        click.echo("Please login first!")
        user = user_login()
        if user is None:
            click.echo("❌ Login failed. Aborting...")
            return
    
    # Validate input parameters
    if not (0 <= positive <= 8) or not (0 <= negative <= 8):
        click.echo("Error: Positive and negative counts must be between 0 and 8")
        return
    
    # Auto-detect language if not specified
    if language is None:
        language = detect_language(file_path)
        if language == 'unknown':
            click.echo("Error: Could not detect language. Please specify with --language")
            return
    if language != "python" and language != "cpp":
        click.echo("Error: This language is not supported yet...")
        return
    
    click.echo(f"Generating {positive} positive and {negative} negative test cases for {file_path}")
    click.echo(f"Language: {language}, Framework: {framework}")
    
    # Generate test cases using AI
    test_content = generate_test_cases(file_path, language, framework, positive, negative)
    
    if test_content is None:
        click.echo("Error: Failed to generate test cases")
        return
    
    # Save test file
    output_path = save_test_file(file_path, test_content, language, framework, positive, negative, output)
    
    # test_content, output_path = "hello", "ok"
    # Log usage to backend
    log_usage_to_backend(language, tokens_used=len(test_content))  # Example values
    
    click.echo(f"✅ Test cases generated successfully!")
    click.echo(f"🔧 Language: {language}, Framework: {framework}")
    click.echo(f"📊 Test cases: {positive} positive, {negative} negative")
    if language == "cpp" and framework == "gtest":
        click.echo("[IMPORTANT] Please create CMakeLists and then use cmake to compile and build the test file!")
    click.echo(f"📁 Output file: {output_path}")
"""

"""
@online_group.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--framework', '-f', default='pytest', help='Testing framework')
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory')
@click.option('--positive', '-p', default=2, help='Number of positive test cases per file')
@click.option('--negative', '-n', default=2, help='Number of negative test cases per file')
def project(project_path, framework, output_dir, positive, negative):
    #Generate test cases for an entire project
    
    click.echo(f"Generating test cases for project: {project_path}")
    click.echo(f"Framework: {framework}")
    click.echo(f"Test cases per file: {positive} positive, {negative} negative")
    
    # Find all code files in the project
    project_path = Path(project_path)
    code_files = []
    
    for ext in ['.py', '.cpp', '.c', '.js', '.ts', '.java', '.go']:
        code_files.extend(project_path.rglob(f"*{ext}"))
    
    if not code_files:
        click.echo("No code files found in the project")
        return
    
    click.echo(f"Found {len(code_files)} code files")
    
    # Generate tests for each file
    for file_path in code_files:
        try:
            language = detect_language(str(file_path))
            if language == 'unknown':
                continue
                
            click.echo(f"\nProcessing: {file_path}")
            
            # Generate test cases
            test_content = generate_test_cases(str(file_path), language, framework, positive, negative)
            
            if test_content is None:
                click.echo(f"❌ Failed to generate tests for {file_path}")
                continue
            
            # Save test file
            output_path = save_test_file(str(file_path), test_content, language, framework, positive, negative)
            click.echo(f"✅ Generated: {output_path}")
            
        except Exception as e:
            click.echo(f"❌ Error processing {file_path}: {e}")
    
    click.echo(f"\n🎉 Project test generation complete!")
"""
# print("Project test generation complete!")