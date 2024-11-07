import requests, bson, os

from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib import messages
from django import forms
from django.apps import apps
from django.conf import settings
from django.core.paginator import Paginator

from firebase_admin import storage
from allauth.account.adapter import DefaultAccountAdapter as account_adapter
from allauth.socialaccount.models import SocialAccount
from allauth.account.models import EmailAddress
import allauth.account.forms as forms
from dal import autocomplete

from .models import NotificacionUsuario, NotificacionUsuarioCount, CustomUser
from .forms import FormularioUsuario, EditUsuarioForm

from applications.core.utils import bad_json, success_json, get_query_params, \
    save_error, get_url_params, upload_image_to_firebase_storage

# Create your views here.
class NotificacionesView(LoginRequiredMixin, ListView):
    template_name = 'core/notificaciones/notificaciones.html'
    context_object_name = 'notificaciones'
    paginate_by = 20
    page_kwarg = 'pagina'
    model = NotificacionUsuario

    def get_queryset(self):
        usuario = self.request.user
        return NotificacionUsuario.objects.filter(usuario_notificado=usuario).order_by('-id')
    

class MyUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            action, data = get_query_params(request)
            context = {}
            if action:  
                context['action'] = action  

                if action == 'edit_perfil':
                    context['title'] = "Editar perfil"
                    context['action'] = "edit_perfil"
                    context["form"] = EditUsuarioForm(initial={
                        "username": request.user.username,
                        "nombres": request.user.first_name,
                        "apellidos": request.user.last_name,
                        "email": request.user.email,
                    })
                    return render(request, 'core/usuarios/edit_perfil.html', context)
                
            else:
                usuario = request.user

                tp = 'perfil'
                if 'tp' in request.GET:
                    tp = request.GET['tp']
                context["tp"] = tp

                if tp == 'perfil': # Perfil de usuario
                    context["form"] = FormularioUsuario(initial={
                        "username": request.user.username,
                        "nombres": request.user.first_name,
                        "apellidos": request.user.last_name,
                        "nombre_visible": request.user.get_nombre_completo,
                        "email": request.user.email,
                    })

                    return render(request, 'core/usuarios/usuario_perfil.html', context)
                                        
        except Exception as ex:
            print(ex)
            save_error(request, ex, "MY_USER_VIEW GET")
            return bad_json(error=ex)

    def post(self, request, *args, **kwargs):
        try:
            action, data = get_query_params(request)
            user = request.user
            context = {}
            context['action'] = action

            if not action:
                return bad_json(mensaje="No se ha enviado el parametro action")
            
            if action == 'edit_perfil':
                form = EditUsuarioForm(request.POST)
                if form.is_valid():
                    username = form.cleaned_data['username']
                    email = form.cleaned_data['email']
                    if CustomUser.objects.filter(username=username).exclude(id=user.id).exists():
                        return bad_json(mensaje="El nombre de usuario ya existe")
                    
                    if CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
                        return bad_json(mensaje="El correo electrónico ya existe")

                    user.username = form.cleaned_data['username']
                    user.first_name = form.cleaned_data['nombres']
                    user.last_name = form.cleaned_data['apellidos']
                    user.email = form.cleaned_data['email']
                    user.save()

                    if 'imagen' in request.FILES:
                        imagen = request.FILES['imagen']
                        user.imagen = imagen
                        user.save()
                    else:
                        user.imagen = None
                        user.save()

                    if 'fondo_horizontal' in request.FILES:
                        fondo_horizontal = request.FILES['fondo_horizontal']
                        perfil = user.mi_perfil_profesor()
                        perfil.fondo_horizontal = fondo_horizontal
                        perfil.save()
                    else:
                        perfil = user.mi_perfil_profesor()
                        perfil.fondo_horizontal = None
                        perfil.save()

                    if 'fondo_cuadrado' in request.FILES:
                        fondo_cuadrado = request.FILES['fondo_cuadrado']
                        perfil = user.mi_perfil_profesor()
                        perfil.fondo_cuadrado = fondo_cuadrado
                        perfil.save()
                    else:
                        perfil = user.mi_perfil_profesor()
                        perfil.fondo_cuadrado = None
                        perfil.save()

                    url = reverse_lazy('core:my_usuario') + "?tp=perfil"
                    return success_json(mensaje="Perfil actualizado", url=url)
                else:
                    return bad_json(mensaje="Error al actualizar el perfil")


        except Exception as ex:
            print(ex)
            save_error(request, ex, "MY_USER_VIEW POST")
            return bad_json(mensaje=str(ex))


