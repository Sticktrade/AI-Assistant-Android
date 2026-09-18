import os
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Leemos la API Key desde las variables de entorno de Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Inicializamos el cliente oficial de Gemini
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

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
    if not client:
        return jsonify({"respuesta_voz": "Error: La API Key de Gemini no está configurada en Render."}), 200

    datos = request.get_json(silent=True) or {}
    comando_usuario = datos.get("texto", "")

    if not comando_usuario:
        return jsonify({"respuesta_voz": "No te he oído bien, ¿puedes repetir?"}), 200

    try:
        # Petición a Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=comando_usuario,
            config=types.GenerateContentConfig(
                tools=[controlar_wifi],
                system_instruction=(
                    "Eres el asistente personal inteligente del usuario en su teléfono Android. "
                    "Responde de forma concisa, clara y directa para ser leída por voz. "
                    "Usa un tono natural en español."
                ),
                temperature=0.3,
            ),
        )

        acciones = []
        respuesta_texto = ""

        if response.function_calls:
            for call in response.function_calls:
                acciones.append({
                    "funcion": call.name,
                    "parametros": dict(call.args)
                })
            respuesta_texto = "Ejecutando la acción requerida."
        elif response.text:
            respuesta_texto = response.text
        else:
            respuesta_texto = "Entendido."

        return jsonify({
            "respuesta_voz": respuesta_texto,
            "acciones": acciones
        }), 200

    except Exception as e:
        # Imprimimos el error exacto en los logs de Render para depurar
        print(f"Error detallado de Gemini: {str(e)}")
        return jsonify({"respuesta_voz": f"Error en la API de Gemini: {str(e)}"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
