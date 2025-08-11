import subprocess
import sys
import os

def abdo(file_path: str):
    """
    Executes a Python script.

    This function only works on Linux systems.

    Args:
        file_path: The path to the Python file to be executed.
                   Can be a relative or absolute path.
    """
    if not sys.platform.startswith('linux'):
        print("This library only supports Linux.", file=sys.stderr)
        return

    absolute_path = os.path.abspath(file_path)

    if not os.path.exists(absolute_path):
        print(f"Error: File not found at '{absolute_path}'", file=sys.stderr)
        return

    if not absolute_path.endswith('.py'):
        print(f"Error: '{absolute_path}' is not a Python file.", file=sys.stderr)
        return

    try:
        # Using subprocess.run to execute the script
        # We pass the python executable path to ensure we're using the same python
        # that's running this script.
        result = subprocess.run([sys.executable, absolute_path], check=True, capture_output=True, text=True)
        print("Script output:")
        print(result.stdout)
        if result.stderr:
            print("Script errors:")
            print(result.stderr)
    except FileNotFoundError:
        print(f"Error: python executable not found.", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the script: {absolute_path}", file=sys.stderr)
        print(f"Return code: {e.returncode}", file=sys.stderr)
        print(f"Output:\n{e.stdout}", file=sys.stderr)
        print(f"Error output:\n{e.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
