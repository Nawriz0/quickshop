"""
URL configuration for QuickShop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import TemplateView

def handler404(request, exception):
    return TemplateView.as_view(template_name='main/error.html')(request, status=404, context={
        'error_message': 'Страница не найдена',
        'error_description': 'К сожалению, запрашиваемая страница не существует.'
    })

def handler500(request):
    return TemplateView.as_view(template_name='main/error.html')(request, status=500, context={
        'error_message': 'Произошла ошибка',
        'error_description': 'Извините, произошла внутренняя ошибка сервера. Мы уже работаем над её устранением.'
    })

def handler403(request, exception):
    return TemplateView.as_view(template_name='main/error.html')(request, status=403, context={
        'error_message': 'Доступ запрещен',
        'error_description': 'У вас нет прав для доступа к этой странице.'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
