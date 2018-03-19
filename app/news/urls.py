from django.conf.urls import url

from . import views

app_name = "news"

urlpatterns = [
    # /news/
    url(r'^$', views.news, name="list"),
    # /news/empty_news/
    url(r'^empty_news/$', views.empty_news, name="empty_news"),

    # /news/add/
    url(r'^add/$', views.add, name="add"),
    # /news/modify/1/
    url(r'^modify/(?P<id_news>\d+)/$', views.modify, name="modify"),
    # /news/delete/1/
    url(r'^delete/(?P<id_news>\d+)/$', views.delete, name="delete"),
]
