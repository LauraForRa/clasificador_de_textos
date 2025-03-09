<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Clasificador de Noticias</title>

  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" integrity="sha512-Fo3rlrZj/k7ujTnHg4CGR2DhKNp2a3J9S/5zy1nnKcR5GjsS05Zh9fPSZpZ5T3YXxS2nuNEa6DxR5y+0ha1bEg==" crossorigin="anonymous" referrerpolicy="no-referrer"/>

  <style>
    :root {
      --bg-dark: #2B1B4E;
      --panel-bg: #3F2A5D;
      --bot-bubble: #5E3D82;
      --user-bubble: #6B4F8E;
      --text-color: #FFFFFF;
    }

    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'Poppins', sans-serif;
      color: var(--text-color);
      background: linear-gradient(135deg, var(--bg-dark) 0%, var(--panel-bg) 100%);
    }

    .light-mode {
      --bg-dark: #F5F5F5;
      --panel-bg: #E0E0E0;
      --bot-bubble: #D6D6D6;
      --user-bubble: #C0C0C0;
      --text-color: #000;
    }

    .app-container {
      display: flex;
      min-height: 100vh;
    }

    .gif-panel {
      width: 35%;
      background: url("foto_container.jpeg") center/cover no-repeat;
      height: 108vh;
    }

    .chat-panel {
      width: 65%;
      display: flex;
      flex-direction: column;
      padding: 20px;
      background-color: var(--panel-bg);
      border-radius: 0 10px 10px 0;
      box-shadow: -2px 0 8px rgba(0,0,0,0.3);
    }

    .chat-title {
      font-size: 28px;
      text-align: center;
      color: rgb(255, 0, 225);
    }

    .messages-wrapper {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      padding-bottom: 10px;
      max-height: calc(100vh - 240px); /* Limita el contenedor de los mensajes */
    }

    .messages-container {
      display: flex;
      flex-direction: column;
    }

    .bot-message {
      background-color: var(--bot-bubble);
      padding: 15px;
      border-radius: 10px;
      max-width: 70%;
      margin-bottom: 10px;
    }

    .input-container {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: auto;
    }

    .user-input {
      background-color: var(--user-bubble);
      border: none;
      border-radius: 15px;
      padding: 10px;
      color: var(--text-color);
      font-size: 16px;
      resize: vertical;
      width: 100%;
      min-height: 50px;
    }

    .file-button {
      background-color: var(--user-bubble);
      border: none;
      border-radius: 10px;
      padding: 10px 15px;
      color: var(--text-color);
      font-size: 16px;
      cursor: pointer;
    }

    .footer-banner {
      background-color: #1A1A1A;
      color: #FFFFFF;
      text-align: center;
      padding: 10px;
      font-size: 14px;
    }

    .theme-toggle {
      background: none;
      border: 2px solid #fff;
      border-radius: 25px;
      padding: 5px 15px;
      cursor: pointer;
      color: #fff;
      font-size: 18px;
    }
  </style>
</head>
<body>
  <div class="app-container">
    <div class="gif-panel"></div>

    <div class="chat-panel">
      <h1 class="chat-title">Clasificador de Textos</h1>

      <div class="messages-wrapper">
        <div class="messages-container">
          <div class="bot-message">Hola, soy Trickster. ¿Quieres saber de qué tema es tu noticia? 😊</div>
        </div>
      </div>

      <div class="input-container">
        <textarea class="user-input" placeholder="Introduce una noticia..."></textarea>
        <textarea class="user-input url-box" placeholder="Introduce una URL..."></textarea>
        <input type="file" class="file-button" accept=".txt">
      </div>

      <button class="theme-toggle">🌞/🌙</button>
    </div>
  </div>

  <footer class="footer-banner">
    Robert López | Laura Fornós |
    <a href="https://github.com/robertiki2001/clasificador_textos_ia" target="_blank">
      <i class="fab fa-github"></i> Project Github
    </a> |
    <i class="fas fa-envelope"></i> robertrlm16@gmail.com |
    <i class="fas fa-envelope"></i> laurafornosramirez@gmail.com
  </footer>

  <script>
  async function classifyText(text) {
    try {
      const response = await fetch('http://localhost:5000/clasificar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto: text })
      });

      const data = await response.json();
      
      if (data.categoria) {
        showBotMessage(`La categoría de la noticia es: ${data.categoria}`);
      } else {
        showBotMessage("Hubo un error al clasificar el texto. 😔");
      }
    } catch (error) {
      showBotMessage("No se pudo conectar con la API. Verifica que esté funcionando. 🚨");
    }
  }

  function showBotMessage(text) {
    const chatContainer = document.querySelector('.messages-container');
    const message = document.createElement('div');
    message.classList.add('bot-message');
    message.textContent = text;
    chatContainer.appendChild(message);
    document.querySelector('.messages-wrapper').scrollTop = document.querySelector('.messages-wrapper').scrollHeight;
  }

  // Manejar el evento de subida del archivo
  document.querySelector('.file-button').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    
    if (file) {
        console.log("Archivo seleccionado:", file.name, "Tamaño:", file.size);

        const reader = new FileReader();
        reader.onload = async function(e) {
            const fileContent = e.target.result.trim();  // Eliminar espacios en blanco extra
            console.log("Contenido del archivo:", fileContent || "[ARCHIVO VACÍO]");

            if (!fileContent) {
                showBotMessage("El archivo está vacío. 🚨 Intenta con otro.");
                return;
            }

            showBotMessage("Procesando archivo...");
            await classifyText(fileContent);
        };

        reader.readAsText(file);
    } else {
        showBotMessage("No se seleccionó ningún archivo. 🚨");
    }
});

// Manejar el evento de "Enter" en el textarea de URL
document.querySelector('.url-box').addEventListener('keydown', async (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    const urlInput = event.target.value.trim();
    
    if (urlInput) {
      showBotMessage("Estoy procesando la URL...");
      await classifyText(urlInput);
      event.target.value = '';
    }
  }
});

  document.querySelector('.theme-toggle').addEventListener('click', () => {
    document.body.classList.toggle('light-mode');
  });

  document.querySelector('.user-input').addEventListener('keydown', async (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      const userInput = event.target.value.trim();
      
      if (userInput) {
        showBotMessage(`Estoy procesando tu noticia...`);
        await classifyText(userInput);
        event.target.value = '';
      }
    }
  });
</script>
</body>

</html>
