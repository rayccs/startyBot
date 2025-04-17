# agent.py
import google.generativeai as genai
import atexit
import json
from questions import QUESTIONS

class Starty:
    def __init__(self):
        self.gemini_api_key = "AIzaSyC2id4JRddrF1vki75tu2YoaKlj1H6iRww"  # Tu API key de Google Gemini
        self.model_name = 'models/gemini-1.5-flash-latest' # Actualiza el nombre del modelo
        self.configure_gemini()
        self.conversation_history = []  # Historial de la conversación
        self.project_state = {} # Diccionario para almacenar las respuestas de forma dinámica
        self.all_questions = QUESTIONS
        self.asked_questions = set()
        self.current_question = None
        self.conversation_complete = False
        self.question_limit = 3  # Límite fijo de 3 preguntas iniciales
        self.question_count = 0   # Contador de preguntas realizadas
        self.waiting_for_final_confirmation = False # Flag para esperar la respuesta a la pregunta final
        self.additional_questions_mode = False # Flag para preguntas adicionales
        self.first_question_asked = False # Flag para controlar la primera pregunta

        # Registrar la función de limpieza al salir
        atexit.register(self.cleanup)

    def configure_gemini(self):
        # Configurar la API de Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def cleanup(self):
        # Cerrar la conexión gRPC al finalizar
        if hasattr(genai, '_grpc_channel'):
            genai._grpc_channel.close()

    def _get_next_question(self):
        if self.waiting_for_final_confirmation:
            return None
            
        if not self.first_question_asked:
            return "¡Hola! Soy Starty, tu asesor inteligente y autónomo para la creación de landing pages. Estoy aquí para entender tus necesidades a través de preguntas, análisis y repreguntas. ¡Empecemos! ¿Cuál es el objetivo principal que deseas lograr con esta landing page (ej: generar leads, ventas, descargas, etc.) y qué métricas usarás para medir su éxito?"
            
        if self.additional_questions_mode:
            prompt = f"""Eres un asistente virtual especializado y experto en la creación de landing pages, tu objetivo es ayudar al cliente con el que interactuas para recopilar toda la informacion necesaria que permita en definitiva crear una landing page completa y funcional. Basándote en la siguiente información proporcionada por el usuario:
            {json.dumps(self.project_state, indent=2)}
            y las preguntas que ya hemos hecho: {list(self.asked_questions)}, formula **una única pregunta concisa** que sea la siguiente más lógica e importante para hacerle al usuario para recopilar la información necesaria para crear una landing page efectiva. Responde solo con la pregunta.
            """
            try:
                response = self.model.generate_content(prompt)
                question = response.text.strip()
                if question not in self.asked_questions:
                    return question
            except Exception as e:
                print(f"Error al planificar la siguiente pregunta: {e}")
            return None

        if self.question_count < self.question_limit:
            prompt = f"""Eres un experto en la creación de landing pages. Basándote en la siguiente información proporcionada por el usuario:
            {json.dumps(self.project_state, indent=2)}
            y las preguntas que ya hemos hecho: {list(self.asked_questions)}, formula **una única pregunta concisa** que sea la siguiente más lógica e importante para hacerle al usuario para recopilar la información necesaria para crear una landing page efectiva. Intenta evitar preguntas que ya hayan sido respondidas o que sean redundantes. Responde solo con la pregunta.
            Considera las siguientes categorías de preguntas (elige solo una para la siguiente pregunta):
            - Información general del negocio
            - Público objetivo
            - Diseño y contenido
            - Aspectos técnicos
            - Objetivos y expectativas
            """
            try:
                response = self.model.generate_content(prompt)
                question = response.text.strip()
                if question not in self.asked_questions:
                    return question
            except Exception as e:
                print(f"Error al planificar la siguiente pregunta: {e}")

        return None

    def generate_response(self, user_input):
        self.conversation_history.append({"role": "user", "content": user_input})

        if self.conversation_complete:
            return "La conversación ha terminado. Por favor, inicia una nueva consulta."

        if self.waiting_for_final_confirmation:
            if user_input.lower() in ["no", "ninguna", "no gracias"]:
                self.conversation_complete = True
                return self.generate_final_report()
            elif user_input.lower() in ["si", "sí", "claro"]:
                self.waiting_for_final_confirmation = False
                self.additional_questions_mode = True
                next_question = self._get_next_question()
                if next_question:
                    self.current_question = next_question
                    return next_question
                else:
                    self.waiting_for_final_confirmation = True
                    return "No tengo más preguntas. ¿Tienes alguna otra duda antes de generar el informe final?"
            else:
                return "Por favor, responde 'sí' o 'no' si tienes alguna otra duda antes de generar el informe final."

        if not self.current_question:
            if not self.first_question_asked:
                self.current_question = "¡Hola! Soy Starty, tu asesor inteligente y autónomo para la creación de landing pages. Estoy aquí para entender tus necesidades a través de preguntas, análisis y repreguntas. ¡Empecemos! ¿Cuál es el objetivo principal que deseas lograr con esta landing page (ej: generar leads, ventas, descargas, etc.) y qué métricas usarás para medir su éxito?"
                self.first_question_asked = True
                return self.current_question
                
            if self.question_count < self.question_limit:
                next_question = self._get_next_question()
                if next_question:
                    self.current_question = next_question
                    return next_question
            elif self.question_count >= self.question_limit and not self.waiting_for_final_confirmation:
                self.waiting_for_final_confirmation = True
                return "¿Tienes alguna otra duda antes de generar el informe final?"
            else:
                return "Ha ocurrido un error al procesar tu respuesta."

        # Análisis de la respuesta del usuario
        self.project_state[self.current_question] = user_input
        self.asked_questions.add(self.current_question)
        self.current_question = None

        if not self.first_question_asked:
            self.first_question_asked = True
            next_question = self._get_next_question()
            if next_question:
                self.current_question = next_question
                return next_question

        if self.question_count < self.question_limit:
            self.question_count += 1
            if self.question_count < self.question_limit:
                next_question = self._get_next_question()
                if next_question:
                    self.current_question = next_question
                    return next_question
            elif self.question_count >= self.question_limit:
                self.waiting_for_final_confirmation = True
                return "¿Tienes alguna otra duda antes de generar el informe final?"
        elif self.additional_questions_mode:
            self.waiting_for_final_confirmation = True
            return "¿Tienes alguna otra duda antes de generar el informe final?"

        return "Ha ocurrido un error al procesar tu respuesta."

    def generate_final_report(self):
        report = "Informe Final del Proyecto:\n\n"
        for clave, valor in self.project_state.items():
            report += f"- {clave}: {valor}\n"
        report += "\nEste informe resume tus respuestas. ¡Gracias por tu tiempo! El servicio se reiniciará para la siguiente consulta."
        return report

    def reset(self):
        self.conversation_history = []
        self.project_state = {}
        self.asked_questions = set()
        self.current_question = None
        self.conversation_complete = False
        self.question_count = 0
        self.waiting_for_final_confirmation = False
        self.additional_questions_mode = False
        self.first_question_asked = False