from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo


def get_sun_times(city_name, lat, lon, selected_date):

    tf = TimezoneFinder()

    timezone_name = tf.timezone_at(
        lat=lat,
        lng=lon
    )

    if timezone_name is None:
        timezone_name = "UTC"

    timezone = ZoneInfo(timezone_name)

    location = LocationInfo(
        city_name,
        "",
        timezone_name,
        lat,
        lon
    )

    result = sun(
        location.observer,
        date=selected_date,
        tzinfo=timezone
    )

    return {
        "sunrise": result["sunrise"],
        "sunset": result["sunset"]
    }