from django.conf.urls import url

from . import views

urlpatterns = [
    # /team/
    url(r'^$', views.profile, name="profile"),
    # /team/register/
    url(r'^register/$', views.register, name="register"),
    # /team/login/
    url(r'^login/$', views.login_user, name="login"),
    # /team/logout/
    url(r'^logout/$', views.logout_user, name="logout"),
    # /team/logout/
    url(r'^team_infos/$', views.team_infos, name="team_infos"),
    # /team/get_all_mails/
    url(r'^get_all_mails/$', views.mails, name="get_all_mails"),
]
