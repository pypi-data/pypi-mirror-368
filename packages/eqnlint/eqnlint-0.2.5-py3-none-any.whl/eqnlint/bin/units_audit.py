#!/usr/bin/env python3
"""
units_audit.py — Audit LaTeX equations for unit consistency (SI preferred).

This is part of the eqnlint audit suite. Can be run independently or as part of eqnlint.py.
"""

import sys
from pathlib import Path
import asyncio
sys.path.append(str(Path(__file__).resolve().parents[1] / "lib"))

# from eqnlint.lib._fewshots import few_shot_symbols, few_shot_dimensions
from eqnlint.lib._fewshots import FewShotLibrary
from .audit_template import AuditStateMachine
# from eqnlint.bin.audit_template import State
from .audit_template import State

class UnitsAuditStateMachine(AuditStateMachine):
    def _get_few_shots(self):
        # Sets the system prompt and few-shot examples for unit/dimensional audits.
        self.system_prompt = "You are auditing LaTeX equations for unit system consistency and detecting non-standard units."
        self.few_shots = FewShotLibrary.units()
        self.state = State.CALL_AI_WITH_FEW_SHOTS_AND_TARGETS
        self.log.debug(f"Audit Units: few shots returns {self.few_shots}")
        self.log.debug(f"Audit Units: After State call {self.state}")

    def _build_prompt(self, eq: dict) -> str:
        return (
            f"Check the units in:\n{eq['equation']}\n"
            f"Context: {eq['context']}\n"
            "Make sure all units are consistent (preferably SI) and note any mixed or invalid unit usage.\n"
            "Return one of: ✅ CONSISTENT, ❌ INCONSISTENT, ⚠️ MIXED UNITS. Be brief, but state the reason for your decision.\n"
        )

def main():
    asyncio.run(UnitsAuditStateMachine().run())

if __name__ == "__main__":
    main()