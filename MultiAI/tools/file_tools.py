import os
import subprocess
from rich.console import Console
from rich.syntax import Syntax
from datetime import datetime
import config

console = Console()

def append_to_journal(text: str) -> str:
    """Appends a new entry to the core memory journal with a timestamp."""
    try:
        with open(config.CORE_MEMORY_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n[{datetime.now().isoformat()}] {text}")
        return f"Successfully appended to journal: '{text}'"
    except Exception as e:
        return f"Error appending to journal: {e}"

def list_files() -> str:
    """Lists all files in the current directory."""
    try:
        return f"Files in current directory: {os.listdir('.')}"
    except Exception as e:
        return f"Error listing files: {e}"

def read_from_file(filename: str) -> str:
    """Reads the content of a specified file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"Content of '{filename}':\n{content}"
    except Exception as e:
        return f"Error reading file '{filename}': {e}"

def save_to_file(filename: str, content: str) -> str:
    """Saves content to a specified file."""
    print(f"> Saving code to '{filename}'...")
    syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully saved content to '{filename}'."
    except Exception as e:
        return f"Error saving file '{filename}': {e}"

def execute_python_script(filename: str, confirm_execution: bool = True) -> str:
    """Executes a Python script and captures its output, with optional confirmation."""
    if confirm_execution:
        if console.input(f"Execute '{filename}'? (y/n): ").lower() != 'y':
            return "User declined execution."
    
    # If confirm_execution is False, this part runs automatically.
    try:
        result = subprocess.run(
            ['python', filename],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return f"Execution result of '{filename}':\n{output if output else 'Script ran without output.'}"
    except Exception as e:
        return f"Error executing script '{filename}': {e}"