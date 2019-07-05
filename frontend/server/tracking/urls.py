from django.urls import re_path
from tracking.views import start_process, track, get_services

urlpatterns = [
    re_path('start_process/', start_process),
    re_path('track/(?P<pool_id>[0-9]*)', track),
    re_path('get_services/', start_process),
]
