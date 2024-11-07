from django.shortcuts import render
from django.views.generic import View
from django.contrib import messages

from applications.blog.models import Post

class HomeView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context['recursos'] = [
            'Depresión',
            'Estres',
            'Autoestima Baja',
            'Ansiedad',
            'Ruptura Amorosa',
            'No puedo gestionar mis emociones',
        ]

        context['posts'] = Post.objects.all()

        return render(request, 'main/home.html', context)


