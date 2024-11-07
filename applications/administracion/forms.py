from django import forms
from django.utils.safestring import mark_safe
from django.core.validators import FileExtensionValidator
from django.contrib.flatpages.models import FlatPage
from django.contrib.auth.models import Group

# import datetime
from datetime import datetime

from tinymce.widgets import TinyMCE
from dal import autocomplete, forward

from applications.core.forms import BaseForm, ModelBaseForm
from applications.core.models import CHOICES_TIPO_NOTIFICACION, CorreoTemplate, CustomUser, AplicacionWeb, Alerta, \
    LlamadoAccion
from applications.blog.models import Post
from applications.blog.models import Categoria as CategoriaBlog

class ActualizarTablasForm(BaseForm):
    archivo = forms.FileField(required=True, label="Archivo", validators=[FileExtensionValidator( ['xlsx'] ) ])
    
TINYMCE_DEFAULT_CONFIG2 = {
    "theme": "silver",
    "height": 400,
    "menubar": False,
    "plugins": "preview,advlist,lists,link,image,charmap,image,media,table",
    # "external_plugins": {
    #     "tiny_mce_wiris": 'https://www.wiris.net/demo/plugins/tiny_mce/plugin.min.js',                  
    # },
    "toolbar":  "image | blocks | "
    "bold italic | alignleft aligncenter "
    "| bullist numlist | "
    # "tiny_mce_wiris_formulaEditor tiny_mce_wiris_formulaEditorChemistry "
    "table superscript subscript charmap preview",
    "images_upload_url": "/upload_image/",
    # "document_base_url": "https://goeducativa.com/",
    "relative_urls": False,
    "convert_urls": False,
}

# *****************************************************************************************************
# Sección Aplicación
# *****************************************************************************************************
class AplicacionWebForm(ModelBaseForm):
    class Meta:
        model = AplicacionWeb
        fields = '__all__'
        # exclude = []
        labels = {
            'descripcion': 'Descripción',
        }
        widgets = {
            'meta_description': forms.Textarea(attrs={'rows': 2}),
        }

class CustomUserForm(BaseForm):
    cedula = forms.CharField(max_length=100, label='Cédula')
    first_name = forms.CharField(max_length=100, label='Nombre')
    last_name = forms.CharField(max_length=100, label='Apellido')
    email = forms.EmailField(max_length=100, label='Correo Electrónico')
    generar_usuario = forms.BooleanField(required=False, label='Generar Usuario', initial=True,
            widget=forms.CheckboxInput(attrs={'separator': 'Si selecciona esta opción, se generará un usuario con la información ingresada'}))
    username = forms.CharField(max_length=100, label='Nombre Usuario', required=False)

    def clean(self):
        cleaned_data = super().clean()

        # If generar_usuario is checked, the usuario field is required
        generar_usuario = cleaned_data.get("generar_usuario")
        username = cleaned_data.get("username")
        if not generar_usuario and not username:
            self.add_error('username', 'Este campo es obligatorio si desea generar un usuario')

        if not generar_usuario:
            if CustomUser.objects.filter(username=username).exists():
                self.add_error('username', 'El nombre de usuario ya está en uso')
            
        if CustomUser.objects.filter(cedula=cleaned_data.get("cedula")).exists():
            self.add_error('cedula', 'La cédula ya está en uso')
        
        if CustomUser.objects.filter(email=cleaned_data.get("email")).exists():
            self.add_error('email', 'El correo electrónico ya está en uso')
        
        return cleaned_data
    
class EditUserForm(ModelBaseForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'username': 'Nombre de Usuario',
        }
    
    def clean(self):
        cleaned_data = super().clean()

        if CustomUser.objects.filter(username=cleaned_data.get("username")).exclude(pk=self.instance.pk).exists():
            self.add_error('username', 'El nombre de usuario ya está en uso')
        
        if CustomUser.objects.filter(email=cleaned_data.get("email")).exclude(pk=self.instance.pk).exists():
            self.add_error('email', 'El correo electrónico ya está en uso')
        
        return cleaned_data
    
class GruposUsuarioForm(BaseForm):
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), 
        required=False, label='Grupos',
        widget=autocomplete.Select2Multiple()
    )
    

# *****************************************************************************************************
# Sección Notificaciones
# *****************************************************************************************************

class NotificacioWebPushForm(BaseForm):
    head = forms.CharField(required=True, label="Encabezado")
    body = forms.CharField(required=True, label="Cuerpo")
    url = forms.CharField(required=True, label="URL")

class CorreoPersonalizadoForm(BaseForm):
    correo = forms.EmailField(max_length=100, label='Correo Electrónico')
    title = forms.CharField(max_length=500, label='Título')
    message = forms.CharField(required=True, label="Mensaje", widget=TinyMCE(mce_attrs = TINYMCE_DEFAULT_CONFIG2))
    button_text = forms.CharField(max_length=200, label='Texto del Botón')
    button_url = forms.CharField(max_length=200, label='Link del Botón')

