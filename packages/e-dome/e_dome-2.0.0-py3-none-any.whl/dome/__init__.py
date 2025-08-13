# FILE 1: dome/__init__.py (Main Library File)
"""
DOME - Natural Language Programming with Claude AI
=================================================

Usage:
    import dome
    dome.start()
    # Then type natural language directly
"""

import sys
import ast
import code
import types
import traceback
import threading
import builtins
import readline
import atexit
import signal
import subprocess
import tempfile
import os
import logging
import re
from typing import Any, Dict, Optional
import requests
import json
from datetime import datetime

__version__ = "2.0.0"
__author__ = "e-dome.dev"
__description__ = "DOME - Natural Language Programming"

# REPLACE WITH YOUR ACTUAL CLAUDE API KEY
CLAUDE_API_KEY = "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"

# Security Configuration
DOME_SECURITY_ENABLED = True
DOME_EXECUTION_TIMEOUT = 30
DOME_RESTRICTED_IMPORTS = {
    'os.system', 'subprocess.run', 'subprocess.call', 'subprocess.Popen',
    'eval', 'exec', '__import__', 'shutil.rmtree', 'os.remove'
}

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - DOME - %(message)s')
logger = logging.getLogger('DOME')


class DOMESecurityError(Exception):
    """Security violation error"""
    pass


class ClaudeTranslator:
    """Translates natural language to Python using Claude AI"""

    def __init__(self):
        self.api_key = CLAUDE_API_KEY
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }

    def translate_to_python(self, natural_language: str, context: Dict = None) -> str:
        """Translate natural language to Python with advanced error handling"""
        try:
            # Primary translation
            return self._primary_translation(natural_language, context)
        except Exception as e:
            logger.warning(f"Primary translation failed: {e}")
            # Try stronger Claude API
            try:
                return self._stronger_claude_api(natural_language, context)
            except Exception as e2:
                logger.warning(f"Stronger API failed: {e2}")
                # Enhanced pattern matching fallback
                return self._enhanced_pattern_matching(natural_language)

    def _primary_translation(self, natural_language: str, context: Dict = None) -> str:
        """Primary Claude API translation"""
        if not self.api_key or self.api_key == "your-claude-api-key-here":
            raise Exception("Claude API key not configured")

        context_info = ""
        if context:
            vars_info = {k: str(type(v).__name__) for k, v in context.items()
                         if not k.startswith('_') and not callable(v)}
            if vars_info:
                context_info = f"Available variables: {vars_info}\n"

        is_multiline = '\n' in natural_language or len(
            natural_language.split('.')) > 3

        if is_multiline:
            prompt = f"""Convert this multi-line natural language program into a complete Python script. Return ONLY the Python code, no explanations.

{context_info}

Rules:
- Return executable Python code only
- Import ALL required libraries at the top
- Print meaningful results at each step
- Use clear variable names
- Handle errors gracefully

Multi-line Program:
{natural_language}

Python script:"""
        else:
            prompt = f"""Convert this natural language to Python code. Return ONLY the Python code, no explanations.

{context_info}

Rules:
- Return executable Python code only
- Import required libraries
- Print meaningful results
- Use clear variable names

Command: {natural_language}

Python code:"""

        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 2000 if is_multiline else 1000,
            "messages": [{"role": "user", "content": prompt}]
        }

        response = requests.post(
            self.api_url, headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        python_code = result['content'][0]['text'].strip()

        # Clean up code blocks
        if '```python' in python_code:
            python_code = python_code.split('```python')[1].split('```')[0]
        elif '```' in python_code:
            python_code = python_code.split('```')[1].split('```')[0]

        return python_code.strip()

    def _stronger_claude_api(self, natural_language: str, context: Dict = None) -> str:
        """Stronger Claude API with more detailed prompt"""
        stronger_prompt = f"""You are an expert Python programmer. Convert this natural language to Python code with MAXIMUM ACCURACY.

CRITICAL INSTRUCTIONS:
1. Return ONLY Python code - no explanations, no markdown
2. The code MUST be executable and complete
3. Import ALL required libraries at the top
4. Print meaningful, user-friendly output
5. Handle edge cases gracefully

Command: {natural_language}

Python code:"""

        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 2000,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": stronger_prompt}]
        }

        response = requests.post(
            self.api_url, headers=self.headers, json=payload, timeout=45)
        response.raise_for_status()

        result = response.json()
        python_code = result['content'][0]['text'].strip()

        # Clean more aggressively
        lines = python_code.split('\n')
        cleaned_lines = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if not in_code_block:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines).strip()

    def _enhanced_pattern_matching(self, command: str) -> str:
        """Enhanced pattern matching fallback"""
        command = command.lower().strip()

        patterns = {
            r'calculate factorial of (\d+)': lambda m: f"""
import math
result = math.factorial({m.group(1)})
print(f"Factorial of {m.group(1)}: {{result:,}}")
""",
            r'make a list of (?:the )?first (\d+) square numbers': lambda m: f"""
squares = [i**2 for i in range(1, {int(m.group(1))+1})]
print(f"First {m.group(1)} square numbers: {{squares}}")
""",
            r'create (?:a )?fibonacci sequence up to (\d+)': lambda m: f"""
fib = [0, 1]
while True:
    next_fib = fib[-1] + fib[-2]
    if next_fib > {m.group(1)}:
        break
    fib.append(next_fib)
print(f"Fibonacci sequence up to {m.group(1)}: {{fib}}")
""",
            r'load data from (["\']?)([^"\'\\s]+)\\.csv\\1': lambda m: f"""
try:
    import pandas as pd
    data = pd.read_csv('{m.group(2)}.csv')
    print(f"Loaded data from {m.group(2)}.csv - Shape: {{data.shape}}")
    print(data.head())
except ImportError:
    print("Install pandas: pip install pandas")
except Exception as e:
    print(f"Error: {{e}}")
""",
            r'hello world': lambda m: 'print("Hello, World!")',
        }

        for pattern, code_func in patterns.items():
            match = re.search(pattern, command)
            if match:
                try:
                    return code_func(match).strip()
                except:
                    continue

        return f'print("⚠️ Command not understood: {command}")'


