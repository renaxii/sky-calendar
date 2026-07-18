import requests


def search_locations(query):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": query,
        "count": 5,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params
    )

    data = response.json()

    results = []

    for place in data.get("results", []):

        results.append({
            "name": place.get("name", ""),
            "state": place.get("admin1", ""),
            "country": place.get("country", ""),
            "latitude": place.get("latitude"),
            "longitude": place.get("longitude")
        })

    return results