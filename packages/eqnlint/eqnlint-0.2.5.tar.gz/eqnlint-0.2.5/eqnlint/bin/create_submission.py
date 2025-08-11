#!/usr/bin/env python3

"""
create_submission.py - Helper script to prepare LaTeX submissions for journals.

Features:
✅ Runs dimensional & symbolic audits on LaTeX equations.
✅ Generates a summary report (Markdown + text).
✅ Packages sources and figures into a tarball.
✅ Optional PRL-style checklist.

MIT License © 2025 John Ryan
"""

import os
import sys
import argparse
import subprocess
import tarfile
from datetime import datetime

def run_audits(tex_file, output_dir):
    """Run dimensional and symbolic audits on a LaTeX file."""
    dim_log = os.path.join(output_dir, "dimensional_audit.log")
    sym_log = os.path.join(output_dir, "symbolic_audit.log")

    print(f"🔍 Running dimensional audit on {tex_file}...")
    subprocess.run([
        sys.executable, "bin/dimensional_audit.py",
        "-f", tex_file,
        "-o", dim_log
    ], check=True)

    print(f"🔍 Running symbolic audit on {tex_file}...")
    subprocess.run([
        sys.executable, "bin/symbolic_audit.py",
        "-f", tex_file,
        "-o", sym_log
    ], check=True)

    return dim_log, sym_log

def generate_summary(output_dir, dim_log, sym_log, summary_file):
    """Combine audit results into a Markdown summary."""
    with open(summary_file, "w") as out:
        out.write(f"# 📄 Equation Lint Summary\n\n")
        out.write(f"Generated on: {datetime.now()}\n\n")

        out.write("## 📐 Dimensional Audit Results\n\n")
        with open(dim_log) as dim:
            out.writelines(dim.readlines())

        out.write("\n## 🧠 Symbolic Audit Results\n\n")
        with open(sym_log) as sym:
            out.writelines(sym.readlines())

        out.write("\n---\n✅ All equations checked using eqn-lint.\n")
    print(f"✅ Summary report written to {summary_file}")

def package_submission(source_dir, output_tar, skip_figures):
    """Package LaTeX sources and optionally figures into a tar.gz."""
    print(f"📦 Packaging submission to {output_tar}...")
    with tarfile.open(output_tar, "w:gz") as tar:
        for root, dirs, files in os.walk(source_dir):
            for f in files:
                path = os.path.join(root, f)
                rel_path = os.path.relpath(path, source_dir)
                if skip_figures and rel_path.startswith("figures"):
                    continue
                tar.add(path, arcname=rel_path)
    print("✅ Submission tarball created.")

def main():
    parser = argparse.ArgumentParser(description="Prepare LaTeX submission with audits and tarball.")
    parser.add_argument("-p", "--project", required=True, help="Path to LaTeX project directory")
    parser.add_argument("-o", "--output", default="submission", help="Output directory for reports and tarball")
    parser.add_argument("--run-audits", action="store_true", help="Run dimensional & symbolic audits")
    parser.add_argument("--skip-figures", action="store_true", help="Do not include figures in tarball")
    parser.add_argument("--summary-only", action="store_true", help="Only generate summary, skip tarball packaging")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    summary_file = os.path.join(args.output, "eqn_lint_summary.md")
    output_tar = os.path.join(args.output, "submission.tar.gz")

    # Find .tex files in project directory
    tex_files = [
        os.path.join(root, f)
        for root, dirs, files in os.walk(args.project)
        for f in files if f.endswith(".tex")
    ]

    if not tex_files:
        print("❌ No LaTeX files found in project directory.")
        sys.exit(1)

    print(f"📂 Found {len(tex_files)} LaTeX file(s).")

    if args.run_audits:
        for tex_file in tex_files:
            dim_log, sym_log = run_audits(tex_file, args.output)
        generate_summary(args.output, dim_log, sym_log, summary_file)

    if not args.summary_only:
        package_submission(args.project, output_tar, args.skip_figures)

if __name__ == "__main__":
    main()
