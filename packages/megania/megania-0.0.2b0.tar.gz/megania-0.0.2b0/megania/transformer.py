# megania/transformer.py
"""
megania.transformer
Versión 0.0.2b0 - Transformador simplificado, funcional y autocontenido.

Características principales:
- Linear (proyección) con inicialización determinista.
- LayerNorm (implementación simple en Python).
- MultiHeadAttention (scaled dot-product) con manejo de heads.
- FeedForward (2-layer MLP con activación GELU/Relu opcional).
- Positional Embeddings (sin dependencias).
- SimpleTransformerBlock que combina atención + feed-forward + residual + layernorm.
- TransformerModel que encadena varios bloques y expone forward() y encode().
- Utilities para reshape entre (seq, dim) <-> (seq, heads, head_dim).
- Diseñado para usar la clase Tensor del paquete (no numpy).

Requisitos: que la clase Tensor de megania.tensor implemente al menos:
- Tensor.random(shape, scale=.., seed=..)
- Tensor.zeros(shape)
- Tensor.matmul(other)
- Tensor.transpose2d()
- Tensor.add(other_or_scalar)
- Tensor.mul_scalar(scalar)
- Tensor.softmax()  (soporta 1D y 2D)
- Tensor.tolist(), Tensor.shape
- Tensor.__repr__()

Todos los cálculos están hechos con listas internas y conversiones a Tensor cuando conviene,
para mantener claridad y compatibilidad con la implementación básica de Tensor.
"""

from typing import List, Tuple, Optional, Callable, Any, Dict
import math
import random

from .tensor import Tensor

# -------------------------
# Helpers / util functions
# -------------------------

def _seed_random(seed: Optional[int]) -> random.Random:
    """Devuelve un Random con semilla si seed no es None"""
    if seed is None:
        return random
    return random.Random(seed)

def _ensure_2d(t: Tensor) -> Tensor:
    """Asegura que Tensor sea 2D (seq x dim). Si es 1D, lo convierte a 2D con shape (1, n)."""
    if len(t.shape) == 1:
        return Tensor([t.data]) if isinstance(t.data, list) else Tensor([t.tolist()])
    return t

def _average_pool_rows(t: Tensor) -> List[float]:
    """Promedia las filas de un tensor 2D -> vector (dim,)"""
    if len(t.shape) == 0:
        return [t.data]
    if len(t.shape) == 1:
        return t.data
    rows = t.tolist()
    seq = len(rows)
    dim = len(rows[0]) if rows else 0
    acc = [0.0] * dim
    for r in rows:
        for j, v in enumerate(r):
            acc[j] += v
    if seq > 0:
        for j in range(dim):
            acc[j] /= seq
    return acc

def _dot_product(a: List[float], b: List[float]) -> float:
    """Producto punto de dos vectores (mismo tamaño)."""
    return sum(x*y for x,y in zip(a,b))

def _vector_add(a: List[float], b: List[float]) -> List[float]:
    return [x+y for x,y in zip(a,b)]

def _vector_sub(a: List[float], b: List[float]) -> List[float]:
    return [x-y for x,y in zip(a,b)]

def _vector_mul(a: List[float], scalar: float) -> List[float]:
    return [x*scalar for x in a]

def _gather_rows(matrix: List[List[float]], indices: List[int]) -> List[List[float]]:
    return [matrix[i] for i in indices]

# -------------------------
# Linear layer
# -------------------------

