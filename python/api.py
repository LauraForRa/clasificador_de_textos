import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
import unicodedata


nltk.download('stopwords')

app = Flask(__name__)  # Instancia de la aplicación Flask
CORS(app)  # Habilitar CORS si planeas hacer peticiones desde un frontend

# Cargar lista de stopwords en español y ampliarla
stop_words = set(stopwords.words('spanish'))
extra_stopwords = {'ser', 'estar', 'haber', 'tener', 'hacer', 'decir', 'ir', 'ver', 'dar',
                   'poder', 'querer', 'saber', 'pasar', 'deber', 'poner', 'parecer',
                   'quedar', 'creer', 'hablar', 'llevar', 'dejar', 'seguir', 'encontrar'}
stop_words.update(extra_stopwords)

# Cargar el modelo entrenado
model = load_model('modelo_mejorado.keras')

# Cargar el tokenizer y las categorías
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

with open('categories.pickle', 'rb') as handle:
    categories_list = pickle.load(handle)

maxlen = 350  # Debe coincidir con el valor usado durante el entrenamiento
print("Lista de categorías:", categories_list)

# Función para eliminar acentos
def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')

# Función de preprocesamiento mejorada
def preprocess_text(text):
    text = text.lower()                           # Convertir a minúsculas
    text = remove_accents(text)                   # Eliminar acentos
    text = re.sub(r'\d+', '', text)               # Eliminar números
    text = re.sub(r'[^\w\s\-]', '', text)          # Mantener guiones dentro de palabras
    text = re.sub(r'\s+', ' ', text).strip()       # Eliminar espacios extra

    # Normalizar variaciones del español
    text = text.replace('usted', 'tu').replace('vos', 'tu')

    words = text.split()
    words = [word for word in words if len(word) > 1 and word not in stop_words]  # Filtrar stopwords y palabras de 1 carácter
    return ' '.join(words)

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Intentar encontrar el primer párrafo dentro de un <article>, si existe
            if soup.find('article'):
                first_paragraph = soup.find('article').find('p')
            else:
                first_paragraph = soup.find('p')  # Si no hay <article>, tomar el primer <p>

            if first_paragraph:
                full_text = first_paragraph.get_text()
                words = full_text.split()[:30]  # Obtener solo las primeras 30 palabras
                limited_text = ' '.join(words)

                return limited_text
            else:
                print("No se encontró ningún párrafo en la página.")
                return None
        else:
            print("Error en la solicitud:", response.status_code)
            return None
    except Exception as e:
        print("Error al extraer el contenido:", e)
        return None

@app.route('/clasificar', methods=['POST'])
def clasificar():
    data = request.get_json()
    texto = data.get('texto', '')

    # Si es una URL, extraer el contenido
    if texto.strip().startswith("http"):
        extracted_text = extract_text_from_url(texto)
        
        # ✅ Imprimir el texto extraído para ver qué se está obteniendo
        print("\n=== TEXTO EXTRAÍDO DE LA URL ===")
        print(extracted_text)
        print("================================\n")

        if extracted_text is None or not extracted_text.strip():
            return jsonify({'error': 'No se pudo extraer el texto de la URL'}), 400
        
        texto = extracted_text

    if not texto.strip():
        return jsonify({'error': 'No se recibió un texto válido'}), 400

    # Preprocesar texto
    texto_preprocesado = preprocess_text(texto)

    # Tokenización y padding
    secuencia = tokenizer.texts_to_sequences([texto_preprocesado])

    # ✅ Verificar si hay palabras tokenizadas
    print("\n=== SECUENCIA TOKENIZADA ===")
    print(secuencia)
    print("===========================\n")

    if not secuencia or not secuencia[0]:
        error_msg = 'No se encontraron palabras relevantes en el texto'
        print("Error:", error_msg)
        return jsonify({'error': error_msg}), 400

    secuencia_pad = pad_sequences(secuencia, maxlen=maxlen)

    # ✅ Imprimir la forma de la secuencia de entrada al modelo
    print("\n=== FORMA DE LA SECUENCIA PAD ===")
    print(secuencia_pad.shape)
    print("=================================\n")

    # Predicción
    prediccion = model.predict(secuencia_pad)

    # ✅ Imprimir la predicción del modelo
    print("\n=== PREDICCIÓN DEL MODELO ===")
    print(prediccion)
    print("============================\n")

    # Obtener la categoría con mayor probabilidad
    categoria_index = np.argmax(prediccion)
    categoria = categories_list[categoria_index]

    return jsonify({'categoria': categoria})

if __name__ == '__main__':
    app.run(port=5000)