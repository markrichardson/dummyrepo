#!/usr/bin/env python3
"""Check if any of the files being changed are managed by the Rhiza template."""

import os
import subprocess  # nosec B404
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


def get_base_ref():
    """Try to determine the base branch for comparison."""
    # Common base branches
    candidates = ["origin/main", "origin/master", "main", "master"]

    # Check if we are in a GitHub Action
    github_base = os.environ.get("GITHUB_BASE_REF")
    if github_base:
        # In PRs, this is the target branch (e.g. main)
        # We might need origin/github_base
        candidates.insert(0, f"origin/{github_base}")
        candidates.insert(0, github_base)

    for ref in candidates:
        try:
            subprocess.run(  # nosec B603, B607
                ["git", "rev-parse", "--verify", ref],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            continue
        return ref

    return None


def is_modified(file_path, base_ref=None):
    """Check if the file is modified.

    1. In the working tree or index (staged/unstaged).
    2. Committed but different from base_ref (if provided and in CI).
    """
    file_str = str(file_path)

    # 1. Check working tree/index status
    try:
        status_res = subprocess.run(  # nosec B603, B607
            ["git", "status", "--porcelain", file_str],
            capture_output=True,
            text=True,
            check=False,
        )
        if status_res.returncode == 0 and status_res.stdout.strip():
            return True
    except Exception:  # nosec B110
        pass

    # 2. Check committed changes relative to base (ONLY IN CI)
    # We avoid checking this locally to prevent "make fmt" from failing
    # on unmerged syncs or feature branches.
    if base_ref and os.environ.get("CI"):
        try:
            # git diff --name-only base...HEAD -- file
            # verifies if file changed in the commit range
            diff_res = subprocess.run(  # nosec B603, B607
                ["git", "diff", "--name-only", f"{base_ref}...HEAD", "--", file_str],
                capture_output=True,
                text=True,
                check=False,
            )
            if diff_res.returncode == 0 and diff_res.stdout.strip():
                return True
        except Exception:  # nosec B110
            pass

    return False


def main():  # noqa: D103
    changed_files = sys.argv[1:]

    if not changed_files:
        return 0

    managed_files = load_managed_files()
    if not managed_files:
        return 0

    # Determine base ref for committed change detection
    base_ref = get_base_ref()

    violations = []

    for file_path in changed_files:
        normalized_path = str(Path(file_path))

        if normalized_path in managed_files:
            if is_modified(file_path, base_ref):
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
