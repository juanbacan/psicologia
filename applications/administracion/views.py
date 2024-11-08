from bs4 import BeautifulSoup

from django.shortcuts import render, redirect
from django.views.generic import View
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.db import transaction
from django.contrib import messages
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils.text import slugify

from allauth.account.adapter import DefaultAccountAdapter as account_adapter

from applications.core.utils import get_url_params, success_json, bad_json, \
    get_query_params, send_notification_to_user, notificacion_push_masiva,\
    send_email_thread, notificar_usuario, notificacion_push_app_usuario

from applications.core.models import AplicacionWeb, Alerta
from applications.core.views import SuperuserRequiredMixin
from applications.blog.models import Post, ImagenPost
from applications.blog.models import Categoria as CategoriaBlog
from .forms import *
from django.db import connection
from crudbuilder.views import ViewBuilder

from applications.core.crud import AlertaCrud, CustomUserCrud




class AdministracionView(SuperuserRequiredMixin, View):

    def post(self, request):
        context = {}
        action, data = get_query_params(request)
        if action:
            context['action'] = action
            # ******************************************************************************************
            # Aplicación
            # ******************************************************************************************
            context['heading'] = "Aplicacion"
            context['pageview'] = "Parámetros Principales"

            if action == 'guardar_parametros_app':
                try:
                    with transaction.atomic():
                        aplicacionweb = AplicacionWeb.objects.get_or_create(id=1)[0]
                        form = AplicacionWebForm(request.POST, request.FILES, instance=aplicacionweb)
                        if form.is_valid():
                            form.save()
                            context['form'] = form
                            messages.success(request, "Datos guardados correctamente")
                            url = request.META.get('HTTP_REFERER')
                            return redirect(url)
                        else:
                            context['heading'] = "Aplicacion"
                            context['form'] = form
                            context['pageview'] = "Parámetros Principales"
                            aplicacionweb = AplicacionWeb.objects.get_or_create(id=1)[0]
                            return render(request, 'administracion/aplicacion/parametros_app.html', context)
                except Exception as ex:
                    print("Error: ", str(ex))
                    messages.error(request, "Ha ocurrido un error al guardar los datos")
                    return render(request, 'administracion/dashboard.html', context)

            context['heading'] = "Aplicacion"

            context['pageview'] = "Lista de Usuarios"
            if action == 'add_usuario':
                try:
                    with transaction.atomic():
                        form = CustomUserForm(request.POST)
                        if form.is_valid():
                            email = form.cleaned_data['email']
                            
                            generar_usuario = form.cleaned_data['generar_usuario']
                            cedula = form.cleaned_data['cedula']
                            username = form.cleaned_data['username']
                            first_name = form.cleaned_data['first_name']
                            last_name = form.cleaned_data['last_name']
                            email = form.cleaned_data['email']

                            if generar_usuario:
                                adaptador = account_adapter()
                                username = adaptador.generate_unique_username([first_name, last_name, email])
                            else:
                                username = form.cleaned_data['username']

                            usuario = CustomUser.objects.create_user(
                                cedula=cedula,
                                username=username,
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                password=cedula
                            )
                            
                            if '_addanother' in request.POST:
                                return redirect(request.path + '?action=add_usuario')
                            elif 'continue' in request.POST:
                                return redirect(request.path + '?action=edit_usuario&id=' + str(usuario.id))
                            else:
                                return redirect(request.path + '?action=usuarios')
                        else:
                            context['title'] = 'Agregar Usuario'
                            context['form'] = form
                            return render(request, 'administracion/aplicacion/add_usuario.html', context)

                except Exception as ex:
                    messages.error(request, str(ex))
                    return redirect(request.path + '?action=usuarios')

            if action == 'edit_usuario':
                try:
                    with transaction.atomic():
                        usuario = CustomUser.objects.get(id=data.get('id'))
                        form = EditUserForm(request.POST, instance=usuario)
                        if form.is_valid():
                            form.save()
                            messages.success(request, 'Usuario editado correctamente')
                            if '_addanother' in request.POST:
                                return redirect(request.path + '?action=add_usuario')
                            elif '_continue' in request.POST:
                                return redirect(request.path + '?action=edit_usuario&id=' + str(form.instance.id))
                            else:
                                return redirect(request.path + '?action=usuarios')
                        else:
                            messages.error(request, 'Error al editar el usuario')
                            context['title'] = 'Editar Usuario'
                            context['object'] = usuario
                            context['formdeleteaction'] = "del_usuario"
                            context['form'] = form
                            return render(request, 'administracion/aplicacion/add_usuario.html', context)

                except Exception as ex:
                    return bad_json(mensaje=str(ex))
                
            if action == 'edit_grupos_usuario':
                try:
                    with transaction.atomic():
                        id = data.get('id')
                        usuario = CustomUser.objects.get(pk=id)
                        form = GruposUsuarioForm(request.POST)
                        if form.is_valid():
                            grupos = form.cleaned_data.get('grupos')
                            usuario.groups.set(grupos)
                            messages.success(request, 'Grupos de usuario actualizados correctamente')
                            return success_json(mensaje="Grupos de usuario actualizados correctamente", url=request.META.get('HTTP_REFERER'))
                        else:
                            return bad_json(mensaje=form.errors)
                except Exception as ex:
                    messages.error(request, 'Error al actualizar los grupos de usuario')
                    return bad_json(mensaje=str(ex))
                
            if action == 'del_usuario':
                try:
                    with transaction.atomic():
                        id = data.get('id')
                        usuario = CustomUser.objects.get(pk=id)

                        if usuario == request.user:
                            messages.error(request, 'No puede eliminar su propio usuario')
                            return bad_json(mensaje="No puede eliminar su propio usuario")

                        usuario.is_active = False
                        usuario.save()
                        messages.success(request, 'Usuario eliminado correctamente')
                        return success_json(mensaje="Usuario eliminado correctamente", url=request.META.get('HTTP_REFERER'))
                except Exception as ex:
                    messages.error(request, 'Error al eliminar el usuario')
                    return bad_json(mensaje=str(ex))
                
            if action == 'reset_password':
                try:
                    with transaction.atomic():
                        id = data.get('id')
                        usuario = CustomUser.objects.get(pk=id)

                        if usuario == request.user:
                            messages.error(request, 'No puede restablecer su propia contraseña')
                            return bad_json(mensaje="No puede restablecer su propia contraseña")

                        usuario.set_password(usuario.cedula)
                        usuario.save()
                        messages.success(request, 'Contraseña restablecida correctamente del usuario ' + usuario.get_nombre_completo())
                        return success_json(mensaje="Contraseña restablecida correctamente", url=request.META.get('HTTP_REFERER'))
                except Exception as ex:
                    messages.error(request, 'Error al restablecer la contraseña')
                    return bad_json(mensaje=str(ex))
                
            # ******************************************************************************************
            # Notificaciones
            # ******************************************************************************************
            context['heading'] = "Notificaciones"
            context['pageview'] = "Correos"
            if action == 'notificaciones_correo_personalizado':
                try:
                    with transaction.atomic():
                        form = CorreoPersonalizadoForm(request.POST)
                        if form.is_valid():
                            context={}
                            context['title'] = form.cleaned_data['title']
                            context['message'] = form.cleaned_data['message']
                            context['button_text'] = form.cleaned_data['button_text']
                            context['button_url'] = form.cleaned_data['button_url']
                            application = AplicacionWeb.objects.first()
                            context['application'] = application
                            template = render_to_string('correo/base_correo.html', context)
                            send_email_thread(
                                subject="Prueba de Envio de Correos", 
                                body=template, 
                                to=form.cleaned_data['correo']
                            )
                            return success_json(mensaje="Correo enviado correctamente")
                        else:
                            return bad_json(mensaje=str(form.errors))
                except Exception as ex:
                    return bad_json(mensaje=str(ex))
                
            if action == 'notificaciones_correo_usuario':
                try:
                    with transaction.atomic():
                        form = CorreoUsuarioForm(request.POST)
                        if form.is_valid():
                            context={}
                            context['title'] = form.cleaned_data['title']
                            context['message'] = form.cleaned_data['message']
                            context['button_text'] = form.cleaned_data['button_text']
                            context['button_url'] = form.cleaned_data['button_url']
                            application = AplicacionWeb.objects.first()
                            context['application'] = application
                            template = render_to_string('correo/base_correo.html', context)
                            send_email_thread(
                                subject="Prueba de Envio de Correos", 
                                body=template, 
                                to=form.cleaned_data['usuario'].mi_email()
                            )
                            return success_json(mensaje="Correo enviado correctamente")
                        else:
                            return bad_json(mensaje=str(form.errors))
                except Exception as ex:
                    return bad_json(mensaje=str(ex))
                
            if action == 'notificaciones_correo_masivo':
                try:
                    with transaction.atomic():
                        form = CorreoUsuarioForm(request.POST)
                        if form.is_valid():
                            context={}
                            context['title'] = form.cleaned_data['title']
                            context['message'] = form.cleaned_data['message']
                            context['button_text'] = form.cleaned_data['button_text']
                            context['button_url'] = form.cleaned_data['button_url']
                            application = AplicacionWeb.objects.first()
                            context['application'] = application
                            template = render_to_string('correo/base_correo.html', context)
                            # send_email_thread(
                            #     subject="Prueba de Envio de Correos", 
                            #     body=template, 
                            #     to=form.cleaned_data['usuario'].mi_email()
                            # )
                            return success_json(mensaje="Correo enviado correctamente")
                        else:
                            return bad_json(mensaje=str(form.errors))
                except Exception as ex:
                    return bad_json(mensaje=str(ex))
    
            context['pageview'] = "Push y App"
            if action == 'notificaciones_push_usuario':
                try:
                    with transaction.atomic():
                        form = NotificacionPushUsuarioForm(request.POST)
                        if form.is_valid():
                            application = AplicacionWeb.objects.first()

                            if not application or not application.logo_webpush or not application.url:
                                return bad_json(mensaje="No se ha configurado la aplicación web")
                            aplicacion_url = application.url
                            if application.url[-1] == '/':
                                aplicacion_url = application.url
                            aplicacion_url = aplicacion_url + application.logo_webpush.url

                            user = form.cleaned_data['usuario']
                            payload = {
                                "head": form.cleaned_data['head'], 
                                "body": form.cleaned_data['body'],
                                'icon': aplicacion_url, 
                                'url': form.cleaned_data['url'],
                            }
                            send_notification_to_user(user=user, payload=payload)
                            return success_json(mensaje="Notificación enviada correctamente")
                        else:
                            return bad_json(mensaje=str(form.errors))
                except Exception as ex:
                    print("Error: ", str(ex))
                    return bad_json(mensaje=str(ex))
                
            if action == 'notificaciones_app_usuario':
                try:
                    with transaction.atomic():
                        form = NotificacionAppUsuarioForm(request.POST)
                        if form.is_valid():
                            usuario_notificado = form.cleaned_data['usuario_notificado']
                            tipo = form.cleaned_data['tipo_notificacion']
                            mensaje = form.cleaned_data['mensaje']
                            url = form.cleaned_data['url']
                            notificar_usuario(
                                usuario_notifica=CustomUser.objects.get(username="juanbacan"),
                                usuario_notificado=usuario_notificado,
                                tipo=tipo, 
                                mensaje=mensaje, 
                                url=url
                            )
                            return success_json(mensaje="Notificación enviada correctamente")
                        else:
                            return bad_json(mensaje=str(form.errors))
                except Exception as ex:
                    return bad_json(mensaje=str(ex))
                
            if action == 'notificaciones_pushapp_usuario':
                try:
                    with transaction.atomic():
                        form = NotificacionPushAppUsuarioForm(request.POST)
                        if form.is_valid():
                            usuario_notificado = form.cleaned_data['usuario_notificado']
                            body = form.cleaned_data['body']
                            url = form.cleaned_data['url']
                            tipo = form.cleaned_data['tipo_notificacion']
                            notificacion_push_app_usuario(
                                usuario_notifica=CustomUser.objects.get(username="juanbacan"),
                                usuario_notificado=usuario_notificado,
                                tipo=tipo,
                                url=url,
                                mensaje=body,
                            )
                            return success_json(mensaje="Notificación enviada correctamente")
                        else:
                            return bad_json(mensaje=str(form.errors))
                except Exception as ex:
                    return bad_json(mensaje=str(ex))
                
            if action == 'notificaciones_push_masiva':
                try:
                    with transaction.atomic():
                        form = NotificacionPushMasivaForm(request.POST)
                        if form.is_valid():
                            application = AplicacionWeb.objects.first()
                            if not application or not application.logo_webpush or not application.url or not application.group_name_webpush:
                                return bad_json(mensaje="No se ha configurado la aplicación web")
                            aplicacion_url = application.url
                            if application.url[-1] == '/':
                                aplicacion_url = application.url
                            aplicacion_url = aplicacion_url + application.logo_webpush.url
                            payload = {
                                "head": form.cleaned_data['head'], 
                                "body": form.cleaned_data['body'],
                                'icon': aplicacion_url, 
                                'url': form.cleaned_data['url'],
                            }
                            notificacion_push_masiva(group_name=application.group_name_webpush, payload=payload) 
                            return success_json(mensaje="Notificación enviada correctamente")
                        else:
                            return bad_json(mensaje=str(form.errors))
                except Exception as ex:
                    return bad_json(mensaje=str(ex))
                
            if action == 'notificaciones_correo_template_crear':
                try:
                    with transaction.atomic():
                        form = CorreoTemplateForm(request.POST)
                        if form.is_valid():
                            form.save()
                            return success_json(mensaje="Template creado correctamente", url = request.META.get('HTTP_REFERER'))
                        else:
                            return bad_json(mensaje=str(form.errors))
                except Exception as ex:
                    return bad_json(mensaje=str(ex))
                
            if action == 'notificaciones_correo_template_editar':
                try:
                    with transaction.atomic():
                        template = CorreoTemplate.objects.get(id=data.get('id'))
                        form = CorreoTemplateForm(request.POST, instance=template)
                        if form.is_valid():
                            form.save()
                            return success_json(mensaje="Template editado correctamente", url = request.META.get('HTTP_REFERER'))
                        else:
                            return bad_json(mensaje=str(form.errors))
                except Exception as ex:
                    return bad_json(mensaje=str(ex))
                
            if action == 'notificaciones_correo_template_eliminar':
                try:
                    with transaction.atomic():
                        template = CorreoTemplate.objects.get(id=data.get('id'))
                        template.delete()
                        return success_json(mensaje="Template eliminado correctamente", url = request.META.get('HTTP_REFERER'))
                except Exception as ex:
                    return bad_json(mensaje=str(ex))
                
            if action == 'notificaciones_correo_template_enviar':
                try:
                    with transaction.atomic():
                        form = CorreoTemplateEnviarForm(request.POST)
                        if form.is_valid():
                            template = CorreoTemplate.objects.get(id=data.get('id'))
                            context={}
                            context['title'] = template.nombre
                            context['message'] = template.html
                            context['button_text'] = template.button_text
                            context['button_url'] = template.button_url
                            application = AplicacionWeb.objects.first()
                            context['application'] = application
                            template_html = render_to_string('correo/base_correo.html', context)

                            if form.cleaned_data['masivo']:
                                print("TODO!!!!!")
                            else:
                                correo = form.cleaned_data['correo']
                                usuario = form.cleaned_data['usuario']

                                if not correo and not usuario:
                                    return bad_json(mensaje="No se ha enviado el correo ni el usuario")

                                if correo:
                                    send_email_thread(
                                        subject= template.subject,
                                        body=template_html, 
                                        to=correo
                                    )

                                elif usuario:
                                    send_email_thread(
                                        subject= template.subject,
                                        body=template_html, 
                                        to=usuario.mi_email()
                                    )

                            return success_json(mensaje="Correo enviado correctamente")
                        else:
                            return bad_json(mensaje=str(form.errors))
                except Exception as ex:
                    return bad_json(mensaje=str(ex))
            
        

    def get(self, request):
        context = {}
        action, data = get_query_params(request)
        
        try:
            with transaction.atomic():
                if action:
                    context['action'] = action
                    # ******************************************************************************************
                    # Aplicación
                    # ******************************************************************************************
                    context['heading'] = "Aplicacion"
                    
                    context['pageview'] = "Parámetros Principales"
                    if action == 'parametros_app':
                        aplicacionweb = AplicacionWeb.objects.get_or_create(id=1)[0]
                        context['form'] = AplicacionWebForm(instance=aplicacionweb)
                        return render(request, 'administracion/aplicacion/parametros_app.html', context)
                                    

                    context['pageview'] = "Lista de Usuarios"
                    if action == 'usuarios':    
                        if data.get('kword', None):
                            kword = data.get('kword')
                            usuarios = CustomUser.objects.filter(
                                Q(username__icontains=kword) |
                                Q(first_name__icontains=kword) |
                                Q(last_name__icontains=kword), is_active=True
                            )
                        else:
                            usuarios = CustomUser.objects.filter(is_active=True)
                        
                        context['usuarios'] = usuarios

                        paginator = Paginator(usuarios, 30)
                        page_number = request.GET.get('pagina', 1)
                        context['page_obj'] = paginator.get_page(page_number)
                        context['url_params'] = get_url_params(self.request)
                        return render(request, 'administracion/aplicacion/usuarios.html', context)

                    if action == 'add_usuario':
                        context['title'] = 'Agregar Usuario'
                        context['form'] = CustomUserForm()
                        return render(request, 'administracion/aplicacion/add_usuario.html', context)
                    
                    if action == 'edit_usuario':
                        context['title'] = 'Editar Usuario'
                        context['object'] = usuario = CustomUser.objects.get(id=data.get('id'))
                        context['formdeleteaction'] = "del_usuario"
                        context['form'] = EditUserForm(instance=usuario)
                        return render(request, 'administracion/aplicacion/add_usuario.html', context)

                    if action == 'edit_grupos_usuario':
                        id = data.get('id')
                        usuario = CustomUser.objects.get(pk=id)
                        context['title'] = 'Editar Grupos de Usuario'
                        context['formid'] = usuario.id
                        context['form'] = GruposUsuarioForm(initial={'grupos': usuario.groups.all()})
                        return render(request, 'forms/formModal.html', context)
                    
                    if action == 'del_usuario':
                        id = data.get('id')
                        usuario = CustomUser.objects.get(pk=id)
                        context['title'] = 'Eliminar Usuario'
                        context['message'] = '¿Está seguro de eliminar el usuario ' + usuario.username + '?'
                        context['formid'] = usuario.id
                        context['delete_obj'] = True
                        return render(request, 'forms/formModal.html', context)

                    if action == "ingresar_usuario":
                        usuario_original = request.user.id
                        id = data.get('id')
                        usuario = CustomUser.objects.get(id=id)
                        usuario.backend = 'allauth.account.auth_backends.AuthenticationBackend'
                        logout(request)
                        login(request, usuario)
                        request.session['usuario_original'] = usuario_original
                        request.session['volver_usuario'] = True
                        request.session['volver_usuario_url'] = request.META.get('HTTP_REFERER')
                        return success_json(resp = {"sessionid": request.session.session_key})
                    
                    if action == 'reset_password':
                        id = data.get('id')
                        usuario = CustomUser.objects.get(pk=id)
                        context['title'] = 'Restablecer Contraseña'
                        context['message'] = '¿Está seguro de restablecer la contraseña del usuario ' + usuario.get_nombre_completo() + '?'
                        context['formaction'] = 'reset_password'
                        context['formid'] = usuario.id
                        return render(request, 'forms/formModal.html', context)
                    
                    # ******************************************************************************************
                    # Notificaciones
                    # ******************************************************************************************
                    context['heading'] = "Notificaciones"
                    if action == 'correos':
                        context['pageview'] = "Correos"
                        templates = CorreoTemplate.objects.all()
                        context['correos'] = templates.filter(tipo='correos')
                        return render(request, 'administracion/notificaciones/correos.html', context)
                    
                    if action == 'pushapp':
                        context['pageview'] = "Push y App"
                        return render(request, 'administracion/notificaciones/pushapp.html', context)
                    
                    if action == 'notificaciones_correo_personalizado':
                        context['title'] = 'Enviar correo personalizado'
                        context['message'] = 'Se enviará un email a este correo'
                        context['form'] = CorreoPersonalizadoForm()
                        return render(request, 'forms/formModal.html', context)
                    
                    if action == 'notificaciones_correo_usuario':
                        context['title'] = 'Enviar correo a un usuario'
                        context['message'] = 'Se enviará un email al usuario seleccionado'
                        context['form'] = CorreoUsuarioForm()
                        return render(request, 'forms/formModal.html', context)
                    
                    if action == 'notificaciones_correo_masivo':
                        context['title'] = 'Enviar correo a masivo'
                        context['message'] = 'Se enviará un email a todos los usuarios activos'
                        context['form'] = CorreoMasivoForm()
                        return render(request, 'forms/formModal.html', context)
                    
                    if action == 'notificaciones_correo_template':
                        application = AplicacionWeb.objects.first()
                        context['application'] = application
                        context['title'] = 'Template Base de correos'
                        context['message'] = 'Aquí se pueden ver los templates base de correos'
                        correo_template = render_to_string('correo/base_correo.html', context)
                        context['title'] = 'Template Base de todos los correos'
                        context['body'] = correo_template
                        return render(request, 'modals/modal.html', context)    

                    if action == 'notificaciones_android_masiva':
                        context['title'] = 'Enviar notificación a todos los usuarios'
                        context['message'] = 'Se enviará una notificación a todos los usuarios'
                        context['form'] = NotificacionAndroidMasivaForm()
                        return render(request, 'forms/formModal.html', context)
                    
                    if action == 'notificaciones_correo_template_editar':
                        template = CorreoTemplate.objects.get(id=data.get('id'))
                        context['title'] = 'Editar Template'
                        context['form'] = CorreoTemplateForm(instance=template)
                        context['formid'] = template.id
                        return render(request, 'forms/formModal.html', context)

                    if action == 'notificaciones_correo_template_crear':
                        context['title'] = 'Crear Template'
                        form =  CorreoTemplateForm()
                        tipo = data.get('tipo', 'correos')
                        form.add_form(tipo)
                        context['form'] = form
                        return render(request, 'forms/formModal.html', context)
                    
                    if action == 'notificaciones_correo_template_eliminar':
                        template = CorreoTemplate.objects.get(id=data.get('id'))
                        context['title'] = 'Eliminar Template'
                        context['message'] = '¿Está seguro de que desea eliminar el template ' + template.nombre + '?'
                        context['formid'] = template.id
                        return render(request, 'forms/formModal.html', context)

                    if action == 'notificaciones_correo_template_ver':
                        context['usuario'] = request.user
                        correo = CorreoTemplate.objects.get(id=data.get('id'))
                        application = AplicacionWeb.objects.first()
                        context['application'] = application
                        context['title'] = correo.nombre
                        context['message'] = correo.html
                        context['button_text'] = correo.button_text
                        context['button_url'] = correo.button_url
                        template = render_to_string('correo/base_correo.html', context)
                        context['body'] = template
                        return render(request, 'modals/modal.html', context)

                    if action == 'notificaciones_correo_template_enviar':
                        context['title'] = 'Enviar Template'
                        template = CorreoTemplate.objects.get(id=data.get('id'))
                        context['formid'] = template.id
                        context['form'] = CorreoTemplateEnviarForm()
                        return render(request, 'forms/formModal.html', context)
                    
                    if action == 'notificaciones_push_usuario':
                        context['title'] = 'Enviar notificación push a un usuario'
                        context['message'] = 'Se enviará una notificación push al usuario seleccionado'
                        context['form'] = NotificacionPushUsuarioForm()
                        return render(request, 'forms/formModal.html', context)

                    if action == 'notificaciones_app_usuario':
                        context['title'] = 'Enviar notificación app a un usuario'
                        context['message'] = 'Se enviará una notificación app al usuario seleccionado'
                        context['form'] = NotificacionAppUsuarioForm()
                        return render(request, 'forms/formModal.html', context)

                    if action == 'notificaciones_pushapp_usuario':
                        context['title'] = 'Enviar notificación pushapp a un usuario'
                        context['message'] = 'Se enviará una notificación pushapp al usuario seleccionado'
                        context['form'] = NotificacionPushAppUsuarioForm()
                        return render(request, 'forms/formModal.html', context)

                    if action == 'notificaciones_push_masiva':
                        context['title'] = 'Enviar notificación push masiva'
                        context['message'] = 'Se enviará una notificación push a todos los usuarios'
                        context['form'] = NotificacionPushMasivaForm()
                        return render(request, 'forms/formModal.html', context)
                        
                return render(request, 'administracion/dashboard.html', context)
    
        except Exception as ex:
            print(ex)
            messages.error(request, str(ex))
            return render(request, 'administracion/dashboard.html', context)


