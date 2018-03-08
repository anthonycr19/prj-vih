from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^v1/', include([
        url(r'^ciudadanos/', include([
            url(r'^(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/$',
                views.CiudadanoDataAPIView.as_view(),
                name='afiliacion_ciudadano'),
        ])),
        url(r'^pacientes/', include([
            url(r'^(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/$',
                views.PacienteDataAPIView.as_view(), name='afiliacion_paciente'),
        ])),
        url(r'^citas/', include([
            url(r'^$', views.CitaListAPIView.as_view(), name='afiliacion_citas'),
            url(r'^(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/$',
                views.CitaAPIView.as_view(), name='afiliacion_cita'),
        ])),
        url(r'^inmunizaciones/', include([
            url(r'^$', views.InmunicacionAPIView.as_view(), name='afiliacion_inmunizaciones'),
        ])),
        url(r'^ciex/$', views.CIEListAPIView.as_view(), name='afiliacion_cies'),
        url(r'^cpt/$', views.CPTListAPIView.as_view(), name='afiliacion_cpts'),
        url(r'^departamentos/$', views.DepartamentoView.as_view(), name='departamentos'),
        url(r'^provincias/(?P<codigo_dep>\w+)/$', views.ProvinciaView.as_view(), name='provincias'),
        url(r'^distritos/(?P<codigo_dep>\w+)/(?P<codigo_pro>\w+)/$',
            views.DistritoView.as_view(), name='distritos'),
        url(r'^localidades/(?P<codigo_dep>\w+)/(?P<codigo_pro>\w+)/(?P<codigo_dis>\w+)/$',
            views.LocalidadView.as_view(), name='localidades'),
        url(r'^coordenada/(-?\d+\.\d+)/(-?\d+\.\d+)/$', views.coordenada, name='coordenada'),
        url(r'^docs/', include('rest_framework_docs.urls')),
    ], namespace='v1')),
]
