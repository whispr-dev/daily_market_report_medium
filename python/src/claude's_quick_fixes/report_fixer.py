"""
Script to analyze and fix a broken report file.
"""
import os
import sys
import re
from datetime import datetime

def analyze_report_file(filename):
    """
    Analyze a report file to determine what's wrong with it.
    
    Args:
        filename: Path to the report file
        
    Returns:
        dict: Analysis results
    """
    if not os.path.exists(filename):
        return {"error": f"File not found: {filename}"}
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_size = os.path.getsize(filename)
        
        analysis = {
            "file_size": file_size,
            "content_length": len(content),
            "is_html": content.strip().startswith("<!DOCTYPE html>") or content.strip().startswith("<html>"),
            "contains_python_code": "def " in content or "import " in content or "class " in content,
            "first_100_chars": content[:100]
        }
        
        # Check if it's valid HTML
        if analysis["is_html"]:
            analysis["has_body"] = "<body" in content.lower()
            analysis["has_head"] = "<head" in content.lower()
            analysis["has_closing_tags"] = "</html>" in content.lower()
        
        # Check if it's Python code
        if analysis["contains_python_code"]:
            analysis["looks_like_python_module"] = content.strip().startswith('"""') or content.strip().startswith('#')
            analysis["has_main_function"] = "def main" in content
        
        return analysis
    
    except Exception as e:
        return {"error": f"Error analyzing file: {str(e)}"}

def fix_report_file(filename, fix_type="simple"):
    """
    Attempt to fix a broken report file.
    
    Args:
        filename: Path to the report file
        fix_type: Type of fix to apply ('simple', 'content', 'generate')
        
    Returns:
        str: Path to the fixed file or None if failed
    """
    if not os.path.exists(filename):
        print(f"Error: File not found: {filename}")
        return None
    
    try:
        # Read the file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Analyze content
        analysis = analyze_report_file(filename)
        print(f"File analysis: {analysis}")
        
        if fix_type == "simple":
            # Simple fix: Try to wrap the content in HTML tags if it's not already HTML
            if not analysis.get("is_html", False):
                fixed_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Fixed Stock Market Report</title>
</head>
<body>
    <h1>Stock Market Report</h1>
    <div>
        {content}
    </div>
</body>
</html>
"""
            else:
                # If it's already HTML, but broken, try to fix missing tags
                if not analysis.get("has_body", False):
                    content = re.sub(r'<html[^>]*>', '<html>\n<body>', content, flags=re.IGNORECASE)
                
                if not analysis.get("has_closing_tags", False):
                    content += "\n</body>\n</html>"
                
                fixed_content = content
        
        elif fix_type == "content":
            # Content fix: Create a new report with the current content as debug info
            fixed_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Debug Stock Market Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow: auto; }}
    </style>
</head>
<body>
    <h1>Stock Market Report Debug</h1>
    <p>The original report file had issues. Here's the debug information:</p>
    <h2>File Analysis</h2>
    <pre>{str(analysis)}</pre>
    <h2>Original Content</h2>
    <pre>{content.replace('<', '&lt;').replace('>', '&gt;')}</pre>
</body>
</html>
"""
        
        elif fix_type == "generate":
            # Generate fix: Create a new basic report from scratch
            from simple_report_generator import main as generate_report
            print("Generating a new report...")
            return generate_report()
        
        else:
            print(f"Unknown fix type: {fix_type}")
            return None
        
        # Save the fixed content
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        fixed_filename = f"{os.path.splitext(filename)[0]}_fixed_{timestamp}.html"
        
        with open(fixed_filename, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"Fixed report saved as: {fixed_filename}")
        return fixed_filename
    
    except Exception as e:
        print(f"Error fixing report file: {e}")
        return None

def main():
    """Main function to fix a report file."""
    print("Stock Market Report Fixer")
    print("========================")
    
    # Get the filename
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # Find the most recent report file
        report_files = [f for f in os.listdir('.') if f.startswith('report_') and f.endswith('.html')]
        
        if not report_files:
            print("No report files found in the current directory.")
            return
        
        # Sort by modification time (most recent first)
        report_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        filename = report_files[0]
        print(f"Using most recent report file: {filename}")
    
    # Analyze the file
    print(f"\nAnalyzing {filename}...")
    analysis = analyze_report_file(filename)
    
    for key, value in analysis.items():
        print(f"  {key}: {value}")
    
    # Decide on the fix type
    if "error" in analysis:
        print(f"\nError in analysis: {analysis['error']}")
        return
    
    if analysis.get("is_html", False) and analysis.get("has_body", False) and analysis.get("has_closing_tags", False):
        print("\nFile appears to be valid HTML. Do you still want to fix it?")
        choice = input("Enter 'y' to continue, anything else to exit: ").strip().lower()
        if choice != 'y':
            return
        fix_type = "content"
    elif analysis.get("contains_python_code", False):
        print("\nFile appears to contain Python code instead of HTML.")
        fix_type = "generate"
    else:
        print("\nFile appears to be broken HTML or non-HTML content.")
        fix_type = "simple"
    
    # Offer fix options
    print("\nChoose a fix type:")
    print("1. Simple fix (try to repair HTML structure)")
    print("2. Content fix (create debug HTML with original content)")
    print("3. Generate new report (create a new basic report)")
    
    choice = input("Enter choice (1-3) or 'q' to quit: ").strip().lower()
    
    if choice == 'q':
        return
    elif choice == '1':
        fix_type = "simple"
    elif choice == '2':
        fix_type = "content"
    elif choice == '3':
        fix_type = "generate"
    else:
        # Use default fix type
        pass
    
    # Apply the fix
    print(f"\nApplying {fix_type} fix...")
    fixed_filename = fix_report_file(filename, fix_type)
    
    if fixed_filename:
        print(f"\nSuccess! Fixed report saved as: {fixed_filename}")
        
        # Open the file in browser
        print("Do you want to open the fixed report in your browser?")
        choice = input("Enter 'y' to open, anything else to exit: ").strip().lower()
        if choice == 'y':
            import webbrowser
            webbrowser.open(fixed_filename)
    else:
        print("\nFailed to fix the report.")

if __name__ == "__main__":
    main()