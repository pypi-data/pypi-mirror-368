from django.urls import path

from .views import CityCHAutocompleteView

urlpatterns = [
    path('city_ch_autocomplete/', CityCHAutocompleteView.as_view(), name='city-ch-autocomplete'),
]
