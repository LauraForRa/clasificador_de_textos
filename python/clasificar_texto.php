<?php
// El texto que queremos clasificar (esto puede ser un archivo .txt o un texto ingresado por el usuario)
$texto = "Este es un artículo sobre avances en la medicina moderna.";

$data = array(
    'texto' => $texto
);

// Configurar cURL
$ch = curl_init('http://localhost:5000/clasificar');  // URL de la API en Python
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    'Content-Type: application/json'
));

// Ejecutar la solicitud
$response = curl_exec($ch);

// Verificar si hubo algún error en la solicitud cURL
if ($response === false) {
    echo "Error en la solicitud cURL: " . curl_error($ch);
} else {
    // Verificar si la respuesta contiene la clave 'categoria'
    $response_data = json_decode($response, true);
    if (isset($response_data['categoria'])) {
        echo "Categoría predicha: " . $response_data['categoria'];
    } else {
        echo "Error en la respuesta: " . json_encode($response_data);
    }
}

// Cerrar la conexión cURL
curl_close($ch);
?>
