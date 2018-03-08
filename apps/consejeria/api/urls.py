from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^v1/', include([
        url(r'consejerias-pre/$', views.CreateConsejeriaPreAPIView.as_view(), name='pre_consejerias'),
        url(r'consejerias-pre/(?P<pk>\d+)/$', views.DataConsejeriaPreAPIView.as_view(), name='pre_consejeria'),
        url(r'consejerias-post/$', views.ConsejeriaPostListAPIView.as_view(), name='post_consejerias'),
    ], namespace='v1')),
]
