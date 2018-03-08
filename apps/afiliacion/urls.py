from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^brigada/', include([
        url(r'^crear-brigada/$', views.BrigadaCrearView.as_view(), name='crear_brigada'),
    ])),

    url(r'^afiliacion/', include([
        url(r'^$', views.AfiliacionView.as_view(), name='afiliacion_paciente'),
        url(r'^buscar-paciente/$', views.PacienteBuscarView.as_view(), name='buscar_paciente'),
        url(
            r'^editar-paciente/(?P<paciente_id>[\w-]+)/$',
            views.PacienteUpdateView.as_view(),
            name='editar_paciente'
        ),
        url(
            r'^familia-paciente/(?P<dni_paciente>[\d]+)/$',
            views.PacienteListFamiliaView.as_view(),
            name='familia_paciente'),
        url(
            r'^buscar-contacto-familia/(?P<paciente_id>[\w-]+)/$',
            views.PacienteBuscarFamiliaView.as_view(),
            name='buscar_familia_paciente'
        ),
        url(
            r'^resultado-buscar-familia-paciente',
            views.PacienteResultadoBuscarFamiliaView.as_view(),
            name='resultado_buscar_familia_paciente'
        ),
        url(
            r'^crear-familia-paciente/(?P<paciente_id>[\w-]+)/(?P<dni_paciente>[\d]+)/$',
            views.PacienteGuardarFamiliaView.as_view(),
            name='crear_familia_paciente'),
        url(
            r'^eliminar-datos-familia/(?P<id_contactofamilia>[\d]+)/$',
            views.eliminar_datos_familia_view,
            name='eliminar_datos_familia'
        ),
        url(r'^crear-paciente/$', views.PacienteCreateView.as_view(), name='crear_paciente'),
        url(r'^ver-paciente/$', views.verpaciente, name='ver_paciente'),
        url(r'^reportes/reporte-consolidado/$', views.ConsolidadoExcelView.as_view(), name='reporte_consolidado'),
    ])),
    url(r'^api/', include('apps.afiliacion.api.urls')),
]
