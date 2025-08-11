"""
Transformer simplificado:
- Proyección lineal (matmul + bias)
- Atención 'scaled dot-product' simplificada (sin masks)
- Feed-forward sencillo
Todo en pura Python usando megania.tensor.Tensor
"""

from .tensor import Tensor
import math
import random

class Linear:
    def __init__(self, in_dim, out_dim, seed=None):
        self.W = Tensor.random((in_dim, out_dim), scale=0.1, seed=seed)
        self.b = Tensor.random((out_dim,), scale=0.01, seed=(seed or 0)+1)

    def __call__(self, x: Tensor):
        # x: 2D tensor (batch x in_dim) ; W: in_dim x out_dim
        return x.matmul(self.W).add(self.b)  # shape: batch x out_dim

def scaled_dot_product_attention(Q: Tensor, K: Tensor, V: Tensor):
    # Q,K,V: 2D tensors (seq_len x dim)
    dk = Q.shape[1]
    scores = Q.matmul(K.transpose2d())  # seq x seq
    # scale
    scale = math.sqrt(dk) if dk>0 else 1.0
    # divide
    def div_matrix(M, s):
        return Tensor([[x/s for x in row] for row in M.data])
    scores = div_matrix(scores, scale)
    # softmax rows
    attn = scores.softmax()  # shape seq x seq
    # output = attn * V  (matmul)
    out = attn.matmul(V)
    return out

class SimpleTransformerBlock:
    def __init__(self, dim, hidden_dim=None, seed=None):
        self.dim = dim
        self.hidden_dim = hidden_dim or (dim * 4)
        self.q = Linear(dim, dim, seed=seed)
        self.k = Linear(dim, dim, seed=(seed or 0)+2)
        self.v = Linear(dim, dim, seed=(seed or 0)+3)
        self.ff1 = Linear(dim, self.hidden_dim, seed=(seed or 0)+4)
        self.ff2 = Linear(self.hidden_dim, dim, seed=(seed or 0)+5)

    def __call__(self, x: Tensor):
        # x: seq x dim
        Q = self.q(x)
        K = self.k(x)
        V = self.v(x)
        attn_out = scaled_dot_product_attention(Q, K, V)  # seq x dim
        # add & norm simplified: we skip layernorm; do residual add
        res = Tensor([[a + b for a,b in zip(row1,row2)] for row1,row2 in zip(x.data, attn_out.data)])
        # feed-forward
        ff = self.ff1(res)
        # activation ReLU
        ff_act = Tensor([[max(0.0, v) for v in row] for row in ff.data])
        ff2 = self.ff2(ff_act)
        out = Tensor([[a + b for a,b in zip(r,f)] for r,f in zip(res.data, ff2.data)])
        return out
