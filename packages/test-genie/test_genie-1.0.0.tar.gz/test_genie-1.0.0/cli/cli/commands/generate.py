import click
import requests
import json
import os
import sys
from typing import Optional
from pathlib import Path
from cli.auth import get_authenticated_user

# Backend API configuration
BACKEND_API_URL = "https://testgenie.fly.dev"
# BACKEND_API_URL = "http://localhost:8000"

# Global configuration cache
_config_cache = None

MAX_LINES_FREE = 500
MAX_LINES_PRO_EXCLUSIVE = 2000  # strictly less than 2000

def get_cli_config() -> Optional[dict]:
    """Fetch CLI configuration from backend"""
    global _config_cache
    
    # Return cached config if available
    if _config_cache:
        return _config_cache
    
    # Fetch from backend
    config = make_authenticated_request("/api/cli/config")
    if config:
        _config_cache = config
        click.echo("✅ Using backend configuration")
        return config
    
    click.echo("⚠️  Using fallback configuration")
    return None

def get_mistral_api_key() -> str:
    """Get Mistral API key from backend or environment"""
    config = get_cli_config()
    if config and config.get('mistral_api_key'):
        return config['mistral_api_key']
    return ""

def get_python_agent_id() -> Optional[str]:
    res = make_authenticated_request("/api/cli/agent/python")
    if res and res.get("agent_id"):
        return res["agent_id"]
    return None

def get_cpp_agent_id() -> Optional[str]:
    res = make_authenticated_request("/api/cli/agent/cpp")
    if res and res.get("agent_id"):
        return res["agent_id"]
    return None

def get_prompt(language: str, framework: str, code: str, positive_cases: int, negative_cases: int) -> str:
    """Get prompt template from backend"""
    config = get_cli_config()
    if config and config.get('prompts'):
        prompts = config['prompts']
        if language in prompts and framework in prompts[language]:
            template = prompts[language][framework]
            prompt = template.format(
                code=code,
                positive_cases=positive_cases,
                negative_cases=negative_cases
            )
            click.echo(f"📝 Using backend prompt for {language}/{framework}")
            return prompt
    return None
    # Fallback to default prompts
    # click.echo(f"📝 Using fallback prompt for {language}/{framework}")
    # return get_default_prompt(language, framework, code, positive_cases, negative_cases)

def get_suffix(language: str, framework: str) -> str:
    """Get suffix template from backend"""
    config = get_cli_config()
    if config and config.get('suffixes'):
        suffixes = config['suffixes']
        if language in suffixes and framework in suffixes[language]:
            click.echo(f"📝 Using backend suffix for {language}/{framework}")
            return suffixes[language][framework]
    
    # Fallback to default suffixes
    return None
    # return get_default_suffix(language, framework)

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
            click.echo(
                "❌ Error 401 - Unauthorized\n"
                "If you are on the Free plan, this feature is not accessible.\n"
                "To upgrade your plan, please visit: https://thetestgenie.com/pricing"
            )
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
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c++': 'cpp',
        '.c': 'c',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust'
    }
    return language_map.get(ext, 'python')


def enforce_local_line_limits(code: str) -> bool:
    """Client-side guardrail: warn and block on egregious sizes before server call.
    We cannot know user plan here; just hard block at 2000+, and warn above 500.
    """
    num_lines = len(code.splitlines())
    if num_lines >= MAX_LINES_PRO_EXCLUSIVE:
        click.echo(f"❌ File has {num_lines} lines; maximum allowed is 1999 lines.")
        return False
    if num_lines > MAX_LINES_FREE:
        click.echo(f"ℹ️ Note: File has {num_lines} lines (> {MAX_LINES_FREE}). Free plan will be blocked on server; Pro required.")
    return True


def generate_test_cases(file_path: str, language: str, framework: str, positive_cases: int = 2, negative_cases: int = 2) -> Optional[str]:
    """Generate test cases for the given file"""
    code_content = read_file_content(file_path)

    if not enforce_local_line_limits(code_content):
        return None

    # Unified backend generation for python/cpp/java
    if language in { 'python', 'cpp', 'java' }:
        if language == 'python' and framework == 'gtest':
            return "PYTHON DOES NOT SUPPORT GTEST FRAMEWORK"
        if language == 'cpp' and framework == 'pytest':
            return "CPP DOES NOT SUPPORT PYTEST FRAMEWORK"
        response = make_authenticated_request("/api/cli/generate", method="POST", data={
            "code_content": code_content,
            "framework": framework,
            "positive_cases": positive_cases,
            "negative_cases": negative_cases,
            "language": language
        })
        if response and "content" in response:
            return response["content"]
        return None
    else:
        click.echo(f"❌ Unsupported language: {language}")
        return None

