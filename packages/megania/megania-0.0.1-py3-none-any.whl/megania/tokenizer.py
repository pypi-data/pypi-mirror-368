"""
SimpleTokenizer: tokeniza por espacios y controla vocab básico.
No usa subword ni BPE, solo mapeo palabra->id.
"""

from typing import List, Dict

class SimpleTokenizer:
    def __init__(self, vocab: Dict[str,int]=None, unk_token="<UNK>"):
        self.unk_token = unk_token
        if vocab is None:
            # vocab base con unas palabras comunes; el usuario puede entrenar/ampliar
            self.vocab = {unk_token:0, "<PAD>":1, "<BOS>":2, "<EOS>":3}
            self._next_id = 4
        else:
            self.vocab = dict(vocab)
            self._next_id = max(vocab.values())+1

    def add_token(self, token: str):
        if token not in self.vocab:
            self.vocab[token] = self._next_id
            self._next_id += 1
        return self.vocab[token]

    def encode(self, text: str, add_bos=False, add_eos=False) -> List[int]:
        toks = text.strip().split()
        ids = []
        if add_bos:
            ids.append(self.vocab.get("<BOS>",0))
        for t in toks:
            ids.append(self.vocab.get(t, self.vocab.get(self.unk_token, 0)))
        if add_eos:
            ids.append(self.vocab.get("<EOS>",0))
        return ids

    def decode(self, ids: List[int]) -> str:
        inv = {v:k for k,v in self.vocab.items()}
        words = [inv.get(i, self.unk_token) for i in ids]
        return " ".join(words)
