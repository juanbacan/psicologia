from crudbuilder.abstract import BaseCrudBuilder
from .models import Alerta, CustomUser

class CustomUserCrud(BaseCrudBuilder):
    model = CustomUser
    search_fields = ['username', 'email']
    tables2_fields = ('username', 'email', 'is_active')
    tables2_css_class = "table table-bordered table-condensed"
    tables2_pagination = 20  # default is 10
    


class AlertaCrud(BaseCrudBuilder):
    model = Alerta
    search_fields = ['titulo', 'descripcion']
    tables2_fields = ('titulo', 'descripcion', 'activo')
    tables2_css_class = "table table-bordered table-condensed"
    tables2_pagination = 20  # default is 10
    # modelform_excludes = ['usuario']
    # login_required = True
    # permission_required = 'auth.add_user'
    # custom_templates = [
    #     # ('list', 'core/alerta_list.html'),
    #     # ('add', 'core/alerta_add.html'),
    #     # ('update', 'core/alerta_update.html')
    # ]
    # custom_modelform = None
    # custom_queryset = None
    # custom_context = None
    # paginate_by = 30
    # extra_context = {'title': 'Alertas', 'button': 'Agregar Alerta'}
    # home_url_name = 'home'
    # login_url = 'login'
    # permission_denied_message = 'Permission Denied'
    # delete_not_allowed = False
    # order_by = ['-id']
    # form_action = ''
    # form_class = None
    # permission_required = 'auth.add_user'
    # delete_permission_required = 'auth.delete_user'
    # decorators = [login_required]
    # messages = {
    #     "save": "Guardado Correctamente",
    #     "update": "Actualizado Correctamente",
    #     "delete": "Eliminado Correctamente",
    # }
    # fields = None
    # exclude = None
    # inlines = []
    # inline_formsets = []
    # foreignkey_search = 'id'
    # date_hierarchy = None
    # list_filter = None
    # list_display = None
    # list_display_links = None
    # list_per_page = 100
    # list_max_show_all = 200
    # list_select_related = False
    # list_editable = None
    # save_as = False
    # save_on_top = False
    # paginator = Paginator
    # form = ModelForm
    # filter_horizontal = []
    # filter_vertical = []
    # radio_fields = {}
    # prepopulated_fields = {}
    # formfield_overrides = {}
    # readonly_fields = []
    # modelform_factory = modelform_factory
    # modelform_exclude = None
    # modelform_fields = None