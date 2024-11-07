# from re import template
from django.urls import path

from . import views


urlpatterns = [
    path('', views.AdministracionView.as_view(), name='administracion'),
]
