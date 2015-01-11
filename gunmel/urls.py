from __future__ import absolute_import

from django.conf.urls import patterns, include, url
from django.contrib import admin
from .views import PriceHistoryView

urlpatterns = patterns('gunmel/',
    url(r'^price-history/', PriceHistoryView.as_view(), name='price-history')
)
