from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from django.contrib import admin
from .views import HomePageView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'xgunicorn.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^gunmel/', include('gunmel.urls', namespace='gunmel')),
)
