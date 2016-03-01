from django.conf.urls import url

from modeldiffsync.api import GeomodeldiffList, Update


urlpatterns = [
    url(r'^geomodeldiff$', GeomodeldiffList.as_view()),
    url(r'^update', Update.as_view()),
]
