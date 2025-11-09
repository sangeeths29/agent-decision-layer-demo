"""
ACT mode - runs actual Python code!
Generates and executes code safely for calculations and data tasks
"""

import re
import math
from typing import Dict, Any
from app.llm import llm_client


# Only allow these built-in functions (for security)
SAFE_BUILTINS = {
    'abs': abs,
    'round': round,
    'min': min,
    'max': max,
    'sum': sum,
    'len': len,
    'range': range,
    'enumerate': enumerate,
    'zip': zip,
    'sorted': sorted,
    'list': list,
    'dict': dict,
    'set': set,
    'tuple': tuple,
    'str': str,
    'int': int,
    'float': float,
    'bool': bool,
    'print': print,
    'True': True,
    'False': False,
    'None': None,
}

# Math functions are safe, so let's allow those
SAFE_MATH = {
    'sqrt': math.sqrt,
    'pow': math.pow,
    'log': math.log,
    'log10': math.log10,
    'exp': math.exp,
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'pi': math.pi,
    'e': math.e,
    'ceil': math.ceil,
    'floor': math.floor,
    'factorial': math.factorial,
}


def safe_execute_python(code: str) -> Dict[str, Any]:
    """
    Runs Python code in a restricted environment.
    Blocks dangerous stuff like file access, imports, etc.
    """
    # Block anything sketchy
    dangerous_patterns = [
        r'import\s+(?!math)',  # No imports except math
        r'__import__',         # No sneaky imports
        r'exec\(',             # No eval/exec tricks
        r'eval\(',
        r'compile\(',
        r'open\(',             # No file access
        r'file\(',
        r'input\(',            # No user input
        r'raw_input\(',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return {
                "success": False,
                "error": f"Blocked: unsafe operation detected ({pattern})"
            }
    
    # Set up a safe environment with limited functions
    safe_globals = {
        '__builtins__': SAFE_BUILTINS,
        'math': type('math', (), SAFE_MATH)()
    }
    
    safe_locals = {}
    
    try:
        # Actually run the code
        exec(code, safe_globals, safe_locals)
        
        # Figure out what the result is
        result = None
        
        # Check if they used 'result' variable
        if 'result' in safe_locals:
            result = safe_locals['result']
        # Or maybe 'answer'
        elif 'answer' in safe_locals:
            result = safe_locals['answer']
        # Otherwise just grab the last thing they assigned
        elif safe_locals:
            result = list(safe_locals.values())[-1]
        
        return {
            "success": True,
            "result": result,
            "variables": {k: v for k, v in safe_locals.items() if not k.startswith('_')}
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


ACT_SYSTEM_PROMPT = """You are a Python code generator. When given a calculation or data task:

1. Write clean, simple Python code to solve it
2. Use the variable name 'result' for the final answer
3. Only use basic Python and math operations (no imports except math is available)
4. Include comments explaining the logic

Format your response as:

```python
# Your code here
result = ...
```

IMPORTANT: Only output the Python code block, nothing else."""


def handle_act(query: str) -> dict:
    """
    Takes a calculation task, generates Python code, and runs it.
    Pretty cool that the LLM can write working code!
    """
    # Ask the LLM to write Python code for this
    code_response = llm_client.generate(
        prompt=query,
        system_prompt=ACT_SYSTEM_PROMPT,
        temperature=0.3,  # Lower temp = more reliable code
        max_tokens=800
    )
    
    # Extract the actual code from markdown blocks (if it used them)
    code_match = re.search(r'```python\n(.*?)```', code_response, re.DOTALL)
    
    if code_match:
        code = code_match.group(1).strip()
    else:
        # Sometimes it just returns code without markdown
        code = code_response.strip()
    
    # Run it!
    execution_result = safe_execute_python(code)
    
    if execution_result["success"]:
        result_value = execution_result.get("result")
        
        return {
            "mode": "ACT",
            "answer": f"Result: {result_value}",
            "result": result_value,
            "code": code,
            "metadata": {
                "tool_used": "python_repl",
                "execution_success": True,
                "variables": execution_result.get("variables", {})
            }
        }
    else:
        # Something went wrong with the code
        return {
            "mode": "ACT",
            "answer": f"Execution failed: {execution_result['error']}",
            "result": None,
            "code": code,
            "metadata": {
                "tool_used": "python_repl",
                "execution_success": False,
                "error": execution_result["error"]
            }
        }

