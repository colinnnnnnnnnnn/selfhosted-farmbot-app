"""
URL configuration for farmbot_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from api.views import social_auth_callback_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('social-auth-callback/', social_auth_callback_view, name='social_auth_callback'),
    path('api/', include('api.urls')),
]

# Serve farm_images in development
if settings.DEBUG:
    from django.views.static import serve
    from django.urls import re_path
    import os
    
    urlpatterns += [
        re_path(r'^farm_images/(?P<path>.*)$', serve, {
            'document_root': os.path.join(settings.BASE_DIR, 'farm_images'),
        }),
    ]
