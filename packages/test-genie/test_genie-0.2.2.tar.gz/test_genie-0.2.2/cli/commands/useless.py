
def get_python_test_prompt_2(code_content: str, framework: str, positive_cases: int = 2, negative_cases: int = 2) -> str:
    """Generate prompt for Python test cases based on framework"""
    
    def get_all_positive_cases(count):
        return "\n".join([f"    def positive_test_case_{i+1}(self):" for i in range(count)])
    
    def get_all_negative_cases(count):
        return "\n".join([f"    def negative_test_case_{i+1}(self):" for i in range(count)])
    
    if framework == "pytest":
        def get_all_positive_cases_pytest(count):
            return "\n".join([f"def test_positive_case_{i+1}():" for i in range(count)])
        
        def get_all_negative_cases_pytest(count):
            return "\n".join([f"def test_negative_case_{i+1}():" for i in range(count)])
        
        return f"""Generate comprehensive pytest test cases for the following Python code. Create {positive_cases} positive test cases and {negative_cases} negative test cases.

Code to test:
{code_content}

Requirements:
1. Use pytest framework
2. Import necessary modules
3. Create {positive_cases} positive test cases that test normal functionality
4. Create {negative_cases} negative test cases that test edge cases and error conditions
5. Use descriptive test names
6. Include proper assertions

Generate the complete test file with the following structure:
{get_all_positive_cases_pytest(positive_cases)}
{get_all_negative_cases_pytest(negative_cases)}

Make sure to call all the test functions in the main section if needed."""

    elif framework == "unittest":
        return f"""Generate comprehensive unittest test cases for the following Python code. Create {positive_cases} positive test cases and {negative_cases} negative test cases.

Code to test:
{code_content}

Requirements:
1. Use unittest framework
2. Import necessary modules including unittest
3. Create a test class that inherits from unittest.TestCase
4. Create {positive_cases} positive test methods that test normal functionality
5. Create {negative_cases} negative test methods that test edge cases and error conditions
6. Use descriptive test method names starting with 'test_'
7. Include proper assertions

Generate the complete test file with the following structure:
class TestGenerated(unittest.TestCase):
{get_all_positive_cases(positive_cases)}
{get_all_negative_cases(negative_cases)}

if __name__ == '__main__':
    unittest.main()

Make sure to call all the test methods."""

    else:  # Default to unittest
        return f"""Generate comprehensive unittest test cases for the following Python code. Create {positive_cases} positive test cases and {negative_cases} negative test cases.

Code to test:
{code_content}

Requirements:
1. Use unittest framework
2. Import necessary modules including unittest
3. Create a test class that inherits from unittest.TestCase
4. Create {positive_cases} positive test methods that test normal functionality
5. Create {negative_cases} negative test methods that test edge cases and error conditions
6. Use descriptive test method names starting with 'test_'
7. Include proper assertions

Generate the complete test file with the following structure:
class TestGenerated(unittest.TestCase):
{get_all_positive_cases(positive_cases)}
{get_all_negative_cases(negative_cases)}

if __name__ == '__main__':
    unittest.main()

Make sure to call all the test methods."""

