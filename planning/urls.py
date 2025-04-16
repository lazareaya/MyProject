# planning/urls.py
from django.urls import path
from .views import calendar_view, api_seances

urlpatterns = [
    path('', calendar_view, name='calendar_view'),
    path('api/', api_seances, name='api_seances'),
]
