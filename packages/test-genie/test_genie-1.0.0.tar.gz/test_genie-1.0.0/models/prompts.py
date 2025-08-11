"""
LLM prompts for test case generation
"""

def get_test_generation_prompt(
    code_content: str,
    language: str = "python",
    framework: str = "pytest",
    test_type: str = "unit"
) -> str:
    """Generate a prompt for test case generation"""
    
    if language == "python" and framework == "pytest":
        return f"""You are a test case generation expert. Generate comprehensive {test_type} tests for the following Python code using pytest.

Code to test:
```python
{code_content}
```

Requirements:
1. Use pytest framework
2. Include proper imports
3. Test all functions and methods
4. Include edge cases and error conditions
5. Use descriptive test names
6. Add docstrings to test functions
7. Use fixtures where appropriate
8. Mock external dependencies if needed

Generate only the test code, no explanations:"""

    elif language in ["javascript", "typescript"] and framework == "jest":
        return f"""You are a test case generation expert. Generate comprehensive {test_type} tests for the following {language} code using Jest.

Code to test:
```{language}
{code_content}
```

Requirements:
1. Use Jest framework
2. Include proper imports
3. Test all functions and methods
4. Include edge cases and error conditions
5. Use descriptive test names
6. Mock external dependencies if needed
7. Use describe blocks for organization

Generate only the test code, no explanations:"""

    else:
        return f"""You are a test case generation expert. Generate comprehensive {test_type} tests for the following {language} code using {framework}.

Code to test:
```{language}
{code_content}
```

Requirements:
1. Use {framework} framework
2. Include proper imports
3. Test all functions and methods
4. Include edge cases and error conditions
5. Use descriptive test names
6. Follow {framework} best practices

Generate only the test code, no explanations:"""

def get_code_analysis_prompt(code_content: str, language: str = "python") -> str:
    """Generate a prompt for code analysis"""
    
    return f"""Analyze the following {language} code and provide a summary of:

1. Functions and methods that need testing
2. Input parameters and their types
3. Expected outputs
4. Edge cases to consider
5. Dependencies that should be mocked

Code:
```{language}
{code_content}
```

Provide a structured analysis:"""

def get_test_improvement_prompt(
    code_content: str,
    test_content: str,
    language: str = "python",
    framework: str = "pytest"
) -> str:
    """Generate a prompt for improving existing tests"""
    
    return f"""Review and improve the following {framework} tests for this {language} code.

Code:
```{language}
{code_content}
```

Current tests:
```{language}
{test_content}
```

Improve the tests by:
1. Adding missing test cases
2. Improving test coverage
3. Adding edge cases
4. Better error handling tests
5. More descriptive test names
6. Better organization

Generate only the improved test code:""" 