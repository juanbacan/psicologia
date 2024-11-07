from applications.core.forms import BaseForm, ModelBaseForm
from tinymce.widgets import TinyMCE
from django import forms
from dal import autocomplete, forward

TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "height": 200,
    "menubar": False,
    "plugins": "preview,advlist,lists,link,charmap,image,media,table,paste,wordcount",
    "external_plugins": {
        "tiny_mce_wiris": 'https://www.wiris.net/demo/plugins/tiny_mce/plugin.min.js',                  
    },
    "toolbar":  "image | "
    "bold italic | alignleft aligncenter "
    "| bullist numlist | "
    "tiny_mce_wiris_formulaEditor tiny_mce_wiris_formulaEditorChemistry "
    "table superscript subscript charmap preview",
    "images_upload_url": "/upload_image/",
    "document_base_url": "https://goeducativa.com/",
    "relative_urls": False,
    "convert_urls": False,
}

class EjemploForm(BaseForm):
    solucion = forms.CharField(widget=TinyMCE(mce_attrs = TINYMCE_DEFAULT_CONFIG), label='Escribe tu Solución')
    nombre = forms.CharField(max_length=50, label='Nombre')

# class TrabajaConNosotrosForm(ModelBaseForm):
#     class Meta:
#         model = TrabajaConNosotros
#         exclude = ['usuario', 'tipo']
#         widgets = {
#             'mensaje': forms.Textarea(attrs={'rows': 3}),
#             # 'usuario': autocomplete.ModelSelect2(url='core:model_autocomplete', forward=(forward.Const('CustomUser', 'model'), )),
#         }