import json, bson, requests, math, sys, os
import imghdr

import pandas as pd
from bs4 import BeautifulSoup
from threading import Thread

from django.http import JsonResponse, Http404
from django.utils import timezone
from django.core.management.color import no_style
from django.db import connection, transaction
from django.core.mail import EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.views.debug import ExceptionReporter
from django.conf import settings
from django.contrib import messages


from webpush.models import Group
from .notificaciones import send_notification_to_user, send_notification_to_group_thread

# *********************************************************************************
# Envia una notificación a través de la app
# *********************************************************************************
def notificar_usuario(usuario_notificado, usuario_notifica, url, mensaje = "", tipo='agradecimiento_solucion'):
    from applications.core.models import NotificacionUsuario, NotificacionUsuarioCount
    try:
        notificacion = NotificacionUsuario.objects.create(
            usuario_notificado=usuario_notificado,
            usuario_notifica=usuario_notifica,
            tipo=tipo,
            url=url,
            mensaje=mensaje,
        )

        numero_noti = NotificacionUsuarioCount.objects.get_or_create(usuario=usuario_notificado)
        count = numero_noti[0].numero + 1
        numero_noti[0].numero = count
        numero_noti[0].save()

        return notificacion
    
    except Exception as e:
        return

# *********************************************************************************
# Notifica a un usuario en la aplicación y mediante push notification
# *********************************************************************************
def notificacion_push_app_usuario(usuario_notificado, usuario_notifica, url, tipo='agradecimiento_solucion', mensaje=""):
    
    from applications.core.models import AplicacionWeb
    
    try:
        aplicacion = AplicacionWeb.objects.first()

        notificacion = notificar_usuario(
            usuario_notificado=usuario_notificado,
            usuario_notifica=usuario_notifica,
            tipo=tipo,
            url=url,
            mensaje=mensaje,
        )

        payload = {
            "head": notificacion.titulo(),
            "body": notificacion.mensaje_final(),
            'icon': aplicacion.url_safe() + aplicacion.logo_webpush.url,
            'url': url,
        }

        send_notification_to_user(usuario_notificado, payload)
        
    except Exception as e:
        print(e)
        return
# *********************************************************************************
# Notificación push Masiva
# *********************************************************************************
def notificacion_push_masiva(group_name, payload, ttl=0):
    send_notification_to_group_thread(group_name, payload, ttl)
    return

# *********************************************************************************


def reset_model(model):
    model.objects.all().delete()
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), [model])
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)
    return

def null_safe_float_to_int(value):
    if pd.isnull(value):
        return None
    else:
        return int(value)

def null_safe_string(value):
    
    if pd.isnull(value):
        return None
    else:
        return str(value)


def success_json(mensaje=None, resp=None, url=None):

    data = {'result': 'ok'}

    if resp:
        data['resp'] = resp

    if url:
        data['url'] = url
        data['redirected'] = True
    else:
        data['redirected'] = False
        
    if mensaje:
        data['mensaje'] = mensaje

    return JsonResponse(data)


def bad_json(mensaje=None, error=None, form=None, extradata=None):
    data = {'result': 'error'}
    if mensaje:
        data['mensaje'] = mensaje
    try:
        if error:
            if error >= 0:
                if error == 0:
                    data['mensaje'] = "Solicitud incorrecta"
                elif error == 1:
                    data['mensaje'] = "Error al guardar los datos"
                elif error == 2:
                    data['mensaje'] = "Error al eliminar los datos"
        if extradata:
            data.update(extradata)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse(data)
    
def error_json(mensaje=None, error=None, form=None, extradata=None):
    data = {'result': 'error'}
    if mensaje:
        data['mensaje'] = mensaje
    try:
        if error:
            if error >= 0:
                if error == 0:
                    data['mensaje'] = "Solicitud incorrecta"
                elif error == 1:
                    data['mensaje'] = "Error al guardar los datos"
                elif error == 2:
                    data['mensaje'] = "Error al eliminar los datos"
        if extradata:
            data.update(extradata)
        return JsonResponse(data, status=400)
    except Exception as ex:
        return JsonResponse(data, status=400)
    

def get_query_params(request):
    if request.method == 'GET':
        action = request.GET.get('action', '')
        data = request.GET.dict()
        if 'action' in data:
            del data['action']
        return action, data
    elif request.method == 'POST':
        action = ""
        try:
            data = json.loads(request.body)
            if 'action' in data:
                if 'action' in data:
                    action = data['action']
                else:
                    action == None
            if action == None or action == "":
                try:
                    action = request.GET.get('action', '')    
                except Exception as e:
                    action = ""
        except:
            data = request.POST.dict()
            pass
        
        if action == "" or action == None:
            action = request.POST.get('action', None)

        if action == "" or action == None:
            action = request.GET.get('action', None)
           
        return action, data

