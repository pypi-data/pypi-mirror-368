# megania/__init__.py
"""
megania - package entrypoint
Version: 0.0.2b0
"""

from .tensor import Tensor
from .tokenizer import SimpleTokenizer, TokenizerConfig
from .transformer import Linear, SimpleTransformerBlock, scaled_dot_product_attention
from .megan import Megan
from .utils import normalize_text

__all__ = [
    "Tensor",
    "SimpleTokenizer",
    "TokenizerConfig",
    "Linear",
    "SimpleTransformerBlock",
    "scaled_dot_product_attention",
    "Megan",
    "normalize_text",
]
