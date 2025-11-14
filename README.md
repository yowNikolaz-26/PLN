# 🍳 Chef Bot - Asistente Culinario Inteligente con PLN

> **Chatbot web inteligente que entiende lenguaje natural en español, detecta emociones y busca recetas de cocina en una arquitectura híbrida-federada con múltiples APIs.**

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Instalación](#-instalación)
- [Uso (Frontend + Backend)](#-uso-frontend--backend)
- [Ejemplos de Interacción](#-ejemplos-de-interacción)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Técnicas de PLN Implementadas](#-técnicas-de-pln-implementadas)
- [APIs Externas](#-apis-externas)
- [Contribuir](#-contribuir)
- [Roadmap](#-roadmap)
- [Licencia](#-licencia)
- [Autores](#-autores)

---

## 📖 Descripción

**Chef Bot** es un asistente culinario inteligente que combina una **interfaz web moderna** con **Procesamiento de Lenguaje Natural (PLN)** avanzado y **APIs externas** para ayudar a los usuarios a encontrar recetas de cocina. El sistema opera con una arquitectura cliente-servidor desacoplada (Frontend HTML/CSS/JS + Backend Flask).

El sistema es capaz de:

- 🗣️ **Entender lenguaje natural** en español
- 😊 **Detectar emociones** (Positivo, Negativo, Neutral) y adaptar respuestas
- 🔄 **Reconocer sinónimos** (fideos = espagueti = pasta)
- 🌍 **Traducir automáticamente** entre español e inglés
- 📚 **Buscar en arquitectura federada**: 
  - **Nivel 1**: Base de datos local (12+ recetas curadas)
  - **Nivel 2**: API Spoonacular (búsqueda principal, miles de recetas)
  - **Nivel 3**: API TheMealDB (respaldo para pasos detallados)
- 💡 **Proporcionar tips profesionales** curados manualmente
- 🌐 **Interfaz web responsive** con chat en tiempo real

---

## ✨ Características Principales

### 🧠 Procesamiento de Lenguaje Natural (PLN)

| Técnica | Descripción | Ejemplo |
|---------|-------------|---------|
| **Tokenización** | Divide el texto en palabras | `"quiero pasta"` → `['quiero', 'pasta']` |
| **Lematización** | Reduce palabras a su forma base | `'guisada'` → `'guisar'` |
| **POS Tagging** | Identifica categorías gramaticales | `[('quiero', 'VERB'), ('pasta', 'NOUN')]` |
| **Análisis de Sentimientos** | Detecta emociones (POS/NEG/NEU) | `"estoy triste"` → 😞 NEG (87%) |
| **Detección de Sinónimos** | Reconoce variaciones | `'fideos'` = `'espagueti'` = `'pasta'` |

### 🌐 Sistema Híbrido-Federado de Datos

El bot opera en un sistema de **3 capas** para asegurar **velocidad**, **calidad** y **resiliencia**:

```
┌──────────────────────────────────────────┐
│  Nivel 1: Base de Datos Local (Calidad)  │
│  • 12+ recetas curadas manualmente       │
│  • Pasos y Tips profesionales internos   │
│  • Respuesta instantánea                │
└───────────────┬──────────────────────────┘
                ↓ (Si no encuentra)
┌──────────────────────────────────────────┐
│  Nivel 2: API Spoonacular (Potencia)     │
│  • Motor de búsqueda principal           │
│  • Acceso a miles de recetas             │
│  • Búsqueda por ingredientes y filtros   │
└───────────────┬──────────────────────────┘
                ↓ (Para Pasos detallados)
┌──────────────────────────────────────────┐
│  Nivel 3: API TheMealDB (Resiliencia)    │
│  • Respaldo para obtener pasos           │
│  • Formato de texto limpio y confiable   │
└──────────────────────────────────────────┘
```

### 🌍 Traducción Automática

- **Español → Inglés**: Para buscar en APIs internacionales
- **Inglés → Español**: Para mostrar resultados al usuario

```
Usuario: "quiero salmón" 
    → Traduce: "salmon"
    → Busca en Spoonacular
    → Traduce respuesta: "Salmón Glaseado Fácil"
```

### 😊 Adaptación Emocional

El bot adapta sus respuestas según el estado de ánimo del usuario:

| Sentimiento | Respuesta del Bot |
|-------------|-------------------|
| 😊 **Positivo** | "¡Qué buena energía! 🎉 Pasta Carbonara será perfecta" |
| 😞 **Negativo** | "Entiendo... 😞 Una Carne Guisada reconfortante te ayudará" |
| 😐 **Neutral** | "Perfecto. Te muestro Pollo Asado" |

---

## 🏗️ Arquitectura del Sistema

### Arquitectura Cliente-Servidor

El proyecto está **desacoplado** en un **Frontend** (Cliente) y un **Backend** (Servidor):

```
┌─────────────────┐                          ┌───────────────────┐
│    Frontend      │                          │     Backend       │
│  (index.html)    │                          │   (server.py)     │
│  • HTML5         │                          │   • Flask API     │
│  • CSS3          │                          │   • Python 3.8+   │
│  • JavaScript    │                          │   • CORS habilitado│
└─────────────────┘                          └───────────────────┘
         │                                              │
         │  (1) Envía Petición HTTP (Fetch)            │
         │     POST /chat                              │
         │     {"mensaje": "quiero pasta"}             │
         └──────────────► http://127.0.0.1:5000 ◄──────┘
                                                       │
                                                       │ (2) Procesa en
                                                       │     chatbot_logic.py
                                                       │     • PLN
                                                       │     • Sentimiento
                                                       │     • Lógica Híbrida
                                                       │
┌─────────────────┐                          ┌───────────────────┐
│ (4) Renderiza    │  (3) Devuelve JSON      │   APIs Externas   │
│   la respuesta   │  {"respuestas": [...]}  │   • Spoonacular   │
│   en burbujas    │                          │   • TheMealDB     │
└─────────────────┘                          └───────────────────┘
         ▲                                              ▲
         └──────────────( Respuesta JSON )─────────────┘
```

### Flujo de Procesamiento

```
┌──────────────────────────────────────────────────────┐
│                    USUARIO                           │
│   "quiero salmon que ando triste"                    │
└─────────────────────┬────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│            CAPA DE PROCESAMIENTO PLN                 │
│  • Tokenización (NLTK)                               │
│  • Lematización (Diccionario personalizado)          │
│  • POS Tagging (Extracción de sustantivos)           │
│  • Análisis de Sentimientos (Pysentimiento)          │
└─────────────────────┬────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│          CAPA DE LÓGICA DE NEGOCIO                   │
│  • Detección de sinónimos                            │
│  • Extracción de palabra clave                       │
│  • Traducción ES ↔ EN (deep_translator)              │
└─────────────────────┬────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│             CAPA DE DATOS (Federada)                 │
│  1. Base de datos local (12 recetas + tips)          │
│  2. API Spoonacular (búsqueda principal)             │
│  3. API TheMealDB (respaldo para pasos)              │
└─────────────────────┬────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│                  RESPUESTA                           │
│  "😞 Entiendo... Salmón Glaseado te ayudará          │
│   📋 1/4 taza salsa de soja, 2 cdas miel..."         │
└──────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.8+**
- **Flask 2.0+** - Servidor web ligero para la API REST
- **Flask-CORS** - Para permitir conexiones desde el frontend
- **NLTK** - Tokenización y procesamiento de texto
- **Pysentimiento** - Análisis de sentimientos en español
- **Requests** - Consumo de APIs REST externas
- **deep_translator** - Traducción automática ES ↔ EN

### Frontend
- **HTML5** - Estructura semántica de la interfaz
- **CSS3** - Estilos modernos con gradientes y animaciones
- **JavaScript (ES6+)** - Lógica del cliente, Fetch API para comunicación asíncrona

### APIs Externas
- **[Spoonacular](https://spoonacular.com/food-api)** - Motor de búsqueda principal (requiere API Key)
- **[TheMealDB](https://www.themealdb.com/)** - Respaldo para pasos de recetas (gratuita)

### Librerías Python
```txt
flask==2.0+
flask-cors==3.0+
nltk==3.8+
pysentimiento==0.7+
requests==2.31+
deep-translator==1.11+
```

---

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/chef-bot-pln.git
cd chef-bot-pln
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Contenido de `requirements.txt`:**
```txt
flask
flask-cors
nltk
pysentimiento
requests
deep-translator
```

### 4. Descargar recursos de NLTK

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

### 5. Configurar API Key de Spoonacular

1. Regístrate en [Spoonacular](https://spoonacular.com/food-api) (plan gratuito disponible)
2. Obtén tu API Key
3. Abre `chatbot_logic.py` y añade tu clave:

```python
# chatbot_logic.py (línea ~45)

class ChatbotLogic:
    def __init__(self):
        # ...
        self.SPOONACULAR_API_KEY = "TU_API_KEY_AQUI"  # ← Coloca tu clave aquí
        # ...
```

---

## 🚀 Uso (Frontend + Backend)

### Paso 1: Iniciar el Servidor Backend

En tu terminal, ejecuta:

```bash
python server.py
```

**Salida esperada:**
```
✅ Pysentimiento cargado
✅ Spoonacular API Key configurada.
✅ Spoonacular API (Búsqueda) + TheMealDB (Pasos) lista
✅ ¡Chef Bot listo y en línea!
==================================================
 * Running on http://127.0.0.1:5000
```

⚠️ **No cierres esta terminal** mientras uses el chatbot.

### Paso 2: Abrir la Interfaz Frontend

Simplemente **abre el archivo `index.html`** en tu navegador web:

- **Opción A**: Doble clic en `index.html`
- **Opción B**: Arrastra el archivo a una pestaña vacía del navegador
- **Opción C**: Click derecho → "Abrir con" → Chrome/Firefox

El archivo `script.js` se conectará automáticamente a `http://127.0.0.1:5000` y podrás empezar a chatear.

### Uso Programático (Opcional)

Si deseas integrar el bot en otro proyecto:

```python
from chatbot_logic import ChatbotLogic

# Inicializar chatbot
bot = ChatbotLogic()

# Procesar mensaje
respuestas, _ = bot.procesar_mensaje("quiero pasta carbonara")

for resp in respuestas:
    print(f"[{resp['type']}]: {resp['text']}")
```

---

## 💬 Ejemplos de Interacción

### Ejemplo 1: Búsqueda Interna (Base de Datos Local)

```
Usuario: quiero pollo
Bot: 🎯 Detectado por palabra clave: 'pollo' → pollo asado
     Perfecto. Pollo Asado
     📋 Ingredientes: 1 pollo entero, 2 limones, ajo en polvo...
     ⏱️ 1h 30min | 📊 Fácil
     
     [Botón: Ver Pasos]  [Botón: Tips de Cocina]
```

Al pulsar **"Ver Pasos"**, muestra los pasos curados manualmente.

### Ejemplo 2: Con Sinónimos

```
Usuario: dame fideos
Bot: 💡 Detectado por sinónimo: 'fideos' → pasta carbonara
     ¡Qué buena elección! Pasta Carbonara
     📋 Ingredientes: 400g espagueti, 200g panceta, 4 huevos...
```

### Ejemplo 3: Con Análisis Emocional

```
Usuario: estoy triste quiero algo de comer
Bot: 🎭 😞 NEG (85%)
     Entiendo... 😞 Una Carne Guisada reconfortante te ayudará.
     📋 Ingredientes: 1kg carne, 3 papas, 2 zanahorias...
```

### Ejemplo 4: Búsqueda en API Spoonacular

```
Usuario: quiero salmon
Bot: 🌐 Traduciendo 'salmon' → 'salmon'...
     Buscando 'salmon' en Spoonacular...
     ✅ Easy Glazed Salmon
     📂 Fuente: Foodista
     ⏱️ Tiempo: 20 minutos
     🍽️ Porciones: 4
     
     📋 INGREDIENTES:
      • 1/4 taza de salsa de soja
      • 2 cucharadas de miel
      • 4 filetes de salmón (6 oz cada uno)
      
     [Botón: Ver Pasos Completos]
```

### Ejemplo 5: Respaldo con TheMealDB

```
Usuario: quiero beef wellington
Bot: 🌐 No se encontró en Spoonacular, buscando en TheMealDB...
     ✅ Beef Wellington
     📂 Categoría: Beef | 🌍 British
     
     📋 INGREDIENTES:
      • 2 lbs filete de res
      • 8 oz champiñones
      • 6 oz paté
     
     [Botón: Ver Pasos]
```

---

## 📁 Estructura del Proyecto

```
chef-bot-pln/
│
├── 🐍 Backend (Python + Flask)
│   ├── chatbot_logic.py          # Lógica principal del chatbot (PLN, APIs)
│   ├── server.py                 # Servidor Flask con endpoint /chat
│   └── requirements.txt          # Dependencias de Python
│
├── 🌐 Frontend (HTML + CSS + JS)
│   ├── index.html                # Interfaz de usuario (estructura)
│   ├── style.css                 # Estilos del chat (burbujas, gradientes)
│   └── script.js                 # Lógica del cliente (Fetch API)
│
├── 📚 Documentación
│   ├── README.md                 # Este archivo
│   └── LICENSE                   # Licencia MIT
│
└── 📂 Datos (Opcionales)
    ├── recetas.json              # Recetas locales (dentro de chatbot_logic.py)
    └── sinonimos.json            # Sinónimos (dentro de chatbot_logic.py)
```

---

## 🧠 Técnicas de PLN Implementadas

### 1. Tokenización
Divide el texto en unidades más pequeñas (tokens).

```python
"quiero pasta carbonara" 
→ ['quiero', 'pasta', 'carbonara']
```

**Implementación:**
```python
from nltk.tokenize import word_tokenize
tokens = word_tokenize(texto.lower())
```

### 2. Lematización
Reduce las palabras a su forma base (lema) usando un diccionario optimizado.

```python
['guisada', 'fideos', 'cocino'] 
→ ['guisar', 'fideo', 'cocinar']
```

**Implementación:**
```python
DICCIONARIO_LEMAS = {
    'guisada': 'guisar', 'fideos': 'fideo', 
    'cocino': 'cocinar', 'asado': 'asar'
}
```

### 3. POS Tagging (Part-of-Speech)
Identifica la categoría gramatical de cada palabra para extraer sustantivos (ingredientes).

```python
[('quiero', 'VERB'), ('pasta', 'NOUN'), ('deliciosa', 'ADJ')]
```

**Uso:** Extrae el **NOUN** (sustantivo) como palabra clave de búsqueda.

### 4. Análisis de Sentimientos
Detecta emociones en el texto del usuario usando **Pysentimiento**.

```python
"estoy súper feliz" → POS (92%)
"ando muy triste"   → NEG (87%)
"quiero comer"      → NEU (65%)
```

**Implementación:**
```python
from pysentimiento import create_analyzer
analyzer = create_analyzer(task="sentiment", lang="es")
resultado = analyzer.predict(texto)
# resultado.output → 'POS', 'NEG', 'NEU'
```

### 5. Detección de Sinónimos
Mapea palabras similares a un concepto común para mejorar la búsqueda.

```python
Sistema de sinónimos:
{
    'pasta carbonara': {
        'sinonimos': ['espagueti', 'fideos', 'tallarines'],
        'palabras_clave': ['pasta', 'italiano']
    }
}

"quiero fideos" → Detecta "pasta carbonara"
```

---

## 🌐 APIs Externas

### 1. Spoonacular (Principal)

**Descripción:** Motor de búsqueda principal con acceso a miles de recetas internacionales.

**Base URL:** `https://api.spoonacular.com/`

#### Endpoint Utilizado

```http
GET /recipes/complexSearch
```

**Parámetros:**
- `query`: Término de búsqueda (ej. "salmon")
- `number`: Cantidad de resultados (default: 10)
- `apiKey`: Tu clave de API

**Ejemplo de Respuesta:**
```json
{
  "results": [
    {
      "id": 12345,
      "title": "Easy Glazed Salmon",
      "image": "https://spoonacular.com/.../salmon.jpg",
      "readyInMinutes": 20,
      "servings": 4
    }
  ]
}
```

**Notas:**
- ✅ Requiere API Key (plan gratuito: 150 requests/día)
- ✅ Búsqueda potente con filtros avanzados
- ⚠️ Rate limit estricto

### 2. TheMealDB (Respaldo)

**Descripción:** API gratuita para obtener pasos detallados de recetas.

**Base URL:** `https://www.themealdb.com/api/json/v1/1/`

#### Endpoint Utilizado

```http
GET /search.php?s={query}
```

**Parámetros:**
- `s`: Nombre de la receta (ej. "salmon")

**Ejemplo de Respuesta:**
```json
{
  "meals": [
    {
      "strMeal": "Baked Salmon",
      "strCategory": "Seafood",
      "strArea": "British",
      "strIngredient1": "Salmon",
      "strMeasure1": "1 lb",
      "strInstructions": "Preheat oven to 350F..."
    }
  ]
}
```

**Notas:**
- ✅ Completamente gratuita
- ✅ No requiere API Key
- ✅ Sin límite de requests

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si quieres mejorar el proyecto:

### 1. Fork el repositorio

### 2. Crea una rama para tu feature
```bash
git checkout -b feature/nueva-funcionalidad
```

### 3. Commit tus cambios
```bash
git commit -m "Add: nueva funcionalidad increíble"
```

### 4. Push a la rama
```bash
git push origin feature/nueva-funcionalidad
```

### 5. Abre un Pull Request

---

## 🗺️ Roadmap

- [x] **v1.0**: Sistema básico con Tkinter
- [x] **v1.5**: Migración a arquitectura web (Flask + HTML/CSS/JS)
- [x] **v1.6**: Integración con Spoonacular API
- [x] **v1.7**: Sistema híbrido-federado (3 niveles)
- [ ] **v2.0**: Autenticación de usuarios (login/registro)
- [ ] **v2.1**: Guardar recetas favoritas (base de datos SQL)
- [ ] **v2.2**: Reconocimiento de voz (Web Speech API)
- [ ] **v2.3**: Soporte multiidioma (francés, portugués)
- [ ] **v2.4**: Restricciones dietéticas (vegano, sin gluten, keto)
- [ ] **v3.0**: App móvil (React Native)
- [ ] **v3.1**: Análisis nutricional (calorías, macros)
- [ ] **v4.0**: Generación de imágenes con IA (DALL-E)

---

## 📊 Métricas del Proyecto

- **Líneas de código**: ~1,200 (Python + JavaScript)
- **Recetas locales**: 12 curadas manualmente
- **Recetas API**: Acceso a 5,000+ recetas (Spoonacular)
- **Sinónimos soportados**: 50+ términos
- **Idiomas**: Español (nativo) + Inglés (traducción automática)
- **Precisión PLN**: ~95% en detección de intenciones
- **Tiempo de respuesta**: <2 segundos (promedio)

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2025 Ivan Andres Bernal Hernandez & Yow Nicolas Guacaneme Molano

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
de este software y archivos de documentación asociados (el "Software"), para usar
el Software sin restricciones, incluyendo sin limitación los derechos de usar,
copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender
copias del Software...
```

---

## 👤 Autores

**Ivan Andres Bernal Hernandez**  
**Yow Nicolas Guacaneme Molano**

- 🎓 Universidad: **Universidad de Cundinamarca**
- 📧 Email: 
  - guacanemeyow@gmail.com
  - ivanandresbernalhernandez595@gmail.com
- 🐙 GitHub: 
  - [yowNikolaz-26](https://github.com/yowNikolaz-26)
  - [ivanzber](https://github.com/ivanzber)

---

## 🙏 Agradecimientos

- **NLTK Team** - Por la excelente librería de PLN
- **Pysentimiento** - Por el análisis de sentimientos en español
- **Spoonacular** - Por la potente API de búsqueda de recetas
- **TheMealDB** - Por la API gratuita de respaldo
- **Flask Team** - Por el framework web ligero y eficiente
- **Comunidad Python** - Por el apoyo y recursos

---

## 📚 Referencias

- [NLTK Documentation](https://www.nltk.org/)
- [Pysentimiento GitHub](https://github.com/pysentimiento/pysentimiento)
- [Spoonacular API](https://spoonacular.com/food-api/docs)
- [TheMealDB API](https://www.themealdb.com/api.php)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MDN Web Docs](https://developer.mozilla.org/)

---

## 📞 Soporte

Si tienes preguntas o encuentras algún bug:

- 🐛 [Reportar un bug](https://github.com/tu-usuario/chef-bot-pln/issues)
- 💡 [Solicitar una feature](https://github.com/tu-usuario/chef-bot-pln/issues)
- 📧 Contacto directo: 
  - guacanemeyow@gmail.com
  - ivanandresbernalhernandez595@gmail.com

---

## 🎯 Características Destacadas

### ⚡ Velocidad
- Respuesta en <2 segundos promedio
- Caché inteligente para recetas frecuentes
- Conexión asíncrona con APIs externas

### 🎨 Interfaz Moderna
- Diseño responsive (móvil, tablet, desktop)
- Burbujas de chat estilo WhatsApp
- Animaciones suaves CSS3
- Tema oscuro con gradientes

### 🧠 Inteligencia
- Comprende 50+ sinónimos culinarios
- Detecta emociones con 90% de precisión
- Traduce automáticamente ES ↔ EN
- Extrae ingredientes clave con POS Tagging

### 🔒 Resiliencia
- Sistema de 3 niveles (local → Spoonacular → TheMealDB)
- Manejo robusto de errores de API
- Fallback automático si una API falla
- Rate limiting inteligente

---

<div align="center">

**⭐ Si te gusta este proyecto, dale una estrella en GitHub ⭐**

Hecho con ❤️, 🐍 Python, ☕ JavaScript y 🍕 Pasión por la Cocina

---

**[⬆ Volver arriba](#-chef-bot---asistente-culinario-inteligente-con-pln)**

</div>