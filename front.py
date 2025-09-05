import tkinter as tk
from tkinter import ttk
import spacy
from nltk.tokenize import word_tokenize
import nltk

nltk.download('punkt')
pln = spacy.load("es_core_news_sm")

class ChatbotPLN:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot PLN")
        self.saludado = False

        self.chat_box = tk.Text(root, height=20, width=60, state=tk.DISABLED)
        self.chat_box.pack(pady=5)

        self.frame = tk.Frame(root)
        self.frame.pack(pady=5)

        self.entrada = tk.Entry(self.frame, width=40)
        self.entrada.pack(side=tk.LEFT, padx=5)

        self.opcion_var = tk.StringVar(value="Tokenizar")
        self.opciones = ["Tokenizar", "Lematizar", "POS-tagging"]
        self.opcion_menu = ttk.OptionMenu(self.frame, self.opcion_var, self.opciones[0], *self.opciones)
        self.opcion_menu.pack(side=tk.LEFT, padx=5)

        self.boton_enviar = tk.Button(self.frame, text="Enviar", command=self.enviar)
        self.boton_enviar.pack(side=tk.LEFT, padx=5)

        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, "Bot: Bienvenido a ChatYow, tu asistente virtual.\n")
        self.chat_box.insert(tk.END, "Bot: Por favor, salúdame escribiendo 'hola'.\n")
        self.chat_box.config(state=tk.DISABLED)

    def enviar(self):
        mensaje = self.entrada.get()
        if not mensaje.strip():
            return
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, f"Tú: {mensaje}\n")
        if not self.saludado:
            tokens = word_tokenize(mensaje.lower())
            if 'hola' in tokens:
                self.saludado = True
                self.chat_box.insert(tk.END, "Bot: ¡Gracias por saludarme! Ahora puedes procesar tus mensajes.\n")
                self.chat_box.insert(tk.END, "Bot: Porfavor escribe la oracion y selecciona la opcion\n")
            else:
                self.chat_box.insert(tk.END, "Bot: Ojalá ser saludado por ti.\n")
            self.chat_box.config(state=tk.DISABLED)
            self.entrada.delete(0, tk.END)
            return

        opcion = self.opcion_var.get()
        if opcion == "Tokenizar":
            tokens = word_tokenize(mensaje.lower())
            respuesta = f"Bot: Tokens: {tokens}\n"
        elif opcion == "Lematizar":
            doc = pln(mensaje)
            lemas = [token.lemma_ for token in doc]
            respuesta = f"Bot: Lemas: {lemas}\n"
        elif opcion == "POS-tagging":
            doc = pln(mensaje)
            detalles = "\n".join([f"Token: {token.text}, Lemma: {token.lemma_}, POS: {token.pos_}" for token in doc])
            respuesta = f"Bot:\n{detalles}\n"
        else:
            respuesta = "Bot: Opción no válida.\n"
        self.chat_box.insert(tk.END, respuesta)
        self.chat_box.config(state=tk.DISABLED)
        self.entrada.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotPLN(root)
    root.mainloop()