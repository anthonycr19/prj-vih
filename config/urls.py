from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings

handler403 = 'dashboard.views.handler_403'

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include('apps.cauth.urls', namespace='user')),
    url(r'^', include('apps.consejeria.urls', namespace='consejeria')),
    url(r'^', include('apps.medicamentos.urls', namespace='medicamento')),
    url(r'^', include('apps.laboratorio.urls', namespace='laboratorio')),
    url(r'^', include('apps.atencion.urls', namespace='atencion')),
    url(r'^', include('apps.dashboard.urls', namespace='app')),
    url(r'^', include('apps.afiliacion.urls', namespace='afiliacion')),
    url(r'^', include('apps.servicios.urls', namespace='servicio')),
    url(r'^', include('minsalogin.urls', namespace='minsalogin')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