def get_hace_tiempo(created):
    ahora = timezone.now()
    diferencia = ahora - created
    segundos = round(diferencia.total_seconds())
    minutos = math.floor(segundos / 60)
    horas = math.floor(minutos / 60)
    dias = math.floor(horas / 24)
    meses = math.floor(dias / 30)

    if meses == 1:
        return "hace un mes"
    elif meses > 1:
        return f"hace {meses} meses"
    elif dias == 1:
        return f"hace {dias} día"
    elif dias > 0:
        return f"hace {dias} días"
    elif horas == 1:
        return f"hace {horas} hora"
    elif horas > 0:
        return f"hace {horas} horas"
    elif minutos == 1:
        return f"hace {minutos} minuto"
    elif minutos > 0:
        return f"hace {minutos} minutos"
    else:
        return f"hace {segundos} segundos"
    
def get_tiempo_string(tiempo):
    horas = tiempo // 3600
    tiempo = tiempo % 3600
    minutos = tiempo // 60
    tiempo = tiempo % 60
    segundos = tiempo
    
    if horas > 0 and minutos > 0 and segundos > 0:
        return f"{horas} horas {minutos} minutos {segundos} segundos"
    if horas > 0 and minutos > 0 and segundos == 0:
        return f"{horas} horas {minutos} minutos"
    if horas > 0 and minutos == 0 and segundos > 0:
        return f"{horas} horas {segundos} segundos"
    if horas > 0 and minutos == 0 and segundos == 0:
        return f"{horas} horas"
    if horas == 0 and minutos > 0 and segundos > 0:
        return f"{minutos} minutos {segundos} segundos"
    if horas == 0 and minutos > 0 and segundos == 0:
        return f"{minutos} minutos"
    else:
        return f"{segundos} segundos"
    
def get_seconds_to_string(seconds): # Convert seconds to 20:10
    
    if seconds >= 3600:
        hours = seconds // 3600
        seconds = seconds % 3600
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{hours}:{minutes}:{seconds}"
    else:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds}"
    
def check_is_superuser(request):
    if request.user.is_superuser:
        return
    else:
        raise Http404("Página no encontrada")

def get_url_params(request, exclude=['pagina']):
    url_parameters = request.GET.copy()
    
    for param in exclude:
        if param in url_parameters:
            del url_parameters[param]
    
    return url_parameters.urlencode() 


# *********************************************************************************
# Funciones para cargar imagenes a Firebase Storage
# *********************************************************************************
def upload_image_to_firebase_storage(image, bucket_name=settings.FIREBASE_BUCKET_NAME, folder=settings.TINYMCE_IMAGES_FOLDER):
    print("Estamos cargando la imagen Firebase desde Imagen")
    try:
        from firebase_admin import storage
        bucket = storage.bucket(bucket_name)
        tipo_archivo = imghdr.what(None, image.read())
        blob = bucket.blob(folder + "/" + str(bson.ObjectId()) + "." + tipo_archivo)
        image.seek(0)   # Pone el cursor al inicio del archivo
        blob.upload_from_file(image, content_type=image.content_type)
        blob.make_public()
        return blob.public_url
    except Exception as ex:
        print(ex)
        return None
    
def upload_url_image_to_firebase_storage(url, bucket_name=settings.FIREBASE_BUCKET_NAME, folder=settings.FIREBASE_IMAGES_FOLDER):
    print("Estamos cargando la imagen Firebase desde URL")
    try:
        from firebase_admin import storage
        bucket = storage.bucket(bucket_name)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.content
            tipo_archivo = imghdr.what(None, content)
            blob = bucket.blob(folder + "/" + str(bson.ObjectId()) + "." + tipo_archivo)
            blob.upload_from_string(response.content, content_type=response.headers['content-type'])
            blob.make_public()
            return blob.public_url
        else:
            print(f"Error al obtener la imagen: {response.status_code}")
            return None
    except Exception as ex:
        print(ex)
        return None
    


# *********************************************************************************
# Envio de un solo email
# *********************************************************************************
def reset_all_accounts():
    from .models import EmailCredentials
    with transaction.atomic():
        # Restablecer el conteo de todas las cuentas a 0
        EmailCredentials.objects.update(conteo=0, activo=False)
        # Activar la primera cuenta en la lista
        first_account = EmailCredentials.objects.order_by('id').first()
        if first_account is not None:
            first_account.activo = True
            first_account.save()

def get_active_email():
    from .models import EmailCredentials
    active_email = EmailCredentials.objects.filter(activo=True).first()
    if active_email is None or active_email.conteo >= 490:
        if not EmailCredentials.objects.filter(conteo__lt=490).exists():
            reset_all_accounts()
        else:
            active_email = EmailCredentials.objects.filter(conteo__lt=490, activo=True).first()
    return active_email

