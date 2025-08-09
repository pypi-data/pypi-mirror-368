#!/usr/bin/env python3
"""
citation_audit.py — Audit LaTeX citations for presence, correctness, and plausibility.
Part of the eqnlint audit suite.
"""

import sys, re
from pathlib import Path
import asyncio
sys.path.append(str(Path(__file__).resolve().parents[1] / "lib"))

from eqnlint.lib._fewshots import FewShotLibrary
from .audit_template import AuditStateMachine, State

class CitationAuditStateMachine(AuditStateMachine):
    def __init__(self):
        super().__init__()
        # Parent expects 'equation' + 'context' in each target
        self.required_keys = ["equation", "context"]

    def _extract_targets(self):
        """
        Find \cite{...} instances and grab ±1 paragraph of surrounding context.
        Store the full cite string in 'equation' to satisfy parent flow.
        """
        tex = self.text
        pat = re.compile(r"(\\cite\{(.*?)\})")
        targets = []

        for m in pat.finditer(tex):
            full_cite = m.group(1).strip()     # e.g., \cite{planck2020}
            # You can keep the keys if you want to use them later
            # keys = [k.strip() for k in m.group(2).split(",")]

            start, end = m.span()
            cstart = tex.rfind("\n\n", 0, start); cstart = 0 if cstart == -1 else cstart
            cend   = tex.find("\n\n", end);       cend   = len(tex) if cend == -1 else cend
            context = tex[cstart:cend].strip()

            targets.append({
                "equation": full_cite,  # << satisfy parent loop
                "context": context,
            })

        self.equations = targets
        self.log.debug(f"Audit Citations: Found {len(targets)} citation targets")

        # Advance state (or exit on dry-run)
        if getattr(self, "args", None) and getattr(self.args, "dry_run", False):
            from eqnlint.lib._textio import emit_human, emit_json
            from eqnlint.lib._cli import write_outputs
            lines = [
                f"\\n--- Citation {i+1} ---\\n{t['equation']}\\n\\n{t['context']}"
                for i, t in enumerate(self.equations)
            ]
            human = emit_human("=== DRY RUN: Citations ===", lines)
            write_outputs(
                human,
                emit_json(citations=[t["equation"] for t in self.equations]),
                self.args.output,
                self.args.json
            )
            self.state = State.SHUTDOWN
        else:
            self.state = State.GET_FEW_SHOTS

    def _get_few_shots(self):
        self.system_prompt = (
            "You are an expert in LaTeX and academic citation checking. "
            "You determine whether each citation is defined in the bibliography or may be fabricated."
        )
        self.few_shots = FewShotLibrary.citations()
        self.state = State.CALL_AI_WITH_FEW_SHOTS_AND_TARGETS
        self.log.debug(f"Audit Citations: few shots returns {self.few_shots}")
        self.log.debug(f"Audit Citations: After State call {self.state}")

    def _build_prompt(self, item: dict) -> str:
        # item['equation'] holds the full \cite{...}, and item['context'] is nearby text
        return (
            "Check the following LaTeX citation for consistency:\n"
            f"Citation: {item['equation']}\n"
            f"Context:\n\"\"\"\n{item['context']}\n\"\"\"\n"
            "Respond with exactly one of:\n"
            "✅ DEFINED   — if it’s present/valid.\n"
            "❌ UNDEFINED — if missing from bibliography.\n"
            "⚠️ POSSIBLY FABRICATED — if it seems non‑existent or unverifiable.\n"
            "Keep it short."
        )

def main():
    asyncio.run(CitationAuditStateMachine().run())

if __name__ == "__main__":
    main()