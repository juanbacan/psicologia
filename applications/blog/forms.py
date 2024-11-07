from django import forms
        
from applications.core.forms import BaseForm, ModelBaseForm
from applications.blog.models import Post, Categoria

from tinymce.widgets import TinyMCE
from dal import autocomplete, forward

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
    "document_base_url": "https://goeducativa.com/",
    "relative_urls": False,
    "convert_urls": False,
}

class PostForm(ModelBaseForm):
    contenido = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model = Post
        fields = '__all__'
        exclude = ['fecha']
        widgets = {
            'titulo': forms.Textarea(attrs={'rows': 2}),
            'meta_description': forms.Textarea(attrs={'rows': 2}),
            # 'contenido': TinyMCE(mce_attrs = TINYMCE_DEFAULT_CONFIG2),
            'categorias': autocomplete.Select2Multiple(),
        }

class CategoriaPostForm(ModelBaseForm):
    class Meta:
        model = Categoria
        exclude = ['parent']
        labels = {
            'description': 'Descripción',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }