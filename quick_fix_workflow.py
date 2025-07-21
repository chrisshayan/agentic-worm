#!/usr/bin/env python3

import os

def fix_workflow_syntax():
    """Fix the syntax error in workflow.py around line 635."""
    
    # Read the current file
    workflow_path = "src/agentic_worm/intelligence/workflow.py"
    
    with open(workflow_path, 'r') as f:
        lines = f.readlines()
    
    # Find the problematic section (around lines 625-645)
    # The issue is with the indentation after the try block
    
    # Fix: Ensure proper indentation after the try block
    fixed_lines = []
    in_fix_section = False
    fix_applied = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Start of the section to fix
        if line_num == 629 and "if self.memory_manager:" in line:
            in_fix_section = True
            fixed_lines.append(line)
            continue
            
        # Fix the try block indentation
        if in_fix_section and line_num == 630 and "try:" in line:
            fixed_lines.append("                try:\n")
            continue
            
        # Fix the subsequent lines to have proper indentation
        if in_fix_section and line_num >= 631 and line_num <= 640:
            if line.strip() and not line.startswith("                    "):
                # Fix indentation - should be 20 spaces (5 levels)
                content = line.lstrip()
                fixed_lines.append("                    " + content)
                fix_applied = True
            else:
                fixed_lines.append(line)
            continue
            
        # End of fix section
        if line_num > 640:
            in_fix_section = False
            
        fixed_lines.append(line)
    
    # Write the fixed file
    if fix_applied:
        with open(workflow_path, 'w') as f:
            f.writelines(fixed_lines)
        print(f"✅ Fixed syntax error in {workflow_path}")
        return True
    else:
        print(f"⚠️ No syntax fix needed in {workflow_path}")
        return False

if __name__ == "__main__":
    success = fix_workflow_syntax()
    
    # Test the syntax
    import ast
    try:
        with open("src/agentic_worm/intelligence/workflow.py", 'r') as f:
            content = f.read()
        ast.parse(content)
        print("✅ Syntax is now valid!")
    except SyntaxError as e:
        print(f"❌ Syntax error still exists: Line {e.lineno}: {e.msg}")
        print("🔧 Manual fix required") 