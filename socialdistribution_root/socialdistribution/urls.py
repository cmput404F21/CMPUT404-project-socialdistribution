"""socialdistribution URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

urlpatterns = [
    path('', include('apps.core.urls')),
    path('site/posts/', include('apps.posts.urls')),
    path('site/admin/', admin.site.urls),
    path('site/accounts/', include('django.contrib.auth.urls')), #this handles user authentication
    # These are our apis
    path('/', include('apis.authors.urls')),
    # path('author/<str:author_id>/followers/', include('apis.followers.urls')),
    # path('author/<str:author_id>/posts/', include('apis.posts.urls')),
    # path('author/<str:author_id>/comments/', include('apis.comments .urls')),
    # path('author/<str:author_id>/inbox/', include('apis.comments .urls')),
]
