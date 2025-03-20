import google.generativeai as genai
import atexit

class Starty:
    def __init__(self):
        self.gemini_api_key = "AIzaSyC2id4JRddrF1vki75tu2YoaKlj1H6iRww"  # Tu API key de Google Gemini
        self.configure_gemini()
        self.conversation_history = []  # Historial de la conversación
        self.project_state = {
            "objective": None,
            "target_audience": None,
            "design_preferences": None,
            "content_requirements": None,
            "color_palette": None,
            "template_elements": None,
            "headlines": None,
            "hooks": None,
            "technical_tools": None,
            "hosting": None,
            "domain": None,
        }
        self.questions = [
            "¿Cuál es el objetivo principal de tu landing page? (ej: generar leads, vender un producto, etc.)",
            "¿Quién es tu público objetivo?",
            "¿Tienes alguna preferencia de diseño? (ej: moderno, minimalista, colorido)",
            "¿Qué tipo de contenido quieres incluir? (ej: título, descripción, testimonios, formulario)",
            "¿Tienes alguna preferencia de colores? (ej: colores neutros, colores vibrantes)",
            "¿Qué elementos debe tener la plantilla? (ej: encabezado, testimonios, formulario, pie de página)",
            "¿Tienes ideas para los titulares y ganchos? (ej: 'Impulsa tu negocio con nuestras soluciones')",
            "¿Necesitas alguna herramienta técnica específica? (ej: HTML, CSS, JavaScript, Bootstrap)",
            "¿Tienes preferencias de hosting y dominio? (ej: Netlify, Namecheap)",
        ]
        self.current_question_index = 0
        self.conversation_complete = False

        # Registrar la función de limpieza al salir
        atexit.register(self.cleanup)

    def configure_gemini(self):
        # Configurar la API de Gemini
        genai.configure(api_key=self.gemini_api_key)

    def cleanup(self):
        # Cerrar la conexión gRPC al finalizar
        if hasattr(genai, '_grpc_channel'):
            genai._grpc_channel.close()

    def get_current_question(self):
        # Obtener la pregunta actual
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        else:
            return None

    def generate_response(self, user_input):
        # Agregar la entrada del usuario al historial de la conversación
        self.conversation_history.append({"role": "user", "content": user_input})

        # Si la conversación inicial ha terminado, manejar preguntas adicionales
        if self.current_question_index >= len(self.questions):
            return self._handle_additional_questions(user_input)

        # Actualizar el estado del proyecto basado en la pregunta actual
        self._update_project_state(user_input)

        # Pasar a la siguiente pregunta
        self.current_question_index += 1

        # Verificar si todas las preguntas han sido respondidas
        if self.current_question_index >= len(self.questions):
            return "Gracias por responder las preguntas iniciales. ¿Tienes alguna otra duda o deseas generar el informe?"

        # Devolver la siguiente pregunta
        return self.questions[self.current_question_index]

    def _handle_additional_questions(self, user_input):
        # Manejar preguntas adicionales después de las preguntas iniciales
        if "generar informe" in user_input.lower() or "sí" in user_input.lower() or "si" in user_input.lower():
            self.conversation_complete = True
            return self.generate_final_report()
        else:
            # Usar Gemini para responder preguntas adicionales
            prompt = f"Eres Starty, un asesor especialista en la creación de landing pages. Responde de manera amigable y profesional. Aquí está la pregunta del usuario: {user_input}"
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            self.conversation_history.append({"role": "assistant", "content": response.text})
            return f"{response.text}\n\n¿Estás satisfecho con mi respuesta o tienes otra duda?"

    def _update_project_state(self, user_input):
        # Actualizar el estado del proyecto basado en la pregunta actual
        if self.current_question_index == 0:
            self.project_state["objective"] = user_input
        elif self.current_question_index == 1:
            self.project_state["target_audience"] = user_input
        elif self.current_question_index == 2:
            self.project_state["design_preferences"] = user_input
        elif self.current_question_index == 3:
            self.project_state["content_requirements"] = user_input
        elif self.current_question_index == 4:
            self.project_state["color_palette"] = user_input
        elif self.current_question_index == 5:
            self.project_state["template_elements"] = user_input
        elif self.current_question_index == 6:
            self.project_state["headlines"] = user_input
        elif self.current_question_index == 7:
            self.project_state["technical_tools"] = user_input
        elif self.current_question_index == 8:
            self.project_state["hosting"] = user_input
            self.project_state["domain"] = user_input

    def generate_final_report(self):
        # Generar un informe final en formato prompt
        prompt = "Informe Final del Proyecto (Formato Prompt):\n\n"
        prompt += "El cliente desea una landing page con las siguientes características:\n"
        prompt += f"- Objetivo: {self.project_state['objective']}\n"
        prompt += f"- Público objetivo: {self.project_state['target_audience']}\n"
        prompt += f"- Preferencias de diseño: {self.project_state['design_preferences']}\n"
        prompt += f"- Requerimientos de contenido: {self.project_state['content_requirements']}\n"
        prompt += f"- Paleta de colores: {self.project_state['color_palette']}\n"
        prompt += f"- Elementos de la plantilla: {self.project_state['template_elements']}\n"
        prompt += f"- Titulares y ganchos: {self.project_state['headlines']}\n"
        prompt += f"- Herramientas técnicas: {self.project_state['technical_tools']}\n"
        prompt += f"- Hosting y dominio: {self.project_state['hosting']}, {self.project_state['domain']}\n"
        prompt += "\nEste informe está listo para ser entregado al equipo de desarrollo, diseño y QA."
        return prompt