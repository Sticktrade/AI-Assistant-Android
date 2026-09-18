import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Leemos la API Key desde las variables de entorno de Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

@app.route('/', methods=['GET'])
def inicio():
    return jsonify({"estado": "Servidor del Asistente Activo y Escuchando 24/7"}), 200

@app.route('/asistente', methods=['POST'])
def atender_comando():
    if not GEMINI_API_KEY:
        return jsonify({"respuesta_voz": "Error: La API Key de Gemini no está configurada en Render."}), 200

    datos = request.get_json(silent=True) or {}
    comando_usuario = datos.get("texto", "")

    if not comando_usuario:
        return jsonify({"respuesta_voz": "No te he oído bien, ¿puedes repetir?"}), 200

    try:
        # Inicializamos el modelo oficial estándar
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Prompt con la instrucción del sistema
        prompt = (
            "Eres el asistente personal inteligente del usuario en su teléfono Android. "
            "Responde de forma muy concisa, clara y directa para ser leída por voz en español. "
            f"Pregunta del usuario: {comando_usuario}"
        )

        response = model.generate_content(prompt)
        respuesta_texto = response.text if response.text else "Entendido."

        return jsonify({
            "respuesta_voz": respuesta_texto
        }), 200

    except Exception as e:
        print(f"Error detallado de Gemini: {str(e)}")
        return jsonify({"respuesta_voz": f"Error en la API: {str(e)}"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