@csrf_exempt
def one_tap_google_login(request):
    try:
        credential = request.POST.get('credential')
        resp = requests.post('https://oauth2.googleapis.com/tokeninfo?id_token=' + credential)
        if resp.status_code != 200:
            # Manejar el error de acuerdo a tus necesidades
            return HttpResponse('Error: ' + resp.text)
        data = resp.json()
        extra_data = {
            'id': data['sub'] if 'sub' in data else None,
            'email': data['email'] if 'email' in data else None,
            'verified_email': data['email_verified'] if 'email_verified' in data else None,
            'name': data['name'] if 'name' in data else None,
            'given_name': data['given_name'] if 'given_name' in data else None,
            'family_name': data['family_name'] if 'family_name' in data else None,
            'picture': data['picture'] if 'picture' in data else None,
            'locale': 'es',
        }
        
        social = SocialAccount.objects.filter(uid=data['sub'], provider='google').exists()

        if social:
            user = SocialAccount.objects.get(uid=data['sub'], provider='google').user

            try:
                email = EmailAddress.objects.get_or_create(
                    user=user,
                    email=data['email'],
                )
                email[0].verified = data['email_verified'].capitalize()
                email[0].save()
            except Exception as ex:
                save_error(request, ex, "ONE TAP GOOGLE LOGIN 2")
                pass

            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            messages.success(request, 'Ha iniciado sesión sesión exitosamente como ' + user.username)
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            try:
                # user = CustomUser.objects.get(email=data['email'])
                email = EmailAddress.objects.get(email=data['email'])
                if email.verified:
                    user = email.user
                    social = SocialAccount.objects.create(
                        user=user,
                        uid=data['sub'],
                        provider='google',
                        extra_data=extra_data
                    )
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    messages.success(request, 'Ha iniciado sesión sesión exitosamente como ' + user.username)
                    login(request, user)
                    return redirect(request.META.get('HTTP_REFERER', '/'))
                
                else:
                    form = forms.Form()
                    form.cleaned_data = {
                        'first_name': data['given_name'] if 'given_name' in data else None,
                        'last_name': data['family_name'] if 'family_name' in data else None,
                        'email': data['email'],
                    }

                    new_user = account_adapter().new_user(request)
                    usuario = account_adapter().save_user(request, new_user, form=form)            

                    social = SocialAccount.objects.create(
                        user=usuario,
                        uid=data['sub'],
                        provider='google',
                        extra_data=extra_data
                    )

                    EmailAddress.objects.create(
                        user=usuario,
                        email=data['email'],
                        verified=data['email_verified'].capitalize(),
                        primary=True
                    )

                    usuario.backend = 'django.contrib.auth.backends.ModelBackend'
                    messages.success(request, 'Ha iniciado sesión sesión exitosamente como ' + usuario.username)
                    login(request, usuario)
                    return redirect(request.META.get('HTTP_REFERER', '/'))

            except EmailAddress.DoesNotExist:

                form = forms.Form()
                form.cleaned_data = {
                    'first_name': data['given_name'] if 'given_name' in data else None,
                    'last_name': data['family_name'] if 'family_name' in data else None,
                    'email': data['email'],
                }

                new_user = account_adapter().new_user(request)
                usuario = account_adapter().save_user(request, new_user, form=form)            

                social = SocialAccount.objects.create(
                    user=usuario,
                    uid=data['sub'],
                    provider='google',
                    extra_data=extra_data
                )

                EmailAddress.objects.create(
                    user=usuario,
                    email=data['email'],
                    verified=data['email_verified'].capitalize(),
                    primary=True
                )
                
                usuario.backend = 'django.contrib.auth.backends.ModelBackend'
                messages.success(request, 'Ha iniciado sesión sesión exitosamente como ' + usuario.username)
                login(request, usuario)
                return redirect(request.META.get('HTTP_REFERER', '/'))
    except Exception as ex:
        save_error(request, ex, "ONE TAP GOOGLE LOGIN")
        return redirect('account_login')


