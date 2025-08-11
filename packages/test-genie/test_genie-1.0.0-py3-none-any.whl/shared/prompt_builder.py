"""
Shared prompt building utilities for TestGenie
"""

from typing import Dict, Any, List, Optional

class PromptBuilder:
    """Builder class for constructing LLM prompts"""
    
    def __init__(self):
        self.context = {}
        self.instructions = []
        self.examples = []
    
    def add_context(self, key: str, value: Any):
        """Add context information"""
        self.context[key] = value
        return self
    
    def add_instruction(self, instruction: str):
        """Add an instruction"""
        self.instructions.append(instruction)
        return self
    
    def add_example(self, input_text: str, output_text: str):
        """Add an example input/output pair"""
        self.examples.append({
            "input": input_text,
            "output": output_text
        })
        return self
    
    def build(self) -> str:
        """Build the final prompt"""
        prompt_parts = []
        
        # Add context
        if self.context:
            context_str = "\n".join([f"{k}: {v}" for k, v in self.context.items()])
            prompt_parts.append(f"Context:\n{context_str}")
        
        # Add instructions
        if self.instructions:
            instructions_str = "\n".join([f"- {instruction}" for instruction in self.instructions])
            prompt_parts.append(f"Instructions:\n{instructions_str}")
        
        # Add examples
        if self.examples:
            examples_str = "\n\n".join([
                f"Example {i+1}:\nInput: {ex['input']}\nOutput: {ex['output']}"
                for i, ex in enumerate(self.examples)
            ])
            prompt_parts.append(f"Examples:\n{examples_str}")
        
        return "\n\n".join(prompt_parts)

def build_test_generation_prompt(
    code_content: str,
    language: str = "python",
    framework: str = "pytest",
    test_type: str = "unit",
    additional_context: Optional[Dict[str, Any]] = None
) -> str:
    """Build a test generation prompt using the PromptBuilder"""
    
    builder = PromptBuilder()
    
    # Add basic context
    builder.add_context("Language", language)
    builder.add_context("Framework", framework)
    builder.add_context("Test Type", test_type)
    builder.add_context("Code", f"```{language}\n{code_content}\n```")
    
    # Add additional context if provided
    if additional_context:
        for key, value in additional_context.items():
            builder.add_context(key, value)
    
    # Add instructions
    builder.add_instruction(f"Generate comprehensive {test_type} tests using {framework}")
    builder.add_instruction("Include proper imports and dependencies")
    builder.add_instruction("Test all functions and methods")
    builder.add_instruction("Include edge cases and error conditions")
    builder.add_instruction("Use descriptive test names")
    builder.add_instruction("Follow best practices for the chosen framework")
    builder.add_instruction("Generate only the test code, no explanations")
    
    return builder.build()

def build_code_analysis_prompt(
    code_content: str,
    language: str = "python",
    analysis_type: str = "comprehensive"
) -> str:
    """Build a code analysis prompt"""
    
    builder = PromptBuilder()
    
    builder.add_context("Language", language)
    builder.add_context("Analysis Type", analysis_type)
    builder.add_context("Code", f"```{language}\n{code_content}\n```")
    
    builder.add_instruction("Analyze the code structure and identify testing requirements")
    builder.add_instruction("List all functions and methods that need testing")
    builder.add_instruction("Identify input parameters and their types")
    builder.add_instruction("List expected outputs and return types")
    builder.add_instruction("Identify edge cases to consider")
    builder.add_instruction("List dependencies that should be mocked")
    builder.add_instruction("Provide a structured analysis")
    
    return builder.build() 