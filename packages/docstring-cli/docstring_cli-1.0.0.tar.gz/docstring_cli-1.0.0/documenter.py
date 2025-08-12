#!/usr/bin/env python3
"""
Simple Python Code Documenter
Usage: python documenter.py <filename> [function_name]
"""

import ast
import sys
import re
import requests
from typing import Optional, List, Dict

# LLM Configuration

class SimpleDocumenter:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 30

    def get_auth_token(self) -> str:
        """Get authentication token from auth service."""
        try:
            response = self.session.get(AUTH_SERVICE_URL)
            return response.text.replace("'", "").replace('"', '')
        except Exception as e:
            print(f"Auth failed: {e}")
            sys.exit(1)

    def call_llm(self, prompt: str) -> str:
        """Call LLM to generate docstring."""
        headers = {"Authorization": f"SystemAuth {self.get_auth_token()}"}
        payload = {
            "prompt": prompt,
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        try:
            response = self.session.post(KITES_URL, json=payload, headers=headers)
            result = response.json()
            return result["data"][0]["data"].strip()
        except Exception as e:
            print(f"LLM call failed: {e}")
            return ""

    def has_docstring(self, node) -> bool:
        """Check if function/class already has docstring."""
        return ast.get_docstring(node) is not None

    def get_function_signature(self, node) -> str:
        """Extract function signature as string."""
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                try:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                except:
                    pass
            args.append(arg_str)
        
        # Handle defaults
        defaults_start = len(node.args.args) - len(node.args.defaults)
        for i, default in enumerate(node.args.defaults):
            try:
                args[defaults_start + i] += f" = {ast.unparse(default)}"
            except:
                pass
        
        sig = f"def {node.name}({', '.join(args)})"
        if node.returns:
            try:
                sig += f" -> {ast.unparse(node.returns)}"
            except:
                pass
        return sig + ":"

    def generate_docstring(self, node, code_lines: List[str]) -> str:
        """Generate docstring for function/class."""
        if isinstance(node, ast.FunctionDef):
            signature = self.get_function_signature(node)
            
            # Get function body (first few lines)
            body = ""
            if hasattr(node, 'end_lineno') and node.end_lineno:
                start = node.lineno
                end = min(node.end_lineno, node.lineno + 10)
                body = "\n".join(code_lines[start-1:end])
            
            prompt = f"""Generate a concise Google-style docstring for this Python function.

Function: {signature}

Code:
{body}

Requirements:
- One line summary (imperative, no period)
- Args: section if function has parameters  
- Returns: section if function returns something
- Keep it concise and clear
- Return ONLY the docstring content (no triple quotes)

Example format:
Summary line

Args:
    param1: Description
    param2: Description

Returns:
    Description of return value
"""
        
        elif isinstance(node, ast.ClassDef):
            methods = [item.name for item in node.body if isinstance(item, ast.FunctionDef)]
            
            prompt = f"""Generate a concise Google-style docstring for this Python class.

Class: {node.name}
Methods: {', '.join(methods[:5])}

Requirements:  
- One line summary of class purpose
- Brief description of what the class does
- Return ONLY the docstring content (no triple quotes)

Example:
Summary line describing the class purpose

Brief description of functionality and usage.
"""
        
        response = self.call_llm(prompt)
        if response:
            # Clean response - remove any markdown or extra formatting
            response = response.replace('```python', '').replace('```', '').strip()
            # Remove any existing quotes that might be in the response
            response = response.replace('"""', '').replace("'''", '')
            return response
        return ""

    def format_docstring(self, content: str, base_indent: int) -> List[str]:
        """Format docstring with proper indentation."""
        if not content:
            return []
        
        lines = content.split('\n')
        formatted_lines = []
        indent_str = ' ' * base_indent
        
        # Add opening quotes
        formatted_lines.append(f'{indent_str}"""')
        
        # Add content lines with proper indentation
        for line in lines:
            if line.strip():  # Non-empty line
                formatted_lines.append(f'{indent_str}{line}')
            else:  # Empty line
                formatted_lines.append('')
        
        # Add closing quotes
        formatted_lines.append(f'{indent_str}"""')
        
        return formatted_lines

    def should_add_inline_comment(self, line: str, existing_lines: List[str], line_idx: int) -> bool:
        """Check if line should get an inline comment - only for important constructs."""
        stripped = line.strip()
        
        # Skip if already has comment
        if '#' in line:
            return False
            
        # Skip docstrings and comments
        if stripped.startswith(('"""', "'''", '#')):
            return False
            
        # Check if next line is already a comment explaining this line
        if line_idx + 1 < len(existing_lines):
            next_line = existing_lines[line_idx + 1].strip()
            if next_line.startswith('#'):
                return False
        
        # ONLY add comments for these important constructs:
        
        # 1. HTTP/API requests
        if re.search(r'\.(get|post|put|delete|patch)\s*\(', line):
            return True
            
        # 2. For loops (important iteration logic)
        if re.match(r'\s*for\s+\w+\s+in\s+', line):
            return True
            
        # 3. While loops
        if re.match(r'\s*while\s+.*:', line):
            return True
            
        # 4. Important conditionals (skip trivial ones)
        if re.match(r'\s*if\s+.*:', line) and 'if __name__' not in line:
            # Only for non-trivial conditions
            if any(important in line for important in [
                'status_code', '.get(', 'len(', 'isinstance(', 
                'not ', 'None', 'empty', 'valid'
            ]):
                return True
                
        # 5. Exception handling
        if stripped in ['try:', 'finally:'] or 'except' in stripped:
            return True
            
        # 6. Database operations
        if any(db in line for db in ['.execute(', '.query(', '.commit(', '.rollback(']):
            return True
        
        return False

    def get_smart_comment(self, line: str, context: Dict) -> str:
        """Generate simple, contextual inline comments."""
        stripped = line.strip()
        
        # For loops - just say what we're iterating over
        if re.match(r'\s*for\s+(\w+)\s+in\s+(.+):', line):
            match = re.match(r'\s*for\s+(\w+)\s+in\s+(.+):', line)
            var_name = match.group(1)
            collection = match.group(2).strip()
            
            # Clean up the collection name
            if '.items()' in collection:
                collection = collection.replace('.items()', '')
                return f"# Iterate over {collection} pairs"
            elif '.keys()' in collection:
                collection = collection.replace('.keys()', '')
                return f"# Iterate over {collection} keys"
            elif '.values()' in collection:
                collection = collection.replace('.values()', '')
                return f"# Iterate over {collection} values"
            elif 'range(' in collection:
                return f"# Iterate with range"
            else:
                return f"# Iterate over {collection}"
                
        # If conditions - describe what we're checking
        if re.match(r'\s*if\s+.*:', line) and 'if __name__' not in line:
            # Extract the main condition being checked
            condition = re.sub(r'\s*if\s+(.+):\s*', r'\1', stripped)
            
            # Simplify common patterns
            if 'status_code == 200' in condition:
                return "# Check if request successful"
            elif 'not ' in condition and any(x in condition for x in ['len(', 'numbers', 'items']):
                return "# Check if empty"
            elif '.get(' in condition:
                field_match = re.search(r"\.get\(['\"](\w+)['\"]", condition)
                if field_match:
                    return f"# Check if {field_match.group(1)} exists"
                return "# Check field value"
            elif 'None' in condition:
                return "# Check if value exists"
            else:
                # For other conditions, keep it simple
                return "# Check condition"
            
        # # HTTP requests - simple and direct
        # if re.search(r'\.(get|post|put|delete|patch)\s*\(', line):
        #     method = re.search(r'\.(get|post|put|delete|patch)', line).group(1).upper()
        #     return f"# Make {method} request"
            
        # Error handling
        if 'try:' in stripped:
            return "# Handle potential errors"
        elif 'except' in stripped:
            return "# Handle error"
            
        return ""

    def add_inline_comments(self, lines: List[str]) -> List[str]:
        """Add contextually relevant inline comments."""
        result = []
        context = {
            'in_class': False, 
            'in_function': False,
            'current_function': None,
            'current_class': None
        }
        
        for i, line in enumerate(lines):
            original = line
            stripped = line.strip()
            
            # Update context
            if stripped.startswith('class '):
                context['in_class'] = True
                context['current_class'] = stripped.split()[1].split('(')[0].rstrip(':')
            elif stripped.startswith('def '):
                context['in_function'] = True
                context['current_function'] = stripped.split()[1].split('(')[0]
            
            # Skip adding comments in certain cases
            if not self.should_add_inline_comment(line, lines, i):
                result.append(original)
                continue
            
            # Get appropriate comment
            comment = self.get_smart_comment(line, context)
            
            # Add comment if relevant and line isn't too long
            if comment and len(line.rstrip()) + len('  ' + comment) <= 100:
                # Ensure proper spacing - add comment at end of line
                result.append(line.rstrip() + '  ' + comment)
            else:
                result.append(original)
                
        return result

    def document_file(self, filename: str, target_function: Optional[str] = None):
        """Document entire file or specific function."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            print(f"Syntax error in file: {e}")
            return
        
        lines = code.split('\n')
        changes_made = False
        
        print(f"Processing {filename}...")
        
        # Process in reverse order to maintain line numbers
        nodes_to_process = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # Skip if targeting specific function and this isn't it
                if target_function and node.name != target_function:
                    continue
                    
                # Skip if already has docstring
                if self.has_docstring(node):
                    print(f"  Skipping {node.name} (already has docstring)")
                    continue
                    
                nodes_to_process.append(node)
        
        # Sort by line number in reverse order
        nodes_to_process.sort(key=lambda x: x.lineno, reverse=True)
        
        # Add docstrings
        for node in nodes_to_process:
            print(f"  Adding docstring to {node.name}...")
            
            # Generate docstring content
            docstring_content = self.generate_docstring(node, lines)
            if not docstring_content:
                print(f"    Failed to generate docstring for {node.name}")
                continue
            
            # Calculate proper indentation
            def_line = lines[node.lineno - 1]
            base_indent = len(def_line) - len(def_line.lstrip()) + 4
            
            # Format docstring with proper indentation
            formatted_docstring = self.format_docstring(docstring_content, base_indent)
            
            # Insert after the function/class definition line
            insert_position = node.lineno
            lines[insert_position:insert_position] = formatted_docstring
            
            changes_made = True
            
            # If targeting specific function, we're done
            if target_function:
                break
        
        # Add inline comments for full file processing
        if not target_function and changes_made:
            print("  Adding inline comments...")
            lines = self.add_inline_comments(lines)
        
        # Write back to file if changes were made
        if changes_made:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                print(f"✓ Updated {filename}")
            except Exception as e:
                print(f"Error writing file: {e}")
        else:
            print("  No changes needed")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Simple Python Code Documenter")
    parser.add_argument('files', nargs='+', help='Python file(s) to document')
    parser.add_argument('-f', '--functions', nargs='*', help='Function(s) to document (applies to all files, or use file:function)')
    args = parser.parse_args()

    # Parse function targets: allow file:function or just function (applies to all files)
    file_func_map = {file: set() for file in args.files}
    if args.functions:
        for func in args.functions:
            if ':' in func:
                file, fname = func.split(':', 1)
                if file in file_func_map:
                    file_func_map[file].add(fname)
            else:
                for file in file_func_map:
                    file_func_map[file].add(func)

    documenter = SimpleDocumenter()
    for file in args.files:
        if file_func_map[file]:
            for func in file_func_map[file]:
                documenter.document_file(file, func)
        else:
            documenter.document_file(file)

if __name__ == "__main__":
    main()