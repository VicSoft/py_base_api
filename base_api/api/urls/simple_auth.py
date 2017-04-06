from django.conf.urls import url
from ..views.auth.admin import Admin

urlpatterns = [
    url(r'^$', Admin.as_view()),
    url(r'^simple_auth/$', Admin.as_view()),
    url(r'^simple_auth/(?P<token>[a-zA-Z\-]+)/?$', Admin.as_view()),
]
