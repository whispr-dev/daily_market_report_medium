"""
Script to find and fix all config imports in a Python project.
"""
import os
import re
import glob

def fix_config_imports(project_dir):
    """
    Fix all config imports in the project.
    
    Args:
        project_dir: The root directory of the project
    """
    # Find all Python files in the project
    python_files = glob.glob(os.path.join(project_dir, '**', '*.py'), recursive=True)
    
    # Fix imports in all Python files
    for python_file in python_files:
        # Read the file
        with open(python_file, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                content = f.read()
            except UnicodeDecodeError:
                print(f"Warning: Could not read {python_file} due to encoding issues. Skipping.")
                continue
        
        # Fix direct config imports
        # Pattern: from mod.config import ...
        config_import_pattern = r'from\s+config\s+import\s+([\w\.,\s]+)'
        
        # Replace with mod.config
        new_content = re.sub(config_import_pattern, r'from mod.config import \1', content)
        
        # Only write if changes were made
        if new_content != content:
            with open(python_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Fixed config import in {python_file}")

def main():
    """Main function."""
    project_dir = r"D:\code\repos\GitHub_Desktop\daily_stonk_market_report"
    
    print(f"Fixing config imports in {project_dir}...")
    fix_config_imports(project_dir)
    print("\nAll done!")
    
    print("\nNow try running your code from the project root directory with:")
    print(f"cd {project_dir}")
    print(f"python -m mod.main_enhanced")

if __name__ == "__main__":
    main()