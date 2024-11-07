from django.urls import path
from .views import *

app_name = 'core'

urlpatterns = [
    path('notificaciones/', NotificacionesView.as_view(), name='notificaciones'),
    path('mi_perfil/', MyUserView.as_view(), name='my_usuario'),
    #TODO: Cambiar a usuario/<int:id>/
    path('usuario/<int:id>/', MyUserView.as_view(), name='usuario'),
    path('loginModal/', LoginModalView.as_view(), name='loginModal'),
    path('model_autocomplete/', ModelAutocompleteView.as_view(), name='model_autocomplete'),
    path('api/', api, name='api_administracion'), 
    path('upload_image/', upload_image, name='upload_image'),
]
