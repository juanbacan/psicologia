from django import forms
from django.utils.safestring import mark_safe
from tinymce.widgets import TinyMCE
# <class 'dal_select2.widgets.ModelSelect2'>
from dal_select2.widgets import ModelSelect2, Select2, Select2Multiple, ModelSelect2Multiple


class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            self.configure_field(field)

        try:
            errorList=list(self.errors)
            for item in errorList:
                self.fields[item].widget.attrs.update({'autofocus': ''})
                break
        except:
            pass

    def configure_field(self, field):
        if not isinstance(field.widget, TinyMCE) and not isinstance(field.widget, Select2) and not isinstance(field.widget, ModelSelect2):
            if "class" in field.widget.attrs:
                field.widget.attrs["class"] += " form-control"
            else:
                field.widget.attrs["class"] = "form-control"

            # Check if field.widget has input_type attribute
            if hasattr(field.widget, "input_type"):
                if field.widget.input_type == "checkbox":
                    field.widget.attrs["class"] = field.widget.attrs["class"].replace("form-control", "form-check-input")
                if field.widget.input_type == "select":
                    field.widget.attrs["class"] += " form-select"

            if "validate" in field.widget.attrs:
                validation_attrs = self.get_validation_attrs(field.widget.attrs["validate"])
                field.widget.attrs.update(validation_attrs)
        
        if field.required and hasattr(field, 'label') and field.label:
            field.label = mark_safe(field.label + '<span class="text-danger">*</span> ')


    def get_validation_attrs(self, validation_type):
        validation_attrs = {}
        if validation_type == "telefono_movil":
            validation_attrs['pattern'] = "[0]{1}[9]{1}[0-9]{8}"
            validation_attrs['validate'] = "Núm. móvil incorrecto. Ejm: 0987654321"
        elif validation_type == "telefono_fijo":
            validation_attrs['pattern'] = "[0]{1}[2-8]{1}[0-9]{7}"
            validation_attrs['validate'] = "Núm. fijo incorrecto. Ejm: 022345678"
        elif validation_type == "cedula":
            validation_attrs['pattern'] = "[0-9]{10}"
            validation_attrs['validate'] = "La cédula debe tener 10 dígitos"
        elif validation_type == "email":
            validation_attrs['pattern'] = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$"
            validation_attrs['validate'] = "Correo electrónico incorrecto."
        return validation_attrs


class ModelBaseForm(BaseForm, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelBaseForm, self).__init__(*args, **kwargs)

        


class FormularioUsuario(BaseForm):
    username = forms.CharField(max_length=100, label='Nombre de usuario', widget=forms.TextInput(attrs={'labelwidth': 12, 'disabled': True}))
    nombres = forms.CharField(max_length=100, label='Nombres', widget=forms.TextInput(attrs={'labelwidth': 12, 'disabled': True}))
    apellidos = forms.CharField(max_length=100, label='Apellidos', widget=forms.TextInput(attrs={'labelwidth': 12, 'disabled': True}))
    nombre_visible = forms.CharField(max_length=100, label='Nombre visible', widget=forms.TextInput(attrs={'labelwidth': 12, 'disabled': True}))
    email = forms.CharField(max_length=100, label='Dirección de correo electrónico', widget=forms.TextInput(attrs={'labelwidth': 12, 'disabled': True}))


class EditUsuarioForm(BaseForm):
    username = forms.CharField(max_length=100, label='Nombre de usuario')
    nombres = forms.CharField(max_length=100, label='Nombres')
    apellidos = forms.CharField(max_length=100, label='Apellidos')
    cedula = forms.CharField(max_length=10, label='Cédula o Pasaporte')
    email = forms.CharField(max_length=100, label='Dirección de correo electrónico')