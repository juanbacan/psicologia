from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.blog'

    def ready(self):
        import applications.blog.signals
