from django.conf.urls import url
from ..views.auth.admin import OzeAdmin

urlpatterns = [
    url(r'^$', OzeAdmin.as_view()),
    url(r'^simple_auth/$', OzeAdmin.as_view()),
    url(r'^simple_auth/(?P<token>[a-zA-Z\-]+)/?$', OzeAdmin.as_view()),
]