# class BaseCrudView:
#     heading = ''
#     pageview = ''

#     def __init__(self, heading='', pageview='', *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.heading = heading or self.heading
#         self.pageview = pageview or self.pageview

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['heading'] = self.heading
#         context['pageview'] = self.pageview
#         return context
    
#     def get_additional_context(self):
#         return {}
    
# def create_custom_views_for_model(builder, heading, pageview):
#     views = builder.classes
#     custom_views = {}
    
#     # Itera sobre las vistas y agrega la clase base para el contexto
#     for view_name, view_class in views.items():
#         # Crea una nueva vista personalizada que herede de BaseCrudView
#         custom_view_class = type(
#             f"Custom{view_name}",
#             (BaseCrudView, view_class),
#             {
#                 # Sobreescribe el método get_context_data
#                 'get_context_data': lambda self, **kwargs: {**super(type(self), self).get_context_data(**kwargs), **self.get_additional_context()},
#                 'heading': heading,  # Asigna el heading específico para cada modelo
#                 'pageview': pageview  # Asigna el pageview específico para cada modelo
#             }
#         )
        
#         # Agrega la vista personalizada al diccionario
#         custom_views[view_name] = custom_view_class
#     return custom_views

# tables = connection.introspection.table_names()
# if "django_content_type" in tables:

#     builder_alerta = ViewBuilder('core', 'alerta', AlertaCrud)
#     builder_alerta.generate_crud()

#     custom_views_alerta = create_custom_views_for_model(builder_alerta, 'Aplicacion', 'Parámetros Principales')

#     # Vistas personalizadas para Alerta
#     CustomAlertaListView = custom_views_alerta['AlertaListView']
#     CustomAlertaCreateView = custom_views_alerta['AlertaCreateView']
#     CustomAlertaUpdateView = custom_views_alerta['AlertaUpdateView']
#     CustomAlertaDeleteView = custom_views_alerta['AlertaDeleteView']

#     builder_customuser = ViewBuilder('core', 'customuser', CustomUserCrud)
#     builder_customuser.generate_crud()

#     custom_views_customuser = create_custom_views_for_model(builder_customuser, 'Aplicacion', 'Parámetros Principales')

#     # Vistas personalizadas para CustomUser
#     CustomCustomUserListView = custom_views_customuser['CustomuserListView']
#     CustomCustomUserCreateView = custom_views_customuser['CustomuserCreateView']
#     CustomCustomUserUpdateView = custom_views_customuser['CustomuserUpdateView']
#     CustomCustomUserDeleteView = custom_views_customuser['CustomuserDeleteView']