"""inshack_scoreboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from information import views

app_name = "scoreboard"

urlpatterns = [
    # /
    url(r'^$', views.home, name="home"),
    # /challenges/
    url(r'^challenges/', include('challenges.urls', namespace='challenges')),
    # /team/*
    url(r'^team/', include('user_manager.urls', namespace='team')),
    # /news/*
    url(r'^news/', include('news.urls', namespace='news')),
    # /admin/*
    url(r'^admin/', admin.site.urls),
]
