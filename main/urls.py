from django.urls import path
from .controllers.home import home

urlpatterns = [
    path('', home),
]
