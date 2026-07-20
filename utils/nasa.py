import requests

API_KEY = "bI0M5tohRc4HTs6rRHTVCCcKgxyI89Y6n9Tg0S1b"


def get_apod(selected_date):

    url = "https://api.nasa.gov/planetary/apod"

    response = requests.get(
        url,
        params={
            "api_key": API_KEY,
            "date": selected_date.isoformat()
        }
    )

    if response.ok:
        return response.json()

    return None