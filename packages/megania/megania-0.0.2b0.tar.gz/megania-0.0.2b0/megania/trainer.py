# megania/trainer.py
"""
Módulo de entrenamiento para IA Megan (versión 0.0.2b0).

Simula un proceso interno de entrenamiento con preguntas y respuestas,
evalúa respuestas de Megan y da feedback 'Bueno' o 'Mal'.

No usa dependencias externas.
"""

from typing import List, Tuple, Dict
from megania.megan import Megan
import re

class Trainer:
    """
    Clase para simular entrenamiento y evaluación de IA Megan.
    """

    def __init__(self, megan: Megan):
        self.megan = megan
        # Lista de tuplas (pregunta, respuesta_esperada)
        self.dataset: List[Tuple[str, str]] = []
        # Resultados acumulados (pregunta, respuesta_ia, resultado)
        self.results: List[Tuple[str, str, bool]] = []

    def load_default_dataset(self):
        """
        Carga un dataset de entrenamiento básico interno.
        """
        self.dataset = [
            ("Hola", "¡Hola! ¿Cómo puedo ayudarte hoy?"),
            ("¿Qué es Python?", "Python es un lenguaje de programación muy popular y versátil."),
            ("Cuéntame un chiste", "¿Por qué el libro de matemáticas estaba triste? Porque tenía muchos problemas."),
            ("No entiendo", "Lo siento, ¿podrías reformular tu pregunta?"),
            ("Gracias", "¡De nada! Estoy aquí para ayudarte."),
            ("Adiós", "Adiós, ¡que tengas un buen día!"),
            ("¿Quién eres?", "Soy Megan, una inteligencia artificial simplificada creada para ayudarte."),
            ("¿Qué tiempo hace?", "No tengo acceso en tiempo real al clima, pero espero que sea agradable donde estés."),
            ("¿Cómo programar?", "Programar es escribir instrucciones para que una computadora realice tareas específicas."),
            ("No sé", "No te preocupes, estoy aquí para aprender y ayudarte poco a poco."),
            # Agrega más ejemplos reales o generados para entrenamiento...
            # Total para simular ~50 entradas
        ]
        # Extender para ~50 líneas con variedad
        extra = [
            ("¿Dónde estás?", "Estoy en tu dispositivo, listo para asistirte."),
            ("Sí", "¡Perfecto!"),
            ("No", "Entiendo, ¿quieres que te ayude con otra cosa?"),
            ("Por favor", "Claro, dime en qué puedo ayudarte."),
            ("Ok", "Entendido."),
            ("¿Qué es IA?", "IA significa inteligencia artificial, sistemas que pueden aprender y tomar decisiones."),
            ("Ánimo", "¡No te rindas! Cada paso cuenta."),
            ("¿Cuánto es 2 + 2?", "2 + 2 es igual a 4."),
            ("¿Qué hora es?", "No tengo acceso a la hora actual, pero puedes consultarla en tu dispositivo."),
            ("Internet", "Internet es una red global que conecta computadoras y dispositivos en todo el mundo."),
            ("¿Quién te creó?", "Fui creada por Luis Fernando Montaño Hernández como un proyecto personal."),
            ("¿Qué puedes hacer?", "Puedo responder preguntas simples y aprender con el tiempo."),
            ("¿Qué tal?", "Estoy funcionando perfectamente. ¿Y tú?"),
            ("Disculpa", "No hay problema, dime cómo puedo ayudarte."),
            ("Mal", "Lo siento que te sientas mal. ¿Quieres que te ayude en algo?"),
            ("Bien", "Me alegra que estés bien."),
            ("Adiós", "Adiós, ¡que tengas un buen día!"),
            ("Chiste", "¿Por qué el libro de matemáticas estaba triste? Porque tenía muchos problemas."),
            ("Motivación", "La motivación te impulsa a comenzar, el hábito te mantiene en camino."),
            ("Gracias", "¡De nada! Estoy aquí para ayudarte."),
            ("No entiendo tu pregunta", "Lo siento, no pude comprender eso. ¿Puedes reformularlo?"),
            ("Cuánto es 7 + 8", "7 más 8 es igual a 15."),
            ("Sigue adelante", "Sigue adelante, el esfuerzo siempre vale la pena."),
            ("No te rindas", "Nunca te rindas, cada obstáculo es una oportunidad."),
            ("Hola", "¡Hola! ¿Cómo puedo ayudarte hoy?"),
            ("Buenas noches", "¡Buenas noches! Que descanses bien."),
            ("¿Qué haces?", "Estoy procesando información para asistirte mejor."),
            ("Por qué", "Esa es una gran pregunta. A veces la respuesta está en el conocimiento y la experiencia."),
            ("Cómo", "Depende del contexto. ¿Puedes ser más específico?"),
            ("Dónde", "Eso depende del lugar que mencionas. ¿Puedes darme más detalles?"),
            ("Cuándo", "El tiempo es relativo, pero puedo ayudarte a buscar información."),
            ("No sé qué decir", "Está bien, tómate tu tiempo. Aquí estaré cuando quieras."),
            ("Comenzar", "Vamos a empezar, dime qué quieres saber."),
            ("Iniciar", "Iniciando sesión contigo. ¿En qué puedo ayudarte?"),
            ("Estoy cansado", "Descansa un poco, la recuperación es importante."),
            ("Tengo hambre", "Recuerda alimentarte bien para mantenerte fuerte y saludable."),
            ("Me gusta", "¡Me alegra que te guste!"),
            ("No me gusta", "Lo siento, ¿quieres que hablemos de otra cosa?"),
            ("Gracias", "¡De nada! Estoy aquí para ayudarte."),
            ("Hola", "¡Hola! ¿Cómo puedo ayudarte hoy?"),
            ("Adiós", "Adiós, ¡que tengas un buen día!"),
        ]
        self.dataset.extend(extra)

    def evaluate_response(self, expected: str, actual: str) -> bool:
        """
        Evalúa la respuesta de Megan comparándola con la esperada.
        Método básico que puede ser mejorado.
        """
        # Normalizar texto para comparación sencilla
        def norm(text: str) -> str:
            return re.sub(r"\W+", "", text.lower())

        return norm(expected) == norm(actual)

    def run_training(self):
        """
        Corre el entrenamiento/evaluación con el dataset cargado.
        """
        if not self.dataset:
            print("Dataset vacío, cargando datos por defecto...")
            self.load_default_dataset()

        print(f"Iniciando evaluación con {len(self.dataset)} ejemplos...\n")
        self.results.clear()

        for idx, (pregunta, resp_esperada) in enumerate(self.dataset, 1):
            resp_ia = self.megan.reply(pregunta)
            bueno = self.evaluate_response(resp_esperada, resp_ia)
            self.results.append((pregunta, resp_ia, bueno))

            status = "Bueno" if bueno else "Mal"
            print(f"{idx:03d}. Pregunta: '{pregunta}'")
            print(f"     Esperada: '{resp_esperada}'")
            print(f"     Megan:    '{resp_ia}'")
            print(f"     Resultado: {status}\n")

        print("Evaluación finalizada.")

    def get_report(self) -> Dict[str, int]:
        """
        Retorna un resumen de la evaluación:
        total preguntas, aciertos, errores, porcentaje acierto.
        """
        total = len(self.results)
        aciertos = sum(1 for r in self.results if r[2])
        errores = total - aciertos
        porcentaje = (aciertos / total * 100) if total > 0 else 0

        return {
            "total": total,
            "aciertos": aciertos,
            "errores": errores,
            "porcentaje": round(porcentaje, 2),
        }

    def summary(self):
        """
        Imprime el resumen final.
        """
        reporte = self.get_report()
        print(f"\nResumen de Evaluación:")
        print(f"Total preguntas: {reporte['total']}")
        print(f"Aciertos: {reporte['aciertos']}")
        print(f"Errores: {reporte['errores']}")
        print(f"Porcentaje acierto: {reporte['porcentaje']}%")

# ---------------------------------
# Ejemplo de uso (no ejecutar directo)
# ---------------------------------

if __name__ == "__main__":
    print("Este módulo es para uso interno y no debe ejecutarse directamente.")
