import os
import sys
from pathlib import Path
import subprocess
import venv

VERSION = "0.2.0"

def find_venv_path(search_parents=False):
    current = Path.cwd()
    search_dirs = [current] + list(current.parents) if search_parents else [current]
    for directory in search_dirs:
        for folder in [".venv", "venv", "env"]:
            win = directory / folder / "Scripts" / "python.exe"
            unix = directory / folder / "bin" / "python"
            if win.exists():
                return str(win)
            if unix.exists():
                return str(unix)
    return None

def find_requirements_file():
    """Find common requirements file names in current directory"""
    current = Path.cwd()
    common_names = [
        "requirements.txt", "req.txt", "requirements-dev.txt", 
        "requirements-test.txt", "dev-requirements.txt", "reqs.txt",
        "pip-requirements.txt", "requirements.pip"
    ]
    
    for name in common_names:
        req_file = current / name
        if req_file.exists():
            return str(req_file)
    return None

def check_venv_exists():
    """Check if a virtual environment already exists"""
    current = Path.cwd()
    for folder in [".venv", "venv", "env"]:
        venv_dir = current / folder
        if venv_dir.exists() and venv_dir.is_dir():
            return True, folder
    return False, None

def create_venv_and_install():
    """Create virtual environment and install dependencies"""
    current = Path.cwd()
    
    # Check if venv already exists
    exists, venv_name = check_venv_exists()
    if exists:
        print(f"Error: Virtual environment '{venv_name}' already exists in current directory.")
        print("Remove it first or use a different directory.")
        sys.exit(1)
    
    venv_path = current / ".venv"
    print(f"Creating virtual environment at {venv_path}...")
    
    try:
        # Create virtual environment
        venv.create(venv_path, with_pip=True)
        print("Virtual environment created successfully.")
        
        # Find Python executable in the new venv
        venv_python = find_venv_path()
        if not venv_python:
            print("Error: Could not find Python executable in created venv.")
            sys.exit(1)
        
        # Check for requirements file and install dependencies
        req_file = find_requirements_file()
        if req_file:
            print(f"Found requirements file: {req_file}")
            print("Installing dependencies...")
            result = subprocess.run([venv_python, "-m", "pip", "install", "-r", req_file], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("Dependencies installed successfully.")
            else:
                print(f"Warning: Failed to install some dependencies:")
                print(result.stderr)
        else:
            print("No requirements file found. Virtual environment created without additional dependencies.")
            
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        sys.exit(1)

def print_help():
    print(f"""
localpython v{VERSION}
Run Python scripts using the local virtual environment (without activation)

Usage:
  localpython [options] <script> [args...]

Options:
  -p, --search-parent      Search for venv in parent directories
  --which                  Show path to venv Python interpreter
  --setup                Create venv and install dependencies from requirements file
  --version                Show localpython version
  --help                   Show this help message

Examples:
  localpython script.py
  localpython -p script.py --your-script-arg
  localpython --which
  localpython --setup
""")


def main():
    args = sys.argv[1:]
    search_parents = False

    if not args or "--help" in args:
        print_help()
        return

    if "--version" in args:
        print(f"localpython v{VERSION}")
        return

    if "--which" in args:
        venv = find_venv_path("--search-parent" in args or "-p" in args)
        if venv:
            print(venv)
        else:
            print("No virtual environment found.")
            sys.exit(1)
        return

    if "--setup" in args:
        create_venv_and_install()
        return

    if "-p" in args:
        search_parents = True
        args.remove("-p")
    if "--search-parent" in args:
        search_parents = True
        args.remove("--search-parent")

    if not args:
        print("Error: No script provided.\n")
        print_help()
        sys.exit(1)

    script = args[0]
    script_args = args[1:]

    venv_python = find_venv_path(search_parents)
    if not venv_python:
        print("No virtual environment found in current or parent directories.")
        sys.exit(1)

    subprocess.run([venv_python, script] + script_args)

