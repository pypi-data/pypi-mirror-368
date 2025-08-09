#!/usr/bin/env python3
"""
eqnlint.py — Run all available audits sequentially.

This script scans eqnlint/bin for *_audit.py modules and runs their `main()` functions
in order. All command-line args are passed through unchanged.
"""

import sys
import pkgutil
import importlib
from pathlib import Path

def main():
    # Path to bin/ directory
    bin_dir = Path(__file__).resolve().parent

    # Find *_audit.py files
    audits = [
        f.stem for f in bin_dir.glob("*_audit.py")
        if f.is_file() and not f.stem.startswith("_")
    ]

    # Sort for consistent run order
    audits.sort()

    print(f"Running all audits: {', '.join(audits)}\n")

    exit_code = 0
    for audit in audits:
        print(f"=== Running {audit} ===")
        try:
            # import eqnlint.bin.<audit>
            mod = importlib.import_module(f"eqnlint.bin.{audit}")
            if hasattr(mod, "main"):
                mod.main()
            else:
                print(f"[WARN] {audit} has no main() function, skipping.")
        except SystemExit as e:
            # capture exit codes from audit scripts
            if e.code not in (0, None):
                exit_code = e.code
        except Exception as e:
            print(f"[ERROR] {audit} failed: {e}")
            exit_code = 1

    sys.exit(exit_code)

if __name__ == "__main__":
    main()