class Linear:
    """
    Capa lineal simple: y = x @ W + b
    - in_dim: dimensión de entrada
    - out_dim: dimensión de salida
    - seed: semilla para inicialización determinista (opcional)
    """

    def __init__(self, in_dim: int, out_dim: int, seed: Optional[int] = None, scale: float = 0.07):
        self.in_dim = in_dim
        self.out_dim = out_dim
        rnd = _seed_random(seed)
        # inicializamos W: in_dim x out_dim
        W = [[(rnd.random() * 2 - 1) * scale for _ in range(out_dim)] for _ in range(in_dim)]
        b = [(rnd.random() * 2 - 1) * (scale * 0.1) for _ in range(out_dim)]
        self.W = Tensor(W)   # shape: (in_dim, out_dim)
        self.b = Tensor([b]) if False else Tensor([b])  # store as 2D row for easy broadcasting with existing Tensor ops
        # Observación: nuestro Tensor.matmul espera (m x k) @ (k x n) -> (m x n)
        # Para multiplicar entrada X (seq x in_dim) por W (in_dim x out_dim) usamos matmul directamente.

    def __call__(self, x: Tensor) -> Tensor:
        """
        x: Tensor de shape (seq, in_dim) o (batch, in_dim)
        returns: Tensor (seq, out_dim)
        """
        # x.matmul(self.W) -> (seq x out_dim)
        out = x.matmul(self.W)
        # out.add(self.b) -> broadcast b across rows (b is 2D row)
        return out.add(self.b)

    def to_dict(self) -> Dict[str, Any]:
        return {"in_dim": self.in_dim, "out_dim": self.out_dim}

# -------------------------
# Layer Normalization
# -------------------------

class LayerNorm:
    """
    Implementación simple de LayerNorm aplicada por fila (feature-wise).
    No usa parámetros gamma/beta por defecto (pero se permiten).
    """

    def __init__(self, dim: int, eps: float = 1e-5, eps_floor: float = 1e-12, use_gamma_beta: bool = True, seed: Optional[int] = None):
        self.dim = dim
        self.eps = eps
        self.eps_floor = eps_floor
        self.use_gamma_beta = use_gamma_beta
        rnd = _seed_random(seed)
        if use_gamma_beta:
            # gamma alrededor de 1, beta alrededor de 0 (deterministic)
            self.gamma = [1.0 + ((rnd.random() - 0.5) * 0.02) for _ in range(dim)]
            self.beta = [((rnd.random() - 0.5) * 0.02) for _ in range(dim)]
        else:
            self.gamma = [1.0] * dim
            self.beta = [0.0] * dim

    def __call__(self, x: Tensor) -> Tensor:
        """
        x: Tensor (seq x dim)
        Return: Tensor normalized (same shape)
        """
        if len(x.shape) == 1:
            rows = [x.tolist()]
        else:
            rows = x.tolist()
        out = []
        for row in rows:
            mean = sum(row) / max(1, len(row))
            var = sum((v - mean) ** 2 for v in row) / max(1, len(row))
            denom = math.sqrt(var + self.eps)
            denom = max(denom, self.eps_floor)
            normalized = [ (v - mean) / denom for v in row ]
            scaled = [ normalized[i] * self.gamma[i] + self.beta[i] for i in range(self.dim) ]
            out.append(scaled)
        if len(x.shape) == 1:
            return Tensor(out[0])
        return Tensor(out)

# -------------------------
# Activation functions
# -------------------------

def relu_vec(v: List[float]) -> List[float]:
    return [max(0.0, x) for x in v]

def gelu_vec(v: List[float]) -> List[float]:
    # Approximation of GELU
    out = []
    for x in v:
        # 0.5 * x * (1 + tanh( sqrt(2/pi) * (x + 0.044715 x^3) ) )
        inner = math.sqrt(2.0/math.pi) * (x + 0.044715 * (x**3))
        out.append(0.5 * x * (1.0 + math.tanh(inner)))
    return out

# -------------------------
# Multi-Head Attention
# -------------------------

