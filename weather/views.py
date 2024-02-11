from django.shortcuts import render, redirect
from .api import weather_info
from os.path import join as path_join


def weather_search(request, *args, **kwargs):
    context = {}
    return render(request, path_join("weather", "weather_form.html"), context)


def weather_result(request, city, country, *args, **kwargs):
    req = {'city': city, 'country': country}
    context = {
        'information': weather_info(req.get('city'), req.get('country'))
        }
    if not context['information']:
        return render(request, path_join("weather", "weather_not_found.html"), {})
    return render(request, path_join("weather", "weather.html"), context)


def redirect_to_info(request, *args, **kwargs):
    req = dict(request.POST)
    if not req or not req['city'][0] or not req['country'][0]:
        return redirect(f'../')
    city, country = req.get('city')[0], req.get('country')[0]
    return redirect(f'../{city}_{country}/')

