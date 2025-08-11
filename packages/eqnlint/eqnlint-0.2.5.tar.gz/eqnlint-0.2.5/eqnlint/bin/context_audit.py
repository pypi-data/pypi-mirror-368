#!/usr/bin/env python3
"""
context_audit.py — Audit LaTeX citation context for accuracy.
Part of the eqnlint audit suite.
"""

import re
import asyncio
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "lib"))

from eqnlint.lib._fewshots import FewShotLibrary
from eqnlint.lib._textio import emit_human, emit_json, write_outputs
from .audit_template import AuditStateMachine, State

class ContextAuditStateMachine(AuditStateMachine):
    def __init__(self):
        super().__init__()
        self.required_keys = ["cite", "context"]

    def _get_few_shots(self):
        self.system_prompt = "You are an expert scientific reviewer. Audit citations for accuracy."
        self.few_shots = FewShotLibrary.context()
        self.state = State.CALL_AI_WITH_FEW_SHOTS_AND_TARGETS
        self.log.debug(f"Audit Context: few shots returns {self.few_shots}")
        self.log.debug(f"Audit Context: After State call {self.state}")

    def _extract_targets(self):
        tex_data = self.text

        # catches \cite, \citep, \citet, etc.  (optional improvement)
        cite_pattern = r"(\\cite[a-zA-Z]*\{(.*?)\})"
        matches = re.finditer(cite_pattern, tex_data)
        targets = []

        for m in matches:
            full_cite = m.group(1).strip()
            cite_keys = [k.strip() for k in m.group(2).split(",")]
            start, end = m.span()
            context_start = max(0, tex_data.rfind("\n\n", 0, start))
            context_end = tex_data.find("\n\n", end)
            if context_end == -1:
                context_end = len(tex_data)
            context = tex_data[context_start:context_end].strip()
            for key in cite_keys:
                targets.append({"cite": key, "full_cite": full_cite, "context": context})

        # back-compat with parent _call_ai()
        self.equations = targets
        self.log.debug(f"Audit Context: Found {len(targets)} citation targets")

        if getattr(self.args, "dry_run", False):
            lines = [
                f"\n--- Citation {i+1} ---\n{t['full_cite']}\n\n{t['context']}"
                for i, t in enumerate(self.equations)
            ]
            human = emit_human("=== DRY RUN: Citations ===", lines)
            write_outputs(
                human,
                emit_json(citations=[t["full_cite"] for t in self.equations]),
                self.args.output,
                self.args.json
            )
            self.state = State.SHUTDOWN
            self.log.debug(f"[STATE] Transitioning to {self.state.name}")
        else:
            self.state = State.GET_FEW_SHOTS
            self.log.debug(f"[STATE] Transitioning to {self.state.name}")

    def _build_prompt(self, item: dict) -> str:
        return (
            f"Context:\n\"\"\"{item['context']}\"\"\"\n"
            f"Audit:\nDoes \\cite{{{item['cite']}}} support this claim?"
        )
    
    async def _call_ai(self):
        self.results = []
        for item in self.equations:  # these are citation targets
            prompt = self._build_prompt(item)
            self.log.debug(f"[DEBUG] Calling AI with prompt: {prompt}")
            try:
                reply = await self.ai_client.complete(self.system_prompt, prompt, fewshot=self.few_shots)
            except Exception as ex:
                reply = f"ERROR: {ex}"
            display = item.get("full_cite") or f"\\cite{{{item.get('cite','')}}}"
            # keep the 'equation' key so the base _output_results works
            self.results.append({"equation": display, "notes": reply})
            self.log.debug(f"[DEBUG] AI reply: {reply}")
        self.state = State.OUTPUT_RESULTS
        self.log.debug(f"[STATE] Transitioning to {self.state.name}")


def main():
    asyncio.run(ContextAuditStateMachine().run())

if __name__ == "__main__":
    main()