def _reshape_seq_dim_to_heads(rows: List[List[float]], num_heads: int) -> List[List[List[float]]]:
    """
    Convierte lista de filas (seq x dim) a estructura (seq x heads x head_dim)
    donde head_dim = dim // num_heads. No realiza checks de divisibilidad.
    """
    if not rows:
        return []
    seq = len(rows)
    dim = len(rows[0])
    if dim % num_heads != 0:
        raise ValueError(f"dim ({dim}) no divisible por num_heads ({num_heads})")
    head_dim = dim // num_heads
    out = []
    for r in rows:
        heads = []
        for h in range(num_heads):
            start = h * head_dim
            heads.append(r[start:start+head_dim])
        out.append(heads)
    return out  # shape seq x heads x head_dim

def _reshape_heads_to_seq_dim(seq_heads: List[List[List[float]]]) -> List[List[float]]:
    """
    Convierte (seq x heads x head_dim) -> (seq x (heads*head_dim))
    """
    out = []
    for heads in seq_heads:
        row = []
        for h in heads:
            row.extend(h)
        out.append(row)
    return out

class MultiHeadAttention:
    """
    Multi-Head Attention (scaled dot-product) implementado con operaciones sobre listas y Tensor.
    - dim: dimensión total de embedding (debe ser divisible por num_heads)
    - num_heads: número de cabezas
    - seed: semilla para inicialización determinística
    """

    def __init__(self, dim: int, num_heads: int = 4, seed: Optional[int] = None, scale: float = 0.07):
        if dim % num_heads != 0:
            raise ValueError("dim must be divisible by num_heads")
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        # proyecciones Q, K, V y salida O
        self.q_linear = Linear(dim, dim, seed=(None if seed is None else seed+11), scale=scale)
        self.k_linear = Linear(dim, dim, seed=(None if seed is None else seed+13), scale=scale)
        self.v_linear = Linear(dim, dim, seed=(None if seed is None else seed+17), scale=scale)
        self.out_linear = Linear(dim, dim, seed=(None if seed is None else seed+19), scale=scale)

    def _scaled_dot_product(self, Q_rows: List[List[float]], K_rows: List[List[float]], V_rows: List[List[float]]) -> List[List[float]]:
        """
        Q_rows, K_rows, V_rows: listas de filas (seq x dim) --- pero aquí asumimos dim = head_dim
        Retorna: lista de filas (seq x head_dim) del resultado de attention sobre la secuencia.
        Implementación:
          scores = Q @ K^T
          scores = scores / sqrt(head_dim)
          attn = softmax(rows)
          out = attn @ V
        """
        # Convertir a Tensor para aprovechar matmul y softmax (si preferimos),
        # pero aquí implementamos directamente con listas por claridad.
        seq = len(Q_rows)
        if seq == 0:
            return []
        # Q_rows: seq x head_dim
        # K_rows: seq x head_dim
        # V_rows: seq x head_dim
        # compute scores (seq x seq)
        scores = [[0.0]*seq for _ in range(seq)]
        for i in range(seq):
            for j in range(seq):
                scores[i][j] = _dot_product(Q_rows[i], K_rows[j])
        # scale
        scale = math.sqrt(max(1, len(Q_rows[0])))
        for i in range(seq):
            for j in range(seq):
                scores[i][j] /= scale
        # softmax per row
        attn = []
        for i in range(seq):
            row = scores[i]
            m = max(row) if row else 0.0
            ex = [math.exp(x - m) for x in row]
            s = sum(ex) or 1.0
            attn.append([e/s for e in ex])
        # final output: attn (seq x seq) @ V_rows (seq x head_dim) -> seq x head_dim
        out = []
        for i in range(seq):
            # out_i = sum_j attn[i][j] * V_rows[j]
            accum = [0.0] * len(V_rows[0])
            for j in range(seq):
                a = attn[i][j]
                v = V_rows[j]
                for h in range(len(v)):
                    accum[h] += a * v[h]
            out.append(accum)
        return out

    def __call__(self, x: Tensor) -> Tensor:
        """
        x: Tensor (seq x dim)
        returns: Tensor (seq x dim)
        Pipeline:
          Q = x @ Wq   (seq x dim)
          K = x @ Wk
          V = x @ Wv
          split into heads -> seq x heads x head_dim
          for each head: attention -> seq x head_dim
          concat heads -> seq x dim
          out = concat @ Wo
        """
        if len(x.shape) == 1:
            raise ValueError("MultiHeadAttention expects 2D Tensor (seq x dim)")
        seq = x.shape[0]
        # project
        Q = self.q_linear(x)  # seq x dim
        K = self.k_linear(x)
        V = self.v_linear(x)
        Q_rows = Q.tolist()
        K_rows = K.tolist()
        V_rows = V.tolist()
        # reshape into heads
        Q_heads = _reshape_seq_dim_to_heads(Q_rows, self.num_heads)  # seq x heads x head_dim
        K_heads = _reshape_seq_dim_to_heads(K_rows, self.num_heads)
        V_heads = _reshape_seq_dim_to_heads(V_rows, self.num_heads)
        # attention per head
        out_heads_per_seq = []  # seq x heads x head_dim
        for h in range(self.num_heads):
            # gather head h across sequence -> list of row vectors (seq x head_dim)
            Q_h = [ Q_heads[i][h] for i in range(seq) ]
            K_h = [ K_heads[i][h] for i in range(seq) ]
            V_h = [ V_heads[i][h] for i in range(seq) ]
            head_out = self._scaled_dot_product(Q_h, K_h, V_h)  # seq x head_dim
            # append per-head outputs
            if not out_heads_per_seq:
                # initialize with empty lists per sequence
                out_heads_per_seq = [ [] for _ in range(seq) ]
            for i in range(seq):
                out_heads_per_seq[i].append(head_out[i])
        # concat heads
        concat = _reshape_heads_to_seq_dim(out_heads_per_seq)  # seq x dim
        concat_tensor = Tensor(concat)
        # final linear
        out = self.out_linear(concat_tensor)
        return out

