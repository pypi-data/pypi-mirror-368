# mapping.py
import re
from functools import lru_cache

# Static mappings - loaded once
P2P = {
    "False": "⊥", "None": "Ø", "True": "✓", "and": "∧", "as": "↦",
    "assert": "‼", "async": "⟳", "await": "⌛", "break": "⇲", "class": "ℂ",
    "continue": "⇉", "def": "ƒ", "del": "∂", "elif": "⤷", "else": "⋄",
    "except": "⛒", "finally": "⇗", "for": "∀", "from": "←", "global": "⟁",
    "if": "¿", "import": "⇒", "in": "∈", "is": "≡", "lambda": "λ",
    "nonlocal": "∇", "not": "¬", "or": "∨", "pass": "⋯", "raise": "↑",
    "return": "⟲", "try": "∴", "while": "↻", "with": "∥", "yield": "⟰",
    "print": "π",
}

# Inverted map
PHI2P = {v: k for k, v in P2P.items()}

# Compiled regex for batch replacement
_pattern = re.compile('|'.join(re.escape(s) for s in PHI2P.keys()))

@lru_cache(maxsize=256)
def translate(source):
    """Convert PHICODE symbols to Python keywords."""
    return _pattern.sub(lambda m: PHI2P[m.group()], source)