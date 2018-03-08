from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^medicamentos/', include([
        url(r'^buscar-medicamento/$', views.medicamento_search, name='medicamento_search'),
        url(r'^buscar-medicamento-descripcion/$', views.medicamento_descripcion_search,
            name='medicamento_descripcion_search'),
        url(r'^buscar-esquema/$', views.esquema_search,
            name='esquema_search'),
        url(r'^crear-medicamento/$', views.create_medicamento, name='create_medicamento'),
    ])),
    url(r'^api/', include('apps.medicamentos.api.urls')),
]
