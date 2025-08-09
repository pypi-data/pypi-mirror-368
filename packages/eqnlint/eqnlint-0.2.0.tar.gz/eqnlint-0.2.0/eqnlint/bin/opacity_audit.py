#!/usr/bin/env python3
"""
opacity_audit.py — Audit LaTeX equations for undefined/opaque symbols, acronyms, and notation.

This is part of the eqnlint audit suite. Can be run independently or as part of eqnlint.py.
"""

import sys
from pathlib import Path
import asyncio

# Keep parity with other audits that extend the import path for local dev
sys.path.append(str(Path(__file__).resolve().parents[1] / "lib"))

from eqnlint.lib._fewshots import FewShotLibrary
from .audit_template import AuditStateMachine, State

class OpacityAuditStateMachine(AuditStateMachine):
    def _get_few_shots(self):
        # System prompt + few-shots for opacity/undefined symbol checks
        self.system_prompt = (
            "You are an AI that reviews LaTeX papers for opaque or undefined symbols, "
            "acronyms, and notation."
        )
        self.few_shots = FewShotLibrary.opacity()
        self.state = State.CALL_AI_WITH_FEW_SHOTS_AND_TARGETS
        self.log.debug(f"Audit Opacity: few shots returns {self.few_shots}")
        self.log.debug(f"Audit Opacity: After State call {self.state}")

    def _build_prompt(self, eq: dict) -> str:
        # The base template already extracts equations + local context
        return (
            f"Check this equation:\n{eq['equation']}\n"
            f"Context:\n{eq['context']}\n\n"
            "Identify any undefined symbols, acronyms, or notations missing from the context. "
            "Suggest clear definitions, or mark as:\n"
            "✅ ALL SYMBOLS DEFINED if nothing is missing.\n"
            "Prefer a concise verdict first, then a brief reason."
        )

def main():
    asyncio.run(OpacityAuditStateMachine().run())

if __name__ == "__main__":
    main()