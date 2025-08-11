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

def abdophp():
    """
    Installs the latest version of PHP on Debian-based Linux systems (like Ubuntu).

    This function requires 'sudo' privileges to run. It will:
    1. Add the PPA for the latest PHP versions (ppa:ondrej/php).
    2. Update package lists.
    3. Install the latest 'php' package, accepting all prompts.
    """
    if not sys.platform.startswith('linux'):
        print("This function only supports Linux.", file=sys.stderr)
        return

    print("Attempting to install the latest version of PHP...")
    print("This requires sudo privileges and is intended for Debian/Ubuntu-based systems.")

    commands = [
        "sudo apt-get update -y",
        "sudo apt-get install -y software-properties-common",
        "sudo add-apt-repository -y ppa:ondrej/php",
        "sudo apt-get update -y",
        "sudo apt-get install -y php"
    ]

    for command in commands:
        print(f"\nExecuting: {command}")
        try:
            # We split the command into a list to avoid using shell=True
            result = subprocess.run(command.split(), check=True, capture_output=True, text=True, stdin=subprocess.DEVNULL)
            if result.stdout:
                print("Output:", result.stdout)
            if result.stderr:
                # PPA addition sometimes prints to stderr on success, so we just show it
                print("Notice:", result.stderr)
        except FileNotFoundError:
            print(f"Error: Command not found. Is '{command.split()[0]}' installed and in your PATH?", file=sys.stderr)
            print("This function currently only supports Debian/Ubuntu-based systems using 'apt'.", file=sys.stderr)
            return
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while executing: {command}", file=sys.stderr)
            print(f"Return code: {e.returncode}", file=sys.stderr)
            print(f"Output:\n{e.stdout}", file=sys.stderr)
            print(f"Error output:\n{e.stderr}", file=sys.stderr)
            print("\nInstallation failed. Please check the errors above.", file=sys.stderr)
            return
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            return

    print("\nPHP installation process completed successfully!")