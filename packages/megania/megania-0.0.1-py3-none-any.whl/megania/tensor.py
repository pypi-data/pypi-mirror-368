"""
Tensor: implementación mínima sin numpy.
Soporta:
- creation from nested lists
- shape
- basic elementwise add, mul, matmul (2D), transpose (2D)
- softmax over last axis
"""

import math
import random
from typing import List, Tuple

def _is_list(x):
    return isinstance(x, (list, tuple))

def _deep_copy_list(lst):
    if _is_list(lst):
        return [ _deep_copy_list(x) for x in lst ]
    return lst

class Tensor:
    def __init__(self, data):
        # we store nested lists (immutable-like copy)
        self.data = _deep_copy_list(data)
        self.shape = self._infer_shape(self.data)

    def _infer_shape(self, d):
        if not _is_list(d):
            return ()
        if len(d) == 0:
            return (0,)
        first_shape = self._infer_shape(d[0])
        return (len(d),) + first_shape

    @classmethod
    def zeros(cls, shape: Tuple[int, ...]):
        if len(shape) == 0:
            return Tensor(0)
        def make(n, rest):
            if len(rest) == 0:
                return [0 for _ in range(n)]
            return [ make(rest[0], rest[1:]) if False else make_for(rest) for _ in range(n) ]
        # simpler recursive maker
        def rec(s):
            if len(s) == 1:
                return [0 for _ in range(s[0])]
            return [rec(s[1:]) for _ in range(s[0])]
        return cls(rec(list(shape)))

    @classmethod
    def random(cls, shape, scale=0.1, seed=None):
        if seed is not None:
            random.seed(seed)
        def rec(s):
            if len(s) == 1:
                return [random.uniform(-scale, scale) for _ in range(s[0])]
            return [rec(s[1:]) for _ in range(s[0])]
        return cls(rec(list(shape)))

    def tolist(self):
        return _deep_copy_list(self.data)

    def __repr__(self):
        return f"Tensor(shape={self.shape}, data={self.data if len(self.shape)<=2 else '...'} )"

    # elementwise add (supports broadcasting for scalars)
    def add(self, other):
        if not isinstance(other, Tensor):
            # scalar add
            def rec(x):
                if _is_list(x):
                    return [rec(y) for y in x]
                return x + other
            return Tensor(rec(self.data))
        # both tensors: naive elementwise if shapes equal
        if self.shape != other.shape:
            raise ValueError("shapes not equal for add")
        def rec(a,b):
            if not _is_list(a):
                return a + b
            return [rec(x,y) for x,y in zip(a,b)]
        return Tensor(rec(self.data, other.data)) if False else Tensor(rec(self.data, other.data))

    def mul_scalar(self, scalar):
        def rec(x):
            if _is_list(x):
                return [rec(y) for y in x]
            return x * scalar
        return Tensor(rec(self.data))

    # matrix multiplication for 2D tensors
    def matmul(self, other):
        if len(self.shape) != 2 or len(other.shape) != 2:
            raise ValueError("matmul only supports 2D tensors")
        m, k1 = self.shape
        k2, n = other.shape
        if k1 != k2:
            raise ValueError("shapes not aligned for matmul")
        A = self.data
        B = other.data
        # compute result
        C = [[0.0]*n for _ in range(m)]
        for i in range(m):
            ai = A[i]
            for t in range(k1):
                a_it = ai[t]
                bt = B[t]
                for j in range(n):
                    C[i][j] += a_it * bt[j]
        return Tensor(C)

    def transpose2d(self):
        if len(self.shape) != 2:
            raise ValueError("transpose2d supports 2D only")
        m, n = self.shape
        A = self.data
        return Tensor([[A[i][j] for i in range(m)] for j in range(n)])

    # softmax over last axis for 2D (batch x dim)
    def softmax(self):
        if len(self.shape) == 1:
            xs = self.data
            m = max(xs)
            ex = [math.exp(x-m) for x in xs]
            s = sum(ex) or 1.0
            return Tensor([e/s for e in ex])
        if len(self.shape) == 2:
            out = []
            for row in self.data:
                m = max(row)
                ex = [math.exp(x-m) for x in row]
                s = sum(ex) or 1.0
                out.append([e/s for e in ex])
            return Tensor(out)
        raise ValueError("softmax supports 1D or 2D tensors")
