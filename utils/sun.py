from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo


def get_sun_times(city_name, lat, lon):

    tf = TimezoneFinder()

    timezone_name = tf.timezone_at(
        lat=lat,
        lng=lon
    )
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
        tzinfo=timezone
    )

    return {
        "sunrise": result["sunrise"],
        "sunset": result["sunset"]
    }