from django.shortcuts import render, redirect
from django.views.generic import ListView, View
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Post, Categoria, ImagenPost, ContenidoBlog
from .forms import *

from applications.core.utils import get_query_params, get_url_params, error_json, success_json


class PostView(View):
    template_name = 'blog/post.html'


    def get(self, request, *args, **kwargs):
        context = {}
        slug = kwargs['slug']
        post = Post.objects.get(slug=slug)
        context['post'] = Post.objects.get(slug=slug)
        context['posts'] = Post.objects.exclude(slug=slug).order_by('-fecha')[:6]
        return render(request, 'blog/post.html', context)


class PostsListView(ListView):
    model = Post
    template_name = 'blog/posts.html'
    context_object_name = 'posts'
    paginate_by = 20
    page_kwarg = 'pagina'

    def get_queryset(self):
        posts = Post.objects.all()

        kword = self.request.GET.get("kword", None)
        if kword:
            posts = posts.filter(
                Q(titulo__search=kword) | Q(titulo__unaccent__icontains=kword) |
                Q(contenidoblog__contenido__unaccent__icontains=kword) |
                Q(contenidoblog__contenido__search=kword)
            ).distinct()

        return posts.order_by('-fecha')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Lista de Filtros
        context['lista_categorias'] = Categoria.objects.all().order_by('nombre')

        context['url'] = self.request.get_full_path()
        context['url_params'] = get_url_params(self.request)
        context['kword'] = self.request.GET.get("kword", None)
        return context


