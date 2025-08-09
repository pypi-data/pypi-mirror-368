#!/usr/bin/env python3
# bin/audit_template.py

"""
=== AUDIT TEMPLATE MODULE ===

This is a reusable audit template that defines a complete state machine workflow for AI-assisted
LaTeX audits (e.g., dimensional analysis, citation checking, opacity, etc.). It is designed to be
copied or subclassed when creating a new audit type.

EXAMPLE: To create a new audit for detecting rotational symmetry in physics equations:

1. Copy this file to: bin/rotations_audit.py
2. Rename `AuditStateMachine` to something meaningful like `RotationsAuditStateMachine`
3. Override the `_get_few_shots()` method to define a system prompt and few-shot examples
   from `lib/_fewshots.py`, such as:

       from eqnlint.lib._fewshots import few_shot_rotations

       def _get_few_shots(self):
           self.system_prompt = "You are an expert in physics reviewing equations for rotational symmetry."
           self.few_shots = few_shot_rotations
           self.state = State.CALL_AI_WITH_FEW_SHOTS_AND_TARGETS

4. (Optional) Override `_call_ai()` if you need a custom format or behavior
5. Run using: `python3 bin/rotations_audit.py -f paper.tex`

NOTES:
- This template uses a state machine for clean separation of stages
- It supports `--dry-run`, output logging, JSON saving, and future pipeline chaining
- All audit stages are modular, so new types (e.g., symbol, citation, or diagram audits) can be implemented cleanly

"""

import sys
import os
import json
from pathlib import Path
from enum import Enum, auto
import asyncio

sys.path.append(str(Path(__file__).resolve().parents[1] / "lib"))

from eqnlint.lib._cli import base_parser, info_block
from eqnlint.lib._textio import read_text, emit_human, emit_json
from eqnlint.lib._extract import extract_equations_with_context
from eqnlint.lib._ai import AIClient
from eqnlint.lib import _cli, _textio
from eqnlint.lib._textio import write_outputs

class State(Enum):
    READ_COMMAND_LINE = auto()
    VERIFY_FILE = auto()
    VERIFY_AI = auto()
    EXTRACT_TARGETS = auto()
    GET_FEW_SHOTS = auto()
    CALL_AI_WITH_FEW_SHOTS_AND_TARGETS = auto()
    OUTPUT_RESULTS = auto()
    CALL_NEXT_IN_CHAIN = auto()
    SHUTDOWN = auto()
    HANDLE_ERROR = auto()

