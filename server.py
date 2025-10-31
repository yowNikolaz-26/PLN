# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot_logic import ChatbotLogic

# Inicializa la app Flask
app = Flask(__name__)
# Configura CORS para permitir peticiones desde el archivo HTML
CORS(app) 

# --- Carga del Bot ---
# Creamos UNA instancia global de la lógica del bot
# Esto cargará los modelos de IA UNA SOLA VEZ al iniciar.
print("="*50)
print("🧠 Cargando modelos de IA... Esto puede tardar unos segundos.")
try:
    bot = ChatbotLogic()
    print("✅ ¡Chef Bot listo y en línea!")
    print("="*50)
except Exception as e:
    print(f"❌ ERROR FATAL AL CARGAR MODELOS: {e}")
    bot = None
# ---------------------

@app.route('/init', methods=['GET'])
def init_chat():
    """Endpoint para obtener los mensajes de bienvenida."""
    if not bot:
        return jsonify({"error": "Bot no inicializado"}), 500
        
    respuestas = bot.mostrar_bienvenida()
    return jsonify({"responses": respuestas})

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal para procesar mensajes del usuario."""
    if not bot:
        return jsonify({"error": "Bot no inicializado"}), 500

    data = request.json
    mensaje = data.get('message')

    if not mensaje:
        return jsonify({"error": "No message provided"}), 400

    # Llama a la lógica principal del bot
    respuestas, saludado = bot.procesar_mensaje(mensaje)
    
    # Devuelve las respuestas y el estado del saludo
    return jsonify({"responses": respuestas, "saludado": saludado})

@app.route('/action', methods=['POST'])
def action():
    """Endpoint para los botones (Descripción, Pasos, etc.)."""
    if not bot:
        return jsonify({"error": "Bot no inicializado"}), 500
        
    data = request.json
    accion = data.get('action') # "descripcion", "pasos", "tips", "variaciones"
    respuestas = []

    if accion == 'descripcion':
        respuestas = bot.generar_descripcion()
    elif accion == 'pasos':
        respuestas = bot.generar_pasos()
    elif accion == 'tips':
        respuestas = bot.generar_tips()
    elif accion == 'variaciones':
        respuestas = bot.generar_variaciones()
    else:
        respuestas = [bot._crear_respuesta("⚠️ Acción desconocida.", "warning")]

    return jsonify({"responses": respuestas})


if __name__ == '__main__':
    # Inicia el servidor Flask en el puerto 5000
    # debug=False es más estable para los modelos de Transformers
    app.run(host='127.0.0.1', port=5000, debug=False)