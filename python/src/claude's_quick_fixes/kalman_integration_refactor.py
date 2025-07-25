import os
import re

TARGET_DIRS = ["mod/forecast", "mod/analysis"]
REPLACEMENT_PATTERN = r'df\["close"\]\.values'
KALMAN_IMPORT = 'from mod.filters.kalman_filter import apply_kalman_filter\n'
KALMAN_PATCH = (
    '    if "kalman_smooth" in df.columns:\n'
    '        closes = df["kalman_smooth"].values[-30:]\n'
    '    else:\n'
    '        closes = df["close"].values[-30:]\n'
)

def patch_forecast_closes(lines):
    patched = []
    for line in lines:
        if REPLACEMENT_PATTERN in line:
            indent = line[:len(line) - len(line.lstrip())]
            patched.append(f"{indent}{KALMAN_PATCH}")
        else:
            patched.append(line)
    return patched

def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False

    # Ensure Kalman import present
    if KALMAN_IMPORT.strip() not in "".join(lines):
        for i, line in enumerate(lines):
            if line.startswith("import") or line.startswith("from"):
                continue
            lines.insert(i, KALMAN_IMPORT)
            modified = True
            break

    # Replace close.values with Kalman fallback
    if any(REPLACEMENT_PATTERN in line for line in lines):
        lines = patch_forecast_closes(lines)
        modified = True

    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"✅ Patched: {file_path}")
    else:
        print(f"– Skipped: {file_path} (no changes needed)")

def main():
    print("🔧 Running Kalman smoothing refactor...")

    for root_dir in TARGET_DIRS:
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith(".py"):
                    process_file(os.path.join(root, file))

    print("✅ Kalman integration complete!")

if __name__ == "__main__":
    main()
