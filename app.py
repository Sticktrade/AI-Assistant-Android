import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Leemos la API Key desde las variables de entorno de Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Definimos las herramientas disponibles
def controlar_wifi(estado: str):
    """Enciende o apaga el Wi-Fi del dispositivo móvil.
    
    Args:
        estado: 'on' para encender el Wi-Fi, 'off' para apagar el Wi-Fi.
    """
    pass

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
        # Configuración del modelo con el endpoint oficial estable
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[controlar_wifi],
            system_instruction=(
                "Eres el asistente personal inteligente del usuario en su teléfono Android. "
                "Responde de forma concisa, clara y directa para ser leída por voz (Text-to-Speech). "
                "Usa un tono natural en español."
            )
        )

        # Generamos la respuesta
        response = model.generate_content(comando_usuario)

        acciones = []
        respuesta_texto = ""

        # Verificamos si Gemini quiere llamar a una función o dar texto
        if response.candidates and response.candidates[0].function_calls:
            for call in response.candidates[0].function_calls:
                acciones.append({
                    "funcion": call.name,
                    "parametros": dict(call.args)
                })
            respuesta_texto = "Ejecutando la acción en tu dispositivo."
        else:
            respuesta_texto = response.text or "Entendido."

        return jsonify({
            "respuesta_voz": respuesta_texto,
            "acciones": acciones
        }), 200

    except Exception as e:
        print(f"Error detallado de Gemini: {str(e)}")
        return jsonify({"respuesta_voz": f"Error en la API: {str(e)}"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
