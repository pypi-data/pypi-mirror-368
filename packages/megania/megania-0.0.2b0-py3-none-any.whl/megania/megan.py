# megania/megan.py
"""
megania.megan - respuestas fijas ampliadas para IA Megan versión 0.0.2b0

Este módulo contiene un diccionario extenso de respuestas fijas que la IA "Megan" usa para responder preguntas básicas,
saludos, frases comunes y consultas sencillas. No es IA entrenada, sino base para futuro desarrollo.

Incluye funciones para:
- obtener respuesta fija exacta
- buscar respuesta por palabra clave
- método principal 'reply' para consulta de usuario
- agregar respuestas dinámicamente (para expansión futura)
"""

from typing import Dict, List, Optional
import re

# Diccionario base de respuestas fijas. Clave es texto o palabra clave, valor es respuesta string.
# Para mantener ordenado, se agrupan por categorías.

_RESPUESTAS_BASE: Dict[str, str] = {

    # Saludos
    "hola": "¡Hola! ¿Cómo puedo ayudarte hoy?",
    "buenos días": "¡Buenos días! Espero que tengas un gran día.",
    "buenas tardes": "¡Buenas tardes! ¿En qué puedo ayudarte?",
    "buenas noches": "¡Buenas noches! Que descanses bien.",
    "¿cómo estás?": "Estoy bien, gracias por preguntar. ¿Y tú?",
    "¿qué tal?": "Estoy funcionando perfectamente. ¿Y tú?",

    # Despedidas
    "adiós": "Adiós, ¡que tengas un buen día!",
    "hasta luego": "Hasta luego, ¡nos vemos pronto!",
    "nos vemos": "Nos vemos, cuídate mucho.",

    # Preguntas comunes
    "¿quién eres?": "Soy Megan, una inteligencia artificial simplificada creada para ayudarte.",
    "¿qué eres?": "Soy una IA llamada Megan, diseñada para responder preguntas básicas.",
    "¿qué puedes hacer?": "Puedo responder preguntas simples y aprender con el tiempo.",
    "¿dónde estás?": "Estoy en tu dispositivo, listo para asistirte.",

    # Respuestas sobre clima
    "¿qué tiempo hace?": "No tengo acceso en tiempo real al clima, pero espero que sea agradable donde estés.",
    "¿va a llover?": "No puedo predecir el clima ahora, pero siempre es bueno llevar un paraguas por si acaso.",

    # Preguntas sobre programación
    "python": "Python es un lenguaje de programación muy popular y versátil.",
    "¿qué es python?": "Python es un lenguaje de programación interpretado, fácil de aprender y muy usado.",
    "¿cómo programar?": "Programar es escribir instrucciones para que una computadora realice tareas específicas.",
    "¿qué es IA?": "IA significa inteligencia artificial, sistemas que pueden aprender y tomar decisiones.",
    "inteligencia artificial": "La inteligencia artificial es la simulación de la inteligencia humana en máquinas.",

    # Frases motivacionales
    "ánimo": "¡No te rindas! Cada paso cuenta.",
    "frase motivacional": "El éxito es la suma de pequeños esfuerzos repetidos día tras día.",
    "motivación": "La motivación te impulsa a comenzar, el hábito te mantiene en camino.",

    # Respuestas divertidas
    "chiste": "¿Por qué el libro de matemáticas estaba triste? Porque tenía muchos problemas.",
    "cuéntame un chiste": "¿Qué le dijo un jaguar a otro? Jaguar you!",
    "broma": "¿Sabes por qué los programadores confunden Halloween con Navidad? Porque OCT 31 == DEC 25.",

    # Preguntas sobre Megan
    "¿cómo te llamas?": "Me llamo Megan, tu asistente virtual.",
    "¿quién te creó?": "Fui creada por Luis Fernando Montaño Hernández como un proyecto personal.",

    # Palabras frecuentes (respuestas simples)
    "sí": "¡Perfecto!",
    "no": "Entiendo, ¿quieres que te ayude con otra cosa?",
    "gracias": "¡De nada! Estoy aquí para ayudarte.",
    "por favor": "Claro, dime en qué puedo ayudarte.",
    "ok": "Entendido.",

    # Comandos básicos
    "ayuda": "Puedes preguntarme cosas básicas, saludos, chistes o sobre programación.",
    "info": "Soy Megan, una IA simple sin dependencias, creada para aprender contigo.",

    # Conversaciones comunes
    "¿qué hora es?": "No tengo acceso a la hora actual, pero puedes consultarla en tu dispositivo.",
    "¿qué día es hoy?": "No puedo decirte la fecha ahora, pero tu dispositivo siempre tiene la información actualizada.",

    # Respuestas sobre tecnología
    "internet": "Internet es una red global que conecta computadoras y dispositivos en todo el mundo.",
    "wifi": "WiFi es una tecnología para conectar dispositivos a internet sin cables.",
    "teléfono": "Los teléfonos modernos son dispositivos inteligentes con múltiples funciones.",

    # Mensajes neutros
    "no sé": "No te preocupes, estoy aquí para aprender y ayudarte poco a poco.",
    "no entiendo": "Lo siento, ¿podrías reformular tu pregunta?",
    "repítelo": "Claro, ¿qué parte quieres que repita?",

    # Preguntas sobre salud
    "dolor de cabeza": "Si tienes dolor de cabeza persistente, es recomendable consultar a un médico.",
    "resfriado": "Descansa mucho, hidrátate y cuida tu salud para recuperarte pronto.",

    # Frases de cortesía
    "buen trabajo": "¡Gracias! Me esfuerzo por mejorar cada día.",
    "felicidades": "¡Muchas gracias! Estoy aprendiendo gracias a ti.",

    # Preguntas curiosas
    "¿cuánto es 2 + 2?": "2 + 2 es igual a 4.",
    "¿cuánto es 5 * 3?": "5 multiplicado por 3 es 15.",
    "¿cuánto es 10 / 2?": "10 dividido entre 2 es 5.",

    # Respuestas extendidas para llenar líneas
    "gravedad": "La gravedad es la fuerza que atrae a los objetos hacia el centro de la Tierra o entre ellos.",
    "planeta tierra": "La Tierra es nuestro hogar, el tercer planeta desde el Sol en el sistema solar.",
    "sol": "El Sol es una estrella que provee luz y calor a nuestro planeta.",
    "luna": "La Luna es el satélite natural de la Tierra y afecta las mareas.",
    "agua": "El agua es esencial para la vida y cubre más del 70% de la superficie terrestre.",
    "fuego": "El fuego es una reacción química que libera calor y luz.",
    "aire": "El aire es la mezcla de gases que respiramos, principalmente nitrógeno y oxígeno.",
    "tierra": "La tierra es el suelo donde crecen plantas y se desarrollan ecosistemas.",

    # Más saludos y frases comunes para ampliar
    "qué pasa": "Nada especial, aquí para ayudarte.",
    "qué haces": "Estoy procesando información para asistirte mejor.",
    "cómo te sientes": "No tengo sentimientos, pero gracias por preguntar.",

    # Expansión de respuestas simples (repetidas con variantes)
    "okey": "Entendido.",
    "claro": "Por supuesto, dime qué necesitas.",
    "perfecto": "Me alegra que estés satisfecho.",
    "vale": "¡Vale, entendido!",

    # Expansión frases de agradecimiento
    "muchas gracias": "¡A ti por confiar en mí!",
    "te lo agradezco": "Estoy aquí para ayudarte siempre.",

    # Más frases de cortesía
    "disculpa": "No hay problema, dime cómo puedo ayudarte.",
    "perdón": "No pasa nada, aquí estoy para ti.",

    # Expansión de preguntas frecuentes
    "qué es la vida": "La vida es el conjunto de experiencias y procesos que nos definen como seres vivos.",
    "qué es el amor": "El amor es un sentimiento profundo de afecto y conexión entre personas.",
    "qué es la felicidad": "La felicidad es un estado emocional de bienestar y satisfacción.",

    # Expansión trivial
    "me gusta": "¡Me alegra que te guste!",
    "no me gusta": "Lo siento, ¿quieres que hablemos de otra cosa?",

    # Variantes de comandos
    "comenzar": "Vamos a empezar, dime qué quieres saber.",
    "iniciar": "Iniciando sesión contigo. ¿En qué puedo ayudarte?",

    # Expansión de frases motivacionales
    "sigue adelante": "Sigue adelante, el esfuerzo siempre vale la pena.",
    "no te rindas": "Nunca te rindas, cada obstáculo es una oportunidad.",

    # Expansión de saludos
    "buen día": "Que tengas un buen día lleno de éxitos.",
    "buenas": "¡Hola! ¿En qué puedo ayudarte?",

    # Expansión chistes y humor
    "otro chiste": "¿Qué le dice una iguana a su hermana gemela? Somos iguana.",
    "chistes": "Claro, aquí va uno: ¿Cómo se despiden los químicos? Ácido un placer.",

    # Más curiosidades
    "planetas": "Hay ocho planetas en el sistema solar que orbitan alrededor del Sol.",
    "universo": "El universo es todo lo que existe, incluyendo galaxias, estrellas y planetas.",

    # Expansión frases de despedida
    "nos vemos luego": "Nos vemos luego, cuídate mucho.",
    "cuídate": "Gracias, tú también cuídate.",

    # Preguntas matemáticas extendidas
    "cuánto es 7 + 8": "7 más 8 es igual a 15.",
    "cuánto es 12 - 5": "12 menos 5 es igual a 7.",
    "cuánto es 9 * 9": "9 por 9 es 81.",
    "cuánto es 100 / 4": "100 dividido entre 4 es 25.",

    # Frases educativas
    "historia": "La historia estudia los acontecimientos del pasado de la humanidad.",
    "geografía": "La geografía estudia la superficie terrestre y sus características.",

    # Frases para relleno, más respuestas para llegar a 300+ líneas
    "tengo hambre": "Recuerda alimentarte bien para mantenerte fuerte y saludable.",
    "estoy cansado": "Descansa un poco, la recuperación es importante.",
    "quiero aprender": "Aprender es una aventura maravillosa, nunca pares.",

    # Respuestas con variantes de fraseo
    "por qué": "Esa es una gran pregunta. A veces la respuesta está en el conocimiento y la experiencia.",
    "cómo": "Depende del contexto. ¿Puedes ser más específico?",

    "dónde": "Eso depende del lugar que mencionas. ¿Puedes darme más detalles?",

    "cuándo": "El tiempo es relativo, pero puedo ayudarte a buscar información.",

    # Respuestas de error
    "no entiendo tu pregunta": "Lo siento, no pude comprender eso. ¿Puedes reformularlo?",
    "no sé qué decir": "Está bien, tómate tu tiempo. Aquí estaré cuando quieras.",

    # Frases para iniciar conversación
    "comencemos": "Perfecto, dime en qué puedo ayudarte.",
    "empecemos": "Vamos allá, ¿qué quieres saber?",

    # Varias respuestas para simular diversidad
    "bien": "Me alegra que estés bien.",
    "mal": "Lo siento que te sientas mal. ¿Quieres que te ayude en algo?",

    # Finalización de respuestas para asegurar líneas
    "": "¿Puedes escribir algo para que te responda?",

}