def api(request):
    action, data = get_query_params(request)

    if not action:
        return bad_json(mensaje="No se ha enviado el parametro action")
    if not request.user.is_authenticated:
        return bad_json(mensaje="No estás autenticado")

    if request.method == 'POST':
        try:    
            if action == 'reset_notificacion':
                user_id = data.get('user_id', None)
                if user_id:
                    NotificacionUsuarioCount.objects.filter(usuario_id=user_id).update(numero=0)
                return success_json(mensaje="Notificacion reseteada")
            
            elif action == 'ver_notificacion':
                id = data.get('id', None)
                if id:
                    NotificacionUsuario.objects.filter(id=id).update(visto=True)
                return success_json(mensaje="Notificacion vista")


            return bad_json(mensaje="No se encuentra la accion")
        
        except Exception as ex:
            save_error(request, ex, "API MAIN")
            return bad_json(mensaje="Ha ocurrido un error")
        

    if request.method == 'GET':
        if action == "volver_usuario":
            if request.session.get('volver_usuario', None) and request.session.get('usuario_original', None):
                usuario = CustomUser.objects.get(id=request.session['usuario_original'])
                usuario.backend = 'allauth.account.auth_backends.AuthenticationBackend'
                url = request.session.get('volver_usuario_url', "/administracion")
                logout(request)
                login(request, usuario)
                if "volver_usuario" in request.session:
                    del request.session['volver_usuario']
                if "volver_usuario_url" in request.session:
                 del request.session['volver_usuario_url']
                if "usuario_original" in request.session:
                    del request.session['usuario_original']
                return redirect(url)
            else:
                return redirect('/')

    else:
        return success_json(mensaje = "Ok")
    

class ModelAutocompleteView(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        model = self.forwarded.get('model', None)

        if model:
            try:
                model = apps.get_model('main', model)
            except:
                pass
            try:
                model = apps.get_model('core', model)
            except:
                pass
            try:
                model = apps.get_model('ecommerce', model)
            except:
                pass
            
            if self.q:
                qs = model.flexbox_query(self.q)
            else:
                qs = model.objects.all()
            return qs
        return 
    

@csrf_exempt
@login_required
def upload_image(request, series: str=None, article: str=None): 
       
    if request.method != "POST":
        return JsonResponse({'Error Message': "Wrong request"})
    
    if request.user.is_anonymous:
        return JsonResponse({'Error Message': "You are not authenticated"})

    file_obj = request.FILES['file']
    file_name_suffix = file_obj.name.split(".")[-1]
    if file_name_suffix not in ["jpg", "png", "gif", "jpeg", "webp"]:
        return JsonResponse({"Error Message": f"Wrong file suffix ({file_name_suffix}), supported are .jpg, .png, .gif, .webp, .jpeg"})

    if not settings.HABILITADO_FIREBASE:
        file_path = os.path.join(settings.MEDIA_ROOT, 'cargadas', file_obj.name)
        try:
            with open(file_path, 'wb+') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)
        except Exception as ex:
            # Crear carpeta si no existe
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'cargadas_tiny'), exist_ok=True)
            with open(file_path, 'wb+') as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)

        return JsonResponse({
            'message': 'Image uploaded successfully',
            'location': os.path.join(settings.MEDIA_URL, 'cargadas', file_obj.name)
        })
    else: 
        url = upload_image_to_firebase_storage(file_obj)        
        
        return JsonResponse({
            'message': 'Image uploaded successfully',
            'location': url
        })


class SuperuserRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseRedirect("/")
        return super().dispatch(request, *args, **kwargs)
    

class ProfesorRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.es_profesor():
            return HttpResponseRedirect("/perfil/")
        return super().dispatch(request, *args, **kwargs)
    

class LoginModalView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['form'] = forms.LoginForm()
        return render(request, 'forms/formLoginModal.html', context)
    