from crudbuilder.abstract import BaseCrudBuilder
from .models import Alerta, CustomUser, LlamadoAccion

class CustomUserCrud(BaseCrudBuilder):
    model = CustomUser
    search_fields = ['username', 'email']
    tables2_fields = ('username', 'email', 'is_active')
    tables2_css_class = "table table-bordered table-condensed"
    tables2_pagination = 20  # default is 10

    def custom_context(self, request, *args, **kwargs):
        return {
            'heading': 'Aplicacion',
            'pageview': 'Lista de Usuarios'
        }
    


class AlertaCrud(BaseCrudBuilder):
    model = Alerta
    search_fields = ['titulo', 'descripcion']
    tables2_fields = ('titulo', 'descripcion', 'activo')
    tables2_css_class = "table table-bordered table-condensed"
    tables2_pagination = 20 

    def custom_context(self, request, *args, **kwargs):
        return {
            'heading': 'Aplicacion',
            'pageview': 'Lista de Usuarios'
        }
    
class LlamadoAccionCrud(BaseCrudBuilder):
    model = LlamadoAccion
    search_fields = ['url', 'pagina', 'activo']
    tables2_fields = ('imagen', 'url', 'pagina', 'activo')
    tables2_css_class = "table table-bordered table-condensed"
    tables2_pagination = 20 

    def custom_context(self, request, *args, **kwargs):
        return {
            'heading': 'Aplicacion',
            'pageview': 'Lista de Usuarios'
        }