import os
import schedule
import time
from dotenv import load_dotenv
from twilio.rest import Client
from openai import OpenAI
from keep_alive import keep_alive
from datetime import datetime

# Cargar variables desde el archivo .env
load_dotenv()

# Configuración de Twilio
account_sid = os.getenv('ACCOUNT_SID')
auth_token = os.getenv('AUTH_TOKEN')
twilio_number = 'whatsapp:+14155238886'
destinatarios = os.getenv('NUMEROS').split(',')
client_twilio = Client(account_sid, auth_token)

# Configuración de OpenAI
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Función para generar mensaje
def generar_mensaje_tda():
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    hoy = datetime.now()
    fecha = f"{dias[hoy.weekday()]} {hoy.day} de {meses[hoy.month - 1]}"

    prompt = (
        "Actúa como un especialista en neurodiversidad y TDA (Trastorno por Déficit de Atención, sin hiperactividad). Cada día, escribe un mensaje breve (máximo 3 líneas) en español que sea educativo, empático y aporte un consejo, dato curioso o reflexión sobre el TDA en adultos."
        "El mensaje debe estar dirigido a una pareja adulta que está aprendiendo juntos sobre cómo afecta el TDA en la vida diaria: relaciones, trabajo, emociones, comunicación, autoestima y autocuidado."
        "Usa un lenguaje cálido, sencillo y motivador. Varía el tipo de contenido: algunos días da un consejo práctico, otros días una curiosidad científica, una estrategia emocional, una reflexión positiva o una metáfora alentadora."
        "Evita repetir frases de días anteriores. No menciones ni confundas con TDAH."
        "El tono debe ser humano, cercano y adaptado a una comunicación diaria breve y valiosa."
        "No introduzcas saludos ni despedidas, simplemente entrega el contenido principal directamente."

    )
    response = client_openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.7
    )
    contenido = response.choices[0].message.content.strip()

    mensaje_completo = (
        f"📅 *{fecha} – Frase del día sobre TDA:*\n\n"
        f"{contenido}\n\n"
        "🧠 Siempre se aprende algo nuevo."
    )

    return mensaje_completo

# Función para enviar mensaje
def enviar_mensaje():
    mensaje = generar_mensaje_tda()
    for numero in destinatarios:
        numero = numero.strip()
        message = client_twilio.messages.create(
            body=mensaje,
            from_=twilio_number,
            to=f'whatsapp:{numero}'
        )
        print(f"✅ Mensaje enviado a {numero}: {message.sid}")

# Mantener vivo el server para UptimeRobot
keep_alive()

# Programar mensaje diario
schedule.every().day.at("09:00").do(enviar_mensaje)  # Cambia la hora si quieres

# Bucle principal
while True:
    schedule.run_pending()
    time.sleep(30)  # Más rápido para ser más preciso