# -------------------------
# Feed-Forward network
# -------------------------

class FeedForward:
    """
    MLP simple de dos capas: x -> Linear(dim, hidden) -> act -> Linear(hidden, dim)
    - act_fn: function that maps List[float] -> List[float] (aplica por fila)
    """

    def __init__(self, dim: int, hidden_dim: Optional[int] = None, seed: Optional[int] = None,
                 act_fn: Callable[[List[float]], List[float]] = gelu_vec, scale: float = 0.07):
        self.dim = dim
        self.hidden_dim = hidden_dim or (dim * 4)
        self.act_fn = act_fn
        self.fc1 = Linear(dim, self.hidden_dim, seed=(None if seed is None else seed+31), scale=scale)
        self.fc2 = Linear(self.hidden_dim, dim, seed=(None if seed is None else seed+37), scale=scale)

    def __call__(self, x: Tensor) -> Tensor:
        """
        x: Tensor seq x dim
        Apply fc1, activation, fc2
        """
        # fc1 -> Tensor (seq x hidden)
        h = self.fc1(x)
        # apply activation row-wise
        rows = h.tolist()
        act_rows = [ self.act_fn(row) for row in rows ]
        act_tensor = Tensor(act_rows)
        out = self.fc2(act_tensor)
        return out

# -------------------------
# Positional Embeddings
# -------------------------

class PositionalEncoding:
    """
    Embeddings posicionales tipo sinusoidal (deterministas) o learnable.
    - mode: "sinusoidal" o "learned"
    - max_len: longitud máxima esperada
    """

    def __init__(self, dim: int, max_len: int = 1024, mode: str = "sinusoidal", seed: Optional[int] = None):
        self.dim = dim
        self.max_len = max_len
        self.mode = mode
        self.seed = seed
        if mode == "learned":
            rnd = _seed_random(seed)
            self.table = [[ (rnd.random()*2-1)*0.02 for _ in range(dim)] for _ in range(max_len)]
        else:
            # sinusoidal
            self.table = _make_sinusoidal_table(max_len, dim)

    def get_for_len(self, seq_len: int) -> Tensor:
        if seq_len > self.max_len:
            # ampliar tabla sinusoidal si es necesario (regenerar con mayor max_len)
            if self.mode == "sinusoidal":
                self.max_len = max(self.max_len * 2, seq_len)
                self.table = _make_sinusoidal_table(self.max_len, self.dim)
            else:
                raise ValueError("Requested seq_len > max_len for learned positional encodings")
        rows = self.table[:seq_len]
        return Tensor(rows)

