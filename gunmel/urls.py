from __future__ import absolute_import

from django.conf.urls import patterns, url
from django.contrib import admin
from .views import ChartView, PriceHistoryView

urlpatterns = patterns('gunmel/',
    url(r'^price-history/', PriceHistoryView.as_view(), name='price-history'),
    url(r'^chart/(?P<pk>-?\d+)/history_chart.png$', ChartView.as_view(), name='history-chart') 
)
