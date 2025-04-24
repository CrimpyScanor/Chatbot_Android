from flask import Flask, request, jsonify  # Importa Flask y herramientas para manejar peticiones HTTP y respuestas JSON
import subprocess                           # Permite ejecutar comandos del sistema (como el ejecutable de llama)
import os                                   # Para funciones relacionadas al sistema operativo
import traceback                            # Para imprimir trazas detalladas en caso de errores

app = Flask(__name__)  # Crea una instancia de la aplicación Flask

# Rutas
MODEL_PATH = r"C:\Users\berna\llama.cpp\models\tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"  # Ruta absoluta del modelo GGUF
LLAMA_EXE = r"C:\Users\berna\llama.cpp\build\bin\Release\llama-simple.exe"           # Ruta absoluta del ejecutable llama-simple


# Parámetros
N_TOKENS = 128  # Número máximo de tokens a generar por respuesta del modelo


@app.route('/chat', methods=['POST'])  # Define el endpoint `/chat` que acepta solo peticiones POST
def chat():
    data = request.get_json(silent=True)  # Intenta obtener el cuerpo JSON de la petición
    if not data or 'message' not in data:  # Si no hay mensaje, responde con error
        return jsonify({"error": "No se proporcionó ningún mensaje"}), 400

    user_message = data['message']  # Extrae el mensaje del usuario
    system_prompt = "You are Ellie, a friendly assistant that speaks English."  # Mensaje de sistema que define el rol
    prompt = f"You are Ellie, a helpful assistant.\nUser: {user_message}\nEllie:"  # Prompt completo en formato instructivo


    cmd = [  # Lista de argumentos para ejecutar llama-simple
        LLAMA_EXE,             # Ejecutable
        "-m", MODEL_PATH,      # Ruta del modelo
        "-n", str(N_TOKENS),   # Número máximo de tokens
        prompt                 # Prompt a generar
    ]



    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,              # Captura la salida estándar
            stderr=subprocess.STDOUT,            # Redirige errores a stdout
            encoding="utf-8",                    # Decodifica como UTF-8
            errors="ignore"                      # Ignora errores de codificación
        )
        output_text = result.stdout.strip()      # Elimina espacios extras
        print(" Salida de Ellie:\n", output_text)  # Imprime lo generado por llama

    except Exception as e:
        traceback.print_exc()  # Imprime error con traza completa
        return jsonify({"error": f"Fallo al ejecutar el modelo: {e}"}), 500  # Respuesta de error


        # Procesar salida
    response = output_text.split("[/INST]")[-1]  # Elimina el prompt en caso de que esté presente

    # Cortar después de "Ellie:" si hay múltiples apariciones
    response = response.split("Ellie:")[-1].strip()
    if "." in response:
        response = response.split(".")[0] + "."  # Limita hasta el primer punto, para evitar textos muy largos


        # Eliminar basura
    for marker in ["llama_perf_", "main: decoded", "sampling time", "load time", "eval time", "total time"]:
        if marker in response:
            response = response.split(marker)[0]  # Si encuentra logs, los recorta


    if not response or len(response) < 3:
        response = "Sorry, I didn't understand that. Could you repeat it?"  # Mensaje predeterminado si no se obtuvo respuesta útil


    return jsonify({"response": response})  # Devuelve la respuesta al frontend (tu app en Kotlin)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Lanza la API en todas las interfaces (IP local), en el puerto 5000


#python3 Chatbot_Llama.py










