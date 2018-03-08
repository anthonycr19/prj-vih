from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.AtencionAntecedenteView.as_view(), name='atencion_antecedente'),
]
