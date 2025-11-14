# chatbot_logic.py - VERSIÓN HÍBRIDA (Spoonacular Search + TheMealDB Steps)
import random
import requests
import json
import re # Usaremos re para limpiar HTML de Spoonacular

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




class ChatbotLogic:
    
    def __init__(self):
        self.saludado = False
        self.ultimo_sentimiento = "NEU"
        self.ultima_receta = None
        self.ultima_busqueda_api = None # <-- AÑADIDO: Memoria para búsquedas externas
        
        # --- Integración con Spoonacular ---
        # ¡API Key del usuario insertada!
        self.SPOONACULAR_API_KEY = "83b3661ad8d34bf5befa1c09a1f8a4ba" #
        
        if not self.SPOONACULAR_API_KEY or self.SPOONACULAR_API_KEY == "TU_API_KEY_VA_AQUI":
            print("="*50)
            print("⚠️ ADVERTENCIA: Spoonacular API Key no configurada.")
            print("⚠️ El bot NO podrá buscar recetas externas.")
            print("⚠️ Edita 'chatbot_logic.py' y añade tu API Key.")
            print("="*50)
            self.spoonacular_disponible = False
            self.modelo_activo = "Recetas Internas (API EXTERNA DESHABILITADA)"
        else:
            self.spoonacular_disponible = True
            self.modelo_activo = "Spoonacular API (Búsqueda) + TheMealDB (Pasos)"
            print("✅ Spoonacular API Key configurada.")
            
        print(f"✅ {self.modelo_activo} lista")
        # --- FIN NUEVO ---
        
        # Crear el objeto traductor
        if DEEP_TRANSLATOR_DISPONIBLE:
            self.translator = GoogleTranslator(source='en', target='es')
        else:
            self.translator = None
        
        # --- ELIMINADO: Carga de GPT-2 ---
        
        # Sentimientos
        if SENTIMIENTOS_DISPONIBLE:
            try:
                self.analyzer = create_analyzer(task="sentiment", lang="es")
                print("✅ Analizador de sentimientos listo")
            except:
                self.analyzer = None
        else:
            self.analyzer = None
            
        # Sinónimos expandidos (Tu versión)
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
        
        # --- Recetas internas con 'pasos' ---
        self.recetas = {
            'pasta carbonara': {
                'nombre': 'Pasta Carbonara',
                'busqueda_api': 'carbonara',
                'ingredientes': ['400g espagueti', '200g panceta', '4 yemas', 'Queso Pecorino'],
                'tiempo': '20 min',
                'dificultad': 'Media',
                'pasos': [
                    "1. Hierve la pasta en agua con sal hasta que esté al dente.",
                    "2. Mientras, corta la panceta (o guanciale) y fríela en su propia grasa hasta que esté crujiente. Apaga el fuego.",
                    "3. En un bol, bate las yemas de huevo con abundante queso Pecorino rallado y pimienta negra.",
                    "4. Escurre la pasta (reserva un poco de agua de cocción) y añádela a la sartén con la panceta.",
                    "5. Vierte la mezcla de huevo y queso sobre la pasta caliente, mezclando rápidamente. Agrega un chorrito del agua de cocción para crear una salsa cremosa.",
                    "6. Sirve inmediatamente con más queso y pimienta."
                ],
                'tips': [
                    '• NO uses crema, solo huevos y queso pecorino',
                    '• Retira del fuego antes de agregar los huevos para que no se cocinen (efecto \'huevo revuelto\').',
                    '• El guanciale es mejor que la panceta'
                ]
            },
            'pollo asado': {
                'nombre': 'Pollo Asado',
                'busqueda_api': 'roast chicken',
                'ingredientes': ['1 pollo entero', '2 limones', 'Ajo', 'Mantequilla', 'Romero'],
                'tiempo': '1h 30min',
                'dificultad': 'Fácil',
                'pasos': [
                    "1. Precalienta el horno a 200°C (400°F).",
                    "2. Seca muy bien el pollo con papel de cocina. Esto es clave para una piel crujiente.",
                    "3. Sazona generosamente por dentro y por fuera con sal y pimienta.",
                    "4. Rellena la cavidad del pollo con los limones cortados, ajos enteros y ramas de romero.",
                    "5. Unta mantequilla ablandada sobre toda la piel.",
                    "6. Hornea durante 1 hora y 20 minutos, o hasta que los jugos salgan claros."
                ],
                'tips': [
                    '• Seca bien el pollo antes de hornear',
                    '• Unta mantequilla bajo la piel para más sabor',
                    '• Baña con sus jugos cada 20 minutos',
                    '• Deja reposar 10 minutos antes de cortar.'
                ]
            },
            'carne guisada': {
                'nombre': 'Carne Guisada',
                'busqueda_api': 'beef stew',
                'ingredientes': ['1kg carne (ej. morcillo)', '3 papas', '2 zanahorias', '1 cebolla', 'Vino tinto'],
                'tiempo': '2h',
                'dificultad': 'Media',
                'pasos': [
                    "1. Corta la carne en cubos, salpimienta y séllala en una olla caliente con aceite. Retira y reserva.",
                    "2. En la misma olla, sofríe la cebolla, ajo y zanahorias picadas hasta que estén blandas.",
                    "3. Añade la carne de nuevo a la olla y vierte una copa de vino tinto. Deja que el alcohol se evapore.",
                    "4. Cubre con caldo de carne o agua. Tapa y cocina a fuego lento por 1.5 horas.",
                    "5. Pela y corta las papas, añádelas al guiso y cocina por 30 minutos más o hasta que todo esté tierno."
                ],
                'tips': [
                    '• Dora la carne primero para sellar jugos',
                    '• Cocina a fuego lento mínimo 1.5 horas',
                    '• Agrega las papas al final para que no se deshagan'
                ]
            },
            'tacos': {
                'nombre': 'Tacos al Pastor',
                'busqueda_api': 'tacos',
                'ingredientes': ['1kg cerdo (lomo o paleta)', 'Piña', 'Chile ancho y guajillo', 'Achiote', 'Tortillas de maíz'],
                'tiempo': '3h',
                'dificultad': 'Media',
                'pasos': [
                    "1. Hierve los chiles secos para ablandarlos. Licúalos con achiote, vinagre, ajo y especias para crear el adobo.",
                    "2. Corta la carne de cerdo en filetes finos y mézclala con el adobo. Marina en la nevera por al menos 2 horas.",
                    "3. Ensarta la carne en un trompo vertical (o ásala en una sartén si es en casa).",
                    "4. Corta la carne directamente del trompo (o pícala si usaste sartén).",
                    "5. Sirve en tortillas de maíz calientes con piña asada, cebolla y cilantro."
                ],
                'tips': [
                    '• Marina la carne al menos 2 horas',
                    '• Asa con piña para el sabor tradicional',
                    '• Usa tortillas de maíz, no de harina'
                ]
            },
            'arepas': {
                'nombre': 'Arepas Colombianas',
                'busqueda_api': 'arepa',
                'ingredientes': ['2 tazas harina de maíz precocida (blanca o amarilla)', '2.5 tazas de agua tibia', 'Sal', 'Mantequilla (opcional)'],
                'tiempo': '30 min',
                'dificultad': 'Fácil',
                'pasos': [
                    "1. En un bol, mezcla el agua tibia con una cucharadita de sal (y mantequilla si deseas).",
                    "2. Agrega gradualmente la harina de maíz precocida mientras mezclas con la mano.",
                    "3. Amasa durante 3-5 minutos hasta obtener una masa suave, húmeda y que no se pegue a las manos.",
                    "4. Forma bolas del tamaño de tu palma y aplánalas para crear discos de 1 cm de grosor.",
                    "5. Ásalas en una plancha o sartén caliente (ligeramente engrasada) a fuego medio-bajo.",
                    "6. Cocina unos 5-7 minutos por cada lado, hasta que estén doradas y cocidas por dentro.",
                    "7. Rellena con queso, carne, aguacate o lo que prefieras."
                ],
                'tips': [
                    '• La masa debe quedar suave, no pegajosa',
                    '• Agrega sal y un poco de mantequilla al agua',
                    '• Cocina a fuego medio para que doren y no se quemen'
                ]
            },
            'arroz con pollo': {
                'nombre': 'Arroz con Pollo',
                'busqueda_api': 'chicken rice',
                'ingredientes': ['2 tazas arroz', '4 muslos de pollo', 'Caldo de pollo', 'Azafrán o color', 'Verduras (zanahoria, arvejas)'],
                'tiempo': '45 min',
                'dificultad': 'Media',
                'pasos': [
                    "1. Sazona el pollo con sal y pimienta. Dóralo en una olla grande con aceite. Retira y reserva.",
                    "2. En la misma olla, sofríe cebolla, ajo y pimentón picados.",
                    "3. Agrega el arroz y sofríelo por 1 minuto hasta que se selle.",
                    "4. Vuelve a poner el pollo en la olla. Agrega 4 tazas de caldo de pollo caliente y el azafrán/color.",
                    "5. Añade las verduras (zanahoria rallada, arvejas).",
                    "6. Cuando hierva, baja el fuego al mínimo, tapa y cocina por 20 minutos sin destapar.",
                    "7. Deja reposar 5 minutos antes de servir."
                ],
                'tips': [
                    '• Dora el pollo antes de agregar el arroz',
                    '• Usa caldo de pollo, no agua, para más sabor',
                    '• El azafrán da el color dorado característico',
                    '• No destapes la olla en los 20 minutos de cocción.'
                ]
            },
            'sopa de tomate': {
                'nombre': 'Sopa de Tomate',
                'busqueda_api': 'tomato soup',
                'ingredientes': ['1kg tomates maduros', '1 cebolla', '2 dientes de ajo', 'Albahaca fresca', 'Caldo de verduras'],
                'tiempo': '35 min',
                'dificultad': 'Fácil',
                'pasos': [
                    "1. Sofríe la cebolla y el ajo en una olla con aceite de oliva hasta que estén transparentes.",
                    "2. Añade los tomates cortados en cuartos (pueden ser enlatados). Cocina por 5 minutos.",
                    "3. Agrega el caldo de verduras y las hojas de albahaca. Sazona con sal y pimienta.",
                    "4. Deja hervir, luego baja el fuego y cocina por 20 minutos.",
                    "5. Tritura la sopa con una licuadora de inmersión (o licuadora normal con cuidado) hasta que esté cremosa.",
                    "6. Sirve caliente, opcionalmente con un chorrito de crema de leche."
                ],
                'tips': [
                    '• Usa tomates maduros para mejor sabor (o tomates en lata de buena calidad)',
                    '• La albahaca fresca marca la diferencia',
                    '• Sirve con crutones o pan tostado con queso.'
                ]
            },
            'pizza': {
                'nombre': 'Pizza Casera',
                'busqueda_api': 'pizza',
                'ingredientes': ['500g harina de fuerza', '7g levadura seca', 'Agua tibia', 'Salsa de tomate', 'Queso Mozzarella'],
                'tiempo': '2h (incluye levado)',
                'dificultad': 'Media',
                'pasos': [
                    "1. Disuelve la levadura en agua tibia con una pizca de azúcar. Deja reposar 5 min.",
                    "2. Mezcla la harina con sal. Haz un hueco en el centro y vierte la levadura y aceite de oliva.",
                    "3. Amasa por 10-15 minutos hasta que la masa esté elástica y suave.",
                    "4. Deja levar en un bol aceitado y tapado en un lugar cálido por 1-2 horas, o hasta que doble su tamaño.",
                    "5. Precalienta el horno a la máxima temperatura (250°C / 480°F).",
                    "6. Estira la masa, cubre con salsa de tomate, queso mozzarella y tus ingredientes favoritos.",
                    "7. Hornea por 10-12 minutos o hasta que los bordes estén dorados y el queso burbujee."
                ],
                'tips': [
                    '• Deja fermentar la masa mínimo 1 hora',
                    '• Hornea a máxima temperatura',
                    '• No sobrecargues de ingredientes'
                ]
            },
            'hamburguesa': {
                'nombre': 'Hamburguesa Casera',
                'busqueda_api': 'burger',
                'ingredientes': ['500g carne molida (con 20% grasa)', 'Pan de hamburguesa', 'Lechuga', 'Tomate', 'Queso cheddar'],
                'tiempo': '25 min',
                'dificultad': 'Fácil',
                'pasos': [
                    "1. Divide la carne molida en 2 o 3 porciones. No la amases demasiado.",
                    "2. Forma las hamburguesas (un poco más grandes que el pan, ya que encogen). Sazona generosamente con sal y pimienta por ambos lados JUSTO antes de cocinar.",
                    "3. Calienta una sartén de hierro fundido o plancha a fuego alto.",
                    "4. Cocina las hamburguesas 3-4 minutos por cada lado para término medio.",
                    "5. Un minuto antes de sacarlas, pon una loncha de queso encima y tapa para que se derrita.",
                    "6. Tuesta los panes en la misma sartén.",
                    "7. Arma la hamburguesa con lechuga, tomate y tus salsas."
                ],
                'tips': [
                    '• Usa carne con 20% de grasa para que queden jugosas',
                    '• No presiones la carne al cocinar (pierde jugos)',
                    '• Tuesta el pan antes de armar'
                ]
            },
            'ensalada cesar': {
                'nombre': 'Ensalada César',
                'busqueda_api': 'caesar salad',
                'ingredientes': ['Lechuga romana', 'Pechuga de pollo', 'Queso Parmesano', 'Crutones (pan tostado)'],
                'tiempo': '20 min',
                'dificultad': 'Fácil',
                'pasos': [
                    "1. Cocina la pechuga de pollo a la plancha con sal y pimienta. Déjala reposar y córtala en tiras.",
                    "2. Lava y corta la lechuga romana en trozos grandes.",
                    "3. Prepara el aderezo César (puedes usar uno comprado o hacerlo casero con anchoas, yema, ajo, aceite y limón).",
                    "4. En un bol grande, mezcla la lechuga con el aderezo hasta que esté bien cubierta.",
                    "5. Añade el pollo en tiras, los crutones y abundante queso parmesano recién rallado.",
                    "6. Sirve inmediatamente."
                ],
                'tips': [
                    '• Lava y seca bien la lechuga romana',
                    '• Usa parmesano recién rallado, no en polvo',
                    '• Sirve inmediatamente para que los crutones no se ablanden.'
                ]
            },
            'paella': {
                'nombre': 'Paella Valenciana',
                'busqueda_api': 'paella',
                'ingredientes': ['Arroz bomba', 'Pollo', 'Conejo', 'Judías verdes (bajoquetas)', 'Garrofón', 'Azafrán', 'Caldo'],
                'tiempo': '1h',
                'dificultad': 'Difícil',
                'pasos': [
                    "1. Calienta aceite en la paellera y sofríe el pollo y conejo troceados hasta que estén dorados. Sazona.",
                    "2. Añade las judías verdes y el garrofón. Sofríe unos minutos.",
                    "3. Agrega tomate rallado y sofríe hasta que oscurezca.",
                    "4. Añade el arroz (mide en tazas) y sofríelo ('nacara') por 1 minuto.",
                    "5. Vierte el caldo caliente (doble de volumen que el arroz), el azafrán y sal. Mezcla UNA vez.",
                    "6. Cocina a fuego fuerte por 10 min, luego baja el fuego y cocina 8-10 min más hasta que el arroz esté cocido y el líquido se haya evaporado.",
                    "7. Sube el fuego 1 minuto al final para el 'socarrat' (arroz tostado). Deja reposar 5 min."
                ],
                'tips': [
                    '• Usa una paellera (sartén ancha y plana)',
                    '• El socarrat (arroz tostado del fondo) es clave',
                    '• No remuevas el arroz después de agregar el caldo'
                ]
            },
            'lasaña': {
                'nombre': 'Lasaña Boloñesa',
                'busqueda_api': 'lasagna',
                'ingredientes': ['Láminas de lasaña', 'Carne molida (boloñesa)', 'Salsa bechamel', 'Queso Parmesano'],
                'tiempo': '1h 30min',
                'dificultad': 'Media',
                'pasos': [
                    "1. Prepara una salsa boloñesa (carne molida con sofrito de cebolla, zanahoria y apio, y salsa de tomate, cocida lentamente).",
                    "2. Prepara una salsa bechamel (mantequilla, harina, leche).",
                    "3. Precalienta el horno a 180°C (350°F).",
                    "4. En una bandeja para horno, pon una capa fina de bechamel en el fondo.",
                    "5. Alterna capas: lámina de pasta, capa de boloñesa, capa de bechamel, queso parmesano.",
                    "6. Repite hasta llenar la bandeja. Termina con una capa generosa de bechamel y mucho queso parmesano.",
                    "7. Hornea por 30-40 minutos o hasta que esté dorada y burbujeante.",
                    "8. Deja reposar 10 minutos antes de cortar."
                ],
                'tips': [
                    '• Cocina la boloñesa mínimo 1-2 horas para más sabor',
                    '• Asegúrate de que la bechamel no esté muy espesa',
                    '• Deja reposar 10 min antes de cortar para que se asiente.'
                ]
            }
        }
        
        self.categorias = {
            'italiana': "¡Claro! La comida italiana es famosa por sus pastas. ¿Qué tal una 'pasta carbonara' o 'lasaña'?",
            'italiano': "¡Claro! La comida italiana es famosa por sus pastas. ¿Qué tal una 'pasta carbonara' o 'lasaña'?",
            'mexicana': "¡Entendido! La comida mexicana es deliciosa. Te recomiendo unos 'tacos al pastor'.",
            'mexicano': "¡Entendido! La comida mexicana es deliciosa. Te recomiendo unos 'tacos al pastor'.",
            'colombiana': "¡Perfecto! ¿Qué tal unas 'arepas colombianas'?",
            'colombiano': "¡Perfecto! ¿Qué tal unas 'arepas colombianas'?",
            'española': "¡Buena elección! La 'paella' es un plato increíble de España.",
            'español': "¡Buena elección! La 'paella' es un plato increíble de España."
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
            
    # --- AÑADIDO: Función para detectar categorías ---
    def detectar_categoria(self, mensaje):
        """Busca categorías de comida predefinidas."""
        mensaje_lower = mensaje.lower()
        for palabra_clave, respuesta in self.categorias.items():
            if re.search(r'\b' + re.escape(palabra_clave) + r'\b', mensaje_lower):
                return respuesta # Devuelve la respuesta predefinida
        return None
    # --- FIN AÑADIDO ---

    # --- Helpers ---
    def _crear_respuesta(self, texto, tipo="bot"):
        return {"type": tipo, "text": texto.strip()}

    def mostrar_bienvenida(self):
        respuestas = []
        respuestas.append(self._crear_respuesta(
            f"¡Bienvenido! Usando {self.modelo_activo}.", "bot"))
        
        # --- CAMBIO: Mensaje de bienvenida sin IA ---
        if not self.spoonacular_disponible:
             respuestas.append(self._crear_respuesta(
                "⚠️ ADVERTENCIA: La API externa no está configurada. Solo funcionarán las 12 recetas internas.", "warning"))
        
        respuestas.append(self._crear_respuesta(
            "Salúdame con 'hola' para comenzar.", "warning"))
        respuestas.append(self._crear_respuesta(
            "🧠 PLN activo:\n • Tokenización\n • Lematización\n • POS Tagging\n • Sentimientos", "info"))
        respuestas.append(self._crear_respuesta(
            "✨ Puedo:\n • Buscar recetas en Spoonacular\n • Mostrar ingredientes y pasos", "info"))
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
        ignorar = ['dar', 'dame', 'quiero', 'preparar', 'hacer', 'cocinar', 'buscar', 'necesito', 'querer', 'como', 'de', 'un', 'una', 'el', 'la', 'los', 'las', 'para', 'con', 'comer', 'por', 'favor', 'hazme', 'haz','prepara', 'enséñame', 'muéstrame', 'tú', 'yo', 'me', 'te', 'se','quisiera','podrias','podrías','porfa','tenga','contenga','puedes','puedess','buscame','búscame','darme','triste','feliz','hambre','sed','sediento','hambriento','Enojado','enojado','cansado','cansada','aburrido','aburrida']
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
    
    # --- ESTA FUNCIÓN SIGUE USANDO SPOONACULAR (Búsqueda principal) ---
    def buscar_receta_externa(self, consulta):
        """Busca en Spoonacular API y traduce los resultados"""
        respuestas = []
        
        if not self.spoonacular_disponible:
            respuestas.append(self._crear_respuesta(
                "⚠️ La API externa no está configurada. No puedo buscar recetas nuevas.", "warning"))
            return respuestas

        consulta_en = self.traducir_a_ingles(consulta)
        
        if consulta != consulta_en:
            respuestas.append(self._crear_respuesta(
                f"🌐 Traduciendo '{consulta}' → '{consulta_en}'...", "info"))
        
        try:
            # Spoonacular usa 'complexSearch' y podemos pedir la info de la receta de una vez
            url = "https://api.spoonacular.com/recipes/complexSearch"
            params = {
                "apiKey": self.SPOONACULAR_API_KEY,
                "query": consulta_en,
                "number": 1,                      # Solo queremos el mejor resultado
                "addRecipeInformation": True,     # Incluye la receta completa
                "fillIngredients": True           # Incluye info de ingredientes
            }
            
            print(f"🔗 [Spoonacular] Intentando: complexSearch?query={consulta_en}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status() # Lanza un error si la API Key es incorrecta o se supera la cuota
            data = response.json()
            
            if data and data.get('results') and len(data['results']) > 0:
                receta = data['results'][0]
                
                # Traducir campos principales
                nombre = self._traducir(receta.get('title', 'Receta encontrada'))
                fuente = receta.get('sourceName', 'Spoonacular')
                tiempo = receta.get('readyInMinutes', 'N/A')
                
                respuestas.append(self._crear_respuesta(
                    f"✅ {nombre}\n"
                    f"📂 Fuente: {fuente}\n"
                    f"⏱️ Tiempo: {tiempo} minutos", "ia"))
                
                # Ingredientes traducidos
                ingredientes_en_lista = []
                if 'extendedIngredients' in receta:
                    for ing in receta['extendedIngredients']:
                        ingredientes_en_lista.append(f" • {ing.get('original')}")
                
                if ingredientes_en_lista:
                    ingredientes_en_texto = "\n".join(ingredientes_en_lista)
                    ingredientes_es_texto = self._traducir(ingredientes_en_texto)
                    respuestas.append(self._crear_respuesta(
                        "📋 INGREDIENTES:\n" + ingredientes_es_texto, "ia"))
                
                # Instrucciones traducidas
                instrucciones_en = receta.get('instructions', '')
                if instrucciones_en:
                    # Limpiar HTML (ej. <li>, <ol>, <p>) de las instrucciones
                    instrucciones_limpias_en = re.sub(r'<[^>]+>', ' ', instrucciones_en).strip()
                    # Reemplazar múltiples espacios por uno solo
                    instrucciones_limpias_en = re.sub(r'\s{2,}', ' ', instrucciones_limpias_en)
                    
                    instrucciones_es = self._traducir(instrucciones_limpias_en)
                    
                    # Spoonacular a veces numera mal, asegurémonos de que haya saltos de línea
                    instrucciones_formateadas = instrucciones_es.replace(". ", ".\n")
                    
                    respuestas.append(self._crear_respuesta(
                        f"📝 PREPARACIÓN:\n{instrucciones_formateadas}", "ia"))

                imagen = receta.get('image')
                if imagen:
                    respuestas.append(self._crear_respuesta(
                        f"🖼️ Imagen: {imagen}", "info"))
                
                return respuestas
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401: # Error de API Key
                print("❌ ERROR FATAL DE SPOONACULAR: API Key inválida o bloqueada.")
                respuestas.append(self._crear_respuesta("❌ Error de API: La API Key de Spoonacular es inválida.", "warning"))
                self.spoonacular_disponible = False # Deshabilitar para no seguir intentando
                return respuestas
            elif e.response.status_code == 402: # Error de cuota
                print("❌ ERROR DE SPOONACULAR: Se superó la cuota diaria.")
                respuestas.append(self._crear_respuesta("⚠️ Se superó la cuota diaria de la API. Intenta mañana.", "warning"))
                self.spoonacular_disponible = False # Deshabilitar por hoy
                return respuestas
            else:
                print(f"❌ Error HTTP con Spoonacular: {e}")
                
        except Exception as e:
            print(f"❌ Error genérico con Spoonacular: {e}")
            
        # Fallback si Spoonacular falla o no encuentra nada
        respuestas.append(self._crear_respuesta(
            f"⚠️ No encontré '{consulta_en}' en Spoonacular.", "warning"))
        respuestas.append(self._crear_respuesta(
            "💡 Intenta ser más específico (ej. 'chicken curry' en lugar de 'curry').", "info"))
        
        return respuestas
    # --- FIN DE LA FUNCIÓN DE SPOONACULAR ---
    
    # --- ELIMINADO: Función generar_con_gpt2 ---

    def generar_descripcion(self):
        """Muestra descripción general y origen de la receta"""
        
        # --- LÓGICA CORREGIDA ---
        termino_busqueda = None
        if self.ultima_receta: # Prioridad 1: Receta interna
            info = self.recetas[self.ultima_receta]
            termino_busqueda = info.get('busqueda_api', info['nombre'])
            
            # Mostrar info interna primero
            respuestas = []
            respuestas.append(self._crear_respuesta(
                f"📖 DESCRIPCIÓN: {info['nombre']}\n\n"
                f"⏱️ Tiempo: {info['tiempo']}\n"
                f"📊 Dificultad: {info['dificultad']}\n\n"
                f"📋 Ingredientes principales:\n • " + "\n • ".join(info['ingredientes']),
                "ia"))
            
            if not self.spoonacular_disponible:
                respuestas.append(self._crear_respuesta(
                    "⚠️ La API externa no está configurada. No puedo buscar información adicional.", "warning"))
                return respuestas
                
            respuestas.append(self._crear_respuesta(
                f"💡 Buscando '{termino_busqueda}' en Spoonacular...", "info"))
            respuestas.extend(self.buscar_receta_externa(termino_busqueda))
            return respuestas

        elif self.ultima_busqueda_api: # Prioridad 2: Receta externa
            if not self.spoonacular_disponible:
                return [self._crear_respuesta("⚠️ La API externa no está configurada.", "warning")]
                
            respuestas = [self._crear_respuesta(
                f"💡 Buscando '{self.ultima_busqueda_api}' en Spoonacular...", "info")]
            respuestas.extend(self.buscar_receta_externa(self.ultima_busqueda_api))
            return respuestas
            
        else:
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        # --- FIN CORRECCIÓN ---


    # --- CAMBIO TOTAL: Lógica de `generar_pasos` actualizada a Híbrida ---
    def generar_pasos(self):
        """Muestra los pasos: 1ro Internos, 2do TheMealDB, 3ro Spoonacular"""
        
        # --- LÓGICA CORREGIDA ---
        termino_busqueda = None
        consulta_en = None
        respuestas = []

        if self.ultima_receta: # Receta interna
            info = self.recetas[self.ultima_receta]
            # --- PASO 1: Buscar pasos internos (Prioridad #1) ---
            if 'pasos' in info and info['pasos']:
                pasos_texto = "\n".join(info['pasos'])
                respuestas.append(self._crear_respuesta(
                    f"📝 PASOS (Receta Interna) para {info['nombre']}:\n\n{pasos_texto}", "ia"))
                return respuestas
            
            # Receta interna sin pasos, buscar en API
            respuestas.append(self._crear_respuesta(
                f"📝 No tengo pasos internos... Obteniendo de TheMealDB para {info['nombre']}...", "bot"))
            termino_busqueda = info.get('busqueda_api', info['nombre'])
            consulta_en = self.traducir_a_ingles(termino_busqueda)

        elif self.ultima_busqueda_api: # Receta externa
            respuestas.append(self._crear_respuesta(
                f"📝 Obteniendo de TheMealDB para '{self.ultima_busqueda_api}'...", "bot"))
            termino_busqueda = self.ultima_busqueda_api
            consulta_en = self.traducir_a_ingles(termino_busqueda)
            
        else:
            return [self._crear_respuesta("⚠️ Primero selecciona una receta", "warning")]
        # --- FIN CORRECCIÓN (el resto de la función sigue igual) ---

        # --- PASO 2: Fallback a TheMealDB (Prioridad #2) ---
        try:
            # --- Lógica de TheMealDB ---
            url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={consulta_en}"
            print(f"🔗 [TheMealDB] (Pasos) Buscando pasos en: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data and data.get('meals'):
                receta_api = data['meals'][0]
                instrucciones_en = receta_api.get('strInstructions', '')
                
                if instrucciones_en:
                    instrucciones_es = self._traducir(instrucciones_en)
                    
                    # Formateo de pasos
                    pasos = instrucciones_es.split('\n')
                    pasos_limpios = [p.strip() for p in pasos if p.strip()]
                    
                    texto_pasos = "📝 PASOS DE PREPARACIÓN (API TheMealDB):\n\n"
                    for i, paso in enumerate(pasos_limpios, 1):
                        if not paso.startswith(str(i)):
                            texto_pasos += f"{i}. {paso}\n\n"
                        else:
                            texto_pasos += f"{paso}\n\n"
                    
                    respuestas.append(self._crear_respuesta(texto_pasos.strip(), "ia"))
                    return respuestas
                else:
                    raise Exception("API (TheMealDB) devolvió receta sin instrucciones")
            else:
                raise Exception("API (TheMealDB) no devolvió 'meals'")

        except Exception as e_mealdb:
            print(f"❌ Error obteniendo pasos de TheMealDB: {e_mealdb}")
            # --- FIN PASO 2 ---

            # --- PASO 3: Fallback a Spoonacular (Prioridad #3) ---
            if not self.spoonacular_disponible:
                respuestas.append(self._crear_respuesta(
                    "⚠️ Falló TheMealDB y la API Spoonacular no está disponible.", "warning"))
                return respuestas

            respuestas.append(self._crear_respuesta(
                f"⚠️ Falló TheMealDB. Intentando fallback con Spoonacular...", "warning"))
            
            try:
                # Copiamos la lógica de Spoonacular que estaba aquí antes
                search_url = "https://api.spoonacular.com/recipes/complexSearch"
                params_search = { "apiKey": self.SPOONACULAR_API_KEY, "query": consulta_en, "number": 1 }
                print(f"🔗 [Spoonacular] (Pasos-Fallback) Buscando ID para: {consulta_en}")
                response_search = requests.get(search_url, params=params_search, timeout=10)
                response_search.raise_for_status()
                data_search = response_search.json()
                
                if data_search and data_search.get('results') and len(data_search['results']) > 0:
                    receta_id = data_search['results'][0]['id']
                    
                    steps_url = f"https://api.spoonacular.com/recipes/{receta_id}/analyzedInstructions"
                    params_steps = { "apiKey": self.SPOONACULAR_API_KEY }
                    
                    print(f"🔗 [Spoonacular] (Pasos-Fallback) Obteniendo pasos para ID: {receta_id}")
                    response_steps = requests.get(steps_url, params=params_steps, timeout=10)
                    response_steps.raise_for_status()
                    data_steps = response_steps.json()

                    if data_steps and len(data_steps) > 0 and 'steps' in data_steps[0]:
                        pasos_en_lista = []
                        for paso_info in data_steps[0]['steps']:
                            pasos_en_lista.append(f" {paso_info.get('number')}. {paso_info.get('step')}")
                        
                        if pasos_en_lista:
                            instrucciones_en = "\n".join(pasos_en_lista)
                            instrucciones_es = self._traducir(instrucciones_en)
                            respuestas.append(self._crear_respuesta(
                                f"📝 PASOS DE PREPARACIÓN (API Spoonacular):\n\n{instrucciones_es}", "ia"))
                            return respuestas
                    else:
                        # Fallback final (Spoonacular no tiene pasos analizados)
                        respuestas.append(self._crear_respuesta("ℹ️ No se encontraron pasos analizados. Mostrando receta completa...", "info"))
                        respuestas.extend(self.buscar_receta_externa(consulta_en)) # Llama a la búsqueda general
                        return respuestas
            except Exception as e_spoon:
                print(f"❌ Error en fallback de Spoonacular (Pasos): {e_spoon}")
                respuestas.append(self._crear_respuesta(f"⚠️ Error al conectar con Spoonacular: {str(e_spoon)}", "warning"))
                # --- FIN PASO 3 ---

        # Si todo falla
        respuestas.append(self._crear_respuesta("❌ No pude encontrar los pasos ni en TheMealDB ni en Spoonacular.", "warning"))
        return respuestas
    # --- FIN CAMBIO TOTAL ---

    def generar_tips(self):
        """Muestra consejos profesionales para mejorar la receta"""
        
        # --- LÓGICA CORREGIDA ---
        if self.ultima_receta: # Solo funciona para recetas internas
            info = self.recetas[self.ultima_receta]
            
            # Mostrar tips internos (siempre tenemos estos)
            if 'tips' in info and info['tips']:
                tips_texto = "\n".join(info['tips'])
                return [self._crear_respuesta(
                    f"💡 TIPS PROFESIONALES para {info['nombre']}:\n\n{tips_texto}", "ia")]
        
        # Fallback para recetas externas o internas sin tips
        return [self._crear_respuesta(
            f"ℹ️ Los tips personalizados solo están disponibles para mis recetas internas (ej. Lasaña, Pizza, etc.)", "info")]
        # --- FIN CORRECCIÓN ---


    def generar_variaciones(self):
        """Genera variaciones creativas de la receta"""

        # --- LÓGICA CORREGIDA ---
        if not self.ultima_receta: # Solo funciona para recetas internas
            return [self._crear_respuesta(
                "⚠️ Las variaciones solo están disponibles para mis recetas internas (ej. Lasaña, Pizza, etc.)", "info")]
        
        respuestas = []
        info = self.recetas[self.ultima_receta]
        # --- FIN CORRECCIÓN ---
        
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
        
        # --- ELIMINADO: Fallback a GPT-2 ---
        
        if not respuestas:
            respuestas.append(self._crear_respuesta(
                "⚠️ No hay variaciones disponibles para esta receta", "warning"))
        
        return respuestas

    # --- Procesador Principal ---
    def procesar_mensaje(self, mensaje):
        respuestas = []
        
        # Verificar saludo
        if not self.saludado:
            # --- CAMBIO: Lista de saludos más amplia ---
            if any(saludo in mensaje.lower() for saludo in ['hola', 'hi', 'hey', 'buenas', 'oe','ey', 'saludos', 'buen día', 'buen dia','ole']):
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
        
        # --- AÑADIDO: FLUJO 0 para Categorías ---
        respuesta_categoria = self.detectar_categoria(mensaje)
        if respuesta_categoria:
            respuestas.append(self._crear_respuesta(respuesta_categoria, "bot"))
            return respuestas, self.saludado
        # --- FIN AÑADIDO ---
        
        # Detectar receta
        receta, tipo, termino = self.detectar_receta(mensaje)
        
        # FLUJO 1: Receta interna
        if receta:
            self.ultima_receta = receta
            self.ultima_busqueda_api = None # <-- AÑADIDO: Limpiar búsqueda externa
            info = self.recetas[receta]
            
            # Respuesta según sentimiento
            frase_inicio = "Perfecto."
            if sent == "POS":
                frase_inicio = f"¡Buena energía! {info['nombre']} será genial."
            elif sent == "NEG":
                frase_inicio = f"Entendido. ¡Quizás una {info['nombre']} te suba el ánimo!"
            
            texto = f"{frase_inicio}\n\n"
            texto += f"📋 Ingredientes básicos:\n • " + "\n • ".join(info['ingredientes'])
            # --- CAMBIO: Texto del botón actualizado a Híbrido ---
            texto += "\n\n💡 Usa los botones para ver la receta completa"
            
            respuestas.append(self._crear_respuesta(texto, "bot"))
        
        # FLUJO 2: Búsqueda externa
        else:
            consulta = self.extraer_comida(pos_tags)
            
            # Fallback si no se encuentra comida
            if not consulta:
                palabras = mensaje.lower().split()
                # --- CAMBIO: Ampliación de palabras clave de comida ---
                palabras_comida = ['pasta', 'chicken', 'beef', 'pork', 'fish', 'pizza', 
                                  'soup', 'salad', 'rice', 'bread', 'cake', 'cookie',
                                  'salmon', 'tuna', 'shrimp', 'curry', 'stew', 'roast']
                for palabra in palabras:
                    if palabra in palabras_comida:
                        consulta = palabra
                        break
                if not consulta:
                    # Si sigue sin encontrar, usa la última palabra que no sea de "ignorar"
                    ignorar_pln = ['dar', 'dame', 'quiero', 'preparar', 'hacer', 'cocinar', 'buscar', 'necesito', 'querer', 'como', 'de', 'un', 'una', 'el', 'la', 'los', 'las', 'para', 'con', 'comer', 'por', 'favor', 'hazme', 'haz','prepara', 'enséñame', 'muéstrame', 'tú', 'yo', 'me', 'te', 'se']
                    palabras_filtradas = [p for p in palabras if p not in ignorar_pln]
                    consulta = palabras_filtradas[-1] if palabras_filtradas else mensaje
            
            self.ultima_receta = None # <-- AÑADIDO: Limpiar receta interna
            self.ultima_busqueda_api = consulta # <-- AÑADIDO: Guardar búsqueda externa
            
            respuestas.append(self._crear_respuesta(
                f"Buscando '{consulta}' en Spoonacular...", "bot"))
            respuestas.extend(self.buscar_receta_externa(consulta))

        return respuestas, self.saludado