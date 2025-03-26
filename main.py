from flask import Flask, request, jsonify
from agent import Starty  # Importación corregida
import os  # Importar os para acceder a las variables de entorno
from flask_cors import CORS  # Importa CORS

app = Flask(__name__)
CORS(app) 
starty = Starty()

# Mensaje de bienvenida de Starty
WELCOME_MESSAGE = """
¡Hola! Soy Starty, tu asesor integral en la creación de landing pages.
Estoy aquí para guiarte en cada paso, desde la planificación hasta la puesta en producción.
Voy a hacerte algunas preguntas para entender mejor tus necesidades.
"""

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "El campo 'message' es requerido."}), 400

    # Generar una respuesta usando Starty
    response = starty.generate_response(user_input)

    # Verificar si la conversación debe finalizar
    if starty.conversation_complete:
        return jsonify({"response": response, "conversation_complete": True})
    else:
        return jsonify({"response": response, "conversation_complete": False})

@app.route('/report', methods=['GET'])
def report():
    # Obtener el informe final
    report = starty.generate_final_report()
    return jsonify({"report": report})

def start_cli():
    print(WELCOME_MESSAGE)
    while True:
        current_question = starty.get_current_question()
        if current_question is None:
            print("Starty: Gracias por responder las preguntas iniciales. ¿Tienes alguna otra duda o deseas generar el informe?")
        else:
            print(f"Starty: {current_question}")

        user_input = input("Tú: ")
        response = starty.generate_response(user_input)
        print(f"Starty: {response}")

        if starty.conversation_complete:
            break

if __name__ == '__main__':
    import sys

    # Verificar si se está ejecutando en modo CLI
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        start_cli()
    else:
        print(WELCOME_MESSAGE)  # Starty saluda al iniciar el servidor

        # Obtener el puerto de la variable de entorno o usar 5000 por defecto
        port = int(os.environ.get('PORT', 5000))

        # Iniciar la aplicación Flask
        app.run(host='0.0.0.0', port=port)