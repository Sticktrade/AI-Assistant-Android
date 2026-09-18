import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# API Key de Gemini leída desde las variables de entorno de Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/', methods=['GET'])
def inicio():
    return jsonify({"estado": "Servidor del Asistente Activo y Escuchando 24/7"}), 200

@app.route('/asistente', methods=['POST'])
def atender_comando():
    if not GEMINI_API_KEY:
        return jsonify({"respuesta_voz": "Error: La API Key no está configurada en Render."}), 200

    datos = request.get_json(silent=True) or {}
    comando_usuario = datos.get("texto", "")

    if not comando_usuario:
        return jsonify({"respuesta_voz": "No te he oído bien, ¿puedes repetir?"}), 200

    try:
        # Endpoint directo a la API REST de Gemini
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        prompt_sistema = (
            "Eres el asistente personal inteligente del usuario en su teléfono Android. "
            "Responde de forma muy concisa, clara y directa para ser leída por voz en español. "
            f"Pregunta del usuario: {comando_usuario}"
        )

        payload = {
            "contents": [{
                "parts": [{"text": prompt_sistema}]
            }]
        }

        headers = {"Content-Type": "application/json"}
        
        # Petición HTTP directa
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        res_data = response.json()

        if response.status_code == 200:
            respuesta_texto = res_data['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"respuesta_voz": respuesta_texto}), 200
        else:
            mensaje_error = res_data.get('error', {}).get('message', 'Error desconocido')
            return jsonify({"respuesta_voz": f"Error de la API de Google: {mensaje_error}"}), 200

    except Exception as e:
        return jsonify({"respuesta_voz": f"Error de conexión: {str(e)}"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