def _make_sinusoidal_table(max_len: int, dim: int) -> List[List[float]]:
    table = []
    for pos in range(max_len):
        row = []
        for i in range(dim):
            inv_freq = 1.0 / (10000 ** (2 * (i//2) / dim))
            if i % 2 == 0:
                row.append(math.sin(pos * inv_freq))
            else:
                row.append(math.cos(pos * inv_freq))
        table.append(row)
    return table

# -------------------------
# Transformer Block
# -------------------------

class SimpleTransformerBlock:
    """
    Bloque transformador: LayerNorm -> MHA -> residual -> LayerNorm -> FF -> residual
    Opcional: dropout (no implementado porque no hay train-time here)
    """

    def __init__(self, dim: int, num_heads: int = 4, ff_hidden: Optional[int] = None,
                 act_fn: Callable[[List[float]], List[float]] = gelu_vec, seed: Optional[int] = None):
        if dim % num_heads != 0:
            raise ValueError("dim must be divisible by num_heads")
        self.dim = dim
        self.num_heads = num_heads
        self.attn = MultiHeadAttention(dim, num_heads=num_heads, seed=(None if seed is None else seed+101))
        self.ln1 = LayerNorm(dim, seed=(None if seed is None else seed+103))
        self.ff = FeedForward(dim, hidden_dim=ff_hidden, seed=(None if seed is None else seed+107), act_fn=act_fn)
        self.ln2 = LayerNorm(dim, seed=(None if seed is None else seed+109))

    def __call__(self, x: Tensor) -> Tensor:
        """
        x: Tensor (seq x dim)
        """
        # pre-norm
        x_norm = self.ln1(x)
        attn_out = self.attn(x_norm)  # seq x dim
        # residual
        res1 = Tensor([[a + b for a,b in zip(rowx, rowy)] for rowx,rowy in zip(x.tolist(), attn_out.tolist())])
        # second part
        res1_norm = self.ln2(res1)
        ff_out = self.ff(res1_norm)
        out = Tensor([[a + b for a,b in zip(rowx, rowy)] for rowx,rowy in zip(res1.tolist(), ff_out.tolist())])
        return out

# -------------------------
# Transformer Model (stack of blocks)
# -------------------------

class TransformerModel:
    """
    Modelo transformador simple de encoder-only (stack de n bloques).
    - dim: embedding dimension
    - n_layers: número de bloques
    - num_heads: cabezas por bloque
    - max_len: máximo length para positional encodings
    """

    def __init__(self, dim: int = 64, n_layers: int = 2, num_heads: int = 4, max_len: int = 512,
                 ff_hidden: Optional[int] = None, pos_mode: str = "sinusoidal", seed: Optional[int] = 42):
        if dim % num_heads != 0:
            raise ValueError("dim must be divisible by num_heads")
        self.dim = dim
        self.n_layers = n_layers
        self.num_heads = num_heads
        self.seed = seed
        self.pos_enc = PositionalEncoding(dim, max_len=max_len, mode=pos_mode, seed=seed)
        # token embedding: mapping id -> vector; aquí se construye como diccionario
        self._embeddings: Dict[int, List[float]] = {}
        self._init_embeddings(base_size=64, seed=seed)  # si vocab pequeño, se puede ampliar
        # encoder blocks
        self.blocks: List[SimpleTransformerBlock] = []
        for i in range(n_layers):
            self.blocks.append(SimpleTransformerBlock(dim, num_heads=num_heads, ff_hidden=ff_hidden, seed=(None if seed is None else seed + i*10)))
        self.ln_final = LayerNorm(dim, seed=(None if seed is None else seed+999))

    def _init_embeddings(self, base_size: int = 64, seed: Optional[int] = None):
        """
        Inicializa embeddings para ids 0..base_size-1 (si aún no existen).
        Embeddings deterministas en función de id y seed.
        """
        rnd = _seed_random(seed)
        for idx in range(base_size):
            if idx not in self._embeddings:
                # vector determinista: (idx * primes) mod something scaled
                vec = [(((idx * 31) + (j*17) + (rnd.random()*0.001)) % 100) / 100.0 * 0.05 for j in range(self.dim)]
                self._embeddings[idx] = vec

    def _embed_ids(self, ids: List[int]) -> Tensor:
        """
        Convierte lista de ids -> Tensor seq x dim. Añade embeddings nuevos si es necesario.
        """
        rows = []
        for i in ids:
            if i not in self._embeddings:
                # añadir embedding nuevo determinista (basado en i)
                base = i % 100
                vec = [(((i * 29) + (j*13)) % 100) / 100.0 * 0.05 for j in range(self.dim)]
                self._embeddings[i] = vec
            rows.append(self._embeddings[i])
        return Tensor(rows)

    def encode(self, ids: List[int]) -> Tensor:
        """
        Encode: ids -> embeddings + positional -> pass through blocks -> output tensor (seq x dim)
        """
        if not ids:
            return Tensor([])  # empty
        x = self._embed_ids(ids)  # seq x dim
        # add positional encoding
        pos = self.pos_enc.get_for_len(len(ids))
        x = Tensor([[a + b for a,b in zip(rowx, rowp)] for rowx,rowp in zip(x.tolist(), pos.tolist())])
        # pass through blocks
        out = x
        for blk in self.blocks:
            out = blk(out)
        out = self.ln_final(out)
        return out

    def forward(self, ids: List[int]) -> List[float]:
        """
        Conducta de alto nivel: encode y reduce a vector representativo (average pool).
        Retorna vector (dim,)
        """
        encoded = self.encode(ids)
        vec = _average_pool_rows(encoded)
        return vec

    def get_embedding_for_token(self, token_id: int) -> List[float]:
        return self._embeddings.get(token_id, [0.0]*self.dim)

    def set_embedding_for_token(self, token_id: int, vector: List[float]):
        if len(vector) != self.dim:
            raise ValueError("vector length mismatch")
        self._embeddings[token_id] = vector

    def state_dict(self) -> Dict[str, Any]:
        """
        Retorna un diccionario simple con parámetros (para inspección o guardado rudimentario).
        No está pensado para serializar y re-entrenar con frameworks externos.
        """
        state = {
            "dim": self.dim,
            "n_layers": self.n_layers,
            "num_heads": self.num_heads,
            "embeddings_count": len(self._embeddings),
            "blocks": [ blk.__class__.__name__ for blk in self.blocks ]
        }
        return state

# -------------------------
# Small demo utilities
# -------------------------

def demo_run():
    """
    Función de demostración que crea un pequeño modelo, codifica ids de ejemplo y devuelve el vector.
    Útil para pruebas rápidas desde la línea.
    """
    model = TransformerModel(dim=32, n_layers=2, num_heads=4, max_len=64, seed=123)
    sample_ids = [1, 2, 3, 4, 5]
    encoded = model.encode(sample_ids)
    pooled = model.forward(sample_ids)
    print("Encoded shape:", encoded.shape)
    print("Pooled vector len:", len(pooled))
    # imprime primeras 8 dimensiones
    print("Pooled[:8]:", pooled[:8])

# -------------------------
# End of file
# -------------------------
