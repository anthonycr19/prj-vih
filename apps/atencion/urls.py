from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^atenciones/', include([
        url(r'^$', views.AtencionIndexView.as_view(), name='atencion_index'),
        url(r'^(?P<pk>\d+)/', include([
            url(r'^$', views.AtencionCitaView.as_view(), name='atencion_cita'),
            url(r'^pacientes/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/', include([
                url(r'^antecedentes/', include('apps.antecedente.urls')),
                url(r'^triaje/', include([
                    url(r'^$', views.AtencionInicialCreateView.as_view(), name='atencion-inicial-new'),
                    url(r'^(?P<id>\d+)/$', views.AtencionInicialUpdateView.as_view(), name='atencion-inicial-edit'),
                ])),
                url(r'^dx-df/$', views.AtencionDxDefinicionCreateView.as_view(), name='atencion-dx-definicion'),
                url(r'^dx-tarv/$', views.AtencionTratamientoCreateView.as_view(), name='atencion-tratamiento'),
                url(r'^dx-g/$', views.AtencionGestacionCreateView.as_view(), name='atencion-gestacion'),
                url(r'^dx-tp/$', views.AtencionTerapiaCreateView.as_view(), name='atencion-terapia'),
                url(r'^dx-ram/$', views.AtencionRamCreateView.as_view(), name='atencion-ram'),
                url(r'^dx-ex-aux$', views.ExaAuxiliarCreateView.as_view(), name='atencion-examenauxiliar'),
                url(r'^dx-des-coinf/$', views.DescarteCreateView.as_view(), name='atencion-descarte'),
            ])),
        ])),
        url(r'^atencion-cronograma-control/(?P<pk>\d+)/$', views.AtencionCronogramaListView.as_view(),
            name='atencion-cronograma-control'),
    ])),
    url(r'^egreso/', include([
        url(r'^$', views.EgresoIndexView.as_view(), name='egreso-index'),
        url(
            r'^crear/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/',
            views.EgresoCreateView.as_view(),
            name='egreso-crear'
        ),
    ])),
    url(r'^api/', include('apps.atencion.api.urls')),
]
