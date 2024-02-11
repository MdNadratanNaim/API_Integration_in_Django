from django.urls import path
from .views import weather_search, weather_result, redirect_to_info

urlpatterns = [
    path('', weather_search, name='search'),
    path('<str:city>_<str:country>/', weather_result, name='weather_info'),
    path('result/', redirect_to_info, name='redirect_to_info'),
]
