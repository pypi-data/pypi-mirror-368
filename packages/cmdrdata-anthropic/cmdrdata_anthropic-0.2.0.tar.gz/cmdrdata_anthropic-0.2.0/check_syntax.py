#!/usr/bin/env python3
"""
Quick syntax check for fixed files
"""
import ast
import sys
from pathlib import Path


def check_file_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error reading file: {e}"


def main():
    """Check syntax of key files we modified"""
    files_to_check = [
        "tests/test_exceptions.py",
        "cmdrdata_anthropic/context.py", 
        "tests/test_context.py",
        "cmdrdata_anthropic/version_compat.py",
        "cmdrdata_anthropic/validation.py",
        "cmdrdata_anthropic/async_client.py",
        "cmdrdata_anthropic/proxy.py",
    ]
    
    failed_files = []
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            is_valid, error = check_file_syntax(path)
            if is_valid:
                print(f"OK {file_path}: Valid syntax")
            else:
                print(f"ERROR {file_path}: {error}")
                failed_files.append(file_path)
        else:
            print(f"? {file_path}: File not found")
    
    if failed_files:
        print(f"\n{len(failed_files)} files have syntax errors")
        sys.exit(1)
    else:
        print(f"\nAll {len(files_to_check)} checked files have valid syntax!")
        sys.exit(0)


if __name__ == "__main__":
    main()