class CorreoUsuarioForm(BaseForm):
    usuario = forms.ModelChoiceField(label="Usuario", queryset=CustomUser.objects.all(), required=True,
            widget=autocomplete.ModelSelect2(
                url='core:model_autocomplete',
                forward=(forward.Const('CustomUser', 'model'), ),
                attrs={'data-html': True},
            ))
    title = forms.CharField(max_length=500, label='Título')
    message = forms.CharField(required=True, label="Mensaje", widget=TinyMCE(mce_attrs = TINYMCE_DEFAULT_CONFIG2))
    button_text = forms.CharField(max_length=200, label='Texto del Botón')
    button_url = forms.CharField(max_length=200, label='Link del Botón')

class CorreoMasivoForm(BaseForm):
    title = forms.CharField(max_length=500, label='Título')
    message = forms.CharField(required=True, label="Mensaje", widget=TinyMCE(mce_attrs = TINYMCE_DEFAULT_CONFIG2))
    button_text = forms.CharField(max_length=200, label='Texto del Botón')
    button_url = forms.CharField(max_length=200, label='Link del Botón')

class NotificacionPushUsuarioForm(BaseForm):
    usuario = forms.ModelChoiceField(label="Usuario", queryset=CustomUser.objects.all(), required=True,
            widget=autocomplete.ModelSelect2(
                url='core:model_autocomplete',
                forward=(forward.Const('CustomUser', 'model'), ),
                attrs={'data-html': True},
            ))
    head = forms.CharField(required=True, label="Encabezado")
    body = forms.CharField(required=True, label="Cuerpo", widget=forms.Textarea(attrs={'rows': 3}))
    url = forms.CharField(required=True, label="URL")

class NotificacionAppUsuarioForm(BaseForm):
    usuario_notificado = forms.ModelChoiceField(label="Usuario", queryset=CustomUser.objects.all(), required=True,
            widget=autocomplete.ModelSelect2(
                url='core:model_autocomplete',
                forward=(forward.Const('CustomUser', 'model'), ),
                attrs={'data-html': True},
            ))
    tipo_notificacion = forms.ChoiceField(required=True, label="Tipo de Notificación", choices=CHOICES_TIPO_NOTIFICACION)  
    # mensaje is a tinycme field
    # mensaje = forms.CharField(required=True, label="Mensaje", widget=TinyMCE(mce_attrs = TINYMCE_DEFAULT_CONFIG2))
    mensaje = forms.CharField(required=True, label="Mensaje", widget=forms.Textarea(attrs={'rows': 3}))
    url = forms.CharField(required=True, label="URL")

class NotificacionPushAppUsuarioForm(BaseForm):
    usuario_notificado = forms.ModelChoiceField(label="Usuario", queryset=CustomUser.objects.all(), required=True,
            widget=autocomplete.ModelSelect2(
                url='core:model_autocomplete',
                forward=(forward.Const('CustomUser', 'model'), ),
                attrs={'data-html': True},
            ))
    body = forms.CharField(required=True, label="Cuerpo", widget=forms.Textarea(attrs={'rows': 3}))
    url = forms.CharField(required=True, label="URL")
    tipo_notificacion = forms.ChoiceField(required=True, label="Tipo", choices=CHOICES_TIPO_NOTIFICACION)

class NotificacionPushMasivaForm(BaseForm):
    head = forms.CharField(required=True, label="Encabezado")
    body = forms.CharField(required=True, label="Cuerpo", widget=forms.Textarea(attrs={'rows': 3}))
    url = forms.CharField(required=True, label="URL")

class NotificacionAndroidMasivaForm(BaseForm):
    title = forms.CharField(required=True, label="Título")
    body = forms.CharField(required=True, label="Cuerpo", widget=forms.Textarea(attrs={'rows': 3}))
    data = forms.CharField(required=True, label="Datos en JSON")

class CorreoTemplateForm(ModelBaseForm):
    class Meta:
        model = CorreoTemplate
        fields = ['nombre', 'subject', 'html', 'button_text', 'button_url', 'tipo']
        labels = {
            'nombre': 'Título',
            'subject': 'Asunto',
            'html': 'HTML',
            'button_text': 'Texto del Botón',
            'button_url': 'Link del Botón',
        }
        widgets = {
            'html': TinyMCE(mce_attrs = TINYMCE_DEFAULT_CONFIG2),
            'tipo': forms.HiddenInput(),
        }

    def add_form(self, tipo):
        self.fields['tipo'].initial = tipo

class CorreoTemplateEnviarForm(BaseForm):
    masivo = forms.BooleanField(required=False, label='Enviar a todos los usuarios', 
            widget=forms.CheckboxInput(attrs={'separator': 'Si selecciona esta opción, el correo se enviará a todos los usuarios'}))
    correo = forms.EmailField(max_length=100, label='Correo Electrónico', required=False,
            widget=forms.TextInput(attrs={'placeholder': 'Correo Electrónico', 'separator': 'Ingrese solo el correo o seleccione un usuario'}))
    usuario = forms.ModelChoiceField(label="Usuario", queryset=CustomUser.objects.all(), required=False,
            widget=autocomplete.ModelSelect2(
                url='core:model_autocomplete',
                forward=(forward.Const('CustomUser', 'model'), ),
                attrs={'data-html': True},
            ))

# *****************************************************************************************************
# Sección Webscraping
# *****************************************************************************************************
class SubirQuizzizForm(BaseForm):
    archivo = forms.FileField(required=True, label="Archivo", widget=forms.FileInput(attrs={'accept': '.html'}))

class TestRTemporalForm(BaseForm):
    nombre = forms.CharField(required=True, label="Nombre")
