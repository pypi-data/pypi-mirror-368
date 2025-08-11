# lib/_debug.py
import logging

logger = logging.getLogger("eqnlint")
logger.setLevel(logging.INFO)  # Default; overridden by CLI

_handler = logging.StreamHandler()
_formatter = logging.Formatter("[%(levelname)s] %(message)s")
_handler.setFormatter(_formatter)
logger.addHandler(_handler)

def set_level(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)
