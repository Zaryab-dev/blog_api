"""
URL configuration for leather_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from blog.views_ckeditor5_upload import ckeditor5_upload

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/image_upload/', ckeditor5_upload, name='ck_editor_5_upload_file'),  # Override default
    path('upload/ckeditor/', ckeditor5_upload, name='ckeditor_upload'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('api/', include('blog.urls')),
]
