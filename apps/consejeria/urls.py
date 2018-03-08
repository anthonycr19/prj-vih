from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^pre-consejerias/$', views.ConsejeriaPreIndex.as_view(), name='consejeria_pre_index'),
    url(r'^post-consejerias/$', views.ConsejeriaPostIndex.as_view(), name='consejeria_post_index'),
    url(
        r'^crear-post-consejeria/(?P<uuid>\b[0-9A-Fa-f]{8}\b(-\b[0-9A-Fa-f]{4}\b){3}-\b[0-9A-Fa-f]{12}\b)/$',
        views.CrearConsejeriaPostIndex.as_view(),
        name='crear_consejeria_post'
    ),
    url(
        r'^editar-post-consejeria/(?P<id>[\d]+)/$',
        views.EditarConsejeriaPostIndex.as_view(),
        name='editar_consejeria_post'
    ),
    url(
        r'^eliminar-post-consejeria/(?P<id>[\d]+)/$',
        views.EliminarConsejeriaPost.as_view(),
        name='eliminar_consejeria_post'),
    url(r'^api/', include('apps.consejeria.api.urls')),
]
