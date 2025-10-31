// script.js
document.addEventListener("DOMContentLoaded", () => {
    
    // --- URLs y Elementos DOM ---
    const SERVER_URL = 'http://127.0.0.1:5000'; // Dirección de tu servidor Flask
    
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const statusLabel = document.getElementById('status-label');
    const actionButtons = document.querySelectorAll('.action-btn');

    // --- Funciones Principales ---

    /**
     * Añade un mensaje a la caja de chat.
     * @param {string} text - El texto del mensaje.
     * @param {string} type - La clase CSS (user, bot, ia, warning, etc.)
     */
    function addMessage(text, type) {
        const bubble = document.createElement('div');
        bubble.classList.add('message-bubble', type);
        
        // Reemplaza saltos de línea \n con <br> para HTML
        bubble.innerHTML = text.replace(/\n/g, '<br>'); 
        
        chatBox.appendChild(bubble);
        
        // Auto-scroll al fondo
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    /**
     * Procesa una lista de respuestas del servidor.
     * @param {Array} responses - Lista de objetos {type, text}
     */
    function handleResponses(responses) {
        responses.forEach(response => {
            addMessage(response.text, response.type);
        });
    }

    /**
     * Habilita o deshabilita la entrada del usuario.
     * @param {boolean} enabled - true para habilitar, false para deshabilitar.
     */
    function setInputEnabled(enabled) {
        userInput.disabled = !enabled;
        sendButton.disabled = !enabled;
        if (enabled) {
            userInput.focus();
        }
    }

    /**
     * Actualiza el estado de los botones de acción.
     * @param {boolean} saludado - true si el bot ha sido saludado.
     */
    function updateButtonState(saludado) {
        if (saludado) {
            statusLabel.textContent = "✅ Chat activo - PLN + IA funcionando";
            statusLabel.style.color = "#81c784";
            actionButtons.forEach(btn => btn.disabled = false);
        }
    }

    /**
     * Envía un mensaje al endpoint /chat
     */
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user'); // Muestra el mensaje del usuario
        userInput.value = '';
        setInputEnabled(false); // Deshabilita mientras el bot piensa

        try {
            const response = await fetch(`${SERVER_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`Error del servidor: ${response.status}`);
            }

            const data = await response.json();
            handleResponses(data.responses);
            updateButtonState(data.saludado);

        } catch (error) {
            console.error('Error al enviar mensaje:', error);
            addMessage('Error de conexión con el servidor. ¿Está "server.py" ejecutándose?', 'warning');
        } finally {
            setInputEnabled(true); // Vuelve a habilitar la entrada
        }
    }

    /**
     * Envía una acción de botón al endpoint /action
     * @param {string} action - "descripcion", "pasos", "tips", "variaciones"
     */
    async function sendAction(action) {
        addMessage(`Solicitando: ${action}...`, 'user');
        setInputEnabled(false); // Deshabilita mientras el bot piensa

        try {
            const response = await fetch(`${SERVER_URL}/action`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: action })
            });

            if (!response.ok) {
                throw new Error(`Error del servidor: ${response.status}`);
            }

            const data = await response.json();
            handleResponses(data.responses);

        } catch (error) {
            console.error('Error al enviar acción:', error);
            addMessage('Error de conexión con el servidor.', 'warning');
        } finally {
            setInputEnabled(true); // Vuelve a habilitar la entrada
        }
    }

    /**
     * Inicializa el chat, obteniendo el mensaje de bienvenida.
     */
    async function initChat() {
        try {
            const response = await fetch(`${SERVER_URL}/init`);
            if (!response.ok) {
                throw new Error('No se puede conectar al servidor.');
            }
            const data = await response.json();
            handleResponses(data.responses);
            statusLabel.textContent = "Listo. Escribe 'hola' para empezar.";
            setInputEnabled(true); // Habilita la entrada por primera vez
            
        } catch (error) {
            console.error('Error al inicializar:', error);
            statusLabel.textContent = "Error al conectar con el servidor.";
            statusLabel.style.color = "#ff5252";
            addMessage('Error: No se pudo conectar al servidor de Python. Asegúrate de que `server.py` se está ejecutando en la terminal.', 'warning');
        }
    }

    // --- Asignación de Eventos ---
    
    // Enviar con clic
    sendButton.addEventListener('click', sendMessage);
    
    // Enviar con 'Enter'
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Clics en botones de acción
    actionButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Extrae la acción del ID (ej. "btn-descripcion" -> "descripcion")
            const action = btn.id.split('-')[1]; 
            sendAction(action);
        });
    });

    // --- Iniciar el Chat ---
    initChat();
});