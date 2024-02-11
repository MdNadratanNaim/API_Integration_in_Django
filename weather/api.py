import requests
# Key from https://openweathermap.org & https://ipgeolocation.io
from .api_keys import open_weather_key, ip_geolocation_key
from time import gmtime, strftime


def try_to_parse(resp, *args):

    def open_dictionary(first, second):
        try:
            return first[second]
        except KeyError:
            return None

    for i in args:
        resp = open_dictionary(resp, i)
        if not resp:
            return None
    
    return resp


def epoch_to_date_time(epoch):
    if not epoch:
        return None

    return strftime("%Y-%m-%d %H:%M:%S", gmtime(epoch))


def gather_info(resp):

    # ********************************* Collect data from open weather api response ********************************* #

    info_dict = {
        'longitude': try_to_parse(resp, 'coord', 'lon'),
        'latitude': try_to_parse(resp, 'coord', 'lat'),
        'weather_id': try_to_parse(resp, 'weather', 0, 'id'),
        'weather_status': try_to_parse(resp, 'weather', 0, 'main'),
        'description': try_to_parse(resp, 'weather', 0, 'description'),
        'icon': try_to_parse(resp, 'weather', 0, 'icon'),
        'temperature': round(try_to_parse(resp, 'main', 'temp'), 2),  # °C
        'feels_like': round(try_to_parse(resp, 'main', 'feels_like'), 2),  # °C
        'pressure': round(try_to_parse(resp, 'main', 'pressure') * 0.0009869233, 8),  # atm
        'humidity': try_to_parse(resp, 'main', 'humidity'),  # %
        'visibility': try_to_parse(resp, 'visibility'),  # meter
        'wind_speed': try_to_parse(resp, 'wind', 'speed'),  # meter/sec
        'wind_direction_in_degree': try_to_parse(resp, 'wind', 'deg'),  # °
        'wind_gust': try_to_parse(resp, 'wind', 'gust'),  # meter/sec
        'cloudiness': try_to_parse(resp, 'clouds', 'all'),  # %
        'rain_volume_last_1hour': try_to_parse(resp, 'rain', '1h'),
        'rain_volume_last_3hour': try_to_parse(resp, 'rain', '3h'),
        'show_volume_last_1hour': try_to_parse(resp, 'snow', '1h'),
        'show_volume_last_3hour': try_to_parse(resp, 'snow', '3h'),
        'time_of_data_calculation': epoch_to_date_time(try_to_parse(resp, 'dt')),
        'country_code': try_to_parse(resp, 'sys', 'country'),
        'sunrise_unix': try_to_parse(resp, 'sys', 'sunrise'),
        'sunset_unix': try_to_parse(resp, 'sys', 'sunset'),
        'timezone_shift_from_utc_in_sec': try_to_parse(resp, 'timezone'),
        'city_name': try_to_parse(resp, 'name'),
    }

    # ********************************* Call timezone api & collect data ********************************* #

    timezone_info_dict = timezone_info(lat=info_dict['latitude'], lon=info_dict['longitude'])

    info_dict.update({
        'timezone_area': try_to_parse(timezone_info_dict, 'timezone'),
        'timezone_shift_from_utc_in_hour_coefficient': try_to_parse(timezone_info_dict, 'timezone_offset'),
        'local_date': try_to_parse(timezone_info_dict, 'date'),
        'local_date_time': try_to_parse(timezone_info_dict, 'date_time'),
        'local_date_time_text': try_to_parse(timezone_info_dict, 'date_time_text'),
        'local_date_time_wti': try_to_parse(timezone_info_dict, 'date_time_wti'),
        'local_date_time_ymd': try_to_parse(timezone_info_dict, 'date_time_ymd'),
        'local_time_in_unix': try_to_parse(timezone_info_dict, 'date_time_unix'),
        'local_time': try_to_parse(timezone_info_dict, 'time_24'),
    })

    # ********************************* Using above dictionary to calculate info ********************************* #

    # See it's day or night
    day_night_dct = {'n': 'Night', 'd': 'Day'}
    info_dict.update({'day_night': day_night_dct[info_dict['icon'][-1]] if info_dict['icon'] else None})

    # Decorate timezone
    timezone_undecorated = info_dict['local_date_time_wti'].split()[-1] if info_dict['local_date_time_wti'] else None
    info_dict.update({
        'timezone_decorated': f'{timezone_undecorated[:3]}:{timezone_undecorated[3:]}'
        if timezone_undecorated else None
    })

    # Wind direction in text
    N, E, W, S, ss = "North", "East", "West", "South", " "
    wind_direction_list = (N, N+ss+E, N+ss+E, E, E, S+ss+E, S+ss+E, S, S, S+ss+W, S+ss+W, W, W, N+ss+W, N+ss+W, N)
    info_dict.update({
        'wind_direction_in_text': wind_direction_list[int(info_dict['wind_direction_in_degree'] // 22.5)]
        if info_dict['wind_direction_in_degree'] else None
    })

    # Covert unix time to readable date time
    info_dict.update({
        'sunrise': epoch_to_date_time(info_dict['sunrise_unix']),
        'sunset': epoch_to_date_time(info_dict['sunset_unix']),
    })

    return info_dict


def timezone_info(lat: str, lon: str):
    response = requests.get(f"https://api.ipgeolocation.io/timezone?apiKey={ip_geolocation_key}&lat={lat}&long={lon}").json()
    return response


def weather_info(city: str, country: str):
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&APPID={open_weather_key}&units=metric").json()
    if 'cod' in response and response['cod'] != 200:
        return None
    else:
        return gather_info(response)
