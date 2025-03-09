import os
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Embedding, LSTM, Bidirectional, SpatialDropout1D
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.utils import to_categorical
from gensim.models import KeyedVectors
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.utils.class_weight import compute_class_weight
import unicodedata


# ===============================================================
# Cargar embeddings en español: FastText cc.es.300.vec
# Descarga el archivo desde https://fasttext.cc/docs/en/crawl-vectors.html
# y asegúrate de que esté descomprimido en la ruta especificada.
embedding_path = 'C:\\xampp\\htdocs\\laravel\\clasificador_textos_ia\\python\\fasttext-sbwc.3.6.e20.vec'  # Ruta al archivo de embeddings en español
fasttext_model = KeyedVectors.load_word2vec_format(embedding_path, binary=False)
# ===============================================================

data_folder = 'data'
categorias = {
    'deportes.txt': 'Deportes', 'economia.txt': 'Economia', 'medicina.txt': 'Medicina',
    'militar.txt': 'Militar', 'motor.txt': 'Motor', 'religion.txt': 'Religion',
    'informatica.txt': 'Informatica', 'ocio.txt': 'Ocio', 'moda.txt': 'Moda',
    'politico.txt': 'Politico', 'astronomia.txt': 'Astronomia', 'alimentacion.txt': 'Alimentacion'
}

def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

def preprocess_text(text):
    text = text.lower()                  # Convertir a minúsculas
    text = remove_accents(text)          # Eliminar acentos
    return text  # No aplicar isalnum()



texts, labels = [], []
for filename in os.listdir(data_folder):
    if filename.endswith('.txt'):
        with open(os.path.join(data_folder, filename), 'r', encoding='utf-8') as file:
            for news in file.read().split('\n'):
                if news.strip():
                    texts.append(preprocess_text(news.strip()))
                    labels.append(categorias.get(filename, ''))

categories_list = list(categorias.values())
labels = [categories_list.index(label) for label in labels]

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# Tokenización mejorada
tokenizer = Tokenizer(num_words=20000, oov_token='<OOV>')
tokenizer.fit_on_texts(X_train)
X_train_seq = tokenizer.texts_to_sequences(X_train)
X_test_seq = tokenizer.texts_to_sequences(X_test)

maxlen = 350  # Longitud del padding optimizada
X_train_pad = pad_sequences(X_train_seq, maxlen=maxlen)
X_test_pad = pad_sequences(X_test_seq, maxlen=maxlen)

embedding_dim = 300
embedding_matrix = np.zeros((len(tokenizer.word_index) + 1, embedding_dim))
for word, index in tokenizer.word_index.items():
    if word in fasttext_model:
        embedding_matrix[index] = fasttext_model[word]
    else:
        embedding_matrix[index] = np.random.normal(scale=0.6, size=(embedding_dim,))

# One-hot encoding de etiquetas
y_train_onehot = to_categorical(y_train, num_classes=len(categories_list))
y_test_onehot = to_categorical(y_test, num_classes=len(categories_list))

# Calcular pesos de clase (para datos desbalanceados)
class_weights = compute_class_weight('balanced', classes=np.unique(labels), y=labels)
class_weights = dict(enumerate(class_weights))

# Modelo mejorado con mayor número de neuronas
model = Sequential([
    Embedding(input_dim=len(tokenizer.word_index) + 1,
              output_dim=embedding_dim,
              weights=[embedding_matrix],
              input_length=maxlen,
              trainable=True),  # Fine-tuning activado para los embeddings
    SpatialDropout1D(0.2),
    Bidirectional(LSTM(128, return_sequences=True, dropout=0.2, recurrent_dropout=0.2)),
    Bidirectional(LSTM(128, dropout=0.2, recurrent_dropout=0.2)),
    Dense(256, activation='relu'),
    Dropout(0.4),
    Dense(len(categories_list), activation='softmax')
])

model.compile(loss='categorical_crossentropy',
              optimizer=Adam(learning_rate=0.0003),
              metrics=['accuracy'])

# Callbacks para detener el entrenamiento y ajustar la tasa de aprendizaje
early_stopping = EarlyStopping(monitor='val_loss', patience=7, restore_best_weights=True)
lr_reduction = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6)

# Entrenamiento
history = model.fit(X_train_pad, y_train_onehot,
                    epochs=23,
                    batch_size=64,
                    validation_data=(X_test_pad, y_test_onehot),
                    callbacks=[early_stopping, lr_reduction],
                    class_weight=class_weights)

# Evaluación
y_pred = np.argmax(model.predict(X_test_pad), axis=1)
conf_matrix = confusion_matrix(y_test, y_pred)
print(classification_report(y_test, y_pred, target_names=categories_list))

# Guardar modelo y objetos
model.save('modelo_mejorado.keras')
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open('categories.pickle', 'wb') as handle:
    pickle.dump(categories_list, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Graficar resultados
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Entrenamiento')
plt.plot(history.history['val_accuracy'], label='Validación')
plt.title('Precisión')
plt.xlabel('Épocas')
plt.ylabel('Precisión')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Entrenamiento')
plt.plot(history.history['val_loss'], label='Validación')
plt.title('Pérdida')
plt.xlabel('Épocas')
plt.ylabel('Pérdida')
plt.legend()
plt.show()

plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=categories_list, yticklabels=categories_list)
plt.title('Matriz de Confusión')
plt.xlabel('Etiqueta Predicha')
plt.ylabel('Etiqueta Verdadera')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()