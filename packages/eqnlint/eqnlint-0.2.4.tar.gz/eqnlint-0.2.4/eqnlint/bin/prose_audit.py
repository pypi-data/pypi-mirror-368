#!/usr/bin/env python3
import sys, asyncio
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "lib"))

from eqnlint.lib._fewshots import FewShotLibrary
from .audit_template import AuditStateMachine, State

class ProseAuditStateMachine(AuditStateMachine):
    def _get_few_shots(self):
        self.system_prompt = (
            "You review scientific prose for clarity, concision, and flow, "
            "without altering technical meaning. Keep edits minimal."
        )
        self.few_shots = FewShotLibrary.prose()
        self.state = State.CALL_AI_WITH_FEW_SHOTS_AND_TARGETS

    # eqnlint/bin/prose_audit.py (inside ProseAuditStateMachine)

    def _extract_targets(self):
        import re
        tex = self.text

        # Remove preamble and very common non-prose blocks
        # crude but effective for now
        tex = re.sub(r"\\documentclass\[.*?\]\{.*?\}", "", tex)
        tex = re.sub(r"\\usepackage(\[.*?\])?\{.*?\}", "", tex)
        tex = re.sub(r"\\title\{.*?\}", "", tex, flags=re.DOTALL)
        tex = re.sub(r"\\author\{.*?\}", "", tex, flags=re.DOTALL)
        tex = re.sub(r"\\date\{.*?\}", "", tex, flags=re.DOTALL)
        tex = re.sub(r"\\maketitle", "", tex)
        tex = re.sub(r"\\tableofcontents", "", tex)
        tex = re.sub(r"\\begin\{document\}|\\end\{document\}", "", tex)
        tex = re.sub(r"\\begin\{abstract\}|\\end\{abstract\}", "", tex)

        # Drop math blocks entirely (optional for prose audit)
        tex = re.sub(r"\\\[(?:.|\n)*?\\\]", " ", tex)  # \[ ... \]
        tex = re.sub(r"\\begin\{equation\*?\}(?:.|\n)*?\\end\{equation\*?\}", " ", tex)
        tex = re.sub(r"\$\$(?:.|\n)*?\$\$", " ", tex)
        tex = re.sub(r"\$(?:\\\$|[^$])*\$", " ", tex)

        # Remove most commands to reveal prose-ish text
        tex = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^}]*\})*", " ", tex)

        # Split into paragraphs
        paras = [p.strip() for p in re.split(r"\n\s*\n", tex) if p.strip()]

        # Heuristics to keep only “real” prose
        keep = []
        for p in paras:
            # not too short, has spaces (i.e., not a single token), contains letters
            if len(p) >= 30 and " " in p and re.search(r"[A-Za-z]", p):
                keep.append(p)

        self.equations = [{"equation": para, "context": ""} for para in keep]
        self.log.debug(f"Found {len(self.equations)} paragraphs.")
        self.state = State.GET_FEW_SHOTS

    def _build_prompt(self, item: dict) -> str:
        return (
            "Text:\n"
            f"{item['equation']}\n"
            "Task: Start with one verdict (✅ CLEAR, ⚠️ NEEDS EDIT, or ❌ UNCLEAR), "
            "then provide a concise rewrite if needed."
        )

def main():
    asyncio.run(ProseAuditStateMachine().run())

if __name__ == "__main__":
    main()