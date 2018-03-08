from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^v1/', include([
        url(r'atenciones/(?P<pk>[\w-]+)/$', views.AtencionDataAPIView.as_view(), name='atencion'),
        url(r'atenciones/(?P<atencion>\d+)/diagnistico-vih/$',
            views.AtencionDiagnosticoDataAPIView.as_view(),
            name='atencion_diagnostico_vih'),
        url(r'atenciones/(?P<atencion>\d+)/diagnistico/(?P<id>\d+)/$',
            views.AtencionDiagnosticoDataAPIView.as_view(),
            name='atencion_diagnostico'),
        url(r'atenciones/(?P<pk>\d+)/dispensaciones/$',
            views.AtencionDispensacionListAPIView.as_view(),
            name='atencion_dispensaciones'),
        url(r'atenciones/(?P<pk>\d+)/tratamientos/$',
            views.AtencionTratamientoListAPIView.as_view(),
            name='atencion_tratamientos'),
        url(r'^paciente/', include([
            url(r'buscar/$', views.PacienteBuscarNombresApellidosAPIView.as_view(),
                name='buscar_paciente'),
            url(r'ver/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/$',
                views.PacienteVerUUIDDataAPIView.as_view(), name='ver_paciente_uuid'),
        ], namespace='paciente')),
    ], namespace='v1')),
]
