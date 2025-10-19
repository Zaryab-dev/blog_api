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
from blog.views import landing_page
from blog.views_healthcheck import simple_healthcheck, detailed_healthcheck
from core.authentication import SecureTokenObtainView, LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', landing_page, name='landing'),
    path('health/', simple_healthcheck, name='healthcheck'),
    path('healthcheck/', simple_healthcheck, name='healthcheck-alt'),
    path('api/v1/healthcheck/', simple_healthcheck, name='healthcheck-api'),
    path('api/v1/health/detailed/', detailed_healthcheck, name='healthcheck-detailed'),
    path('admin/', admin.site.urls),
    path('ckeditor5/image_upload/', ckeditor5_upload, name='ck_editor_5_upload_file'),
    path('upload/ckeditor/', ckeditor5_upload, name='ckeditor_upload'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('api/auth/login/', SecureTokenObtainView.as_view(), name='token_obtain'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='token_logout'),
    path('api/', include('blog.urls')),
]
