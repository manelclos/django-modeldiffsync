from django.conf.urls import patterns, include, url

from modeldiffsync.api import GeomodeldiffList, Update


urlpatterns = patterns('',
    url(r'^geomodeldiff$', GeomodeldiffList.as_view()),
    url(r'^update', Update.as_view()),
)
