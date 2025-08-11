from eqnlint.lib._fewshots import FewShotLibrary
from .audit_template import AuditStateMachine, State

class SymbolicAuditStateMachine(AuditStateMachine):
    def _get_few_shots(self):
        # Sets the system prompt and few-shot examples for symbolic audits.
        self.system_prompt = "You are an expert in dimensional analysis and LaTeX math."
        self.few_shots = FewShotLibrary.symbols()
        self.state = State.CALL_AI_WITH_FEW_SHOTS_AND_TARGETS
        self.log.debug(f"Audit Symbols: few shots returns {self.few_shots}")
        self.log.debug(f"Audit Symbols: After State call {self.state}")

    def _build_prompt(self, eq: dict) -> str:
        return (
            f"Build a symbol dictionary for: {eq['equation']}\n"
            f"Context: {eq['context']}\n"
            "Output format: JSON dictionary with symbol as key and definition as value."
        )

def main():
    import asyncio
    asyncio.run(SymbolicAuditStateMachine().run())

if __name__ == "__main__":
    main()