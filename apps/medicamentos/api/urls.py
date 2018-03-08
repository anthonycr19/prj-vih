from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^v1/', include([
        url(r'medicamentos/$', views.MedicamentoListAPIView.as_view(), name='medicamentos'),
        url(r'esquemas/$', views.EsquemaListAPIView.as_view(), name='esquemas'),
        url(r'antiretrovirales/$', views.EsquemaMedicamentoListAPIView.as_view(), name='antiretrovirales'),
    ], namespace='v1')),
]
