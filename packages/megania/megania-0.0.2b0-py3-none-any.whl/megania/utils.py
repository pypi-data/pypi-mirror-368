# megania/utils.py
import re
from typing import Iterable, List

def normalize_text(s: str) -> str:
    """
    Normaliza texto: trim, lower, elimina espacios extra y caracteres no imprimibles,
    y simplifica espacios alrededor de puntuación.
    """
    if s is None:
        return ""
    s = str(s)
    s = s.strip()
    s = s.lower()
    # remover caracteres no imprimibles
    s = re.sub(r'[\x00-\x1f\x7f]+', ' ', s)
    # espacios múltiples a uno
    s = re.sub(r'\s+', ' ', s)
    # espacio antes de puntuación: "hola ," -> "hola,"
    s = re.sub(r'\s+([.,;:!?])', r'\1', s)
    # espacio después de parentesis/quotes normalización
    s = re.sub(r'([{(\["\'])\s+', r'\1', s)
    s = re.sub(r'\s+([}\])"\'])', r'\1', s)
    return s

def chunk_list(lst: Iterable, n: int) -> List:
    """
    Divide iterable en chunks de tamaño n (último puede ser menor).
    Retorna lista de listas.
    """
    lst = list(lst)
    return [lst[i:i+n] for i in range(0, len(lst), n)]
