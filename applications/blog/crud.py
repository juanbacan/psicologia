from crudbuilder.abstract import BaseCrudBuilder
from .models import Categoria, Post

class CategoriaCrud(BaseCrudBuilder):
    model = Categoria
    search_fields = ['nombre', 'slug', 'descripcion']
    tables2_fields = ('nombre', 'slug', 'activo')
    tables2_css_class = "table table-bordered table-condensed"
    tables2_pagination = 20  # default is 10

    def custom_context(self, request, *args, **kwargs):
        return {
            'heading': 'Aplicacion',
            'pageview': 'Lista de Usuarios'
        }
    

class PostCrud(BaseCrudBuilder):
    model = Post
    search_fields = ['titulo', 'slug']
    tables2_fields = ('titulo', 'fecha', 'activo')
    tables2_css_class = "table table-bordered table-condensed"
    tables2_pagination = 20  # default is 10

    def custom_context(self, request, *args, **kwargs):
        return {
            'heading': 'Aplicacion',
            'pageview': 'Lista de Usuarios'
        }