class SecuritySandbox:
    """Security sandbox for safe code execution"""

    def __init__(self):
        self.timeout = DOME_EXECUTION_TIMEOUT
        self.restricted_patterns = [
            r'import\s+os\b', r'subprocess\.', r'eval\s*\(', r'exec\s*\(',
            r'__import__\s*\(', r'open\s*\([^)]*["\']w', r'shutil\.rmtree'
        ]

    def check_code_safety(self, code: str) -> tuple[bool, str]:
        """Check if code is safe to execute"""
        if not DOME_SECURITY_ENABLED:
            return True, "Security disabled"

        for pattern in self.restricted_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Restricted pattern: {pattern}"
        return True, "Safe"

    def execute_with_timeout(self, code: str, globals_dict: dict, locals_dict: dict):
        """Execute code with timeout and security checks"""
        is_safe, message = self.check_code_safety(code)
        if not is_safe:
            raise DOMESecurityError(f"Security violation: {message}")

        result = None
        exception = None

        def target():
            nonlocal result, exception
            try:
                result = exec(code, globals_dict, locals_dict)
            except Exception as e:
                exception = e

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout)

        if thread.is_alive():
            raise TimeoutError(
                f"Execution timed out after {self.timeout} seconds")

        if exception:
            raise exception

        return result


class DOMENaturalREPL(code.InteractiveConsole):
    """Custom REPL for natural language programming"""

    def __init__(self, locals=None):
        super().__init__(locals)
        self.translator = ClaudeTranslator()
        self.sandbox = SecuritySandbox()
        self.execution_history = []
        self.setup_environment()

    def setup_environment(self):
        """Setup execution environment"""
        setup_code = """
import math
import random
from datetime import datetime
import json
import re

# Try to import common data science libraries
try:
    import numpy as np
    print("📊 NumPy available")
except ImportError:
    pass

try:
    import pandas as pd
    print("📊 Pandas available")
except ImportError:
    pass

try:
    import matplotlib.pyplot as plt
    print("📊 Matplotlib available")
except ImportError:
    pass

def dome_help():
    print('''
🏛️ DOME - Natural Language Programming

✨ SINGLE-LINE COMMANDS:
   calculate factorial of 15
   make a list of the first 10 square numbers
   create fibonacci sequence up to 100
   load data from sales.csv

🚀 MULTI-LINE PROGRAMS:
   Type: begin program
   ... your multi-line natural language program
   ... end program

🛠️ UTILITIES:
   dome_help()     - Show this help
   dome_history()  - Show execution history
   exit()          - Exit DOME
''')

def dome_history():
    print("\\n📋 Execution History:")
    for i, entry in enumerate(_dome_repl.execution_history, 1):
        status = "✅" if entry['success'] else "❌"
        print(f"{i}. {status} {entry['natural_language'][:50]}...")
        print(f"   ⏰ {entry['timestamp']}")
"""

        try:
            exec(setup_code, self.locals)
            self.locals['_dome_repl'] = self
        except Exception as e:
            print(f"⚠️ Setup warning: {e}")

    def is_natural_language(self, source: str) -> bool:
        """Check if input is natural language"""
        source = source.strip()

        if not source:
            return False

        # Skip obvious Python code
        python_indicators = [
            'def ', 'class ', 'import ', 'from ', 'lambda', 'return ',
            'if __name__', 'try:', 'except:', 'with ', '= ', 'dome_'
        ]

        if any(source.startswith(indicator) for indicator in python_indicators):
            return False

        # Try parsing as Python
        try:
            ast.parse(source)
            # Check for natural language indicators
            natural_words = ['make', 'create', 'calculate', 'show', 'generate',
                             'load', 'save', 'plot', 'analyze', 'build']
            return any(word in source.lower() for word in natural_words)
        except SyntaxError:
            return True

    def execute_safely(self, python_code: str, natural_language: str):
        """Execute code safely with error handling"""
        try:
            self.sandbox.execute_with_timeout(
                python_code, self.locals, self.locals)

            self.execution_history.append({
                'natural_language': natural_language,
                'python_code': python_code,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'success': True
            })

        except DOMESecurityError as e:
            print(f"🔒 Security Error: {e}")
            self._log_failed(natural_language, python_code, str(e))
        except TimeoutError as e:
            print(f"⏱️ Timeout Error: {e}")
            self._log_failed(natural_language, python_code, str(e))
        except Exception as e:
            print(f"🔴 Execution Error: {e}")
            self._log_failed(natural_language, python_code, str(e))

    def _log_failed(self, nl: str, code: str, error: str):
        """Log failed execution"""
        self.execution_history.append({
            'natural_language': nl,
            'python_code': code,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'error': error,
            'success': False
        })

    def runsource(self, source, filename="<dome>", symbol="single"):
        """Handle natural language and multi-line programs"""
        source = source.strip()

        if not source:
            return False

        # Handle help commands
        if source.lower() in ['dome_help()', 'help', 'dome help']:
            self.locals['dome_help']()
            return False

        if source.lower() in ['dome_history()', 'history']:
            self.locals['dome_history']()
            return False

        # Multi-line program mode
        if source.lower().startswith('begin program'):
            print("📝 Multi-line Program Mode")
            print("💡 Type your program in natural language")
            print("💡 Type 'end program' when done")
            print("=" * 50)

            program_lines = []
            while True:
                try:
                    line = input("... ")
                    if line.lower().strip() in ['end program', 'done', 'execute']:
                        break
                    program_lines.append(line)
                except (EOFError, KeyboardInterrupt):
                    print("\n❌ Cancelled")
                    return False

            if program_lines:
                full_program = "\n".join(program_lines)
                print(f"\n🤖 Processing multi-line program...")

                try:
                    python_code = self.translator.translate_to_python(
                        full_program, self.locals)
                    print("🐍 Generated Python code:")
                    print(python_code)
                    print("📊 Executing...")
                    self.execute_safely(python_code, full_program)
                except Exception as e:
                    print(f"🔴 Translation Error: {e}")

            return False

        # Single natural language command
        if self.is_natural_language(source):
            print(f"🤖 Processing: {source}")

            try:
                python_code = self.translator.translate_to_python(
                    source, self.locals)
                print("🐍 Executing...")
                self.execute_safely(python_code, source)
            except Exception as e:
                print(f"🔴 Translation Error: {e}")

            return False
        else:
            # Regular Python code
            if DOME_SECURITY_ENABLED:
                is_safe, message = self.sandbox.check_code_safety(source)
                if not is_safe:
                    print(f"🔒 Security Warning: {message}")
                    return False

            return super().runsource(source, filename, symbol)


def start_dome():
    """Start DOME natural language REPL"""
    print("🏛️ DOME - Natural Language Programming")
    print("=" * 50)
    print("🚀 Type natural language commands directly!")
    print("🔒 Security sandbox enabled")
    print("🛡️ Advanced error handling active")
    print("")
    print("💡 Examples:")
    print("   calculate factorial of 15")
    print("   make a list of square numbers")
    print("   begin program")
    print("   dome_help() for more help")
    print("=" * 50)

    if CLAUDE_API_KEY == "your-claude-api-key-here":
        print("⚠️ Claude API key not configured - using fallback mode")
    else:
        print("✅ Claude AI ready")

    print("=" * 50)

    repl = DOMENaturalREPL()

    try:
        repl.interact()
    except (KeyboardInterrupt, EOFError):
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n🔴 Error: {e}")


# Module replacement for seamless integration
class DOMEModule(types.ModuleType):
    """Custom module for DOME"""

    def __init__(self, name):
        super().__init__(name)
        self.__dict__.update({
            '__version__': __version__,
            '__author__': __author__,
            '__description__': __description__,
            'start': start_dome,
        })

        print("🏛️ DOME - Natural Language Programming System Loaded!")
        print("🚀 Type: dome.start() to begin natural language programming")


# Replace this module
sys.modules[__name__] = DOMEModule(__name__)

# Export main function
start = start_dome
