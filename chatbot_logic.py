# chatbot_logic.py - VERSIÓN OPTIMIZADA (Traducción + PLN + Sentimientos + GPT2 Mejorado)
import random
import requests
import json
import re

# --- Importar traducción ---
try:
    from deep_translator import GoogleTranslator
    DEEP_TRANSLATOR_DISPONIBLE = True
    print("✅ Deep Translator (para traducir) cargado")
except ImportError:
    DEEP_TRANSLATOR_DISPONIBLE = False
    print("⚠️ deep-translator no está instalado. Las recetas saldrán en inglés.")
    print("⚠️ Para arreglarlo, corre: python -m pip install deep-translator")

# --- Importaciones PLN ---
try:
    from nltk.tokenize import word_tokenize
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    NLTK_DISPONIBLE = True
except ImportError:
    NLTK_DISPONIBLE = False
    def word_tokenize(text):
        import string
        text = text.lower()
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        return text.split()

try:
    from pysentimiento import create_analyzer
    SENTIMIENTOS_DISPONIBLE = True
    print("✅ Pysentimiento cargado")
except ImportError:
    SENTIMIENTOS_DISPONIBLE = False
    print("⚠️ Pysentimiento no disponible")

# --- Importación GPT2 (Backup) ---
try:
    from transformers import pipeline
    TRANSFORMERS_DISPONIBLE = True
    print("✅ Transformers disponible (GPT2 como backup)")
except ImportError:
    TRANSFORMERS_DISPONIBLE = False
    print("⚠️ Transformers no disponible")


