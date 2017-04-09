from django.conf.urls import url

from . import views

urlpatterns = [
    # /challenges/
    url(r'^$', views.list_challenges, name='list'),
    # /challenges/validate/1
    url(r'^validate/(?P<chall_id>\d+)/$', views.validate, name='validate'),
    # /challenges/scoreboard/
    url(r'^scoreboard/$', views.scoreboard, name='scoreboard'),
    # /challenges/get_validated_challenges/
    url(r'^get_validated_challenges/$', views.get_validated_challenges, name='get_validated_challenges'),

    ################
    ## Admin actions
    ################

    # /challenges/add_challenge/
    url(r'^add_challenge/$', views.add_challenge, name='add'),
    # /challenges/update/[slug]/
    url(r'^update/(?P<slug>[\w-]+)/$', views.update_challenge, name='update'),
    # /challenges/delete/[slug]/
    url(r'^delete/(?P<slug>[\w-]+)/$', views.delete_challenge, name='delete'),
    # /challenges/admin/
    url(r'^admin/$', views.admin, name='admin'),
    # /challenges/start_ctf/
    url(r'^start_ctf/$', views.start_ctf, name='start_ctf'),
    # /challenges/ctf_not_started/
    url(r'^ctf_not_started/$', views.ctf_not_started, name='ctf_not_started'),
    # /challenges/freeze_local_scoreboard/
    url(r'^freeze_local_scoreboard/$', views.freeze_local_scoreboard, name='freeze_local_scoreboard'),
    # /challenges/stop_local_scoreboard/
    url(r'^stop_local_scoreboard/$', views.stop_local_scoreboard, name='stop_local_scoreboard'),
    # /challenges/freeze_global_scoreboard/
    url(r'^freeze_global_scoreboard/$', views.freeze_global_scoreboard, name='freeze_global_scoreboard'),
    # /challenges/end_ctf/
    url(r'^end_ctf/$', views.end_ctf, name='end_ctf'),

]
