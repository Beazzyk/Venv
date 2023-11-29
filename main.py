import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import json

API_URL = "https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}" \
          "&hourly=rain&daily=rain_sum&timezone=Europe%2FLondon&start_date={searched_date}&end_date={searched_date}"

def retrieve_data(latitude, longitude, searched_date):
    response = requests.get(API_URL.format(latitude=latitude, longitude=longitude, searched_date=searched_date))
    if response.status_code == 200:
        return response.json()
    else:
        return None

def find_cords(city):
    geolocator = Nominatim(user_agent="MyApp")
    location = geolocator.geocode(city)
    return location.latitude, location.longitude

def check_rain(data):
    try:
        rain_sum = data['daily']['rain_sum'][0]
        if rain_sum > 0.0:
            return "Bedzie padac"
        elif rain_sum == 0.0:
            return "Nie bedzie padac"
        else:
            return "Nie wiem"
    except (IndexError, KeyError):
        return "Nie wiem"

def save_to_file(date, result):
    try:
        with open('weather_results.json', 'r+') as file:
            data = json.load(file)
            data[date] = result
            file.seek(0)
            json.dump(data, file)
    except FileNotFoundError:
        with open('weather_results.json', 'w') as file:
            json.dump({date: result}, file)

def read_from_file(date):
    try:
        with open('weather_results.json', 'r') as file:
            data = json.load(file)
            return data.get(date)
    except FileNotFoundError:
        return None

city = input("Podaj nazwe miasta, którego chcesz sprawdzić pogodę: ")
date = input("Podaj datę, która chcesz sprawdzić (YYYY-mm-dd): ")
if not date:
    date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

result = read_from_file(date)
if result is None:
    latitude, longitude = find_cords(city)
    data = retrieve_data(latitude, longitude, date)
    if data:
        result = check_rain(data)
        save_to_file(date, result)
    else:
        result = "Nie można uzyskać danych"

print(result)