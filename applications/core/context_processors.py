from .models import Alerta
from applications.core.models import AplicacionWeb, Alerta
from applications.core.models import NotificacionUsuario, NotificacionUsuarioCount
from django.conf import settings
from django.utils import timezone

from applications.blog.models import Post, Categoria as CategoriaPost

def main_context(request):
    context = {}
    context['alertas'] = Alerta.objects.filter(activo=True)
    context['application'] = AplicacionWeb.objects.first()
    context['last_post'] = Post.objects.filter(activo=True).order_by('-fecha').first()

    if settings.WEBPUSH_HABILITADO:
        context['webpush_habilitado'] = True

    if request.user.is_authenticated:
        notificaciones = NotificacionUsuario.objects.filter(usuario_notificado=request.user).order_by('-id')[:5]
        num_noti = NotificacionUsuarioCount.objects.filter(usuario=request.user)
        if num_noti:
            context['num_notificaciones'] = num_noti[0].numero
        else:
            context['num_notificaciones'] = 0
        context['notificaciones'] = notificaciones
    return context
