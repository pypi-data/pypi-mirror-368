# megania/tokenizer.py
"""
SimpleTokenizer mejorado:
- TokenizerConfig para controles
- Opción add_unknown_to_vocab: si True, añade palabras nuevas automáticamente
- Normalización básica integrada
"""

from typing import List, Dict, Optional
from .utils import normalize_text

class TokenizerConfig:
    def __init__(self, add_unknown_to_vocab: bool = False, unk_token: str = "<UNK>",
                 pad_token: str = "<PAD>", bos_token: str = "<BOS>", eos_token: str = "<EOS>"):
        self.add_unknown_to_vocab = add_unknown_to_vocab
        self.unk_token = unk_token
        self.pad_token = pad_token
        self.bos_token = bos_token
        self.eos_token = eos_token

class SimpleTokenizer:
    def __init__(self, vocab: Optional[Dict[str,int]] = None, config: Optional[TokenizerConfig] = None):
        self.config = config or TokenizerConfig()
        if vocab is None:
            # seed vocab with control tokens in deterministic order
            self.vocab = {
                self.config.unk_token: 0,
                self.config.pad_token: 1,
                self.config.bos_token: 2,
                self.config.eos_token: 3
            }
            self._next_id = 4
        else:
            self.vocab = dict(vocab)
            self._next_id = max(self.vocab.values()) + 1 if len(self.vocab) else 0

    def add_token(self, token: str) -> int:
        token = str(token)
        if token not in self.vocab:
            self.vocab[token] = self._next_id
            self._next_id += 1
        return self.vocab[token]

    def encode(self, text: str, add_bos: bool = False, add_eos: bool = False, expand_vocab: Optional[bool] = None) -> List[int]:
        """
        Convierte texto a ids. Si expand_vocab o el config.allow permite, añade tokens nuevos.
        """
        if text is None:
            return []
        t = normalize_text(text)
        toks = t.split()
        ids = []
        if add_bos:
            ids.append(self.vocab.get(self.config.bos_token, 0))
        for tok in toks:
            if tok in self.vocab:
                ids.append(self.vocab[tok])
            else:
                should_add = expand_vocab if expand_vocab is not None else self.config.add_unknown_to_vocab
                if should_add:
                    ids.append(self.add_token(tok))
                else:
                    ids.append(self.vocab.get(self.config.unk_token, 0))
        if add_eos:
            ids.append(self.vocab.get(self.config.eos_token, 0))
        return ids

    def decode(self, ids: List[int]) -> str:
        inv = {v:k for k,v in self.vocab.items()}
        words = [inv.get(i, self.config.unk_token) for i in ids]
        return " ".join(words)

    def vocab_size(self) -> int:
        return len(self.vocab)
