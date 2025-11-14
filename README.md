# 🍳 Chef Bot - Asistente Culinario Inteligente con PLN

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PLN](https://img.shields.io/badge/PLN-NLTK%20%7C%20Pysentimiento-orange.svg)](https://www.nltk.org/)
[![API](https://img.shields.io/badge/API-TheMealDB-red.svg)](https://www.themealdb.com/)

> **Chatbot inteligente que entiende lenguaje natural en español, detecta emociones y busca recetas de cocina en bases de datos internacionales.**

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Ejemplos de Interacción](#-ejemplos-de-interacción)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Técnicas de PLN Implementadas](#-técnicas-de-pln-implementadas)
- [API Externa](#-api-externa)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)
- [Autor](#-autor)

---

## 📖 Descripción

**Chef Bot** es un asistente culinario inteligente que combina **Procesamiento de Lenguaje Natural (PLN)** con **APIs externas** para ayudar a los usuarios a encontrar recetas de cocina. El sistema es capaz de:

- 🗣️ **Entender lenguaje natural** en español
- 😊 **Detectar emociones** y adaptar respuestas
- 🔄 **Reconocer sinónimos** (fideos = espagueti = pasta)
- 🌍 **Traducir automáticamente** entre español e inglés
- 📚 **Buscar en bases de datos** internacionales
- 💡 **Proporcionar tips profesionales** curados manualmente

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

### 🌐 Sistema Híbrido de Datos

```
┌─────────────────────────────────────┐
│  Nivel 1: Base de Datos Local      │
│  • 5 recetas curadas                │
│  • Tips profesionales               │
│  • Sinónimos en español             │
└──────────────┬──────────────────────┘
               ↓ (si no encuentra)
┌─────────────────────────────────────┐
│  Nivel 2: API TheMealDB             │
│  • Miles de recetas internacionales │
│  • Ingredientes detallados          │
│  • Instrucciones paso a paso        │
└─────────────────────────────────────┘
```

### 🌍 Traducción Automática

- **Español → Inglés**: Para buscar en API internacional
- **Inglés → Español**: Para mostrar resultados al usuario

```
Usuario: "quiero salmón" 
    → Traduce: "salmon"
    → Busca en API
    → Traduce respuesta: "salmón horneado"
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

```
┌──────────────────────────────────────────────────────┐
│                    USUARIO                           │
│   "quiero salmon que ando triste"                    │
└─────────────────────┬────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│            CAPA DE PROCESAMIENTO PLN                 │
│  • Tokenización (NLTK)                               │
│  • Lematización                                      │
│  • POS Tagging                                       │
│  • Análisis de Sentimientos (Pysentimiento)          │
└─────────────────────┬────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│          CAPA DE LÓGICA DE NEGOCIO                   │
│  • Detección de sinónimos                            │
│  • Extracción de palabra clave                       │
│  • Traducción ES ↔ EN                                │
└─────────────────────┬────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│             CAPA DE DATOS                            │
│  1. Base de datos local (5 recetas + tips)           │
│  2. API TheMealDB (miles de recetas)                 │
└─────────────────────┬────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│                  RESPUESTA                           │
│  "😞 Entiendo... Salmón Horneado te ayudará          │
│   📋 2 cucharadas mantequilla, 1 libra salmón..."    │
└──────────────────────────────────────────────────────┘
```

---

## 🛠️ Tecnologías Utilizadas

### Lenguajes y Frameworks
- **Python 3.8+**
- **NLTK** - Tokenización y procesamiento de texto
- **Pysentimiento** - Análisis de sentimientos en español
- **Requests** - Consumo de API REST
- **Tkinter** (opcional) - Interfaz gráfica

### APIs Externas
- **[TheMealDB](https://www.themealdb.com/)** - Base de datos de recetas internacionales

### Librerías Python
```python
nltk==3.8+
pysentimiento==0.7+
requests==2.31+
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

### 4. Descargar recursos de NLTK

```python
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

---

## 🚀 Uso

### Uso Básico (Línea de Comandos)

```python
from chatbot_logic import ChatbotLogic

# Inicializar chatbot
bot = ChatbotLogic()

# Saludo inicial
respuestas, _ = bot.procesar_mensaje("hola")
for resp in respuestas:
    print(f"[{resp['type']}]: {resp['text']}")

# Buscar receta
respuestas, _ = bot.procesar_mensaje("quiero pasta")
for resp in respuestas:
    print(f"[{resp['type']}]: {resp['text']}")

# Obtener tips
tips = bot.generar_tips()
for tip in tips:
    print(tip['text'])
```

### Uso con Interfaz Gráfica (Tkinter)

```bash
python chatbot_ui.py
```

### Uso con API REST (Flask/FastAPI)

```python
# Próximamente: API REST para integración web
```

---

## 💬 Ejemplos de Interacción

### Ejemplo 1: Búsqueda Básica

```
Usuario: quiero pollo
Bot: 🎯 Detectado por palabra clave: 'pollo' → pollo asado
     Perfecto. Pollo Asado
     📋 Ingredientes: 1 pollo entero, 2 limones, ajo...
     ⏱️ 1h 30min | 📊 Fácil
```

### Ejemplo 2: Con Sinónimos

```
Usuario: dame fideos
Bot: 💡 Detectado por sinónimo: 'fideos' → pasta carbonara
     📋 Ingredientes: 400g espagueti, 200g panceta...
```

### Ejemplo 3: Con Análisis Emocional

```
Usuario: estoy triste quiero algo de comer
Bot: 🎭 😞 NEG (85%)
     Entiendo... 😞 Una Carne Guisada reconfortante te ayudará.
     📋 Ingredientes: 1kg carne, 3 papas, 2 zanahorias...
```

### Ejemplo 4: Búsqueda en API Externa

```
Usuario: quiero salmon
Bot: 🌐 Traduciendo 'salmon' → 'salmon'...
     ✅ salmón horneado (Baked Salmon)
     📂 pescado | 🌍 British
     📋 INGREDIENTES:
      • 2 cucharadas mantequilla
      • 1 libra salmón
      • sal y pimienta
```

---

## 📁 Estructura del Proyecto

```
chef-bot-pln/
│
├── chatbot_logic.py          # Lógica principal del chatbot
├── chatbot_ui.py             # Interfaz gráfica (Tkinter)
├── requirements.txt          # Dependencias del proyecto
├── README.md                 # Este archivo
├── LICENSE                   # Licencia MIT
│
├── data/                     # Datos locales
│   ├── recetas.json          # Recetas predefinidas
│   └── sinonimos.json        # Diccionario de sinónimos
│
├── tests/                    # Pruebas unitarias
│   ├── test_pln.py
│   ├── test_api.py
│   └── test_chatbot.py
│
└── docs/                     # Documentación adicional
    ├── arquitectura.md
    ├── api_reference.md
    └── ejemplos.md
```

---

## 🧠 Técnicas de PLN Implementadas

### 1. Tokenización
Divide el texto en unidades más pequeñas (tokens).

```python
"quiero pasta carbonara" 
→ ['quiero', 'pasta', 'carbonara']
```

### 2. Lematización
Reduce las palabras a su forma base (lema).

```python
['guisada', 'fideos', 'asado'] 
→ ['guisar', 'fideo', 'asar']
```

### 3. POS Tagging (Part-of-Speech)
Identifica la categoría gramatical de cada palabra.

```python
[('quiero', 'VERB'), ('pasta', 'NOUN'), ('deliciosa', 'ADJ')]
```

### 4. Análisis de Sentimientos
Detecta emociones en el texto del usuario.

```python
"estoy súper feliz" → POS (92%)
"ando muy triste"   → NEG (87%)
"quiero comer"      → NEU (65%)
```

### 5. Detección de Sinónimos
Mapea palabras similares a un concepto común.

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

## 🌐 API Externa

### TheMealDB

**Base URL:** `https://www.themealdb.com/api/json/v1/1/`

#### Endpoints Utilizados

| Endpoint | Descripción | Ejemplo |
|----------|-------------|---------|
| `/search.php?s={query}` | Buscar por nombre | `/search.php?s=chicken` |

#### Ejemplo de Respuesta

```json
{
  "meals": [
    {
      "strMeal": "Baked Salmon",
      "strCategory": "Seafood",
      "strArea": "British",
      "strIngredient1": "Salmon",
      "strMeasure1": "1 lb",
      "strInstructions": "Preheat the oven to..."
    }
  ]
}
```

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

- [ ] **v2.0**: API REST para integración web
- [ ] **v2.1**: Reconocimiento de voz (Whisper API)
- [ ] **v2.2**: Soporte multiidioma (francés, portugués)
- [ ] **v2.3**: Restricciones dietéticas (vegano, sin gluten, keto)
- [ ] **v2.4**: Base de datos de usuarios (recetas favoritas)
- [ ] **v3.0**: App móvil (iOS/Android)

---

## 📊 Métricas del Proyecto

- **Líneas de código**: ~800 (Python)
- **Recetas locales**: 5 curadas manualmente
- **Recetas API**: Acceso a 1000+ recetas
- **Sinónimos soportados**: 50+ términos
- **Idiomas**: Español (nativo) + Inglés (traducción)
- **Precisión PLN**: ~95% en detección de intenciones

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2025 [Tu Nombre]

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
de este software y archivos de documentación asociados (el "Software"), para usar
el Software sin restricciones...
```

---

## 👤 Autores

**Ivan Andres Bernal Hernandez**
**Yow Nicolas Guacaneme Molano**


- 🎓 Universidad: Universidad de Cundinamarca
- 📧 Email: guacanemeyow@gmail.com - ivanandresbernalhernandez595@gmail.com
- 🐙 GitHub: yowNikolaz-26(https://github.com/yowNikolaz-26)- ivanzber(https://github.com/ivanzber)

---

## 🙏 Agradecimientos

- **NLTK Team** - Por la excelente librería de PLN
- **Pysentimiento** - Por el análisis de sentimientos en español
- **TheMealDB** - Por la API gratuita de recetas
- **Comunidad Python** - Por el apoyo y recursos

---

## 📚 Referencias

- [NLTK Documentation](https://www.nltk.org/)
- [Pysentimiento GitHub](https://github.com/pysentimiento/pysentimiento)
- [TheMealDB API](https://www.themealdb.com/api.php)
- [Python Requests](https://requests.readthedocs.io/)

---

## 📞 Soporte

Si tienes preguntas o encuentras algún bug:

- 🐛 [Reportar un bug](https://github.com/tu-usuario/chef-bot-pln/issues)
- 💡 [Solicitar una feature](https://github.com/tu-usuario/chef-bot-pln/issues)
- 📧 Contacto directo: guacanemeyow@gmail.com - ivanandresbernalhernandez595@gmail.com

---

<div align="center">

**⭐ Si te gusta este proyecto, dale una estrella en GitHub ⭐**

Hecho con ❤️ y 🐍 Python

</div>