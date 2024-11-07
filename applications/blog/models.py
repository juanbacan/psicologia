import os, datetime
from PIL import Image
from django.db import models
from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey
from tinymce import models as tinymce_models
from django_resized import ResizedImageField
from django.utils.functional import cached_property

from applications.core.models import ModeloBase, AplicacionWeb

from .managers import PostManager


class Categoria(MPTTModel):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    activo = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['nombre']

    def __str__(self):
        full_path = [self.nombre]
        k = self.parent
        while k is not None:
            full_path.append(k.nombre)
            k = k.parent
        return ' -> '.join(full_path[::-1])
    

class Etiqueta(ModeloBase):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Post(ModeloBase):
    titulo = models.TextField(max_length=500)
    fecha = models.DateTimeField(default=datetime.datetime.now)
    slug = models.SlugField(max_length=100, unique=True)
    categorias = models.ManyToManyField(Categoria)
    # etiquetas = models.ManyToManyField(Etiqueta)
    activo = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=200, null=True, blank=True)
    meta_keywords = models.CharField(max_length=300, null=True, blank=True)
    meta_description = models.TextField(max_length=500, null=True, blank=True)

    objects = PostManager()
    
    class Meta:
        ordering = ['-fecha']
        unique_together = ('slug', )

    def __str__(self):
        return self.titulo
    
    def mi_imagen(self):
        # Obtiene la imagen principal del post
        imagen = self.imagenpost_set.filter(principal=True).first()
        if imagen:
            return imagen.imagen.url
        else:
            imagen = self.imagenpost_set.all().first()
            if imagen:
                return imagen.imagen.url
            else:
                return None
            
    def mis_imagenes(self):
        return self.imagenpost_set.all().order_by('id')

    def mis_descripciones(self):
        # return self.contenidoblog_set.all().order_by('orden')
        return self.contenidoblog_set.all().order_by('id')
    
    def mi_descripcion_corta(self):
        if self.meta_description:
            return self.meta_description
        else:
            # Obtiene la primera descripción del post
            descripcion = self.contenidoblog_set.all().order_by('orden').first()
            if descripcion:
                return descripcion.contenido
            else:
                return "Sin descripción"

    def mi_post_previo(self):
        post_previo = Post.objects.filter(fecha__lt=self.fecha).order_by('-fecha').first()
        if post_previo:
            return post_previo
        else:
            return None
        
    def mi_post_siguiente(self):
        post_siguiente = Post.objects.filter(fecha__gt=self.fecha).order_by('fecha').first()
        if post_siguiente:
            return post_siguiente
        else:
            return None
        
    def mis_posts_relacionados(self):
        return Post.objects.filter(categorias__in=self.categorias.all()).exclude(id=self.id).distinct()[:3]
    

    def mi_url_relativa(self):
        return '/post/' + self.slug + '/'
    
    def mi_contenido_model(self):
        # Obtiene el contenido del post
        contenido = self.contenidoblog_set.all().order_by('orden').first()
        if contenido:
            return contenido
        else:
            return None

    def mi_contenido(self):
        # Obtiene el contenido del post
        contenido = self.contenidoblog_set.all().order_by('orden').first()
        if contenido:
            return contenido.contenido
        else:
            return "Sin contenido"

    @cached_property
    def mi_url_absoluta(self):
        application = AplicacionWeb.objects.first()
        return application.url_safe() + self.mi_url_relativa()


class ImagenPost(ModeloBase):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    imagen = ResizedImageField(force_format="WEBP", quality=75, upload_to='blog', null=True, blank=True)
    principal = models.BooleanField(default=False)

    def __str__(self):
        return self.post.titulo
    

class ContenidoBlog(ModeloBase):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    contenido = tinymce_models.HTMLField()
    orden = models.IntegerField(default=0)
    
    def __str__(self):
        return self.post.titulo