class ChatbotLogic:
    
    def __init__(self):
        self.saludado = False
        self.ultimo_sentimiento = "NEU"
        self.ultima_receta = None
        
        self.modelo_activo = "TheMealDB API + GPT2 Backup"
        self.api_disponible = True
        print(f"✅ {self.modelo_activo} lista")
        
        # Crear el objeto traductor
        if DEEP_TRANSLATOR_DISPONIBLE:
            self.translator = GoogleTranslator(source='en', target='es')
        else:
            self.translator = None
        
        # Cargar GPT2 como backup con configuración optimizada
        self.gpt2_cargado = True
        if TRANSFORMERS_DISPONIBLE:
            try:
                print("🔄 Cargando GPT2 como backup...")
                self.generador = pipeline(
                    'text-generation', 
                    model='datificate/gpt2-small-spanish',
                    device=-1
                )
                self.gpt2_cargado = True
                print("✅ GPT2 cargado como backup")
            except Exception as e:
                print(f"⚠️ GPT2 no disponible: {e}")
                self.generador = None
        
        # Sentimientos
        if SENTIMIENTOS_DISPONIBLE:
            try:
                self.analyzer = create_analyzer(task="sentiment", lang="es")
                print("✅ Analizador de sentimientos listo")
            except:
                self.analyzer = None
        else:
            self.analyzer = None
            
        # Sinónimos expandidos
        self.sinonimos = {
            'carne guisada': {
                'sinonimos': ['estofado', 'guiso', 'guisado', 'carne estofada', 'cocido', 'beef stew','carnecita'],
                'palabras_clave': ['carne', 'res', 'vaca', 'beef']
            },
            'pasta carbonara': {
                'sinonimos': ['espagueti', 'fideos', 'tallarines', 'pasta', 'carbonara', 'spaghetti'],
                'palabras_clave': ['pasta', 'italiano', 'espagueti']
            },
            'pollo asado': {
                'sinonimos': ['pollo', 'rostizado', 'gallina', 'ave', 'chicken', 'roast chicken','pollito'],
                'palabras_clave': ['pollo', 'ave', 'chicken']
            },
            'tacos': {
                'sinonimos': ['taco', 'taquitos', 'mexicanos'],
                'palabras_clave': ['tacos', 'mexicano', 'tortilla']
            },
            'arepas': {
                'sinonimos': ['arepa', 'arepitas'],
                'palabras_clave': ['arepa', 'maíz', 'colombia']
            },
            'arroz con pollo': {
                'sinonimos': ['arroz', 'rice', 'chicken rice'],
                'palabras_clave': ['arroz', 'rice', 'pollo']
            },
            'sopa de tomate': {
                'sinonimos': ['sopa', 'soup', 'tomate', 'tomato'],
                'palabras_clave': ['sopa', 'soup', 'tomate']
            },
            'pizza': {
                'sinonimos': ['pizza', 'pizzas'],
                'palabras_clave': ['pizza', 'italiano', 'masa']
            },
            'hamburguesa': {
                'sinonimos': ['burger', 'hamburguer', 'hamburguesas'],
                'palabras_clave': ['hamburguesa', 'burger', 'carne']
            },
            'ensalada cesar': {
                'sinonimos': ['ensalada', 'salad', 'cesar', 'caesar'],
                'palabras_clave': ['ensalada', 'salad', 'lechuga']
            },
            'paella': {
                'sinonimos': ['paella', 'arroz español'],
                'palabras_clave': ['paella', 'español', 'arroz']
            },
            'lasaña': {
                'sinonimos': ['lasagna', 'lasaña', 'lasagne'],
                'palabras_clave': ['lasaña', 'pasta', 'italiano']
            }
        }
        
        # Recetas internas con tips
        self.recetas = {
            'pasta carbonara': {
                'nombre': 'Pasta Carbonara',
                'busqueda_api': 'carbonara',
                'ingredientes': ['400g espagueti', '200g panceta', '4 yemas'],
                'tiempo': '20 min',
                'dificultad': 'Media',
                'tips': [
                    '• NO uses crema, solo huevos y queso pecorino',
                    '• Retira del fuego antes de agregar los huevos',
                    '• Usa agua de cocción para cremosidad',
                    '• El guanciale es mejor que la panceta'
                ]
            },
            'pollo asado': {
                'nombre': 'Pollo Asado',
                'busqueda_api': 'roast chicken',
                'ingredientes': ['1 pollo entero', '2 limones', 'ajo'],
                'tiempo': '1h 30min',
                'dificultad': 'Fácil',
                'tips': [
                    '• Seca bien el pollo antes de hornear',
                    '• Unta mantequilla bajo la piel',
                    '• Hornea a 200°C los primeros 20 minutos',
                    '• Baña con sus jugos cada 20 minutos'
                ]
            },
            'carne guisada': {
                'nombre': 'Carne Guisada',
                'busqueda_api': 'beef stew',
                'ingredientes': ['1kg carne', '3 papas', '2 zanahorias'],
                'tiempo': '2h',
                'dificultad': 'Media',
                'tips': [
                    '• Dora la carne primero para sellar jugos',
                    '• Cocina a fuego lento mínimo 1.5 horas',
                    '• Agrega las papas al final (último 30 min)',
                    '• Un chorrito de vino tinto mejora el sabor'
                ]
            },
            'tacos': {
                'nombre': 'Tacos al Pastor',
                'busqueda_api': 'tacos',
                'ingredientes': ['1kg cerdo', 'piña', 'chile'],
                'tiempo': '3h',
                'dificultad': 'Media',
                'tips': [
                    '• Marina la carne al menos 2 horas',
                    '• Asa con piña para el sabor tradicional',
                    '• Usa tortillas de maíz, no de harina',
                    '• Sirve con cebolla y cilantro fresco'
                ]
            },
            'arepas': {
                'nombre': 'Arepas Colombianas',
                'busqueda_api': 'arepa',
                'ingredientes': ['2 tazas harina de maíz', 'agua', 'sal'],
                'tiempo': '30 min',
                'dificultad': 'Fácil',
                'tips': [
                    '• La masa debe quedar suave, no pegajosa',
                    '• Agrega sal y un poco de mantequilla',
                    '• Cocina a fuego medio para que doren',
                    '• Rellénalas con queso, carne o aguacate'
                ]
            },
            'arroz con pollo': {
                'nombre': 'Arroz con Pollo',
                'busqueda_api': 'chicken rice',
                'ingredientes': ['2 tazas arroz', '4 muslos de pollo', 'caldo', 'azafrán'],
                'tiempo': '45 min',
                'dificultad': 'Media',
                'tips': [
                    '• Dora el pollo antes de agregar el arroz',
                    '• Usa caldo de pollo, no agua',
                    '• El azafrán da el color dorado característico',
                    '• Deja reposar 5 min antes de servir'
                ]
            },
            'sopa de tomate': {
                'nombre': 'Sopa de Tomate',
                'busqueda_api': 'tomato soup',
                'ingredientes': ['1kg tomates', 'cebolla', 'ajo', 'albahaca'],
                'tiempo': '35 min',
                'dificultad': 'Fácil',
                'tips': [
                    '• Usa tomates maduros para mejor sabor',
                    '• Sofríe bien la cebolla y el ajo',
                    '• Licúa hasta textura cremosa',
                    '• Sirve con crema y pan tostado'
                ]
            },
            'pizza': {
                'nombre': 'Pizza Casera',
                'busqueda_api': 'pizza',
                'ingredientes': ['500g harina', 'levadura', 'tomate', 'mozzarella'],
                'tiempo': '2h',
                'dificultad': 'Media',
                'tips': [
                    '• Deja fermentar la masa mínimo 1 hora',
                    '• Hornea a máxima temperatura (250°C+)',
                    '• No sobrecargues de ingredientes',
                    '• Usa una piedra para pizza si es posible'
                ]
            },
            'hamburguesa': {
                'nombre': 'Hamburguesa Casera',
                'busqueda_api': 'burger',
                'ingredientes': ['500g carne molida', 'pan', 'lechuga', 'tomate'],
                'tiempo': '25 min',
                'dificultad': 'Fácil',
                'tips': [
                    '• Usa carne con 20% de grasa',
                    '• No presiones la carne al cocinar',
                    '• Tuesta el pan antes de armar',
                    '• Sazona generosamente con sal y pimienta'
                ]
            },
            'ensalada cesar': {
                'nombre': 'Ensalada César',
                'busqueda_api': 'caesar salad',
                'ingredientes': ['lechuga romana', 'pollo', 'parmesano', 'crutones'],
                'tiempo': '20 min',
                'dificultad': 'Fácil',
                'tips': [
                    '• Lava y seca bien la lechuga',
                    '• Prepara la salsa César casera',
                    '• Usa parmesano recién rallado',
                    '• Sirve inmediatamente para que no se marchite'
                ]
            },
            'paella': {
                'nombre': 'Paella Valenciana',
                'busqueda_api': 'paella',
                'ingredientes': ['arroz bomba', 'pollo', 'conejo', 'judías', 'azafrán'],
                'tiempo': '1h',
                'dificultad': 'Difícil',
                'tips': [
                    '• Usa una paellera auténtica',
                    '• El socarrat (arroz tostado) es clave',
                    '• No remuevas el arroz después de agregarlo',
                    '• Usa azafrán real, no colorante'
                ]
            },
            'lasaña': {
                'nombre': 'Lasaña Boloñesa',
                'busqueda_api': 'lasagna',
                'ingredientes': ['pasta lasaña', 'carne molida', 'bechamel', 'queso'],
                'tiempo': '1h 30min',
                'dificultad': 'Media',
                'tips': [
                    '• Cocina la boloñesa mínimo 2 horas',
                    '• Alterna capas: pasta, boloñesa, bechamel',
                    '• Termina con bechamel y queso abundante',
                    '• Deja reposar 10 min antes de cortar'
                ]
            }
        }

    # --- Función para traducir ---
    def _traducir(self, texto):
        """Traduce un texto si el traductor está disponible"""
        if self.translator and texto:
            try:
                return self.translator.translate(texto)
            except Exception as e:
                print(f"⚠️ Error de traducción: {e}")
                return f"[Inglés] {texto}"
        return texto

    # --- PLN (Funciones mejoradas) ---
    def tokenizar(self, texto):
        return word_tokenize(texto.lower())

    def lematizar_simple(self, tokens):
        lemas_dict = {
            'cocino': 'cocinar', 'guisada': 'guisar', 'fideos': 'fideo',
            'tacos': 'taco', 'arepas': 'arepa', 'quiero': 'querer',
            'dame': 'dar', 'estoy': 'estar',
            'das': 'dar', 'doy': 'dar', 'hago': 'hacer', 'haces': 'hacer',
            'soy': 'ser', 'eres': 'ser', 'es': 'ser',
            'necesito': 'necesitar', 'busco': 'buscar'
        }
        return [lemas_dict.get(token, token) for token in tokens]

    def pos_tagging_simple(self, tokens):
        pos_dict = {
            # Verbos
            'cocinar': 'VERB', 'guisar': 'VERB', 'preparar': 'VERB', 'querer': 'VERB',
            'dar': 'VERB', 'hacer': 'VERB', 'tener': 'VERB', 'ser': 'VERB', 
            'estar': 'VERB', 'buscar': 'VERB', 'necesitar': 'VERB', 'comer': 'VERB',
            
            # Sustantivos (Comida)
            'carne': 'NOUN', 'pasta': 'NOUN', 'pollo': 'NOUN', 'taco': 'NOUN', 
            'arepa': 'NOUN', 'fideo': 'NOUN', 'pescado': 'NOUN', 'arroz': 'NOUN',
            'sopa': 'NOUN', 'ensalada': 'NOUN', 'pizza': 'NOUN', 'hamburguesa': 'NOUN',
            'tomate': 'NOUN', 'burger': 'NOUN', 'salad': 'NOUN', 'paella': 'NOUN',
            'lasaña': 'NOUN', 'lasagna': 'NOUN', 'rice': 'NOUN', 'soup': 'NOUN',
            
            # Pronombres
            'me': 'PRON', 'te': 'PRON', 'se': 'PRON', 'yo': 'PRON', 'tu': 'PRON', 'él': 'PRON',
            
            # Determinantes
            'un': 'DET', 'una': 'DET', 'el': 'DET', 'la': 'DET', 'los': 'DET', 'las': 'DET',
            
            # Preposiciones
            'de': 'PREP', 'con': 'PREP', 'para': 'PREP', 'por': 'PREP', 'en': 'PREP', 'a': 'PREP',
            
            # Conjunciones y Adverbios
            'y': 'CONJ', 'o': 'CONJ', 'no': 'ADV', 'como': 'ADV', 'qué': 'PRON'
        }
        return [(token, pos_dict.get(token, 'NOUN')) for token in tokens]

    def extraer_comida(self, pos_tags):
        comida_tokens = [token for token, tag in pos_tags if tag == 'NOUN']
        return " ".join(comida_tokens) if comida_tokens else ""

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

    # --- Helpers ---
    def _crear_respuesta(self, texto, tipo="bot"):
        return {"type": tipo, "text": texto.strip()}

    def mostrar_bienvenida(self):
        respuestas = []
        respuestas.append(self._crear_respuesta(
            f"¡Bienvenido! Usando {self.modelo_activo}.", "bot"))
        respuestas.append(self._crear_respuesta(
            "Salúdame con 'hola' para comenzar.", "warning"))
        respuestas.append(self._crear_respuesta(
            "🧠 PLN activo:\n • Tokenización\n • Lematización\n • POS Tagging\n • Sentimientos", "info"))
        respuestas.append(self._crear_respuesta(
            "✨ Puedo:\n • Buscar recetas en TheMealDB\n • Mostrar ingredientes y pasos\n • Generar descripciones con IA", "info"))
        return respuestas

    def habilitar_funcionalidades(self):
        self.saludado = True
        respuestas = []
        respuestas.append(self._crear_respuesta("¡Hola! ¡Bienvenido! 😊", "bot"))
        respuestas.append(self._crear_respuesta("🎯 RECETAS CON SINÓNIMOS:", "info"))
        respuestas.append(self._crear_respuesta(
            "🥩 Carne → estofado, guiso, cocido\n"
            "🍝 Pasta → espagueti, fideos, carbonara\n"
            "🍗 Pollo → rostizado, ave, chicken\n"
            "🌮 Tacos → taquitos, mexicano\n"
            "🌽 Arepas → arepa, maíz\n"
            "🍚 Arroz → rice, arroz con pollo\n"
            "🍲 Sopa → soup, tomate, caldo\n"
            "🍕 Pizza → italiana, masa, mozzarella\n"
            "🍔 Hamburguesa → burger, carne molida\n"
            "🥗 Ensalada → salad, cesar, lechuga\n"
            "🥘 Paella → española, arroz, azafrán\n"
            "🍝 Lasaña → lasagna, pasta, italiana", "sinonimo"))
        return respuestas
        
    def analizar_pln(self, mensaje):
        tokens = self.tokenizar(mensaje)
        lemas = self.lematizar_simple(tokens)
        pos_tags = self.pos_tagging_simple(lemas)
        return tokens, lemas, pos_tags

    # --- API TheMealDB (Con Traducción) ---
    def traducir_a_ingles(self, texto_es):
        ignorar = ['dar', 'dame', 'quiero', 'preparar', 'hacer', 'cocinar', 'buscar', 'necesito', 'querer', 'como', 'de', 'un', 'una', 'el', 'la', 'los', 'las', 'para', 'con', 'comer', 'por', 'favor', 'hazme', 'haz','prepara', 'enséñame', 'muéstrame', 'tú', 'yo', 'me', 'te', 'se']
        traducciones = {
            'pollo': 'chicken', 'carne': 'beef', 'res': 'beef', 'cerdo': 'pork', 
            'pescado': 'fish', 'camarones': 'shrimp', 'arroz': 'rice', 'pasta': 'pasta', 
            'sopa': 'soup', 'ensalada': 'salad', 'pizza': 'pizza', 'hamburguesa': 'burger', 
            'tacos': 'tacos', 'sandwich': 'sandwich', 'pan': 'bread', 'pastel': 'cake', 
            'galletas': 'cookies', 'helado': 'ice cream', 'tarta': 'pie', 'guisado': 'stew', 
            'estofado': 'stew', 'asado': 'roast', 'frito': 'fried', 'horneado': 'baked', 
            'a la parrilla': 'grilled', 'postre': 'dessert', 'dulce': 'sweet', 
            'chocolate': 'chocolate', 'cafe': 'coffee', 'café': 'coffee', 'te': 'tea', 
            'té': 'tea', 'jugo': 'juice', 'agua': 'water', 'desayuno': 'breakfast', 
            'almuerzo': 'lunch', 'cena': 'dinner', 'rapido': 'quick', 'rápido': 'quick', 
            'facil': 'easy', 'fácil': 'easy', 'tomate': 'tomato', 'cesar': 'caesar',
            'paella': 'paella', 'lasaña': 'lasagna', 'burger': 'burger'
        }
        texto_lower = texto_es.lower().strip()
        if texto_lower in traducciones: 
            return traducciones[texto_lower]
        palabras = texto_lower.split()
        palabras_filtradas = [p for p in palabras if p not in ignorar]
        if not palabras_filtradas: 
            palabras_filtradas = [palabras[-1]] if palabras else [texto_lower]
        palabras_traducidas = [traducciones.get(p, p) for p in palabras_filtradas]
        return ' '.join(palabras_traducidas)
    
    def buscar_receta_externa(self, consulta):
        """Busca en TheMealDB API y traduce los resultados"""
        respuestas = []
        
        consulta_en = self.traducir_a_ingles(consulta)
        
        if consulta != consulta_en:
            respuestas.append(self._crear_respuesta(
                f"🌐 Traduciendo '{consulta}' → '{consulta_en}'...", "info"))
        
        # Búsqueda con alternativas
        terminos_busqueda = [consulta_en]
        palabra_principal = consulta_en.split()[0] if consulta_en else consulta
        alternativas_api = {
            'beef stew': ['beef', 'stew'], 
            'beef': ['beef'], 
            'chicken roast': ['chicken', 'roast chicken'], 
            'pork': ['pork'], 
            'fish': ['fish', 'salmon'], 
            'soup': ['soup'], 
            'stew': ['beef', 'stew'], 
            'roast': ['chicken', 'beef']
        }
        if consulta_en in alternativas_api: 
            terminos_busqueda.extend(alternativas_api[consulta_en])
        elif palabra_principal in alternativas_api: 
            terminos_busqueda.extend(alternativas_api[palabra_principal])
        
        for termino in terminos_busqueda:
            try:
                url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={termino}"
                print(f"🔗 Intentando: {url}")
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data and data.get('meals'):
                    if termino != consulta_en:
                        respuestas.append(self._crear_respuesta(
                            f"✅ Encontré resultados buscando '{termino}'", "info"))
                    
                    receta = data['meals'][0]
                    
                    # Traducir campos principales
                    nombre = self._traducir(receta.get('strMeal', 'Receta encontrada'))
                    categoria = self._traducir(receta.get('strCategory', 'N/A'))
                    area = self._traducir(receta.get('strArea', 'N/A'))
                    
                    respuestas.append(self._crear_respuesta(
                        f"✅ {nombre}\n📂 {categoria} | 🌎 {area}", "ia"))
                    
                    # Ingredientes traducidos
                    ingredientes_en_lista = []
                    for i in range(1, 21):
                        ing = receta.get(f'strIngredient{i}')
                        med = receta.get(f'strMeasure{i}')
                        if ing and ing.strip():
                            ingredientes_en_lista.append(f" • {med.strip()} {ing.strip()}")
                    
                    if ingredientes_en_lista:
                        ingredientes_en_texto = "\n".join(ingredientes_en_lista)
                        ingredientes_es_texto = self._traducir(ingredientes_en_texto)
                        respuestas.append(self._crear_respuesta(
                            "📋 INGREDIENTES:\n" + ingredientes_es_texto, "ia"))
                    
                    # Instrucciones traducidas
                    instrucciones_en = receta.get('strInstructions', '')
                    if instrucciones_en:
                        instrucciones_es = self._traducir(instrucciones_en)
                        pasos_cortos = instrucciones_es[:10000] + "..." if len(instrucciones_es) > 10000 else instrucciones_es
                        respuestas.append(self._crear_respuesta(
                            f"📝 PREPARACIÓN:\n{pasos_cortos}", "ia"))

                    imagen = receta.get('strMealThumb')
                    if imagen:
                        respuestas.append(self._crear_respuesta(
                            f"🖼️ Imagen: {imagen}", "info"))
                    
                    return respuestas
                
            except Exception as e:
                print(f"❌ Error con '{termino}': {e}")
                continue
        
        # Fallback
        respuestas.append(self._crear_respuesta(
            f"⚠️ No encontré '{consulta_en}' en TheMealDB.", "warning"))
        respuestas.append(self._crear_respuesta(
            "💡 Palabras que funcionan bien:\n • chicken, beef, pork, fish, salmon\n • pasta, pizza, rice, soup\n • cake, cookies, bread, pie", "info"))
        
        if self.gpt2_cargado:
            respuestas.append(self._crear_respuesta(
                "🤖 Generando con IA como alternativa...", "info"))
            respuestas.extend(self.generar_con_gpt2(consulta))
        
        return respuestas

    # --- GPT2 con Prompts Mejorados ---
    def generar_con_gpt2(self, consulta):
        respuestas = []
        respuestas.append(self._crear_respuesta(
            "🤖 Generando información básica...", "info"))
        try:
            # Prompt más específico y estructurado
            prompt = f"Para preparar {consulta}, necesitas estos ingredientes básicos: 1) "
            resultado = self.generador(
                prompt, 
                max_length=80,  # Más corto = menos incoherencia
                temperature=0.4,  # Menos creatividad = más coherente
                top_p=0.9,
                do_sample=True,
                num_return_sequences=1,
                pad_token_id=50256  # Evita warnings
            )[0]['generated_text']
            
            # Limpiar el resultado
            resultado = resultado.replace(prompt, "").strip()
            if len(resultado) < 10:
                raise Exception("Respuesta muy corta")
            
            respuestas.append(self._crear_respuesta(
                "⚠️ Información generada por IA - Verifica antes de cocinar", "warning"))
            respuestas.append(self._crear_respuesta(
                f"📖 Sugerencia:\n\n• {resultado}", "ia"))
        except Exception as e:
            respuestas.append(self._crear_respuesta(
                f"⚠️ No pude generar información. Intenta buscar recetas más comunes como:\n"
                "• Pollo asado\n• Pasta carbonara\n• Carne guisada\n• Tacos\n• Arepas", 
                "warning"))
        return respuestas

    def generar_descripcion(self):
        """Muestra descripción general y origen de la receta"""
        if not self.ultima_receta: 
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        respuestas = []
        info = self.recetas[self.ultima_receta]
        
        # Descripción interna primero
        respuestas.append(self._crear_respuesta(
            f"📖 DESCRIPCIÓN: {info['nombre']}\n\n"
            f"⏱️ Tiempo: {info['tiempo']}\n"
            f"📊 Dificultad: {info['dificultad']}\n\n"
            f"📋 Ingredientes principales:\n • " + "\n • ".join(info['ingredientes']),
            "ia"))
        
        # Si quieres más info de TheMealDB
        respuestas.append(self._crear_respuesta(
            "💡 Buscando información adicional en TheMealDB...", "info"))
        
        termino_busqueda = info.get('busqueda_api', info['nombre'])
        respuestas.extend(self.buscar_receta_externa(termino_busqueda))
        
        return respuestas

    def generar_pasos(self):
        """Muestra solo los pasos de preparación detallados"""
        if not self.ultima_receta: 
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        respuestas = []
        info = self.recetas[self.ultima_receta]
        
        respuestas.append(self._crear_respuesta(
            f"📝 Obteniendo pasos detallados para {info['nombre']}...", "bot"))
        
        # Buscar en API solo para obtener instrucciones
        termino_busqueda = info.get('busqueda_api', info['nombre'])
        consulta_en = self.traducir_a_ingles(termino_busqueda)
        
        try:
            url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={consulta_en}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('meals'):
                receta = data['meals'][0]
                instrucciones_en = receta.get('strInstructions', '')
                
                if instrucciones_en:
                    instrucciones_es = self._traducir(instrucciones_en)
                    
                    # Dividir en pasos numerados si es posible
                    pasos = instrucciones_es.split('\n')
                    pasos_limpios = [p.strip() for p in pasos if p.strip()]
                    
                    texto_pasos = "📝 PASOS DE PREPARACIÓN:\n\n"
                    for i, paso in enumerate(pasos_limpios, 1):
                        if not paso.startswith(str(i)):
                            texto_pasos += f"{i}. {paso}\n\n"
                        else:
                            texto_pasos += f"{paso}\n\n"
                    
                    respuestas.append(self._crear_respuesta(texto_pasos.strip(), "ia"))
                    return respuestas
        except Exception as e:
            print(f"Error obteniendo pasos: {e}")
        
        # Fallback si no hay pasos en API
        respuestas.append(self._crear_respuesta(
            "⚠️ No se encontraron pasos detallados en TheMealDB", "warning"))
        
        if self.gpt2_cargado:
            respuestas.append(self._crear_respuesta(
                "🤖 Generando pasos básicos con IA...", "info"))
            try:
                prompt = f"Pasos para preparar {info['nombre']}:\n1. "
                resultado = self.generador(
                    prompt,
                    max_length=100,
                    temperature=0.5,
                    top_p=0.9,
                    num_return_sequences=1,
                    pad_token_id=50256
                )[0]['generated_text']
                
                resultado = resultado.replace(prompt, "").strip()
                respuestas.append(self._crear_respuesta(
                    f"📝 PASOS GENERADOS:\n\n1. {resultado}\n\n⚠️ Verifica antes de seguir", "ia"))
            except:
                respuestas.append(self._crear_respuesta(
                    "❌ No pude generar pasos. Intenta con 'Descripción'", "warning"))
        
        return respuestas

    def generar_tips(self):
        """Muestra consejos profesionales para mejorar la receta"""
        if not self.ultima_receta: 
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        respuestas = []
        info = self.recetas[self.ultima_receta]
        
        # Mostrar tips internos (siempre tenemos estos)
        if 'tips' in info and info['tips']:
            tips_texto = "\n".join(info['tips'])
            respuestas.append(self._crear_respuesta(
                f"💡 TIPS PROFESIONALES para {info['nombre']}:\n\n{tips_texto}", "ia"))
        
        # Agregar tips adicionales con GPT2
        if self.gpt2_cargado:
            respuestas.append(self._crear_respuesta(
                "🤖 Generando tips adicionales...", "info"))
            try:
                prompt = f"Consejos extra para {info['nombre']}: Usa "
                resultado = self.generador(
                    prompt, 
                    max_length=60,
                    temperature=0.5,
                    top_p=0.9,
                    num_return_sequences=1,
                    pad_token_id=50256
                )[0]['generated_text']
                
                resultado = resultado.replace(prompt, "").strip()
                if len(resultado) > 10:
                    respuestas.append(self._crear_respuesta(
                        f"💡 TIP ADICIONAL:\n\n• Usa {resultado}\n\n⚠️ Verifica antes de aplicar", "ia"))
            except:
                pass  # Si falla, no pasa nada, ya mostramos los tips internos
        
        return respuestas

    def generar_variaciones(self):
        """Genera variaciones creativas de la receta"""
        if not self.ultima_receta: 
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        respuestas = []
        info = self.recetas[self.ultima_receta]
        
        # Variaciones predefinidas por receta
        variaciones = {
            'pasta carbonara': [
                "🍝 Carbonara con champiñones: Agrega hongos salteados",
                "🥓 Carbonara ahumada: Usa panceta ahumada",
                "🌶️ Carbonara picante: Agrega chile o pimienta roja",
                "🧀 Carbonara con parmesano: Mezcla pecorino y parmesano"
            ],
            'pollo asado': [
                "🍋 Pollo al limón: Marina con limón y hierbas",
                "🌿 Pollo con romero: Agrega romero fresco",
                "🧄 Pollo al ajo: Usa 10 dientes de ajo",
                "🍯 Pollo glaseado: Baña con miel y mostaza"
            ],
            'carne guisada': [
                "🍷 Guiso con vino tinto: Agrega una copa de vino",
                "🌶️ Guiso picante: Con chiles o ají",
                "🥔 Guiso rústico: Con más papas y menos caldo",
                "🍄 Guiso de lujo: Agrega champiñones portobello"
            ],
            'tacos': [
                "🌮 Tacos de pescado: Usa pescado empanizado",
                "🥑 Tacos vegetarianos: Con frijoles y aguacate",
                "🧀 Tacos gratinados: Cubre con queso y gratina",
                "🌶️ Tacos extra picantes: Doble salsa y jalapeños"
            ],
            'arepas': [
                "🧀 Arepas rellenas: Con queso, carne o aguacate",
                "🌽 Arepas dulces: Agrega azúcar a la masa",
                "🥓 Arepas de desayuno: Con huevo y tocino",
                "🍳 Arepas de choclo: Con maíz tierno"
            ],
            'arroz con pollo': [
                "🥘 Arroz con mariscos: Cambia pollo por camarones",
                "🌶️ Arroz picante: Agrega chiles rojos",
                "🥥 Arroz con coco: Cocina con leche de coco",
                "🍋 Arroz al curry: Usa curry amarillo"
            ],
            'sopa de tomate': [
                "🧀 Sopa cremosa: Agrega queso crema",
                "🌿 Sopa con albahaca: Más albahaca fresca",
                "🥓 Sopa con tocino: Decora con tocino crujiente",
                "🌶️ Sopa picante: Agrega chile chipotle"
            ],
            'pizza': [
                "🍄 Pizza vegetariana: Con hongos, pimientos y aceitunas",
                "🥓 Pizza carnívora: Pepperoni, salchicha y jamón",
                "🍍 Pizza hawaiana: Jamón y piña",
                "🧀 Pizza 4 quesos: Mozzarella, parmesano, gorgonzola y ricotta"
            ],
            'hamburguesa': [
                "🧀 Burger con queso azul: Agrega queso gorgonzola",
                "🥓 Bacon burger: Con tocino crujiente",
                "🌶️ Burger picante: Con jalapeños y salsa chipotle",
                "🍄 Mushroom burger: Con champiñones salteados"
            ],
            'ensalada cesar': [
                "🦐 César con camarones: Cambia pollo por camarones",
                "🥑 César con aguacate: Agrega aguacate fresco",
                "🥓 César con tocino: Añade tocino crujiente",
                "🌿 César vegetariana: Sin pollo, más vegetales"
            ],
            'paella': [
                "🦐 Paella de mariscos: Solo mariscos, sin carnes",
                "🐙 Paella negra: Con tinta de calamar",
                "🌿 Paella vegetariana: Con alcachofas y pimientos",
                "🦆 Paella mixta: Pollo, conejo y mariscos"
            ],
            'lasaña': [
                "🥬 Lasaña vegetariana: Con espinacas y ricotta",
                "🦐 Lasaña de mariscos: Con camarones y pescado",
                "🧀 Lasaña 4 quesos: Sin carne, solo quesos",
                "🍄 Lasaña con champiñones: Boloñesa con hongos"
            ]
        }
        
        if self.ultima_receta in variaciones:
            variaciones_texto = "\n".join(variaciones[self.ultima_receta])
            respuestas.append(self._crear_respuesta(
                f"🎨 VARIACIONES de {info['nombre']}:\n\n{variaciones_texto}", "ia"))
        
        # Generar variación extra con GPT2
        if self.gpt2_cargado:
            respuestas.append(self._crear_respuesta(
                "🤖 Generando variación creativa...", "info"))
            try:
                prompt = f"Variación creativa de {info['nombre']}: Prueba agregar "
                resultado = self.generador(
                    prompt,
                    max_length=60,
                    temperature=0.7,  # Más creatividad aquí
                    top_p=0.9,
                    num_return_sequences=1,
                    pad_token_id=50256
                )[0]['generated_text']
                
                resultado = resultado.replace(prompt, "").strip()
                if len(resultado) > 10:
                    respuestas.append(self._crear_respuesta(
                        f"🎨 VARIACIÓN CREATIVA:\n\n• Prueba agregar {resultado}\n\n⚠️ Experimenta con precaución", "ia"))
            except:
                pass
        
        if not respuestas:
            respuestas.append(self._crear_respuesta(
                "⚠️ No hay variaciones disponibles para esta receta", "warning"))
        
        return respuestas

    # --- Procesador Principal ---
    def procesar_mensaje(self, mensaje):
        respuestas = []
        
        # Verificar saludo
        if not self.saludado:
            if any(saludo in mensaje.lower() for saludo in ['hola', 'hi', 'hey', 'buenas']):
                respuestas.extend(self.habilitar_funcionalidades())
                return respuestas, self.saludado
            else:
                respuestas.append(self._crear_respuesta(
                    "⚠️ Salúdame con 'hola' primero.", "warning"))
                return respuestas, self.saludado

        # Análisis PLN
        tokens, lemas, pos_tags = self.analizar_pln(mensaje)
       
        # Sentimiento
        sent, conf = None, 0.5
        if self.analyzer:
            sent, conf = self.analizar_sentimiento(mensaje)
            if sent:
                self.ultimo_sentimiento = sent
                emojis = {"POS": "😊", "NEG": "😞", "NEU": "😐"}
                respuestas.append(self._crear_respuesta(
                    f"🎭 {emojis.get(sent, '😐')} {sent} ({conf:.0%})", "sentiment"))
        
        # Detectar receta
        receta, tipo, termino = self.detectar_receta(mensaje)
        
        # FLUJO 1: Receta interna
        if receta:
            self.ultima_receta = receta
            info = self.recetas[receta]
            
            # Respuesta según sentimiento
            frase_inicio = "Perfecto."
            if sent == "POS":
                frase_inicio = f"¡Buena energía! {info['nombre']} será genial."
            elif sent == "NEG":
                frase_inicio = f"Entendido. ¡Quizás una {info['nombre']} te suba el ánimo!"
            
            texto = f"{frase_inicio}\n\n"
            texto += f"📋 Ingredientes básicos:\n • " + "\n • ".join(info['ingredientes'])
            texto += "\n\n💡 Usa los botones para ver la receta completa desde TheMealDB"
            
            respuestas.append(self._crear_respuesta(texto, "bot"))
        
        # FLUJO 2: Búsqueda externa
        else:
            consulta = self.extraer_comida(pos_tags)
            
            # Fallback si no se encuentra comida
            if not consulta:
                palabras = mensaje.lower().split()
                palabras_comida = ['pasta', 'chicken', 'beef', 'pork', 'fish', 'pizza', 
                                  'soup', 'salad', 'rice', 'bread', 'cake', 'cookie']
                for palabra in palabras:
                    if palabra in palabras_comida:
                        consulta = palabra
                        break
                if not consulta:
                    consulta = palabras[-1] if palabras else mensaje
            
            respuestas.append(self._crear_respuesta(
                f"Buscando '{consulta}'...", "bot"))
            respuestas.extend(self.buscar_receta_externa(consulta))

        return respuestas, self.saludado