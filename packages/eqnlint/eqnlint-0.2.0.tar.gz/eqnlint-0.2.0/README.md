# eqnlint

`eqnlint` is a scientific LaTeX equation and text auditing toolkit.  
It runs a suite of AI-powered audits to check for consistency, correctness, and plausibility in academic documents.

## Installation

```bash
pip install eqnlint
```

> Requires Python 3.9+

## Command Line Usage

Run **all audits**:

```bash
eqnlint -f my_paper.tex
```

Run an **individual audit**:

```bash
audit-units -f my_paper.tex
audit-symbolic -f my_paper.tex
audit-context -f my_paper.tex
audit-prose -f my_paper.tex
audit-citation -f my_paper.tex
audit-opacity -f my_paper.tex
audit-dimensional -f my_paper.tex
```

## Available Audits

- **citation_audit** – Check LaTeX citations for presence, correctness, and plausibility.
- **context_audit** – Verify that citations match their surrounding context.
- **dimensional_audit** – Check equations for dimensional consistency.
- **opacity_audit** – Identify undefined or unclear notation.
- **prose_audit** – Review surrounding text for clarity and academic tone.
- **symbolic_audit** – Audit symbolic math for correctness.
- **units_audit** – Verify units in equations and expressions.

## Example

```bash
eqnlint -v -f ~/Documents/MyPaper.tex
```

Outputs audit results in human-readable and/or JSON formats.

## License

MIT License. See [LICENSE](LICENSE) for details.
