from django.db import models

# Create your models here.
import datetime, inspect
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser, Group
from django.db.models import Q
from django.dispatch import receiver
# Create your models here.
from allauth.socialaccount.models import SocialAccount
from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up
from django_resized import ResizedImageField

from tinymce import models as tinymce_models

from .utils import get_hace_tiempo


class CustomUser(AbstractUser):
    premium = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to='usuarios', null=True, blank=True)
    # imagen = ResizedImageField(size=[300, 300], force_format="WEBP", quality=75, upload_to='usuarios', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-id', 'last_name', 'first_name']

    def get_photo_user(self):
        if self.imagen:
            return self.imagen.url
        else:
            if self.socialaccount_set.exists():
                social_account = self.socialaccount_set.first()
                return social_account.get_avatar_url()
        return None
    
    def get_nombre_completo(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        else:
            return self.username
    
    def mis_correos(self):
        return EmailAddress.objects.filter(user=self)
        
    def mis_social_accounts(self):
        return SocialAccount.objects.filter(user=self)
    
    def mi_email(self):
        correos = EmailAddress.objects.filter(user=self, verified=True)
        if correos.exists():
            return correos.first().email
        else:
            if self.email:
                return self.email
            else:
                correos = EmailAddress.objects.filter(user=self)
                if correos.exists():
                    return correos.first().email
                else:
                    return None
                
    @staticmethod
    def flexbox_query(query):
        return CustomUser.objects.filter(Q(first_name__search=query) | Q(first_name__icontains=query) | 
                                         Q(last_name__icontains=query) | Q(email__icontains=query) |
                                         Q(username__icontains=query))


class ModeloBase(models.Model):
    """
    Clase base para todos los modelos de la aplicación.
    """
    created_by = models.ForeignKey(CustomUser, related_name='%(class)s_created', editable=False, on_delete=models.SET_NULL, null=True)
    modified_by = models.ForeignKey(CustomUser, related_name='%(class)s_modified', editable=False, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if self.created_at is None:
            self.created_at = datetime.datetime.now()

        for frame_record in inspect.stack():
            if frame_record[3]=='get_response':
                request = frame_record[0].f_locals['request']
                break
            else:
                request = None

        user_id = request.user.id if request else 1
        
        if not self.pk and not self.created_by:
            self.created_by_id = user_id
        self.modified_by_id = user_id
        super(ModeloBase, self).save(*args, **kwargs)

    def get_model_info(self):
        return self._meta.app_label, self._meta.verbose_name_plural.lower()

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s' % self.id

        
class AplicacionWeb(ModeloBase):
    url = models.URLField(null=True, blank=True, max_length=200, verbose_name=u'URL SITIO')
    titulo_sitio = models.CharField(max_length=300, null=True, blank=True, verbose_name=u'Título Corto del Sitio')
    favicon = models.ImageField(upload_to='aplicacion_web', null=True, blank=True)
    logo = ResizedImageField(size=[160, 160], force_format="WEBP", quality=75, upload_to='aplicacion_web', null=True, blank=True, verbose_name=u'Logo')
    image_content = ResizedImageField(size=[1200, None], force_format="WEBP", quality=75, upload_to='aplicacion_web', null=True, blank=True, verbose_name=u'Imagen Contenido')
    # SEO
    social_images = ResizedImageField(size=[1200, None], force_format="WEBP", quality=75, upload_to='aplicacion_web', null=True, blank=True, verbose_name=u'Imagen Social')
    title = models.CharField(max_length=300, null=True, blank=True)
    meta_title = models.CharField(max_length=300, null=True, blank=True)
    meta_description = models.TextField(max_length=500, null=True, blank=True)
    # WEBPUSH
    logo_webpush = ResizedImageField(size=[300, 300], force_format="WEBP", quality=75, upload_to='aplicacion_web', null=True, blank=True)
    group_name_webpush = models.CharField(max_length=100, null=True, blank=True)
    # REDES SOCIALES
    email_contacto = models.EmailField(max_length=300, null=True, blank=True, verbose_name=u'Email de Contacto')
    celular_contacto = models.CharField(max_length=300, null=True, blank=True, verbose_name=u'Celular de Contacto')
    facebook = models.URLField(null=True, blank=True, max_length=200)
    instagram = models.URLField(null=True, blank=True, max_length=200)
    tiktok = models.URLField(null=True, blank=True, max_length=200)
    youtube = models.URLField(null=True, blank=True, max_length=200)
    linkedin = models.URLField(null=True, blank=True, max_length=200)

    def url_safe(self):
        if self.url and self.url[-1] == '/':
            return self.url[:-1]
        return self.url
    
    class Meta:
        verbose_name = 'Aplicación Web'
        verbose_name_plural = 'Aplicación Web'


CHOICES_COLOR = (
    ('primary', 'Primary'),
    ('secondary', 'Secondary'),
    ('success', 'Success'),
    ('danger', 'Danger'),
    ('warning', 'Warning'),
    ('info', 'Info'),
    ('light', 'Light'),
    ('dark', 'Dark'),
)

class Alerta(ModeloBase):
    titulo = models.CharField(max_length=100, verbose_name=u'Título')
    descripcion = tinymce_models.HTMLField(verbose_name=u'Descripción')
    color = models.CharField(max_length=100, choices=CHOICES_COLOR, null=True, blank=True)
    activo = models.BooleanField(default=False)
    url = models.URLField(null=True, blank=True, max_length=200, verbose_name=u'URL')
    orden = models.IntegerField(default=1)

    def __str__(self):
        return self.descripcion
    
    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"


class LlamadoAccion(ModeloBase):

    PAGINA_CHOICES = (
        ('home', 'Home'),
        ('pro', 'Pro'),
        ('free', 'Free'),
    )

    imagen = models.ImageField(upload_to='llamado_accion')
    url = models.URLField(max_length=200, verbose_name=u'URL')
    pagina = models.CharField(max_length=100, choices=PAGINA_CHOICES, default='home')
    activo = models.BooleanField(default=True, verbose_name=u'Activo')

    def __str__(self):
        return self.url
    
    class Meta:
        verbose_name = "Llamado a la Acción"
        verbose_name_plural = "Llamados a la Acción"


class EmailCredentials(models.Model):
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    use_tls = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    conteo = models.IntegerField(default=1)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = "Credencial de Email"
        verbose_name_plural = "Credenciales de Email"


CHOICES_TIPO_NOTIFICACION = (
    ("agradecimiento_solucion", "Agradecimiento Solucion"),
    ("comentario_solucion", "Comentario Solucion"),
    ("comentario_solucion_seguida", "Comentario Solucion Seguida"),
    ("comentario_test_personalizado", "Comentario Test Personalizado"),
    ("comentario_simulador_basico", "Comentario Simulador Basico"),
    ("comentario_simulador_avanzado", "Comentario Simulador Avanzado"),
    ("solicitud_informacion_producto", "Solicitud Informacion Producto"),
    ("nueva_orden_producto", "Nueva Orden Producto"),
    ("notificacion_personalizada", "Notificacion Personalizada")
)


class NotificacionUsuario(ModeloBase):
    usuario_notifica = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    usuario_notificado = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='usuario_notificado')
    tipo = models.CharField(max_length=100, choices=CHOICES_TIPO_NOTIFICACION)
    url = models.CharField(max_length=100)
    mensaje = models.TextField(max_length=1000)
    visto = models.BooleanField(default=False)

    def __str__(self):
        return str(self.mensaje)

    class Meta:
        verbose_name = "Notificacion Usuario"
        verbose_name_plural = "Notificaciones Usuarios"

    def get_hace_tiempo_string(self):
        return get_hace_tiempo(self.created_at)
    
    def titulo(self):
        if self.tipo == "agradecimiento_solucion":
            return "!Alguíen ha agradecido tu solución¡"
        elif self.tipo == "comentario_solucion":
            return "Hay un nuevo comentario en tu solución"
        elif self.tipo == "comentario_solucion_seguida":
            return "Hay un nuevo comentario en una solución que sigues"
        elif self.tipo == "comentario_test_personalizado":
            return "¡Hay un nuevo comentario en tu test personalizado!"
        elif self.tipo == "comentario_simulador_basico":
            return "¡Hay un nuevo comentario en tu simulador básico!"
        elif self.tipo == "comentario_simulador_avanzado":
            return "¡Hay un nuevo comentario en tu simulador avanzado!"
        elif self.tipo == "solicitud_informacion_producto":
            return "¡Hay una nueva solicitud de información de un producto!"
        elif self.tipo == "nueva_orden_producto":
            return "¡Hay una nueva orden de un producto!"
        elif self.tipo == "notificacion_personalizada":
            return "Notificación Personalizada"
        else:
            return "Notificación"
        
    def mensaje_final(self):
        if self.tipo == "agradecimiento_solucion":
            return self.usuario_notifica.username + " ha agradecido tu solución"
        elif self.tipo == "comentario_solucion":
            return self.usuario_notifica.username + " ha comentado tu solución"
        elif self.tipo == "comentario_solucion_seguida":
            return self.usuario_notifica.username + " ha comentado una solución que sigues"
        elif self.tipo == "comentario_test_personalizado":
            return self.usuario_notifica.username + " ha comentado tu test personalizado"
        elif self.tipo == "comentario_simulador_basico":
            return self.usuario_notifica.username + " ha comentado tu simulador básico"
        elif self.tipo == "comentario_simulador_avanzado":
            return self.usuario_notifica.username + " ha comentado tu simulador avanzado"
        elif self.tipo == "solicitud_informacion_producto":
            return "Alguien ha solicitado información de un producto"
        elif self.tipo == "nueva_orden_producto":
            return "Alguien ha realizado una orden de un producto"
        elif self.tipo == "notificacion_personalizada":
            return self.mensaje if self.mensaje else "Notificación Personalizada"
        else:
            return "Notificación"


# Modelo que representa el número de notificaciones que tiene un usuario
class NotificacionUsuarioCount(ModeloBase):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    numero = models.IntegerField(default=0)

    def __str__(self):
        return str(self.usuario)

    class Meta:
        unique_together = ('usuario',)
        verbose_name = "Notificacion Usuario Count"
        verbose_name_plural = "Notificaciones Usuarios Count"


class ErrorApp(ModeloBase):
    path = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    error = models.TextField()
    error_str = models.TextField()
    mensaje = models.TextField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    ip = models.CharField(max_length=255, null=True, blank=True)
    get = models.TextField(null=True, blank=True)
    post = models.TextField(null=True, blank=True)
    cookies = models.TextField(null=True, blank=True)
    headers = models.TextField(null=True, blank=True)
    trace = models.TextField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.url + " - " +  self.mensaje + " - " + self.created_at.strftime('%Y-%m-%d %H:%M:%S')
    
    class Meta:
        verbose_name = "Error de Aplicación"
        verbose_name_plural = "Errores de Aplicación"


class CorreoTemplate(ModeloBase):
    CHOICE_TIPO_CORREO = (
        ('correos', 'Correos'),
        ('inscripciones', 'Inscripciones'),
        ('premium', 'Premium'),
    )
    
    nombre = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    html = models.TextField()
    button_text = models.CharField(max_length=255, null=True, blank=True)
    button_url = models.CharField(max_length=255, null=True, blank=True)
    tipo = models.CharField(max_length=255, choices=CHOICE_TIPO_CORREO, default='correos')

    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Correo Template"
        verbose_name_plural = "Correos Templates"
    


class Modulo(ModeloBase):
    url = models.CharField(max_length=255)
    nombre = models.CharField(max_length=255)
    icon = models.CharField(max_length=255)
    orden = models.IntegerField(default=1)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Módulo"
        verbose_name_plural = "Módulos"
        ordering = ['orden']


class GrupoModulo(ModeloBase):
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE)
    modulos = models.ManyToManyField(Modulo)

    def __str__(self):
        return self.grupo.name
    
    class Meta:
        verbose_name = "Módulos de un Grupo"
        verbose_name_plural = "Grupos  de Módulos"
        ordering = ['grupo__name']