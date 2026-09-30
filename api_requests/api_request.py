import requests

api_key = "3db4f5a4e68dc093afb0b92208968804"
location = "Manila"

api_url = f"https://api.weatherstack.com/current?access_key={api_key}&query={location}"

def fetch_data():
    print("Fetching weather data from Weatherstack API...")
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        print("API response recieved successfully...")
        print(response.json())

    except requests.exeptions.RequestException as e:
        print(f"An error occurred: {e}")
        raise

def fetch_mock_data():
    mock_data = {'request': {'type': 'City', 'query': 'Manila, Philippines', 'language': 'en', 'unit': 'm'}, 'location': {'name': 'Manila', 'country': 'Philippines', 'region': 'Manila', 'lat': '14.604', 'lon': '120.982', 'timezone_id': 'Asia/Manila', 'localtime': '2026-10-01 03:59', 'localtime_epoch': 1790827140, 'utc_offset': '8.0'}, 'current': {'observation_time': '07:59 PM', 'temperature': 27, 'weather_code': 176, 'weather_icons': ['https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0025_light_rain_showers_night.png'], 'weather_descriptions': ['Patchy rain nearby'], 'astro': {'sunrise': '05:46 AM', 'sunset': '05:46 PM', 'moonrise': '09:23 PM', 'moonset': '09:54 AM', 'moon_phase': 'Waning Gibbous', 'moon_illumination': 78}, 'air_quality': {'co': '693', 'no2': '30.9', 'o3': '17', 'so2': '19.2', 'pm2_5': '32.8', 'pm10': '33.2', 'us-epa-index': '2', 'gb-defra-index': '2'}, 'wind_speed': 7, 'wind_degree': 93, 'wind_dir': 'E', 'pressure': 1011, 'precip': 0, 'humidity': 85, 'cloudcover': 99, 'feelslike': 30, 'uv_index': 0, 'visibility': 10, 'is_day': 'no'}}
    return mock_data