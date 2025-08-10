# tokenizer.py
import token
import tokenize
import io
from functools import lru_cache
from .mapping import PHI2P, translate

class Tokenizer:
    __slots__ = ()
    
    @staticmethod
    @lru_cache(maxsize=128)
    def _translate_token(tok_str, tok_type):
        """Cache token translations."""
        if tok_type == token.NAME:
            return PHI2P.get(tok_str, tok_str)
        return tok_str
    
    @staticmethod
    def translate_source(source):
        """Tokenize and translate PHICODE to Python."""
        try:
            tokens = tokenize.generate_tokens(io.StringIO(source).readline)
            result = []
            
            for tok in tokens:
                if tok.type == token.NAME:
                    result.append(Tokenizer._translate_token(tok.string, tok.type))
                elif tok.type not in (token.ENCODING, token.ENDMARKER):
                    result.append(tok.string)
            
            return ''.join(result)
        except tokenize.TokenError:
            # Fallback to regex
            return translate(source)