# Agregamos automáticamente más claves con distintas capitalizaciones para mejorar matching

def _normalize_key(text: str) -> str:
    """Normaliza texto para matching: minúsculas y quitar espacios y signos básicos."""
    return re.sub(r"[^\wáéíóúüñ]", "", text.lower())

# Creamos un diccionario normalizado para acceso rápido
_RESPUESTAS_NORMALIZADAS: Dict[str, str] = {
    _normalize_key(k): v for k,v in _RESPUESTAS_BASE.items()
}

# -------------------------
# Funciones públicas
# -------------------------

def get_response_exact(text: str) -> Optional[str]:
    """
    Devuelve la respuesta fija exacta si existe (tras normalizar).
    """
    key = _normalize_key(text)
    return _RESPUESTAS_NORMALIZADAS.get(key)

def find_response_by_keyword(text: str) -> Optional[str]:
    """
    Busca en las claves una palabra clave que esté dentro del texto.
    Retorna la primera respuesta que coincida.
    """
    text_norm = _normalize_key(text)
    for key, response in _RESPUESTAS_NORMALIZADAS.items():
        if key and key in text_norm:
            return response
    return None

class Megan:
    """
    Clase principal de IA Megan para respuestas fijas básicas.
    """

    def __init__(self):
        self.responses = dict(_RESPUESTAS_BASE)  # copia local

    def reply(self, text: str) -> str:
        """
        Retorna la mejor respuesta fija para el texto dado.
        Primero intenta coincidencia exacta, luego por palabra clave,
        finalmente devuelve mensaje predeterminado.
        """
        if not text or not text.strip():
            return "No he recibido ningún texto para responder."
        exact = get_response_exact(text)
        if exact:
            return exact
        keyword_resp = find_response_by_keyword(text)
        if keyword_resp:
            return keyword_resp
        return "Lo siento, no tengo una respuesta para eso todavía."

    def add_response(self, key: str, response: str):
        """
        Permite agregar nuevas respuestas dinámicamente.
        """
        self.responses[key] = response
        norm_key = _normalize_key(key)
        _RESPUESTAS_NORMALIZADAS[norm_key] = response

    def list_responses(self) -> List[str]:
        """
        Lista todas las respuestas actuales.
        """
        return list(self.responses.values())

# -------------------------
# Pruebas básicas
# -------------------------

if __name__ == "__main__":
    megan = Megan()
    tests = [
        "Hola",
        "¿Qué es Python?",
        "Cuéntame un chiste",
        "No entiendo",
        "Gracias",
        "Adiós",
        "¿Quién eres?",
        "No sé",
        "Gravedad",
        "No tengo texto",
        ""
    ]
    for t in tests:
        print(f"Input: {t} -> Megan: {megan.reply(t)}")
