import requests

def get_weather(lat, lon, units):

    temperature_unit = "fahrenheit" if units == "imperial" else "celsius"

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&temperature_unit={temperature_unit}"
        "&current=temperature_2m,"
        "cloud_cover,"
        "relative_humidity_2m"
    )

    response = requests.get(url)
    data = response.json()
    current = data["current"]

    return {
        "temperature": current["temperature_2m"],
        "clouds": current["cloud_cover"],
        "humidity": current["relative_humidity_2m"]
    }