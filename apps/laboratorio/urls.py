from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^laboratorio/$', views.LaboratorioExamenIndex.as_view(), name='laboratorio_index'),
    url(r'^laboratorio/resultado/$', views.LaboratorioResultadoIndex.as_view(), name='laboratorio_resultado_index'),
    url(r'^api/', include('apps.laboratorio.api.urls')),
    url(
        r'^eliminar-examen/(?P<id>[\d]+)$',
        views.eliminar_examen,
        name='eliminar_examen'
    ),
    url(
        r'^listar-resultado-examen/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/$',
        views.ListarResultadoExamen.as_view(),
        name='listar_resultado_examen'
    ),
    url(
        r'^eliminar-resultado-examen/(?P<id>[\d]+)/$',
        views.EliminarResultadoExamen.as_view(),
        name='eliminar_resultado_examen'
    ),
]
