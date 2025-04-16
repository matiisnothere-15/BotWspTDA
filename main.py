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

# Configuración de OpenAI usando nueva API
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Generar mensaje con OpenAI (con fecha + frase personalizada)
def generar_mensaje_tda():
    # Obtener fecha actual formateada en español (manual por compatibilidad)
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    hoy = datetime.now()
    fecha = f"{dias[hoy.weekday()]} {hoy.day} de {meses[hoy.month - 1]}"

    # Prompt para OpenAI
    prompt = (
        "Actúa como un especialista en neurodiversidad. Cada día, genera un mensaje educativo, empático y útil sobre el Trastorno por Déficit de Atención (TDA, sin hiperactividad). "
        "El objetivo es enseñar algo nuevo a una pareja adulta que quiere aprender día a día sobre cómo funciona el TDA, sus efectos en la vida cotidiana y formas de afrontarlo con comprensión y cariño. "
        "Usa lenguaje sencillo y cálido. El mensaje debe ser breve (máximo 3 líneas). En español. No repitas lo mismo cada día. Evita la palabra TDAH."
    )
    response = client_openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.7
    )
    contenido = response.choices[0].message.content.strip()

    mensaje_completo = (
        f"📅 *{fecha} – Frase del día sobre TDA:*\n\n"
        f"{contenido}\n\n"
        "🧠 siempre se aprende algo nuevo."
    )

    return mensaje_completo

# Enviar mensaje por WhatsApp
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

# Servidor para mantener el bot vivo (UptimeRobot)
keep_alive()


# Programar envío diario a las 09:00 AM hora Chile (13:00 UTC)
schedule.every().day.at("13:00").do(enviar_mensaje)




# Loop principal
while True:
    schedule.run_pending()
    time.sleep(60)
