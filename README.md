🍳 Chef Bot - Asistente Culinario Híbrido con PLN
Chatbot inteligente que entiende lenguaje natural en español, detecta emociones y busca recetas en una arquitectura híbrida-federada.
📋 Tabla de Contenidos
Descripción
Características Principales
Arquitectura del Sistema
Tecnologías Utilizadas
Instalación
Uso (Frontend + Backend)
Ejemplos de Interacción
Estructura del Proyecto
Técnicas de PLN Implementadas
APIs Externas
Autores
📖 Descripción
Chef Bot es un asistente culinario que combina un Frontend Web con un Backend de Flask y un potente motor de Procesamiento de Lenguaje Natural (PLN). Está diseñado para ser un asistente de cocina resiliente y preciso.
El sistema es capaz de:
🗣️ Entender lenguaje natural en español
😊 Detectar emociones (Positivo, Negativo, Neutral) y adaptar respuestas
🔄 Reconocer sinónimos (fideos = espagueti = pasta)
🌍 Traducir automáticamente consultas para APIs internacionales
📚 Buscar en una arquitectura federada: Utiliza Spoonacular para búsquedas potentes y TheMealDB como respaldo para los pasos, garantizando la mejor respuesta.
💡 Proporcionar tips profesionales y pasos detallados para 12 recetas curadas manualmente.
✨ Características Principales
🧠 Procesamiento de Lenguaje Natural (PLN)


Técnica
Descripción
Ejemplo
Tokenización
Divide el texto en palabras
"quiero pasta" → ['quiero', 'pasta']
Lematización
Reduce palabras a su forma base
'guisada' → 'guisar'
POS Tagging
Identifica categorías gramaticales
[('quiero', 'VERB'), ('pasta', 'NOUN')]
Análisis de Sentimientos
Detecta emociones (POS/NEG/NEU)
"estoy triste" → 😞 NEG (87%)
Detección de Sinónimos
Reconoce variaciones
'fideos' = 'espagueti' = 'pasta'

🌐 Sistema Híbrido-Federado de Datos
El bot opera en un sistema de 3 capas para asegurar velocidad, calidad y resiliencia.
┌──────────────────────────────────────────┐
│  Nivel 1: Base de Datos Local (Calidad)  │
│  • 12+ recetas curadas (Lasaña, Pizza...) │
│  • Pasos y Tips profesionales internos    │
│  • Respuesta instantánea                 │
└───────────────┬──────────────────────────┘
                ↓ (Si no encuentra)
┌──────────────────────────────────────────┐
│  Nivel 2: API Spoonacular (Potencia)     │
│  • Motor de búsqueda principal           │
│  • Acceso a miles de recetas             │
│  • Búsqueda por ingredientes y filtros    │
└───────────────┬──────────────────────────┘
                ↓ (Para Pasos)
┌──────────────────────────────────────────┐
│  Nivel 3: API TheMealDB (Resiliencia)    │
│  • Respaldo para obtener pasos           │
│  • Formato de texto limpio y confiable    │
└──────────────────────────────────────────┘


😊 Adaptación Emocional
El bot adapta sus respuestas según el estado de ánimo del usuario:
Sentimiento
Respuesta del Bot
😊 Positivo
"¡Qué buena energía! 🎉 Pasta Carbonara será perfecta"
😞 Negativo
"Entiendo... 😞 Una Carne Guisada reconfortante te ayudará"
😐 Neutral
"Perfecto. Te muestro Pollo Asado"

