from django.utils.safestring import mark_safe
from tinymce.widgets import TinyMCE
from dal_select2.widgets import ModelSelect2, Select2, Select2Multiple, ModelSelect2Multiple


def get_validation_attrs(validation_type):
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

def configure_field(value):
    field = value.field

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
            validation_attrs = get_validation_attrs(field.widget.attrs["validate"])
            field.widget.attrs.update(validation_attrs)
    
    if field.required and hasattr(field, 'label') and field.label:
        field.label = mark_safe(field.label + '<span class="text-danger">*</span> ')

    return value


