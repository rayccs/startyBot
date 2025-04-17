# main.py
from flask import Flask, request, jsonify
from agent import Starty
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
starty = Starty()

WELCOME_MESSAGE = """
¡Hola! Soy Starty, tu asesor inteligente y autónomo para la creación de landing pages.
Estoy aquí para entender tus necesidades a través de preguntas, análisis y repreguntas.
Al final, te mostraré un resumen de tus respuestas. ¡Empecemos!
"""

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "El campo 'message' es requerido."}), 400

    response = starty.generate_response(user_input)

    if starty.conversation_complete:
        final_report = {"response": response, "conversation_complete": True, "report": starty.project_state}
        starty.reset() # Reiniciar el agente después de completar la conversación
        return jsonify(final_report)
    else:
        return jsonify({"response": response, "conversation_complete": False})

@app.route('/report', methods=['GET'])
def report():
    report = starty.generate_final_report()
    return jsonify({"report": report})

def start_cli():
    print(WELCOME_MESSAGE)
    while True:
        current_question = starty.current_question or starty._get_next_question()
        if current_question is None and not starty.additional_questions_mode and not starty.waiting_for_final_confirmation:
            starty.waiting_for_final_confirmation = True
            current_question = "¿Tienes alguna otra duda antes de generar el informe final?"

        if starty.conversation_complete:
            print("Starty: Gracias por tu tiempo. Aquí tienes un resumen de tus respuestas:")
            for clave, valor in starty.project_state.items():
                print(f"- {clave}: {valor}")
            print("\nStarty se ha reiniciado para una nueva consulta.")
            starty.reset()
            break
        elif current_question:
            print(f"Starty: {current_question}")
            user_input = input("Tú: ")
            response = starty.generate_response(user_input)
            print(f"Starty: {response}")
        elif starty.additional_questions_mode or starty.waiting_for_final_confirmation:
            user_input = input("Tú: ")
            response = starty.generate_response(user_input) # Usar generate_response para manejar la lógica de la pregunta final
            print(f"Starty: {response}")
            if starty.conversation_complete:
                print("Starty: Gracias por tu tiempo. Aquí tienes un resumen de tus respuestas:")
                for clave, valor in starty.project_state.items():
                    print(f"- {clave}: {valor}")
                print("\nStarty se ha reiniciado para una nueva consulta.")
                starty.reset()
                break

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        start_cli()
    else:
        print(WELCOME_MESSAGE)
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)