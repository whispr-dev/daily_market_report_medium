import os
import re

OLD_IMPORTS = [
    r"from\s+mod\.utils\.image_utils\s+import\s+img_to_base64",
    r"from\s+mod\.utils\.image_utils\s+import\s+fig_to_base64",
]

NEW_IMPORT = "from mod.utils.image_utils import fig_to_png_bytes"

OLD_CALLS = {
    r"img_to_base64\s*\(": "fig_to_png_bytes(",
    r"fig_to_base64\s*\(": "fig_to_png_bytes(",
}

def refactor_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Remove old imports and add new import
    for old_import in OLD_IMPORTS:
        content = re.sub(old_import, "", content)

    if NEW_IMPORT not in content:
        content = NEW_IMPORT + "\n" + content

    # Replace old function calls
    for old_call, new_call in OLD_CALLS.items():
        content = re.sub(old_call, new_call, content)

    # Cleanup any double blank lines
    content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Patched: {filepath}")
    else:
        print(f"– Skipped (no changes): {filepath}")

def walk_and_refactor(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                fullpath = os.path.join(root, file)
                refactor_file(fullpath)

if __name__ == "__main__":
    target_dir = os.path.abspath(".")  # Run from project root
    print(f"Refactoring image utility calls in: {target_dir}")
    walk_and_refactor(target_dir)
    print("🎉 Refactor complete.")
