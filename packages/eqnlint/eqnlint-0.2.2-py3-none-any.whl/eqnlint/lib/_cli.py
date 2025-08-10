# lib/_cli.py
import argparse, json, sys, pathlib

def base_parser(description, audit_name, extra_args=None):
    p = argparse.ArgumentParser(description=description,
                                formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("-f","--file", required=True, help="Input LaTeX file")
    p.add_argument("-o","--output", help="Write human log to file")
    p.add_argument("--json", help="Write machine-readable JSON to file")
    p.add_argument("--dry-run", action="store_true", help="Parse only; no AI")
    p.add_argument("--model", default="gpt-4o-mini", help="LLM id or 'ollama:phi'")
    p.add_argument("--rate", type=float, default=0.5, help="Max QPS (requests/sec)")
    p.add_argument("--max-tokens", type=int, default=1200, help="LLM token cap")
    p.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    p.add_argument("--help-info", action="store_true",
                   help="Print Info Section for pipeline probing and exit")
    if extra_args: [p.add_argument(*a[0], **a[1]) for a in extra_args]
    p.set_defaults(_audit_name=audit_name)
    return p

def info_block(audit_name, summary, inputs, outputs, steps):
    return f"""\
=== Info Section ({audit_name}) ===
Name: {audit_name}
Summary: {summary}

Inputs:
{inputs}

Outputs:
{outputs}

Steps:
{steps}
"""
