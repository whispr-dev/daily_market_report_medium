"""
Script to fix DataFrame ambiguity issues in your project.
This script will scan your Python files and suggest fixes.
"""
import os
import re
import pandas as pd

def find_dataframe_issues(project_dir):
    """Find potential DataFrame truth value issues in Python files."""
    issues_found = []
    
    # Find all Python files
    for root, dirs, files in os.walk(project_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Read the file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    try:
                        content = f.read()
                        
                        # Look for if statements with potential DataFrame variables
                        # This is a basic check that will catch many but not all cases
                        matches = re.finditer(r'if\s+([\w\.]+)(\s*[=<>!]+.*)?:', content)
                        
                        for match in matches:
                            var_name = match.group(1)
                            # Skip obvious non-DataFrames
                            if var_name in ['not', 'True', 'False', 'None', 'is']:
                                continue
                            
                            # Common DataFrame variable names
                            if ('df' in var_name.lower() or 
                                'data' in var_name.lower() or 
                                '_' in var_name):
                                line_num = content[:match.start()].count('\n') + 1
                                issues_found.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'match': match.group(0),
                                    'var': var_name
                                })
                    except UnicodeDecodeError:
                        continue
    
    return issues_found

def print_report(issues):
    """Print a report of all potential issues."""
    if not issues:
        print("No potential issues found!")
        return
    
    print(f"Found {len(issues)} potential DataFrame truth value issues:")
    print("\nPotential fixes:")
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. In {issue['file']} (line {issue['line']}):")
        print(f"   Original: {issue['match']}")
        print(f"   Suggested fix: if {issue['var']} is not None and not {issue['var']}.empty:")
    
    print("\nNOTE: These are just suggestions. Review each change carefully!")
    print("\nYou might also want to check your report template rendering code. "
          "Convert DataFrames to lists of dicts using .to_dict('records') before "
          "passing them to the template.")

def main():
    project_dir = input("Enter your project directory (default: current directory): ").strip()
    if not project_dir:
        project_dir = os.getcwd()
    
    issues = find_dataframe_issues(project_dir)
    print_report(issues)
    
    if issues:
        choice = input("\nDo you want suggestions on how to fix a specific issue? (y/n): ").strip().lower()
        if choice == 'y':
            idx = int(input("Enter the issue number: "))
            if 1 <= idx <= len(issues):
                issue = issues[idx-1]
                print(f"\nFor issue in {issue['file']} (line {issue['line']}):")
                print(f"1. Check if {issue['var']} is a DataFrame")
                print(f"2. If yes, replace '{issue['match']}' with:")
                print(f"   if {issue['var']} is not None and not {issue['var']}.empty:")
                print("\nAlso check if you're passing DataFrames directly to templates.")
                print("Convert them to lists of dicts with df.to_dict('records') first.")

if __name__ == "__main__":
    main()