def send_email(subject, body, to):
    from applications.core.models import AplicacionWeb
    aplicacion = AplicacionWeb.objects.first()
    name = aplicacion.titulo_sitio if aplicacion else "Sitio Web"
    email_credentials = get_active_email()
    if email_credentials is None:
        print("No hay cuentas de correo disponibles")
        return
    try:
        
        backend = EmailBackend(
            host=email_credentials.host,
            port=email_credentials.port,
            username=email_credentials.username,
            password=email_credentials.password,
            use_tls=email_credentials.use_tls,
            use_ssl=email_credentials.use_ssl
        )

        # Check if to is a list
        if isinstance(to, list):
            to_final = to
        else:
            to_final = [to]    

        email = EmailMessage(
            subject,
            body,
            '{} <{}>'.format(name, email_credentials.username),
            to_final,
            connection=backend
        )
        email.content_subtype = "html"
        # Envía el correo
        email.send()

        email_credentials.conteo += 1
        email_credentials.save()

    except Exception as ex:
        print(f"Error al enviar el correo: {ex}")


class GroupEmailThread(Thread):
    def __init__(self, subject, body, to):
        self.subject = subject
        self.body = body
        self.to = to
        Thread.__init__(self)
        
    def run(self):
        try:
            send_email(self.subject, self.body, self.to)
        except Exception as ex:
            print(ex)
            pass
        
# Create a Thread to send the notification to group
def send_email_thread(subject, body, to):
    GroupEmailThread(subject, body, to).start()
    return


# *********************************************************************************
# Guardar errores de la aplicación
# *********************************************************************************
# Errores en la aplicacion
def save_error(request, exception, mensaje="Error general en la aplicación"):
    from .models import ErrorApp
    try:
        reporter = ExceptionReporter(request, *sys.exc_info())
        text = reporter.get_traceback_text()
        path = request.path
        url = request.META.get('HTTP_REFERER')
        user = request.user
        ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('HTTP_X_REAL_IP')
        get = request.GET.dict()
        post = request.POST.dict()
        # cookies = request.COOKIES.dict()
        # headers = request.META.dict()
        # trace = reporter.format_exception()
        user_agent = request.META.get('HTTP_USER_AGENT')

        ErrorApp.objects.create(
            path=path if path is not None else "",
            error=text if text is not None else "",
            error_str=str(exception),
            mensaje=mensaje if mensaje is not None else "",
            url=url if url is not None else "",
            user=user if user.is_authenticated else None,
            ip=ip if ip is not None else "",
            get=get if get is not None else {},
            post=post if post is not None else {},
            # cookies=cookies,
            # headers=headers,
            # trace=trace,
            user_agent=user_agent if user_agent is not None else "",
        )
        
    except Exception as ex:
        print(ex)
        return

# *********************************************************************************
# Funciones para eliminar imagenes de modelos
# *********************************************************************************
def eliminar_imagenes(sender, instance, imagen_fields, delete=False):
    if not delete:
        try:
            if instance.pk:
                antigua_instancia = sender.objects.get(pk=instance.pk)
                i = 0
                for field in imagen_fields:
                    antigua_imagen = getattr(antigua_instancia, field)
                    nueva_imagen = getattr(instance, field)
                    if antigua_imagen and nueva_imagen != antigua_imagen:
                        if os.path.isfile(antigua_imagen.path):
                            os.remove(antigua_imagen.path)
                    i += 1
                    if i > 50: # Evita un bucle infinito
                        break
        except Exception as ex:
            print(ex)
    else:
        try:
            i = 0
            for field in imagen_fields:
                imagen = getattr(instance, field)
                if imagen:
                    if os.path.isfile(imagen.path):
                        os.remove(imagen.path)
                i += 1
                if i > 50: # Evita un bucle infinito
                    break
        except Exception as ex:
            print(ex)


# *********************************************************************************
# Funciones para eliminar parrafos vacios de un HTML
# *********************************************************************************
def eliminar_parrafos_vacios(html):
    soup = BeautifulSoup(html, 'html.parser')
    # while soup.p and not soup.p.text.strip():
    #     soup.p.extract()

    # while soup.p and (not soup.p.text.strip() and not soup.p.find_all(lambda tag: tag.name == 'img')):
    #     soup.p.extract()
    while soup.p and (not soup.p.text.strip() and not soup.p.find('img')):
        soup.p.extract()
    # while soup.p and not soup.find_all('p')[-1].text.strip():
    #     soup.find_all('p')[-1].extract()
    while soup.p and (not soup.find_all('p')[-1].text.strip() and not soup.find_all('p')[-1].find('img')):
        soup.find_all('p')[-1].extract()
    # Obtener el HTML resultante
    cleaned_html = str(soup)
    # Eliminar \n y \r al principio y al final
    cleaned_html = cleaned_html.lstrip('\n\r').rstrip('\n\r')

    if cleaned_html == "":
        cleaned_html = None
    return cleaned_html