def get_cpp_test_prompt(code_content: str, framework: str, positive_cases: int = 2, negative_cases: int = 2) -> str:
    """Generate prompt for C++ test cases based on framework"""
    
    def get_all_positive_cases(count):
        return "\n".join([f"    void positive_test_case_{i+1}();" for i in range(count)])
    
    def get_all_negative_cases(count):
        return "\n".join([f"    void negative_test_case_{i+1}();" for i in range(count)])
    
    if framework == "gtest":
        def get_all_positive_cases(count):
            return "\n".join([f"TEST_F(TestGenerated, PositiveCase{i+1}) {{" for i in range(count)])
        
        def get_all_negative_cases(count):
            return "\n".join([f"TEST_F(TestGenerated, NegativeCase{i+1}) {{" for i in range(count)])
        
        return f"""Generate comprehensive Google Test (gtest) test cases for the following C++ code. Create {positive_cases} positive test cases and {negative_cases} negative test cases.

Code to test:
{code_content}

Requirements:
1. Use Google Test framework
2. Include necessary headers (#include <gtest/gtest.h>)
3. Include the original C++ file header
4. Create {positive_cases} positive test cases that test normal functionality
5. Create {negative_cases} negative test cases that test edge cases and error conditions
6. Use descriptive test names
7. Include proper assertions using EXPECT_* or ASSERT_*

Generate the complete test file with the following structure:
#include <gtest/gtest.h>
#include "original_file.h"  // Include the original file

{get_all_positive_cases(positive_cases)}
{get_all_negative_cases(negative_cases)}

int main(int argc, char **argv) {{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}}"""

    else:  # Default to basic C++ testing
        return f"""Generate comprehensive C++ test cases for the following C++ code. Create {positive_cases} positive test cases and {negative_cases} negative test cases.

Code to test:
{code_content}

Requirements:
1. Include necessary headers
2. Include the original C++ file
3. Create {positive_cases} positive test functions that test normal functionality
4. Create {negative_cases} negative test functions that test edge cases and error conditions
5. Use descriptive function names
6. Include proper assertions and error checking

Generate the complete test file with the following structure:
#include <iostream>
#include <cassert>
#include "original_file.h"  // Include the original file

{get_all_positive_cases(positive_cases)}
{get_all_negative_cases(negative_cases)}

int main() {{
    // Call all test functions
    // Add your test calls here
    return 0;
}}"""

def get_response_from_python_agent_2(prompt: str, agent_id: Optional[str] = None) -> Optional[str]:
    """Get response from Python agent using Mistral AI"""
    if not agent_id:
        agent_id = PYTHON_AGENT_ID
    
    url = "https://api.mistral.ai/v1/agents/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "agent_id": agent_id,
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

def get_response_from_cpp_agent_2(prompt: str, agent_id: Optional[str] = None) -> Optional[str]:
    """Get response from C++ agent using Mistral AI"""
    if not agent_id:
        agent_id = CPP_AGENT_ID
    
    url = "https://api.mistral.ai/v1/agents/run"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "agent_id": agent_id,
        "input": prompt
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result.get('output', '')
        else:
            click.echo(f"❌ Error calling C++ agent: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        click.echo(f"❌ Error calling C++ agent: {e}")
        return None


def get_default_prompt(language: str, framework: str, code: str, positive_cases: int, negative_cases: int) -> str:
    """Default prompt templates as fallback"""
    if language == "python":
        if framework == "pytest":
            return f"""Generate comprehensive pytest test cases for the following Python function. 
Include both positive and negative test cases with proper assertions.

Function to test:
{code}

Requirements:
- Generate {positive_cases} positive test cases
- Generate {negative_cases} negative test cases
- Use pytest framework
- Include proper docstrings
- Test edge cases and error conditions
- Use descriptive test names"""
        else:  # unittest
            return f"""Generate comprehensive unittest test cases for the following Python function.
Include both positive and negative test cases with proper assertions.

Function to test:
{code}

Requirements:
- Generate {positive_cases} positive test cases
- Generate {negative_cases} negative test cases
- Use unittest framework
- Include proper docstrings
- Test edge cases and error conditions
- Use descriptive test names"""
    elif language == "cpp":
        return f"""Generate comprehensive Google Test cases for the following C++ function.
Include both positive and negative test cases with proper assertions.

Function to test:
{code}

Requirements:
- Generate {positive_cases} positive test cases
- Generate {negative_cases} negative test cases
- Use Google Test framework
- Include proper comments
- Test edge cases and error conditions
- Use descriptive test names
- Include necessary headers"""
    else:
        return f"""Generate comprehensive test cases for the following {language} function.
Include both positive and negative test cases with proper assertions.

Function to test:
{code}

Requirements:
- Generate {positive_cases} positive test cases
- Generate {negative_cases} negative test cases
- Use {framework} framework
- Include proper documentation
- Test edge cases and error conditions
- Use descriptive test names"""

def get_default_suffix(language: str, framework: str) -> str:
    """Default suffix templates as fallback"""
    if language == "python":
        if framework == "pytest":
            return """
# Additional test utilities and fixtures can be added here
if __name__ == "__main__":
    pytest.main([__file__])
"""
        else:  # unittest
            return """
# Additional test utilities can be added here
if __name__ == "__main__":
    unittest.main()
"""
    elif language == "cpp":
        return """
// Additional test utilities can be added here
int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
"""
    else:
        return ""
