from django.urls import path
from .views import *

app_name = 'blog'

urlpatterns = [
    # ******************* Base *******************
    path('post/<str:slug>/', PostView.as_view(), name='post'),
    path('categoria/<slug:categoria>/', PostsCategoriaListView.as_view(), name='posts_categoria'),
    path('posts/', PostsListView.as_view(), name='posts'),

    # ******************* Admin *******************
    path('administracion/blog/', AdminPostsListView.as_view(), name='admin_blog'),

]