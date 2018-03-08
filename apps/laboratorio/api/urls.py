from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^v1/', include([
        url(r'examenes/$', views.ExamenListCreateAPIView.as_view(), name='examenes'),
        url(r'examenes/(?P<pk>\d+)/$', views.DataExamenAPIView.as_view(), name='examen'),
        url(r'resultados/$', views.ExamenResultadoListAPIView.as_view(), name='resultados'),
        url(r'resultados/(?P<pk>\d+)/$', views.ExamenResultadoDataAPIView.as_view(), name='resultado'),
        url(
            r'examenes/crear-resultado/',
            views.CreateExamenResultadoListAPIView.as_view(),
            name='crear_examenes_resultado'
        ),
        url(
            r'examenes/editar-resultado/(?P<pk>\d+)/$',
            views.EditarExamenResultadoUpdateAPIView.as_view(),
            name='editar_examen_resultado'
        ),
    ], namespace='v1')),
]
