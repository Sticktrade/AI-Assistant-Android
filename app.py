import os
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)

# Render leerá la clave de forma segura desde las Variables de Entorno (Environment Variables)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Inicializamos el cliente de Gemini solo si la clave está presente
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# --- HERRAMIENTAS / FUNCIONES QUE GEMINI PUEDE EJECUTAR EN TU MÓVIL ---
def controlar_wifi(estado: str):
    """Enciende o apaga el Wi-Fi del dispositivo móvil.
    
    Args:
        estado: 'on' para encender el Wi-Fi, 'off' para apagar el Wi-Fi.
    """
    pass

# Ruta de prueba para verificar que el servidor está online en Render
@app.route('/', methods=['GET'])
def inicio():
    return jsonify({"estado": "Servidor del Asistente Activo y Escuchando 24/7"}), 200

# Ruta principal que recibirá las peticiones de Tasker desde tu móvil
@app.route('/asistente', methods=['POST'])
def atender_comando():
    if not client:
        return jsonify({"respuesta_voz": "Error: La API Key de Gemini no está configurada en el servidor."}), 500

    datos = request.get_json(silent=True) or {}
    comando_usuario = datos.get("texto", "")

    if not comando_usuario:
        return jsonify({"respuesta_voz": "No recibí ningún comando de voz."}), 400

    try:
        # Enviamos el comando de voz a Gemini indicándole las herramientas del móvil
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=comando_usuario,
            config=types.GenerateContentConfig(
                tools=[controlar_wifi],
                system_instruction=(
                    "Eres el asistente personal inteligente del usuario en su teléfono Android. "
                    "Responde de forma clara, directa y natural para ser leída por voz (Text-to-Speech). "
                    "Si el usuario pide una acción en el dispositivo, utiliza la función correspondiente."
                ),
                temperature=0.3,
            ),
        )

        acciones = []
        respuesta_texto = ""

        # Verificamos si Gemini decidió ejecutar una función o dar una respuesta conversacional
        if response.function_calls:
            for call in response.function_calls:
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
        print(f"Error procesando el comando: {e}")
        return jsonify({"respuesta_voz": "Ocurrió un error al procesar tu solicitud con Gemini."}), 500

if __name__ == '__main__':
    # Para ejecución local de prueba
    app.run(host='0.0.0.0', port=5000, debug=True)
