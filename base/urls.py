"""
URL configuration for base project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.views.static import serve
from django.conf import settings
from django.db import connection

# tables = connection.introspection.table_names()

urlpatterns = [
    # Add Django jet urls
    path('admin/', admin.site.urls),

    # ***************** Main *****************
    path('', include('applications.main.urls')),

    # ***************** Core *****************
    path('', include('applications.core.urls')),

    # ***************** Administracion *****************
    path('administracion/',  include('crudbuilder.urls')),
    path('administracion/', include('applications.administracion.urls')),

    # ***************** Blog *****************
    path('', include('applications.blog.urls')),

    # ***************** Third party *****************
    path('accounts/', include('allauth.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('_nested_admin/', include('nested_admin.urls')),
]

# if "django_content_type" in tables:
#     from applications.administracion.views import *

#     urlpatterns += [
#         path("adminitracion/core/alertas/", CustomAlertaListView.as_view(), name="alertas"),
#         path("adminitracion/core/alertas/<int:pk>/update/", CustomAlertaUpdateView.as_view(), name="update_alerta"),
#         path("adminitracion/core/alertas/<int:pk>/delete/", CustomAlertaDeleteView.as_view(), name="delete_alerta"),
#         path("adminitracion/core/alertas/create/", CustomAlertaCreateView.as_view(), name="create_alerta"),

#         path("adminitracion/core/usuarios/", CustomCustomUserListView.as_view(), name="usuarios"),
#         path("adminitracion/core/usuarios/<int:pk>/update/", CustomCustomUserUpdateView.as_view(), name="update_usuario"),
#         path("adminitracion/core/usuarios/<int:pk>/delete/", CustomCustomUserDeleteView.as_view(), name="delete_usuario"),
#         path("adminitracion/core/usuarios/create/", CustomCustomUserCreateView.as_view(), name="create_usuario"),
#     ]

if settings.WEBPUSH_HABILITADO:
    urlpatterns += [path('webpush/', include('webpush.urls'))]
    urlpatterns += [path('', include('pwa.urls'))]

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [path(r'static/(?P<path>.*)', serve, {'document_root': settings.STATIC_ROOT}),
                    path(r'media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}) ]
    
urlpatterns += [path("pagina/", include("django.contrib.flatpages.urls")),]