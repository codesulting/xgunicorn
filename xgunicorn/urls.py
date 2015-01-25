from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from django.contrib import admin
from .views import HomePageView, SignUpView, LoginView, logout_view

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'xgunicorn.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^gunmel/', include('gunmel.urls', namespace='gunmel')),
    url(r'^accounts/login$', LoginView.as_view(), name='login'),
    url(r'^accounts/logout$', logout_view, name='logout'),
    url(r'^accounts/signup$', SignUpView.as_view(), name='signup'),
    url(r'^admin/', include(admin.site.urls)),
)
