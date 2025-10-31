# chatbot_logic.py - VERSIÓN CON TheMealDB API + GPT2 BACKUP
import random
import requests
import json
import re

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
        
        # API como principal
        self.modelo_activo = "TheMealDB API + GPT2 Backup"
        self.api_disponible = True
        print(f"✅ {self.modelo_activo} lista")
        
        # Cargar GPT2 como backup (opcional)
        self.gpt2_cargado = False
        if TRANSFORMERS_DISPONIBLE:
            try:
                print("🔄 Cargando GPT2 como backup...")
                self.generador = pipeline('text-generation', model='datificate/gpt2-small-spanish', device=-1)
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
            
        # Sinónimos
        self.sinonimos = {
            'carne guisada': {
                'sinonimos': ['estofado', 'guiso', 'guisado', 'carne estofada', 'cocido', 'beef stew'],
                'palabras_clave': ['carne', 'res', 'vaca', 'beef']
            },
            'pasta carbonara': {
                'sinonimos': ['espagueti', 'fideos', 'tallarines', 'pasta', 'carbonara', 'spaghetti'],
                'palabras_clave': ['pasta', 'italiano', 'espagueti']
            },
            'pollo asado': {
                'sinonimos': ['pollo', 'rostizado', 'gallina', 'ave', 'chicken', 'roast chicken'],
                'palabras_clave': ['pollo', 'ave', 'chicken']
            },
            'tacos': {
                'sinonimos': ['taco', 'taquitos', 'mexicanos'],
                'palabras_clave': ['tacos', 'mexicano', 'tortilla']
            },
            'arepas': {
                'sinonimos': ['arepa', 'arepitas'],
                'palabras_clave': ['arepa', 'maíz', 'colombia']
            }
        }
        
        # Recetas internas (básicas)
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
            }
        }

    # --- PLN ---
    def tokenizar(self, texto):
        return word_tokenize(texto.lower())

    def lematizar_simple(self, tokens):
        lemas_dict = {
            'cocino': 'cocinar', 'guisada': 'guisar', 'fideos': 'fideo',
            'tacos': 'taco', 'arepas': 'arepa', 'quiero': 'querer',
            'dame': 'dar', 'estoy': 'estar'
        }
        return [lemas_dict.get(token, token) for token in tokens]

    def pos_tagging_simple(self, tokens):
        pos_dict = {
            'cocinar': 'VERB', 'carne': 'NOUN', 'pasta': 'NOUN',
            'pollo': 'NOUN', 'taco': 'NOUN', 'arepa': 'NOUN'
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
            "🐔 Pollo → rostizado, ave, chicken\n"
            "🌮 Tacos → taquitos, mexicano\n"
            "🌽 Arepas → arepa, maíz", "sinonimo"))
        return respuestas
        
    def analizar_pln(self, mensaje):
        tokens = self.tokenizar(mensaje)
        lemas = self.lematizar_simple(tokens)
        pos_tags = self.pos_tagging_simple(lemas)
        pln_info = f"📊 PLN: Tokens: {tokens[:4]}... | Lemas: {lemas[:4]}... | POS: {pos_tags[:3]}..."
        return pln_info, tokens, lemas, pos_tags

    # --- API TheMealDB ---
    def traducir_a_ingles(self, texto_es):
        """Traduce términos comunes español → inglés para la API"""
        # Palabras a ignorar (verbos comunes)
        ignorar = ['dar', 'dame', 'quiero', 'preparar', 'hacer', 'cocinar', 
                   'buscar', 'necesito', 'querer', 'como', 'de', 'un', 'una',
                   'el', 'la', 'los', 'las', 'para', 'con']
        
        traducciones = {
            # Comidas
            'pollo': 'chicken',
            'carne': 'beef',
            'res': 'beef',
            'cerdo': 'pork',
            'pescado': 'fish',
            'camarones': 'shrimp',
            'arroz': 'rice',
            'pasta': 'pasta',
            'sopa': 'soup',
            'ensalada': 'salad',
            'pizza': 'pizza',
            'hamburguesa': 'burger',
            'tacos': 'tacos',
            'sandwich': 'sandwich',
            'pan': 'bread',
            'pastel': 'cake',
            'galletas': 'cookies',
            'helado': 'ice cream',
            'tarta': 'pie',
            
            # Platos específicos
            'guisado': 'stew',
            'estofado': 'stew',
            'asado': 'roast',
            'frito': 'fried',
            'horneado': 'baked',
            'a la parrilla': 'grilled',
            
            # Postres
            'postre': 'dessert',
            'dulce': 'sweet',
            'chocolate': 'chocolate',
            
            # Bebidas
            'cafe': 'coffee',
            'café': 'coffee',
            'te': 'tea',
            'té': 'tea',
            'jugo': 'juice',
            'agua': 'water',
            
            # Otros
            'desayuno': 'breakfast',
            'almuerzo': 'lunch',
            'cena': 'dinner',
            'rapido': 'quick',
            'rápido': 'quick',
            'facil': 'easy',
            'fácil': 'easy'
        }
        
        texto_lower = texto_es.lower().strip()
        
        # Buscar traducción exacta primero
        if texto_lower in traducciones:
            return traducciones[texto_lower]
        
        # Dividir en palabras y filtrar
        palabras = texto_lower.split()
        palabras_filtradas = [p for p in palabras if p not in ignorar]
        
        # Si quedó vacío, usar la última palabra original
        if not palabras_filtradas:
            palabras_filtradas = [palabras[-1]] if palabras else [texto_lower]
        
        # Traducir cada palabra
        palabras_traducidas = [traducciones.get(p, p) for p in palabras_filtradas]
        
        return ' '.join(palabras_traducidas)
    
    def buscar_receta_externa(self, consulta):
        """Busca en TheMealDB API con múltiples intentos"""
        respuestas = []
        
        # Traducir automáticamente
        consulta_en = self.traducir_a_ingles(consulta)
        
        if consulta != consulta_en:
            respuestas.append(self._crear_respuesta(
                f"🌐 Traduciendo '{consulta}' → '{consulta_en}'...", "info"))
        
        # Lista de búsquedas alternativas (de más específica a más general)
        terminos_busqueda = [consulta_en]
        
        # Agregar variantes si la búsqueda original falla
        palabra_principal = consulta_en.split()[0] if consulta_en else consulta
        
        # Mapeo de términos problemáticos a alternativas que SÍ funcionan en la API
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
        
        # Buscar alternativas
        if consulta_en in alternativas_api:
            terminos_busqueda.extend(alternativas_api[consulta_en])
        elif palabra_principal in alternativas_api:
            terminos_busqueda.extend(alternativas_api[palabra_principal])
        
        # Intentar cada término hasta encontrar resultados
        for termino in terminos_busqueda:
            try:
                url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={termino}"
                print(f"🔗 Intentando: {url}")
                
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data and data.get('meals'):
                    # ¡Encontramos resultados!
                    if termino != consulta_en:
                        respuestas.append(self._crear_respuesta(
                            f"✅ Encontré resultados buscando '{termino}'", "info"))
                    
                    receta = data['meals'][0]
                    nombre = receta.get('strMeal', 'Receta encontrada')
                    categoria = receta.get('strCategory', 'N/A')
                    area = receta.get('strArea', 'N/A')
                    
                    respuestas.append(self._crear_respuesta(
                        f"✅ {nombre}\n📂 {categoria} | 🌍 {area}", "ia"))
                    
                    # Ingredientes
                    ingredientes = []
                    for i in range(1, 21):
                        ing = receta.get(f'strIngredient{i}')
                        med = receta.get(f'strMeasure{i}')
                        if ing and ing.strip():
                            ingredientes.append(f" • {med.strip()} {ing.strip()}")
                    
                    if ingredientes:
                        respuestas.append(self._crear_respuesta(
                            "📋 INGREDIENTES:\n" + "\n".join(ingredientes), "ia"))
                    
                    # Pasos (limitados)
                    instrucciones = receta.get('strInstructions', '')
                    if instrucciones:
                        pasos_cortos = instrucciones[:800] + "..." if len(instrucciones) > 800 else instrucciones
                        respuestas.append(self._crear_respuesta(
                            f"📝 PREPARACIÓN:\n{pasos_cortos}", "ia"))
                    
                    # Imagen
                    imagen = receta.get('strMealThumb')
                    if imagen:
                        respuestas.append(self._crear_respuesta(
                            f"🖼️ Imagen: {imagen}", "info"))
                    
                    return respuestas  # Éxito, salir
                
            except Exception as e:
                print(f"❌ Error con '{termino}': {e}")
                continue
        
        # Si ninguna búsqueda funcionó
        respuestas.append(self._crear_respuesta(
            f"⚠️ No encontré '{consulta_en}' en TheMealDB.", "warning"))
        
        # Sugerir palabras que SÍ funcionan
        respuestas.append(self._crear_respuesta(
            "💡 Palabras que funcionan bien:\n"
            " • chicken, beef, pork, fish, salmon\n"
            " • pasta, pizza, rice, soup\n"
            " • cake, cookies, bread, pie", "info"))
        
        # Fallback a GPT2
        if self.gpt2_cargado:
            respuestas.append(self._crear_respuesta(
                "🤖 Generando con GPT2 como alternativa...", "info"))
            respuestas.extend(self.generar_con_gpt2(consulta))
        
        return respuestas

    def generar_con_gpt2(self, consulta):
        """Genera receta con GPT2 cuando la API falla"""
        respuestas = []
        respuestas.append(self._crear_respuesta(
            "🤖 Usando GPT2 para generar información básica...", "info"))
        
        try:
            # Prompt con mejor estructura para GPT2
            prompt = f"Receta de {consulta}. Ingredientes necesarios:\n• Primer ingrediente:"
            
            resultado = self.generador(
                prompt,
                max_length=100,
                temperature=0.7,
                top_p=0.85,
                do_sample=True,
                num_return_sequences=1
            )[0]['generated_text']
            
            # Advertencia sobre calidad
            respuestas.append(self._crear_respuesta(
                "⚠️ GPT2 puede generar información imprecisa. Verifica antes de cocinar.", "warning"))
            
            respuestas.append(self._crear_respuesta(
                f"📖 Información generada:\n\n{resultado}", "ia"))
        except Exception as e:
            respuestas.append(self._crear_respuesta(
                f"❌ Error con GPT2: {str(e)[:100]}", "warning"))
        
        return respuestas

    # --- Botones ---
    def generar_descripcion(self):
        """Busca receta completa en API"""
        if not self.ultima_receta:
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        info = self.recetas[self.ultima_receta]
        termino_busqueda = info.get('busqueda_api', info['nombre'])
        
        return self.buscar_receta_externa(termino_busqueda)

    def generar_pasos(self):
        """Mismo que descripción (API tiene todo)"""
        return self.generar_descripcion()

    def generar_tips(self):
        """Muestra tips predefinidos (más confiables que GPT2)"""
        if not self.ultima_receta:
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        info = self.recetas[self.ultima_receta]
        
        # Usar tips predefinidos
        if 'tips' in info and info['tips']:
            tips_texto = "\n".join(info['tips'])
            return [self._crear_respuesta(
                f"💡 TIPS PROFESIONALES para {info['nombre']}:\n\n{tips_texto}", "ia")]
        
        # Si no hay tips, intentar con GPT2 (con advertencia)
        elif self.gpt2_cargado:
            respuestas = []
            respuestas.append(self._crear_respuesta(
                "⚠️ Generando con GPT2 (puede ser impreciso)...", "warning"))
            
            try:
                prompt = f"Consejos para cocinar {info['nombre']}:\n• Usa ingredientes frescos"
                
                resultado = self.generador(
                    prompt,
                    max_length=100,
                    temperature=0.6,
                    top_p=0.85,
                    num_return_sequences=1
                )[0]['generated_text']
                
                respuestas.append(self._crear_respuesta(
                    f"💡 TIPS GENERADOS:\n\n{resultado}\n\n⚠️ Verifica antes de usar", "ia"))
            except Exception as e:
                respuestas.append(self._crear_respuesta(
                    f"❌ Error: {str(e)[:50]}", "warning"))
            
            return respuestas
        else:
            # Fallback a API
            return self.generar_descripcion()

    def generar_variaciones(self):
        """Busca variaciones en API o genera con GPT2"""
        if not self.ultima_receta:
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        
        # Buscar en API primero
        return self.generar_descripcion()

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
        pln_info, tokens, lemas, pos_tags = self.analizar_pln(mensaje)
        respuestas.append(self._crear_respuesta(pln_info, "pln"))
        
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
            
            if tipo and termino:
                respuestas.append(self._crear_respuesta(
                    f"💡 Detectado por {tipo}: '{termino}' → {receta}", "sinonimo"))
            
            texto = f"{'¡Buena energía!' if sent == 'POS' else 'Perfecto.'} {info['nombre']}\n\n"
            texto += f"📋 Ingredientes básicos:\n • " + "\n • ".join(info['ingredientes'])
            texto += f"\n\n⏱️ {info['tiempo']} | 📊 {info['dificultad']}"
            texto += "\n\n💡 Usa los botones para ver la receta completa desde TheMealDB"
            
            respuestas.append(self._crear_respuesta(texto, "bot"))
        
        # FLUJO 2: Búsqueda externa
        else:
            consulta = self.extraer_comida(pos_tags)
            if not consulta:
                palabras = mensaje.lower().split()
                # Buscar palabras comunes de comida
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