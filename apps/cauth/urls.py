# coding: utf-8
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^salir/$', views.Logout.as_view(), name='logout'),
    url(r'^medicos/(?P<servicio>\w+)/$', views.medicos, name='medicos'),
]