🏗️ Arquitectura del Sistema
El proyecto está desacoplado en un Frontend (Cliente) y un Backend (Servidor).
┌─────────────────┐                             ┌───────────────────┐
│    Frontend      │                             │     Backend       │
│  (index.html)    │                             │   (server.py)     │
└─────────────────┘                             └───────────────────┘
         |                                                |
         |  (1) Envía Petición HTTP (Fetch)              |
         |     "quiero pasta"                            |
         └─────────────────► [http://127.0.0.1:5000/chat](http://127.0.0.1:5000/chat) ◄──┘
                                                         |
                                                         | (2) Procesa en chatbot_logic.py
                                                         |     • PLN, Sentimiento
                                                         |     • Lógica Híbrida (APIs)
                                                         |
┌─────────────────┐                             ┌───────────────────┐
│    (4) Renderiza   │  (3) Devuelve Respuesta JSON     │     Servidor      │
│     la respuesta  │      { "text": "Perfecto..." }     │     (Flask)       │
└─────────────────┘                             └───────────────────┘
         ▲                                                ▲
         └───────────────────────( JSON )─────────────────┘


🛠️ Tecnologías Utilizadas
Backend
Python 3.8+
Flask - Servidor web ligero para la API REST
Flask-CORS - Para permitir la conexión con el frontend
NLTK - Tokenización y procesamiento de texto
Pysentimiento - Análisis de sentimientos en español
Requests - Consumo de APIs externas
Frontend
HTML5 - Estructura de la interfaz de chat
CSS3 - Estilos modernos para las burbujas de chat
JavaScript (ES6+) - Lógica del cliente, fetch para conectar al backend
APIs Externas
Spoonacular - (Principal) Búsqueda avanzada de recetas.
TheMealDB - (Respaldo) Obtención de pasos de recetas.
📦 Instalación
1. Clonar el repositorio
git clone [https://github.com/tu-usuario/chef-bot-pln.git](https://github.com/tu-usuario/chef-bot-pln.git)
cd chef-bot-pln


2. Crear entorno virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate


3. Instalar dependencias
Asegúrate de que tu archivo requirements.txt contenga:
nltk
pysentimiento
requests
deep_translator
flask
flask_cors


Luego ejecuta:
pip install -r requirements.txt


4. Descargar recursos de NLTK
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"


🚀 Uso (Frontend + Backend)
Para ejecutar el bot, necesitas iniciar el servidor y luego abrir la interfaz web.
1. Configurar la API Key
Antes de iniciar, abre chatbot_logic.py y añade tu API Key de Spoonacular en la variable self.SPOONACULAR_API_KEY.
# chatbot_logic.py (línea ~45)

class ChatbotLogic:
    def __init__(self):
        # ...
        self.SPOONACULAR_API_KEY = "AQUI_VA_TU_API_KEY_DE_SPOONACULAR" 
        # ...


2. Iniciar el Servidor (Backend)
En tu terminal, ejecuta el servidor Flask:
python server.py


Deberías ver una salida que indica que el servidor está cargando los modelos y ejecutándose en http://127.0.0.1:5000.
✅ Pysentimiento cargado
✅ Spoonacular API Key configurada.
✅ Spoonacular API (Búsqueda) + TheMealDB (Pasos) lista
✅ ¡Chef Bot listo y en línea!
==================================================
 * Running on [http://127.0.0.1:5000](http://127.0.0.1:5000)


¡No cierres esta terminal!
3. Abrir la Interfaz (Frontend)
Ahora, simplemente abre el archivo index.html directamente en tu navegador web (como Chrome o Firefox).
Puedes hacer doble clic en el archivo.
O arrastrar el archivo index.html a una pestaña vacía del navegador.
La interfaz se cargará, el script.js se conectará automáticamente a tu servidor local (Flask) y podrás empezar a chatear.
💬 Ejemplos de Interacción
Ejemplo 1: Búsqueda Interna (Flujo 1)
Usuario: quiero pollo
Bot: 🎯 Detectado por palabra clave: 'pollo' → pollo asado
     Perfecto. Pollo Asado
     📋 Ingredientes: 1 pollo entero, 2 limones, ajo...
     ⏱️ 1h 30min | 📊 Fácil


(Al pulsar "Pasos", muestra los pasos internos curados)
Ejemplo 2: Con Sinónimos
Usuario: dame fideos
Bot: 💡 Detectado por sinónimo: 'fideos' → pasta carbonara
     📋 Ingredientes: 400g espagueti, 200g panceta...


Ejemplo 3: Con Análisis Emocional
Usuario: estoy triste quiero algo de comer
Bot: 🎭 😞 NEG (85%)
     Entendido... 😞 Una Carne Guisada reconfortante te ayudará.
     📋 Ingredientes: 1kg carne, 3 papas, 2 zanahorias...


Ejemplo 4: Búsqueda en API Externa (Flujo 2 - Spoonacular)
Usuario: quiero salmon
Bot: 🌐 Traduciendo 'salmon' → 'salmon'...
     Buscando 'salmon' en Spoonacular...
     ✅ Easy Glazed Salmon
     📂 Fuente: Foodista
     ⏱️ Tiempo: 20 minutos
     📋 INGREDIENTES:
      • 1/4 taza de salsa de soja
      • 2 cucharadas de miel
      • 4 filetes de salmón (6 oz cada uno)
     ...


📁 Estructura del Proyecto
chef-bot-pln/
│
├── chatbot_logic.py          # Lógica principal del chatbot (PLN, APIs)
├── server.py                 # Servidor Backend (Flask API)
├── index.html                # Interfaz de usuario (Frontend)
├── style.css                 # Estilos del chat
├── script.js                 # Lógica del cliente (Fetch)
├── requirements.txt          # Dependencias de Python
└── README.md                 # Este archivo


🧠 Técnicas de PLN Implementadas
1. Tokenización
Divide el texto en unidades más pequeñas (tokens).
"quiero pasta carbonara" 
→ ['quiero', 'pasta', 'carbonara']


2. Lematización
Reduce las palabras a su forma base (lema). Se usa un diccionario simple para velocidad.
['guisada', 'fideos', 'cocino'] 
→ ['guisar', 'fideo', 'cocinar']


3. POS Tagging (Part-of-Speech)
Identifica la categoría gramatical de cada palabra para extraer el sujeto (la comida).
[('quiero', 'VERB'), ('pasta', 'NOUN')]


4. Análisis de Sentimientos
Detecta emociones en el texto del usuario usando pysentimiento.
"estoy súper feliz" → POS (92%)
"ando muy triste"   → NEG (87%)


🌐 APIs Externas
1. Spoonacular (Principal)
Rol: Búsqueda principal de recetas (Flujo 2).
Endpoint: api.spoonacular.com/recipes/complexSearch
Nota: Requiere una API Key que debe ser añadida en chatbot_logic.py.
2. TheMealDB (Respaldo)
Rol: Respaldo para obtener pasos de recetas (Flujo 3).
Endpoint: www.themealdb.com/api/json/v1/1/search.php
Nota: Es gratuita y no requiere API Key.
👤 Autores
Ivan Andres Bernal Hernandez
Yow Nicolas Guacaneme Molano
🎓 Universidad: Universidad de Cundinamarca
📧 Email: guacanemeyow@gmail.com - ivanandresbernalhernandez595@gmail.com
🐙 GitHub: yowNikolaz-26 - ivanzber
<div align="center">
⭐ Si te gusta este proyecto, dale una estrella en GitHub ⭐
Hecho con ❤️, 🐍 y ☕
</div>
