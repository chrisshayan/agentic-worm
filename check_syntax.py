#!/usr/bin/env python3

import ast
import sys

def check_syntax(filename):
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        ast.parse(content)
        print(f"✅ {filename} syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in {filename}:")
        print(f"   Line {e.lineno}: {e.text.strip() if e.text else 'Unknown'}")
        print(f"   Error: {e.msg}")
        print(f"   Position: {' ' * (e.offset - 1) if e.offset else ''}^")
        return False
    except Exception as e:
        print(f"❌ Error reading {filename}: {e}")
        return False

if __name__ == "__main__":
    filename = "src/agentic_worm/intelligence/workflow.py"
    success = check_syntax(filename)
    sys.exit(0 if success else 1) 