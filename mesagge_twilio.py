import os
from twilio.rest import Client
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las variables de entorno necesarias
API_KEY_WAPI = os.getenv('API_KEY_WAPI')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')
import time

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from datetime import datetime

# Configuración de la consulta y la API
query = 'Asuncion'
api_key = API_KEY_WAPI
url_clima = f'http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={query}&days=1&aqi=no&alerts=no'

# Realizar la solicitud a la API del clima
response = requests.get(url_clima)
data = response.json()

# Imprimir la cantidad de horas en el pronóstico
print(len(data['forecast']['forecastday'][0]['hour']))

def get_forecast(data, i):
    """
    Extrae la información del pronóstico para una hora específica.
    """
    hora_data = data['forecast']['forecastday'][0]['hour'][i]
    fecha = hora_data['time'].split()[0]
    hora = int(hora_data['time'].split()[1].split(':')[0])
    condicion = hora_data['condition']['text']
    tempe = float(hora_data['temp_c'])
    rain = hora_data['will_it_rain']
    prob_rain = hora_data['chance_of_rain']
    
    return fecha, hora, condicion, tempe, rain, prob_rain

# Extraer los datos del pronóstico
datos = []
for i in tqdm(range(len(data['forecast']['forecastday'][0]['hour'])), colour='green'):
    datos.append(get_forecast(data, i))

# Crear un DataFrame con los datos del pronóstico
col = ['Fecha', 'Hora', 'Condicion', 'Temperatura', 'Lluvia', 'prob_lluvia']
df = pd.DataFrame(datos, columns=col)
df = df.sort_values(by='Hora', ascending=True)

# Filtrar las horas en las que se espera lluvia
df_rain = df[(df['Lluvia'] == 1) & (df['Hora'] > 6) & (df['Hora'] < 22)]
df_rain = df_rain[['Hora', 'Condicion']]
df_rain.set_index('Hora', inplace=True)

# Crear el mensaje con el pronóstico del tiempo
message_body = f'\nHola! \n\n\n El pronostico del tiempo hoy {df["Fecha"][0]} en {query} es : \n\n\n {df_rain}'

# Esperar 2 segundos antes de enviar el mensaje
time.sleep(2)

# Configuración de Twilio
account_sid = TWILIO_ACCOUNT_SID 
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

# Enviar el mensaje usando Twilio
message = client.messages.create(
    body=message_body,
    from_=PHONE_NUMBER,
    to='+595972459748'
)

print('Mensaje Enviado Correctamente' + message.sid)
