from django.urls import re_path
from tracking.views import start_process, track

urlpatterns = [
    re_path('start_process/', start_process),
    re_path('track/(?P<pool_id>[0-9]*)', track),
]