def save_test_file(file_path: str, test_content: str, language: str, framework: str, positive_cases: int, negative_cases: int, output_path: Optional[str] = None) -> str:
    """Save the generated test content to a file"""
    if not output_path:
        # Generate output filename based on input file
        input_path = Path(file_path)

    # Add imports and main execution based on language and framework
    if language == 'python':
        if framework == 'pytest':
            # For pytest, just add the test content
            import_statement = f"from {Path(file_path).stem} import *\n\n"
            full_content = import_statement + test_content
            test_execution = "\n# Run all test cases\n"
            for i in range(1, positive_cases + 1):
                test_execution += f"test_positive_case_{i}()\n"
            for i in range(1, negative_cases + 1):
                test_execution += f"test_negative_case_{i}()\n"
            test_execution += f"print('ALL TEST CASES PASSED!')"
            full_content = full_content + test_execution
        elif framework == 'unittest':
            print('in here')
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

    elif language == 'java':
        # Java: ensure imports, optional package, and class wrapper
        orig_path = Path(file_path)
        orig_stem = orig_path.stem

        # Strip any accidental markdown fences
        cleaned = test_content.replace("```java", "").replace("```", "").strip()

        # Try to detect package from original file
        package_line = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as srcf:
                for line in srcf.readlines()[:50]:
                    stripped = line.strip()
                    if stripped.startswith('package ') and stripped.endswith(';'):
                        package_line = stripped
                        break
        except Exception:
            pass

        # Imports (JUnit5 + Mockito)
        base_imports = [
            "import org.junit.jupiter.api.Test;",
            "import org.junit.jupiter.api.BeforeEach;",
            "import org.junit.jupiter.api.DisplayName;",
            "import org.junit.jupiter.api.extension.ExtendWith;",
            "import static org.junit.jupiter.api.Assertions.*;",
            "import org.mockito.Mock;",
            "import org.mockito.InjectMocks;",
            "import org.mockito.MockitoAnnotations;",
            "import org.mockito.junit.jupiter.MockitoExtension;",
        ]
        spring_hints = ("org.springframework" in cleaned) or ("@RestController" in cleaned) or ("@Service" in cleaned) or ("@Repository" in cleaned)
        if spring_hints and "@SpringBootTest" in cleaned:
            base_imports.extend([
                "import org.springframework.boot.test.context.SpringBootTest;",
            ])
        existing_imports = {ln.strip() for ln in cleaned.splitlines() if ln.strip().startswith("import ") and ln.strip().endswith(";")}
        final_imports = [imp for imp in base_imports if imp not in existing_imports]

        header_parts = []
        if package_line:
            header_parts.append(package_line)
        header_parts.extend(final_imports)
        header = "\n".join(header_parts)
        if header:
            header += "\n\n"

        # Force single container class TestSuite with @ExtendWith and setup
        body = cleaned
        # guarantee class name and annotation
        if "class TestSuite" not in body:
            # If there is some other class, embed body inside TestSuite
            inner = "\n".join("    " + ln if ln.strip() else ln for ln in body.splitlines())
            body = (
                "@ExtendWith(MockitoExtension.class)\n"
                "class TestSuite {\n"
                "    void initMocks() { MockitoAnnotations.openMocks(this); }\n"
                "    @BeforeEach void setUp() { initMocks(); }\n" +
                inner +
                "\n}"
            )
        else:
            if "@ExtendWith(MockitoExtension.class)" not in body:
                body = body.replace("class TestSuite", "@ExtendWith(MockitoExtension.class)\nclass TestSuite")
            if "void initMocks()" not in body:
                insert_idx = body.find("class TestSuite")
                if insert_idx != -1:
                    brace_idx = body.find("{", insert_idx)
                    if brace_idx != -1:
                        body = body[:brace_idx+1] + "\n    void initMocks() { MockitoAnnotations.openMocks(this); }\n    @BeforeEach void setUp() { initMocks(); }\n" + body[brace_idx+1:]

        # Ensure main method calls initMocks and invokes test methods
        if "public static void main(" not in body:
            # Identify test method names
            positives, negatives = [], []
            for ln in body.splitlines():
                s = ln.strip()
                if s.startswith("void positiveTestCase") and s.endswith(") {"):
                    positives.append(s.split(" ")[-2].split("(")[0])
                if s.startswith("void negativeTestCase") and s.endswith(") {"):
                    negatives.append(s.split(" ")[-2].split("(")[0])
            if not positives and not negatives:
                # fallback names; cannot know requested counts, use a few conventional calls
                positives = ["positiveTestCase1"]
                negatives = ["negativeTestCase1"]
            main_lines = [
                "    public static void main(String[] args) {",
                "        TestSuite t = new TestSuite();",
                "        t.initMocks();",
            ]
            for n in positives:
                main_lines.append(f"        try {{ t.{n}(); System.out.println(\"PASS: {n}\"); }} catch (Throwable ex) {{ System.out.println(\"FAIL: {n} - \" + ex.getMessage()); }}")
            for n in negatives:
                main_lines.append(f"        try {{ t.{n}(); System.out.println(\"PASS: {n}\"); }} catch (Throwable ex) {{ System.out.println(\"FAIL: {n} - \" + ex.getMessage()); }}")
            main_lines.append("    }")
            # Append main before final closing brace of TestSuite
            last_brace = body.rfind("}")
            if last_brace != -1:
                body = body[:last_brace] + "\n" + "\n".join(main_lines) + "\n}" + body[last_brace+1:]

        # Minimal placeholder stubs when common symbols referenced but undefined
        placeholders = []
        common_symbols = ["Book", "Customer", "Order"]
        for sym in common_symbols:
            if sym in body and (f"class {sym}" not in body and f"interface {sym}" not in body):
                placeholders.append(f"    static class {sym} {{ {sym}(){{}} }}")
        repos = ["BookRepository", "CustomerRepository", "OrderRepository"]
        for sym in repos:
            if sym in body and (f"interface {sym}" not in body):
                placeholders.append(f"    interface {sym} {{ }}")
        services = ["BookService", "CustomerService", "OrderService"]
        for sym in services:
            if sym in body and (f"class {sym}" not in body):
                placeholders.append(f"    static class {sym} {{ }}")
        if placeholders:
            # inject placeholders before final brace
            last_brace = body.rfind("}")
            if last_brace != -1:
                body = body[:last_brace] + "\n" + "\n".join(placeholders) + "\n}" + body[last_brace+1:]

        full_content = header + body

    else:
        full_content = test_content

    if output_path is None:
        # Generate output path based on input file - FIXED: Remove double dots
        input_path = Path(file_path)
        if language.lower() == 'java':
            output_path = input_path.parent / f"{input_path.stem}Test.java"
        elif input_path.suffix:
            output_path = input_path.parent / f"test_{input_path.stem}{input_path.suffix}"
        else:
            output_path = input_path.parent / f"test_{input_path.name}"

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        click.echo(f"✅ Test file generated successfully: {output_path}")
        return str(output_path)
    except Exception as e:
        click.echo(f"❌ Error saving test file: {e}")
        return ""

