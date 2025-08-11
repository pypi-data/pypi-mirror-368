"""
Megan: IA ligera sin dependencias.
- Contiene 36 respuestas fijas (exacts)
- Si no hay coincidencia exacta, usa tokenizer y responde con plantilla
- Puede inicializar parámetros del transformer aunque no está entrenado
"""

from .tokenizer import SimpleTokenizer
from .transformer import SimpleTransformerBlock
from .tensor import Tensor
from typing import Optional

class Megan:
    def __init__(self, vocab=None, dim=16, n_layers=1, seed: Optional[int]=42):
        self.tokenizer = SimpleTokenizer(vocab=vocab)
        self.dim = dim
        self.seed = seed
        self.layers = [ SimpleTransformerBlock(dim, seed=(seed or 0)+i) for i in range(n_layers) ]
        # embedding matrix (vocab_size x dim) - start with small vocab then expand on add
        self._embedding = {}  # id -> vector(list)
        self._init_builtin_vocab()
        self.fixed_responses = self._load_fixed_responses()

    def _init_builtin_vocab(self):
        # ensure basic tokens exist in tokenizer vocab
        for t in ["hola","hola!","hola,","adios","gracias","como","estas","bien","mal","ayuda","quien","eres","tu","nombre","qué","porque","porqué","si","no","ok","siempre","nunca","fecha","hora","ayúdame"]:
            self.tokenizer.add_token(t)
        # initialize embedding vectors (deterministic small random)
        for tok, idx in self.tokenizer.vocab.items():
            # simple deterministic pseudo-random based on idx
            v = [((idx * 31 + j*17) % 100)/100.0 * 0.02 for j in range(self.dim)]
            self._embedding[idx] = v

    def _load_fixed_responses(self):
        # 36 respuestas fijas (ejemplo). Puedes editarlas.
        fixed = {
            "hola": "Hola, soy Megan. ¿En qué puedo ayudarte?",
            "hola!": "¡Hola! Soy Megan, lista para ayudar.",
            "quien eres": "Soy Megan, una IA ligera creada para demostración.",
            "quién eres": "Soy Megan, una IA ligera creada para demostración.",
            "como estas": "Estoy bien, gracias por preguntar.",
            "como estas?": "Estoy bien, lista para ayudar.",
            "gracias": "De nada, un placer ayudar.",
            "adios": "Adiós. ¡Que tengas un buen día!",
            "ayuda": "Dime qué necesitas y haré lo posible por ayudar.",
            "nombre": "Mi nombre es Megan.",
            "hola como estas": "Hola — estoy bien. ¿Y tú?",
            "buenos dias": "¡Buenos días! ¿En qué puedo ayudar?",
            "buenas tardes": "¡Buenas tardes! ¿Qué necesitas?",
            "buenas noches": "¡Buenas noches! Que descanses.",
            "que puedes hacer": "Puedo responder con respuestas fijas y hacer demostraciones básicas.",
            "quien creo esta libreria": "Esta librería fue creada por el desarrollador del paquete.",
            "version": "Megan v0.1.0 - minimal transformer demo",
            "ayudame por favor": "Claro, dime en qué puedo ayudarte.",
            "como te llamas": "Me llamo Megan.",
            "dime un chiste": "¿Por qué la computadora fue al médico? Porque tenía un virus :)",
            "saludo": "¡Hola! Encantada de saludarte.",
            "gracias por tu ayuda": "¡Con gusto!",
            "no entiendo": "Lo siento, no he aprendido eso aún.",
            "explica": "Puedo dar explicaciones breves sobre temas simples.",
            "hola megan": "Hola. ¿Cómo puedo ayudarte hoy?",
            "hola megan!": "¡Hola! ¿Qué necesitas?",
            "ayuda tecnica": "Describe el problema técnico y te doy ideas para resolverlo.",
            "como instalo": "Usa pip para instalar paquetes; revisa el README para empaquetado.",
            "documentacion": "Lee el README y los docstrings en el código.",
            "prediccion": "El modelo no está entrenado; usa respuestas fijas por ahora.",
            "entrenar": "La versión actual no implementa entrenamiento automático.",
            "fallback1": "No estoy seguro, pero puedo intentar ayudarte si das más detalle.",
            "fallback2": "No lo sé todavía. ¿Puedes reformular?"
        }
        # ensure exactly 36 keys (pad if needed)
        keys = list(fixed.keys())
        if len(keys) < 36:
            i = 0
            while len(keys) < 36:
                k = f"extra_{i}"
                fixed[k] = "Respuesta por defecto extra."
                keys.append(k)
                i += 1
        return fixed

    def _embed_ids(self, ids):
        # returns Tensor seq x dim
        rows = []
        for i in ids:
            v = self._embedding.get(i)
            if v is None:
                # add new token embedding as small zeros
                v = [0.0 for _ in range(self.dim)]
                self._embedding[i] = v
            rows.append(v)
        return Tensor(rows)

    def _transform(self, emb: Tensor):
        x = emb
        for layer in self.layers:
            x = layer(x)
        return x  # seq x dim

    def respond(self, text: str) -> str:
        key = text.strip().lower()
        # exact match in fixed responses
        if key in self.fixed_responses:
            return self.fixed_responses[key]
        # fallback deterministic pipeline:
        ids = self.tokenizer.encode(text, add_bos=False, add_eos=False)
        if len(ids) == 0:
            return "No entendí tu mensaje. Intenta con otra frase."
        emb = self._embed_ids(ids)  # seq x dim
        tr = self._transform(emb)   # seq x dim
        # reduce to single vector by averaging
        summed = [0.0]*self.dim
        for row in tr.data:
            for j,v in enumerate(row):
                summed[j] += v
        avg = [x / max(1, len(tr.data)) for x in summed]
        # crude decode: pick some words from vocab with highest pseudo-score
        # compute score per token id as dot(embedding, avg)
        scores = []
        for tok_id, vec in self._embedding.items():
            s = sum(a*b for a,b in zip(avg, vec))
            scores.append((s, tok_id))
        scores.sort(reverse=True)
        # choose top 3 token ids to produce a short reply
        chosen = [tok for _,tok in scores[:3]]
        reply = self.tokenizer.decode(chosen)
        # if reply is gibberish (contains <UNK>), fallback to template
        if "<UNK>" in reply or reply.strip() == "":
            return "Lo siento, no tengo una respuesta preparada para eso todavía."
        return reply