class AuditStateMachine:
    State = State  # Expose it as a class attribute
    def __init__(self):
        self.state = State.READ_COMMAND_LINE
        self.args = None
        self.equations = []
        self.results = []
        self.ai_client = None
        self.system_prompt = ""
        self.few_shots = []
        self.log = None
        self.error = None

    async def run(self) -> None:
        while self.state != State.SHUTDOWN:
            try:
                await self.transition()
            except KeyboardInterrupt:
                if self.log:
                    self.log.info("Interrupted by user. Shutting down.")
                else:
                    print("Interrupted by user. Shutting down.")
                self.state = State.SHUTDOWN
            except Exception as e:
                self.error = e
                # If you have a HANDLE_ERROR branch in transition(), do this:
                self.state = State.HANDLE_ERROR
                # Or, if not handling errors specially, just:
                # self.state = State.SHUTDOWN
                
    async def run(self) -> None:
        while self.state != State.SHUTDOWN:
            try:
                await self.transition()
            except Exception as e:
                self.state = State.HANDLE_ERROR
                self.error = e
            except KeyboardInterrupt:
                self.log.info("Interrupted by user. Shutting down.")
                self.state = State.SHUTDOWN
            
    
    def _build_prompt(self, eq: dict) -> str:
        """
        Default prompt — override this in subclasses.
        """
        return f"Equation:\n{eq['equation']}\n\nContext:\n{eq['context']}\n\nTask: Echo equation."


    async def transition(self) -> None:
        if self.state == State.READ_COMMAND_LINE:
            self._read_command_line()

        elif self.state == State.VERIFY_FILE:
            self._verify_file()

        elif self.state == State.VERIFY_AI:
            self._verify_ai()

        elif self.state == State.EXTRACT_TARGETS:
            self._extract_targets()

        elif self.state == State.GET_FEW_SHOTS:
            self._get_few_shots()

        elif self.state == State.CALL_AI_WITH_FEW_SHOTS_AND_TARGETS:
            await self._call_ai()

        elif self.state == State.OUTPUT_RESULTS:
            self._output_results()

        elif self.state == State.CALL_NEXT_IN_CHAIN:
            self._call_next()

        elif self.state == State.HANDLE_ERROR:
            print(f"Error: {self.error}")
            self.state = State.SHUTDOWN

    def _read_command_line(self):
        parser = base_parser("Audit Template", "template")
        self.args = parser.parse_args()
        from eqnlint.lib import _debug
        _debug.set_level(self.args.verbose)
        self.log = _debug.logger

        if self.args.help_info:
            print(info_block("template", "Template audit for equations.", "Input: -f FILE", "Output: -o OUTPUT", "Steps TBD"))
            self.state = State.SHUTDOWN
        else:
            self.state = State.VERIFY_FILE
            self.log.debug(f"[STATE] Transitioning to {self.state.name}")

    def _verify_file(self):
        try:
            self.text = read_text(self.args.file)
            self.log.debug(f"Loaded file: {self.args.file}")
            self.state = State.VERIFY_AI
            self.log.debug(f"[STATE] Transitioning to {self.state.name}")
        except Exception as e:
            raise RuntimeError(f"Could not read input file: {e}")

    def _verify_ai(self):
        try:
            self.ai_client = AIClient(self.args.model, rate=self.args.rate, max_tokens=self.args.max_tokens)
            self.state = State.EXTRACT_TARGETS
            self.log.debug(f"[STATE] Transitioning to {self.state.name}")
        except Exception as e:
            raise RuntimeError(f"AIClient initialization failed: {e}")

    def _extract_targets(self):
        # This function extracts "targets" from the input text.
        # In the current audit, "targets" are mathematical equations with surrounding context.
        #
        # --- BEGIN EXTRACTION ---
        # This is where the target extractor is called. It could easily be replaced with
        # another function like `extract_diagrams_with_context()` if diagrams are the new focus.
        self.equations = extract_equations_with_context(self.text)
        self.log.debug(f"Found {len(self.equations)} equations.")
        # --- END EXTRACTION ---

        # If the `--dry-run` flag is set, we skip AI processing and just dump the extracted targets.
        if self.args.dry_run:
            self.log.info("Dry run mode: extraction only.")
            lines = [f"\n--- Equation {i+1} ---\n{e['equation']}\n\n{e['context']}" for i, e in enumerate(self.equations)]
            human = emit_human("=== DRY RUN: Equations ===", lines)
            write_outputs(
                human,
                {"equations": [e["equation"] for e in self.equations]},
                self.args.output,
                self.args.json
            )
            self.state = State.SHUTDOWN
            self.log.debug(f"[STATE] Transitioning to {self.state.name}")
        else:
            # On normal runs, move to the next state to fetch few-shot examples and prompts.
            self.state = State.GET_FEW_SHOTS

    def _get_few_shots(self):
        # === DEFAULT BEHAVIOR ===
        # This method defines the prompt and few-shot examples to send with the user query.
        # Subclasses or audit variants should override this with task-specific content.
        #
        # You can fetch predefined few-shot sets like so:
        #   from eqnlint.lib._fewshots import few_shot_rotations
        #
        # Then assign:
        #   self.system_prompt = "You are a physicist auditing for rotational symmetry..."
        #   self.few_shots = few_shot_rotations

        self.log.debug(f"[DEBUG] self.state is {self.state}, type = {type(self.state)}")
        self.system_prompt = "You are a helpful math assistant."
        self.few_shots = []
        self.state = State.CALL_AI_WITH_FEW_SHOTS_AND_TARGETS
        self.log.debug(f"[STATE] Transitioning to {self.state.name}")

    async def _call_ai(self):
        # === AI TASK LOOP ===
        # This loop sends each equation and its context to the AI model.
        # Subclasses can customize prompt formatting or error handling if needed.

        self.results = []
        for eq in self.equations:
            # prompt = f"Equation:\n{eq['equation']}\n\nContext:\n{eq['context']}\n\nTask: Echo equation."
            prompt = self._build_prompt(eq)
            self.log.debug(f"[DEBUG] Calling AI with prompt: {prompt}")
            try:
                reply = await self.ai_client.complete(self.system_prompt, prompt, fewshot=self.few_shots)
            except Exception as ex:
                reply = f"ERROR: {ex}"
            self.results.append({"equation": eq['equation'], "notes": reply})
            self.log.debug(f"[DEBUG] AI reply: {reply}")
        self.state = State.OUTPUT_RESULTS
        self.log.debug(f"[STATE] Transitioning to {self.state.name}")
    
    def _output_results(self):
        lines = [f"\n--- Equation {i+1} ---\n{r['equation']}\n{r['notes']}" for i, r in enumerate(self.results)]
        human = emit_human(f"=== {self.args._audit_name.title()} Audit ===", lines)
        json_obj = emit_json(audit=self.args._audit_name, results=self.results)
        write_outputs(human, json_obj, self.args.output, self.args.json)
        print("debugging _output_results")
        # print(human)
        # print(json.dumps(json_obj, indent=2))
        
        self.state = State.SHUTDOWN
        self.log.debug(f"[STATE] Transitioning to {self.state.name}")

    def _call_next(self):
        # Optional: define in chained pipeline mode
        self.state = State.SHUTDOWN
        self.log.debug(f"[STATE] Transitioning to {self.state.name}")

if __name__ == "__main__":
    # AuditStateMachine().run()
    asyncio.run(AuditStateMachine().run())