def user_login():
    os.system("test-genie login")
    user = get_authenticated_user()
    if not user:
        return None
    return user


@click.command()
@click.option('--path', '-pt', 'file_path', required=True, type=click.Path(exists=True), help='Path to the source file')
@click.option('--positive', '-p', 'positive_cases', default=2, help='Number of positive test cases (default: 2)')
@click.option('--negative', '-n', 'negative_cases', default=2, help='Number of negative test cases (default: 2)')
@click.option('--framework', '-f', default="unittest", help='Testing framework (pytest, unittest, gtest, junit)')
@click.option('--language', '-l', default=None, help='Programming language (auto-detected if not specified)')
@click.option('--output', '-o', type=click.Path(), help='Output file path (optional)')
def generate(file_path, positive_cases, negative_cases, framework, language, output):
    """Generate test cases for your code files"""

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
    
    
    # Validate input
    if positive_cases < 0 or positive_cases > 8:
        click.echo("❌ Positive test cases must be between 0 and 8")
        return
    
    if negative_cases < 0 or negative_cases > 8:
        click.echo("❌ Negative test cases must be between 0 and 8")
        return
    
    # Auto-detect language if not specified
    if not language:
        language = detect_language(file_path)
        click.echo(f"🔍 Auto-detected language: {language}")
    
    if language not in {"python", "cpp", "java"}:
        click.echo(f"Error: {language} is not supported yet.\nSupport for {language} is coming soon! Stay tuned\n")
        return
    
    click.echo(f"🚀 Generating test cases for: {file_path}")
    
    # Generate test cases
    test_content = generate_test_cases(file_path, language, framework, positive_cases, negative_cases)
    
    if test_content:
        click.echo(f"Summary-\n -> Language: {language}")
        click.echo(f" -> Framework: {framework}")
        click.echo(f" -> Positive cases: {positive_cases}; Negative cases: {negative_cases}")
        # click.echo(f"")
        # Save test file
        output_path = save_test_file(file_path, test_content, language, framework, positive_cases, negative_cases, output)
        
        if output_path:
            # Log usage to backend
            log_usage_to_backend(language, len(test_content.split()))
            # click.echo("📊 Usage logged to backend")
    else:
        click.echo("❌ Failed to generate test cases") 


# New backend response function
def get_response_from_backend(framework: str, code_content: str, language: str, positive_cases: int, negative_cases: int) -> Optional[str]:
    response = make_authenticated_request("/api/cli/generate", method="POST", data={
        # "prompt": prompt,
        "code_content": code_content,
        "framework": framework,
        "positive_cases": positive_cases,
        "negative_cases": negative_cases,
        "language": language
    })
    # prompt = get_prompt(language, framework, code_content, positive_cases, negative_cases)
    # suffix = get_suffix(language, framework)
    if response and "content" in response:
        return response["content"]
    return None