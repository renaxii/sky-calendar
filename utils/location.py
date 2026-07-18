from geopy.geocoders import Nominatim


def get_coordinates(city):

    geolocator = Nominatim(user_agent="stargaze")

    location = geolocator.geocode(city)

    if location:
        return (
            location.latitude,
            location.longitude
        )

    return None, None