# megania/tensor.py
"""
Tensor: implementación mínima sin numpy.
Mejoras en:
- factories zeros, random
- elementwise ops con broadcast para scalars
- apply_elementwise helper
- representación más segura
"""

import math
import random
from typing import List, Tuple, Callable, Any

def _is_list(x):
    return isinstance(x, (list, tuple))

def _deep_copy_list(lst):
    if _is_list(lst):
        return [ _deep_copy_list(x) for x in lst ]
    return lst

def _create_nested_list(shape: List[int], fill=0):
    if len(shape) == 0:
        return fill
    if len(shape) == 1:
        return [fill for _ in range(shape[0])]
    return [ _create_nested_list(shape[1:], fill) for _ in range(shape[0]) ]

class Tensor:
    def __init__(self, data):
        self.data = _deep_copy_list(data)
        self.shape = self._infer_shape(self.data)

    def _infer_shape(self, d):
        if not _is_list(d):
            return ()
        if len(d) == 0:
            return (0,)
        first = d[0]
        return (len(d),) + self._infer_shape(first)

    @classmethod
    def zeros(cls, shape: Tuple[int, ...]):
        if not shape:
            return Tensor(0)
        return cls(_create_nested_list(list(shape), fill=0))

    @classmethod
    def random(cls, shape, scale=0.1, seed=None):
        if seed is not None:
            rnd = random.Random(seed)
        else:
            rnd = random
        def rec(s):
            if len(s) == 1:
                return [rnd.uniform(-scale, scale) for _ in range(s[0])]
            return [rec(s[1:]) for _ in range(s[0])]
        return cls(rec(list(shape)))

    def tolist(self):
        return _deep_copy_list(self.data)

    def __repr__(self):
        short = self.data if len(self.shape) <= 2 else "..."
        return f"Tensor(shape={self.shape}, data={short})"

    # helpers
    def _apply_elementwise(self, other: Any, fn: Callable[[Any, Any], Any]):
        # scalar other
        if not isinstance(other, Tensor):
            def rec(x):
                if _is_list(x):
                    return [rec(y) for y in x]
                return fn(x, other)
            return Tensor(rec(self.data))
        # both tensors: shapes must match
        if self.shape != other.shape:
            raise ValueError(f"shapes must match for elementwise op: {self.shape} vs {other.shape}")
        def rec2(a,b):
            if not _is_list(a):
                return fn(a,b)
            return [rec2(x,y) for x,y in zip(a,b)]
        return Tensor(rec2(self.data, other.data))

    def add(self, other):
        return self._apply_elementwise(other, lambda a,b: a + b)

    def sub(self, other):
        return self._apply_elementwise(other, lambda a,b: a - b)

    def mul(self, other):
        return self._apply_elementwise(other, lambda a,b: a * b)

    def mul_scalar(self, scalar):
        return self._apply_elementwise(scalar, lambda a,b: a * b)

    # matmul for 2D tensors
    def matmul(self, other):
        if len(self.shape) != 2 or len(other.shape) != 2:
            raise ValueError("matmul requires 2D tensors")
        m,k1 = self.shape
        k2,n = other.shape
        if k1 != k2:
            raise ValueError("matmul shapes not aligned")
        A = self.data
        B = other.data
        C = [[0.0]*n for _ in range(m)]
        for i in range(m):
            for t in range(k1):
                a_it = A[i][t]
                bt = B[t]
                for j in range(n):
                    C[i][j] += a_it * bt[j]
        return Tensor(C)

    def transpose2d(self):
        if len(self.shape) != 2:
            raise ValueError("transpose2d requires 2D tensor")
        m,n = self.shape
        A = self.data
        return Tensor([[A[i][j] for i in range(m)] for j in range(n)])

    def softmax(self):
        if len(self.shape) == 0:
            return Tensor([1.0])
        if len(self.shape) == 1:
            xs = self.data
            m = max(xs) if xs else 0.0
            ex = [math.exp(x - m) for x in xs]
            s = sum(ex) or 1.0
            return Tensor([e/s for e in ex])
        if len(self.shape) == 2:
            out = []
            for row in self.data:
                m = max(row) if row else 0.0
                ex = [math.exp(x - m) for x in row]
                s = sum(ex) or 1.0
                out.append([e/s for e in ex])
            return Tensor(out)
        raise ValueError("softmax supports 1D or 2D tensors only")