class PostsCategoriaListView(ListView):
    model = Post
    template_name = 'blog/posts_categoria.html'
    context_object_name = 'posts'
    paginate_by = 20
    page_kwarg = 'pagina'

    def get_queryset(self):
        slug = self.kwargs['categoria']
        return Post.objects.filter(categorias__slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['categoria']
        context['categoria'] = categoria = Categoria.objects.get(slug=slug)
        context['categoria_filtro'] = categoria

        # Lista de Filtros
        context['lista_categorias'] = Categoria.objects.all().order_by('nombre')

        context['url'] = self.request.get_full_path()
        context['url_params'] = get_url_params(self.request)
        context['kword'] = self.request.GET.get("kword", None)
        return context



class AdminPostsListView(View):

    def get(self, request, *args, **kwargs):
        context = {}
        action, data = get_query_params(request)
        context['action'] = action
        try:
            with transaction.atomic():
                if action:
                    # ******************************************************************************************
                    # Blog
                    # ******************************************************************************************
                    context['heading'] = "Blog"

                    context['pageview'] = "Categorias Post"
                    if action == 'categorias_post':
                        categorias = Categoria.objects.all().order_by('nombre')
                        
                        if data.get('kword', None):
                            kword = data.get('kword')
                            categorias = categorias.filter(
                                Q(nombre__search=kword) |
                                Q(nombre__icontains=kword)).distinct()
                        
                        paginator = Paginator(categorias, 30)
                        page_number = request.GET.get('pagina', 1)
                        context['page_obj'] = paginator.get_page(page_number)
                        context['url_params'] = get_url_params(self.request)
                        return render(request, 'blog/admin/categorias_post.html', context)
                    
                    if action == 'add_categoria_post':
                        context['title'] = 'Agregar Categoria'
                        context['form'] = CategoriaPostForm()
                        context['prepopulated_fields'] = [{'field': 'slug', 'source': 'nombre'}]
                        return render(request, 'forms/formAdmin.html', context)
                    
                    if action == 'edit_categoria_post':
                        context['title'] = 'Editar Categoria'
                        context['object'] = categoria = Categoria.objects.get(id=data.get('id'))
                        context['form'] = CategoriaPostForm(instance=categoria)
                        context['formdeleteaction'] = "del_categoria"
                        return render(request, 'forms/formAdmin.html', context)
                    
                    if action == 'del_categoria_post':
                        context['title'] = 'Eliminar Categoria'
                        context['message'] = '¿Está seguro de eliminar la categoria ' + Categoria.objects.get(id=data.get('id')).nombre + '?'
                        context['delete_obj'] = True
                        context['formid'] = data.get('id')
                        return render(request, 'forms/formModal.html', context)

                    # ******************************************************************************************
                    context['pageview'] = "Posts"
                    if action == 'posts':
                        posts = Post.objects.all().order_by('-id')
                        
                        if data.get('kword', None):
                            kword = data.get('kword')
                            posts = posts.filter(
                                Q(titulo__search=kword) |
                                Q(contenido__search=kword) |
                                Q(titulo__icontains=kword) |
                                Q(contenido__icontains=kword)
                            ).distinct()
                        
                        paginator = Paginator(posts, 30)
                        page_number = request.GET.get('pagina', 1)
                        context['page_obj'] = paginator.get_page(page_number)
                        context['url_params'] = get_url_params(self.request)
                        return render(request, 'blog/admin/posts.html', context)
                    
                    if action == 'add_post':
                        context['title'] = 'Agregar Post'
                        context['form'] = PostForm()
                        return render(request, 'blog/admin/add_post.html', context)
                    
                    if action == 'edit_post':
                        context['title'] = 'Editar Post'
                        context['object'] = post = Post.objects.get(id=data.get('id'))
                        context['form'] = PostForm(instance=post, initial={'contenido': post.mi_contenido()})
                        context['formdeleteaction'] = "del_post"
                        return render(request, 'blog/admin/add_post.html', context)
                    
                    if action == 'del_post':
                        context['title'] = 'Eliminar Post'
                        post = Post.objects.get(id=data.get('id'))
                        context['message'] = '¿Está seguro de eliminar el post ' + post.titulo + '?'
                        context['delete_obj'] = True
                        context['formid'] = data.get('id')
                        return render(request, 'forms/formModal.html', context)
        except Exception as ex:
            print(ex)
            messages.error(request, str(ex))
            return render(request, 'administracion/dashboard.html', context)
    
    def post(self, request):
        context = {}
        action, data = get_query_params(request)
        context['action'] = action
        if action:
            # ******************************************************************************************
            # Aplicación
            # ******************************************************************************************
            context['heading'] = "Blog"

            context['pageview'] = "Posts"
            if action == 'add_post':
                try:
                    with transaction.atomic():
                        form = PostForm(request.POST, request.FILES)
                        if form.is_valid():
                            imagen = request.FILES.get('id_imagen_post')
                            if not imagen:
                                form.add_error(None, 'Debe subir una imagen')
                                context['title'] = 'Agregar Post'
                                context['form'] = form
                                return render(request, 'blog/admin/add_post.html', context)
                            
                            form.save()
                            ContenidoBlog.objects.create(
                                post = form.instance,
                                contenido = form.cleaned_data.get('contenido')
                            )

                            # Guardar la imagen principal
                            ImagenPost.objects.filter(post=form.instance).delete()
                            ImagenPost.objects.create(
                                post = form.instance,
                                imagen = imagen,
                                principal = True
                            )

                            messages.success(request, 'Post agregado correctamente')
                            if '_addanother' in request.POST:
                                return redirect(request.path + '?action=add_post')
                            elif 'continue' in request.POST:
                                return redirect(request.path + '?action=edit_post&id=' + str(form.instance.id))
                            else:
                                return redirect(request.path + '?action=posts')
                        else:
                            context['title'] = 'Agregar Post'
                            context['form'] = form
                            return render(request, 'blog/admin/add_post.html', context)
                except Exception as ex:
                    messages.error(request, str(ex))
                    return redirect(request.path + '?action=posts')
                
            if action == 'edit_post':
                try:
                    with transaction.atomic():
                        post = Post.objects.get(id=data.get('id'))
                        form = PostForm(request.POST, request.FILES, instance=post)
                        if form.is_valid():
                            imagen = request.FILES.get('id_imagen_post')
                            if not imagen:
                                form.add_error(None, 'Debe subir una imagen')
                                context['title'] = 'Agregar Post'
                                context['form'] = form
                                return render(request, 'blog/admin/add_post.html', context)
                        
                            form.save()

                            contenido = post.mi_contenido_model()
                            if contenido:
                                contenido.contenido = form.cleaned_data.get('contenido')
                                contenido.save()

                            # Guardar la imagen principal
                            ImagenPost.objects.filter(post=form.instance).delete()
                            ImagenPost.objects.create(
                                post = form.instance,
                                imagen = imagen,
                                principal = True
                            )

                            messages.success(request, 'Post editado correctamente')
                            if '_addanother' in request.POST:
                                return redirect(request.path + '?action=add_post')
                            elif '_continue' in request.POST:
                                return redirect(request.path + '?action=edit_post&id=' + str(form.instance.id))
                            else:
                                return redirect(request.path + '?action=posts')
                        else:
                            context['title'] = 'Editar Post'
                            context['object'] = post
                            context['formdeleteaction'] = "del_post"
                            context['form'] = form
                            return render(request, 'blog/admin/add_post.html', context)
                except Exception as ex:
                    messages.error(request, str(ex))
                    return redirect(request.path + '?action=posts')
                
            if action == 'del_post':
                try:
                    with transaction.atomic():
                        id = data.get('id')
                        post = Post.objects.get(pk=id)
                        post.delete()
                        messages.success(request, 'Post eliminado correctamente')
                        return success_json(mensaje="Post eliminado correctamente", url=request.path + '?action=posts')
                except Exception as ex:
                    messages.error(request, 'Error al eliminar el post')
                    return error_json(mensaje=str(ex))
                

            context['pageview'] = "Categorias Post"
            if action == 'add_categoria_post':
                try:
                    with transaction.atomic():
                        form = CategoriaPostForm(request.POST)
                        if form.is_valid():
                            form.save()
                            messages.success(request, 'Categoria agregada correctamente')
                            if '_addanother' in request.POST:
                                return redirect(request.path + '?action=add_categoria_post')
                            elif 'continue' in request.POST:
                                return redirect(request.path + '?action=edit_categoria_post&id=' + str(form.instance.id))
                            else:
                                return redirect(request.path + '?action=categorias_post')
                        else:
                            context['title'] = 'Agregar Categoria'
                            context['form'] = form
                            return render(request, 'forms/formAdmin.html', context)
                except Exception as ex:
                    messages.error(request, str(ex))
                    return redirect(request.path + '?action=categorias_post')
                
            if action == 'edit_categoria_post':
                try:
                    with transaction.atomic():
                        categoria = Categoria.objects.get(id=data.get('id'))
                        form = CategoriaPostForm(request.POST, instance=categoria)
                        if form.is_valid():
                            form.save()
                            messages.success(request, 'Categoria editada correctamente')
                            if '_addanother' in request.POST:
                                return redirect(request.path + '?action=add_categoria_post')
                            elif '_continue' in request.POST:
                                return redirect(request.path + '?action=edit_categoria_post&id=' + str(form.instance.id))
                            else:
                                return redirect(request.path + '?action=categorias_post')
                        else:
                            context['title'] = 'Editar Categoria'
                            context['object'] = categoria
                            context['formdeleteaction'] = "del_categoria_post"
                            context['form'] = form
                            return render(request, 'forms/formAdmin.html', context)
                except Exception as ex:
                    messages.error(request, str(ex))
                    return redirect(request.path + '?action=categorias_post')
                
            if action == 'del_categoria_post':
                try:
                    with transaction.atomic():
                        id = data.get('id')
                        categoria = Categoria.objects.get(pk=id)
                        categoria.delete()
                        messages.success(request, 'Categoria eliminada correctamente')
                        return success_json(mensaje="Categoria eliminada correctamente", url=request.path + '?action=categorias_post')
                except Exception as ex:
                    messages.error(request, 'Error al eliminar la categoria')
                    return error_json(mensaje=str(ex))
                