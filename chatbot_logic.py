# chatbot_logic.py - VERSIÓN CON GOOGLE GEMINI API
import random
import requests
import json
import re
import google.generativeai as genai # ¡Importante!

# --- Bloque de importación de PLN (NLTK y Pysentimiento) ---
try:
    from nltk.tokenize import word_tokenize
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    NLTK_DISPONIBLE = True
except ImportError:
    NLTK_DISPONIBLE = False
    # ... (tu función de fallback de word_tokenize) ...
    def word_tokenize(text):
        import string
        text = text.lower()
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        return text.split()

# --- Ya no necesitamos Transformers ---
# try:
#     from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
#     import torch
#     TRANSFORMERS_DISPONIBLE = True
#     print("✅ Transformers cargado")
# except ImportError:
#     TRANSFORMERS_DISPONIBLE = False
#     print("⚠️ Transformers no disponible")
# --- FIN ---

try:
    from pysentimiento import create_analyzer
    SENTIMIENTOS_DISPONIBLE = True
    print("✅ Pysentimiento cargado")
except ImportError:
    SENTIMIENTOS_DISPONIBLE = False
    print("⚠️ Pysentimiento no disponible")


class ChatbotLogic:
    
    def __init__(self):
        self.saludado = False
        self.ultimo_sentimiento = "NEU"
        self.modelo_activo = "Ninguno"
        self.ultima_receta = None
        
        # Cargar modelos y analizador
        self.cargar_modelo_api()
        
        if SENTIMIENTOS_DISPONIBLE:
            try:
                self.analyzer = create_analyzer(task="sentiment", lang="es")
                print("✅ Analizador de sentimientos listo")
            except:
                self.analyzer = None
        else:
            self.analyzer = None
            
        # Sistema de sinónimos
        self.sinonimos = {
            'carne guisada': {
                'sinonimos': ['estofado', 'guiso', 'guisado', 'carne estofada', 'cocido'],
                'palabras_clave': ['carne', 'res', 'vaca', 'ternera']
            },
            'pasta carbonara': {
                'sinonimos': ['espagueti', 'fideos', 'tallarines', 'pasta', 'carbonara', 'spaghetti'],
                'palabras_clave': ['pasta', 'italiano', 'espagueti']
            },
            'pollo asado': {
                'sinonimos': ['pollo', 'rostizado', 'gallina', 'ave', 'pollo horneado', 'chicken'],
                'palabras_clave': ['pollo', 'ave', 'asar', 'hornear']
            },
            'tacos': {
                'sinonimos': ['taco', 'taquitos', 'mexicanos', 'tortilla'],
                'palabras_clave': ['tacos', 'mexicano', 'tortilla']
            },
            'arepas': {
                'sinonimos': ['arepa', 'arepitas'],
                'palabras_clave': ['arepa', 'maíz', 'colombia', 'venezolana']
            }
        }
        
        # Recetas 
        self.recetas = {
            'pasta carbonara': {
                'nombre': 'Pasta Carbonara',
                'ingredientes': ['400g espagueti', '200g panceta', '4 yemas', '100g queso pecorino'],
                'tiempo': '20 min',
                'dificultad': 'Media'
            },
            'pollo asado': {
                'nombre': 'Pollo Asado',
                'ingredientes': ['1 pollo entero', '2 limones', 'ajo', 'romero', 'mantequilla'],
                'tiempo': '1h 30min',
                'dificultad': 'Fácil'
            },
            'carne guisada': {
                'nombre': 'Carne Guisada',
                'ingredientes': ['1kg carne', '3 papas', '2 zanahorias', 'cebolla', 'tomate'],
                'tiempo': '2h',
                'dificultad': 'Media'
            },
            'tacos': {
                'nombre': 'Tacos al Pastor',
                'ingredientes': ['1kg cerdo', 'piña', 'chile', 'tortillas', 'cilantro'],
                'tiempo': '3h',
                'dificultad': 'Media'
            },
            'arepas': {
                'nombre': 'Arepas Colombianas',
                'ingredientes': ['2 tazas harina de maíz', 'agua', 'sal', 'queso', 'mantequilla'],
                'tiempo': '30 min',
                'dificultad': 'Fácil'
            }
        }

    def cargar_modelo_api(self):
        """Configura la API de Gemini"""
        try:
        
            API_KEY = "AIzaSyDbAU04RE9ZSfUMjABHDW4qs7ZePPU2jTA"
                    
            if API_KEY == "PEGA_AQUI_TU_API_KEY_DE_GOOGLE_AI_STUDIO":
                print("="*50)
                print("⚠️ ADVERTENCIA: Debes pegar tu API Key en 'chatbot_logic.py'")
                print("⚠️ Ve a https://aistudio.google.com/ para obtener una.")
                print("="*50)
                self.modelo_cargado = False
                self.modelo_activo = "Ninguno (Falta API Key)"
                return

            genai.configure(api_key=API_KEY)
                    
            generation_config = {
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 512,
            }
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
                    
            self.model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                                generation_config=generation_config,
                                                safety_settings=safety_settings)
                    
            self.modelo_activo = "Gemini 1.0 Pro (API)"
            self.modelo_cargado = True
            print(f"✅ {self.modelo_activo} cargado correctamente")

        except Exception as e:
            print(f"❌ Error configurando la API de Gemini: {e}")
            self.modelo_cargado = False
            self.modelo_activo = "Ninguno"   

    def generar_texto(self, prompt, max_tokens=512): # max_tokens ya no es tan relevante
            """Genera texto con la API de Gemini"""
            if not self.modelo_cargado:
                return "⚠️ No hay modelo de IA disponible. Revisa la API Key."
            
            try:
                # Damos un "rol" al bot para mejores respuestas
                prompt_completo = (
                    "Eres 'Chef Bot', un asistente de cocina experto y amable. "
                    "Responde a la siguiente petición de forma clara, concisa y útil.\n\n"
                    f"PETICIÓN: {prompt}"
                )
                
                response = self.model.generate_content(prompt_completo)
                
                # Limpiamos la respuesta de Markdown (asteriscos)
                respuesta_limpia = response.text.replace('*', '')
                
                return respuesta_limpia
            except Exception as e:
                # Captura errores comunes de la API (ej. bloqueo de seguridad)
                print(f"❌ Error en la API de Gemini: {e}")
                return (
                    "⚠️ Lo siento, no puedo generar una respuesta para esa petición. "
                    "Es posible que haya sido bloqueada por políticas de seguridad."
                )

    def tokenizar(self, texto):
        return word_tokenize(texto.lower())

    def lematizar_simple(self, tokens):
        lemas_dict = {
            'cocino': 'cocinar', 'cocinas': 'cocinar', 'cocinando': 'cocinar',
            'guisada': 'guisar', 'guisado': 'guisar', 'guiso': 'guisar',
            'asado': 'asar', 'rostizado': 'rostizar', 'horneado': 'hornear',
            'fideos': 'fideo', 'espaguetis': 'espagueti', 'tallarines': 'tallarín',
            'tacos': 'taco', 'taquitos': 'taco',
            'arepas': 'arepa', 'arepitas': 'arepa',
            'estoy': 'estar', 'quiero': 'querer', 'dame': 'dar'
        }
        return [lemas_dict.get(token, token) for token in tokens]

    def pos_tagging_simple(self, tokens):
        pos_dict = {
            'el': 'DET', 'la': 'DET', 'los': 'DET', 'las': 'DET',
            'cocinar': 'VERB', 'guisar': 'VERB', 'preparar': 'VERB', 'querer': 'VERB',
            'carne': 'NOUN', 'pasta': 'NOUN', 'pollo': 'NOUN', 'taco': 'NOUN', 
            'arepa': 'NOUN', 'fideo': 'NOUN',
            'delicioso': 'ADJ', 'rico': 'ADJ', 'bueno': 'ADJ',
            'yo': 'PRON', 'tú': 'PRON'
        }
        return [(token, pos_dict.get(token, 'NOUN')) for token in tokens]

    def extraer_comida(self, pos_tags):
        """Extrae sustantivos que podrían ser comida"""
        comida_tokens = [token for token, tag in pos_tags if tag == 'NOUN']
        if comida_tokens:
            return " ".join(comida_tokens)
        return ""

    def detectar_receta(self, mensaje):
        mensaje_lower = mensaje.lower()
        for nombre_receta, info_sinonimos in self.sinonimos.items():
            if nombre_receta in mensaje_lower:
                return nombre_receta, "nombre exacto", nombre_receta
            for sinonimo in info_sinonimos['sinonimos']:
                if sinonimo in mensaje_lower:
                    return nombre_receta, "sinónimo", sinonimo
            for palabra in info_sinonimos['palabras_clave']:
                if palabra in mensaje_lower:
                    return nombre_receta, "palabra clave", palabra
        return None, None, None

    def analizar_sentimiento(self, texto):
        if not self.analyzer:
            return None, 0.5
        try:
            resultado = self.analyzer.predict(texto)
            return resultado.output, resultado.probas[resultado.output]
        except:
            return None, 0.5

    def _crear_respuesta(self, texto, tipo="bot"):
        """Helper para formatear respuestas"""
        return {"type": tipo, "text": texto.strip()}

    def mostrar_bienvenida(self):
        """Devuelve mensajes de bienvenida"""
        respuestas = []
        respuestas.append(self._crear_respuesta(f"¡Bienvenido! Usando {self.modelo_activo}.", "bot"))
        respuestas.append(self._crear_respuesta("Salúdame con 'hola' para comenzar.", "warning"))
        respuestas.append(self._crear_respuesta(
            "🧠 PLN activo:\n • Tokenización\n • Lematización\n • POS Tagging\n • Sentimientos", "info"))
        
        if self.modelo_cargado:
            respuestas.append(self._crear_respuesta(
                f"✨ {self.modelo_activo} puede:\n • Generar descripciones\n • Crear pasos\n • Dar tips", "info"))
        else:
            respuestas.append(self._crear_respuesta("⚠️ IA no disponible.", "warning"))
        
        return respuestas

    def habilitar_funcionalidades(self):
        """Devuelve lista de recetas al saludar"""
        self.saludado = True
        respuestas = []
        respuestas.append(self._crear_respuesta("¡Hola! ¡Bienvenido! 😊", "bot"))
        respuestas.append(self._crear_respuesta("🎯 RECETAS CON SINÓNIMOS:", "info"))
        respuestas.append(self._crear_respuesta(
            "🥩 Carne → estofado, guiso, cocido\n"
            "🍝 Pasta → espagueti, fideos, tallarines\n"
            "🐔 Pollo → rostizado, ave, gallina\n"
            "🌮 Tacos → taquitos, mexicano\n"
            "🌽 Arepas → arepa, maíz", "sinonimo"))
        return respuestas
        
    def analizar_pln(self, mensaje):
        """Analiza mensaje con técnicas PLN"""
        tokens = self.tokenizar(mensaje)
        lemas = self.lematizar_simple(tokens)
        pos_tags = self.pos_tagging_simple(lemas)
        
        pln_info = (f"📊 PLN: Tokens: {tokens[:4]}... | "
                    f"Lemas: {lemas[:4]}... | "
                    f"POS: {pos_tags[:3]}...")
        
        return pln_info, tokens, lemas, pos_tags

    def buscar_receta_externa(self, consulta):
        """Busca en API externa con fallback a IA"""
        respuestas = []
        respuestas.append(self._crear_respuesta(
            f"🌐 Buscando '{consulta}' en TheMealDB...", "info"))
        
        try:
            url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={consulta}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if not data or not data.get('meals'):
                respuestas.append(self._crear_respuesta(
                    f"⚠️ No encontré '{consulta}' en la API.", "warning"))
                respuestas.extend(self.fallback_ia_generica(consulta))
                return respuestas

            receta = data['meals'][0]
            nombre = receta.get('strMeal', 'Receta encontrada')
            cat = receta.get('strCategory', 'N/A')
            
            respuestas.append(self._crear_respuesta(
                f"✅ Encontré en API:\n🔗 {nombre}\nCategoría: {cat}", "ia"))
            
            ingredientes = []
            for i in range(1, 6):
                ing = receta.get(f'strIngredient{i}')
                if ing and ing.strip():
                    ingredientes.append(f" • {ing}")
            
            if ingredientes:
                respuestas.append(self._crear_respuesta("\n".join(ingredientes), "ia"))

        except requests.exceptions.RequestException as e:
            respuestas.append(self._crear_respuesta(
                f"⚠️ Error conectando API: {str(e)[:50]}...", "warning"))
            respuestas.extend(self.fallback_ia_generica(consulta))
            
        return respuestas

    def fallback_ia_generica(self, consulta):
        """Usa IA cuando no hay receta en base de datos ni API"""
        if not self.modelo_cargado:
            return [self._crear_respuesta("⚠️ IA no disponible.", "warning")]
        
        respuestas = []
        respuestas.append(self._crear_respuesta(
            f"🤖 Usando {self.modelo_activo} para generar receta...", "info"))
        
        prompt = f"Escribe una receta simple y corta para preparar {consulta}, incluyendo ingredientes principales y 3 pasos básicos."
        
        resultado = self.generar_texto(prompt, 250)
        
        respuestas.append(self._crear_respuesta(
            f"📖 Receta generada por IA:\n\n{resultado}", "ia"))
        
        return respuestas

    # --- Funciones de botones ---

    def generar_descripcion(self):
        if not self.ultima_receta:
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        info = self.recetas[self.ultima_receta]
        prompt = f"Describe detalladamente el plato {info['nombre']}, su origen, características y por qué es especial."
        
        resultado = self.generar_texto(prompt, 200)
        
        return [self._crear_respuesta(
            f"📖 DESCRIPCIÓN ({self.modelo_activo}):\n\n{resultado}", "ia")]

    def generar_pasos(self):
        if not self.ultima_receta:
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        info = self.recetas[self.ultima_receta]
        prompt = f"Escribe paso a paso cómo preparar {info['nombre']}, numerando cada paso del 1 al 5."
        
        resultado = self.generar_texto(prompt, 250)
        
        return [self._crear_respuesta(
            f"📝 PASOS ({self.modelo_activo}):\n\n{resultado}", "ia")]

    def generar_tips(self):
        if not self.ultima_receta:
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        info = self.recetas[self.ultima_receta]
        prompt = f"Dame 3 consejos profesionales de chef para preparar perfectamente {info['nombre']}."
        
        resultado = self.generar_texto(prompt, 200)
        
        return [self._crear_respuesta(
            f"💡 TIPS DEL CHEF ({self.modelo_activo}):\n\n{resultado}", "ia")]

    def generar_variaciones(self):
        if not self.ultima_receta:
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        info = self.recetas[self.ultima_receta]
        prompt = f"Sugiere 2 variaciones creativas diferentes de {info['nombre']}, explicando qué cambiar en cada una."
        
        resultado = self.generar_texto(prompt, 200)
        
        return [self._crear_respuesta(
            f"🎨 VARIACIONES ({self.modelo_activo}):\n\n{resultado}", "ia")]

    def _limpiar_respuesta_gpt2(self, prompt, resultado):
        """
        Gemini no incluye el prompt en su respuesta,
        así que esta función ya no necesita limpiarlo.
        Solo devolvemos el resultado.
        """
        return resultado.strip()

    def procesar_mensaje(self, mensaje):
        respuestas = []
        
        if not self.saludado:
            if any(saludo in mensaje.lower() for saludo in ['hola', 'hi', 'hey', 'buenas']):
                respuestas.extend(self.habilitar_funcionalidades())
                return respuestas, self.saludado
            else:
                respuestas.append(self._crear_respuesta("⚠️ Salúdame con 'hola' primero.", "warning"))
                return respuestas, self.saludado

        # Análisis PLN
        pln_info, tokens, lemas, pos_tags = self.analizar_pln(mensaje)
        
        # Análisis Sentimiento
        sent, conf = None, 0.5
        if self.analyzer:
            sent, conf = self.analizar_sentimiento(mensaje)
            if sent:
                self.ultimo_sentimiento = sent
                emojis = {"POS": "😊", "NEG": "😞", "NEU": "😐"}
                respuestas.append(self._crear_respuesta(f"🎭 {emojis.get(sent, '😐')} {sent} ({conf:.0%})", "sentiment"))
        
        receta, tipo, termino = self.detectar_receta(mensaje)
        
        # FLUJO 1: RECETA INTERNA
        if receta:
            self.ultima_receta = receta # Guardamos la última receta
            info = self.recetas[receta]
            
            if tipo and termino:
                respuestas.append(self._crear_respuesta(f"💡 {tipo}: '{termino}' → {receta}", "sinonimo"))
            
            
            # --- CAMBIO 2: Mostrar todos los ingredientes ---
            # Unimos la lista de ingredientes con saltos de línea y una viñeta
            ingredientes_formateados = '\n • '.join(info['ingredientes'])
            
            if sent == "POS":
                respuestas.append(self._crear_respuesta(f"¡Buena energía! 😊 {info['nombre']} será perfecta.\n\n"
                                                       # Usamos la nueva variable formateada
                                                       f"📋 Ingredientes:\n • {ingredientes_formateados}\n\n"
                                                       f"⏱️ {info['tiempo']} | 📊 {info['dificultad']}\n\n"
                                                       "💡 Usa los botones para más con IA", "bot"))
            else:
                 respuestas.append(self._crear_respuesta(f"Perfecto. {info['nombre']}.\n\n"
                                                       # Usamos la nueva variable formateada
                                                       f"📋 Ingredientes:\n • {ingredientes_formateados}\n\n"
                                                       f"⏱️ {info['tiempo']} | 📊 {info['dificultad']}\n\n"
                                                       "💡 Usa los botones para más con IA", "bot"))
            # --- FIN CAMBIO 2 ---

        # FLUJO 2: PREGUNTA GENERAL (IA)
        elif '?' in mensaje and self.modelo_cargado:
            respuestas.append(self._crear_respuesta(f"🤖 {self.modelo_activo} pensando...", "info"))
            # Usamos el helper de limpieza de prompt que hicimos antes
            prompt = f"Responde a esta pregunta sobre cocina: {mensaje}"
            resultado_bruto = self.generar_texto(prompt, 150)
            resultado = self._limpiar_respuesta_gpt2(prompt, resultado_bruto)
            
            respuestas.append(self._crear_respuesta(resultado, "ia"))
        
        # FLUJO 3: BÚSQUEDA EXTERNA (API + FALLBACK IA)
        else:
            consulta_comida = self.extraer_comida(pos_tags)
            if not consulta_comida:
                consulta_comida = mensaje
                
            respuestas.append(self._crear_respuesta(f"No tengo '{consulta_comida}' en mis recetas.", "bot"))
            respuestas.extend(self.buscar_receta_externa(consulta_comida))

        return respuestas, self.saludado