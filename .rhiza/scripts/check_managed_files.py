#!/usr/bin/env python3
"""Check for modifications in files managed by the Rhiza template."""

import subprocess  # nosec
import sys
from pathlib import Path

# Path to the history file relative to the project root
HISTORY_FILE = Path(".rhiza/history")


def load_managed_files():
    """Load the list of managed files from the history file."""
    if not HISTORY_FILE.exists():
        return set()

    managed_files = set()
    with open(HISTORY_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            managed_files.add(line)
    return managed_files


def is_file_modified(file_path):
    """Check if the file is modified in git (staged or unstaged)."""
    try:
        # Check if file has any status changes (modified, added, deleted, etc.)
        result = subprocess.run(
            ["git", "status", "--porcelain", str(file_path)], capture_output=True, text=True, check=False
        )  # nosec
        if result.returncode != 0:
            return True  # Assume modified if git fails

        return bool(result.stdout.strip())
    except Exception:
        return True  # Assume modified on error


def main():
    """Main function to check for modifications in managed files."""
    changed_files = sys.argv[1:]

    if not changed_files:
        return 0

    managed_files = load_managed_files()
    if not managed_files:
        return 0

    violations = []

    for file_path in changed_files:
        normalized_path = str(Path(file_path))

        # Only check if the file is managed AND has actual changes
        if normalized_path in managed_files:
            if is_file_modified(file_path):
                violations.append(normalized_path)

    if violations:
        print("ERROR: You are attempting to modify files managed by the Rhiza template.")
        print("The following files are tracked in .rhiza/history and changes will be overwritten on the next sync:")
        for v in violations:
            print(f"  - {v}")
        print("\nTo modify these files permanently:")
        print("1. Add the file to the 'exclude' list in .rhiza/template.yml")
        print("2. Run 'make sync' (or equivalent) to update configuration")
        print("3. Commit your changes")
        print("\nIf you are performing a template sync update, use 'git commit --no-verify' to bypass this check.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
