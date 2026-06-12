import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        return {
            "city": city,
            "country": data["sys"]["country"],
            "latitude": data["coord"]["lat"],
            "longitude": data["coord"]["lon"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "condition": data["weather"][0]["description"]
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {city}: {e}")
        return None
    

if __name__ == "__main__":
    weather = fetch_weather("Mumbai")
    print(weather)