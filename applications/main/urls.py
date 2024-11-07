from django.urls import path
from .views import *

app_name = 'main'

urlpatterns = [
    # ******************* Base *******************
    path('', HomeView.as_view(), name='home'),
]   