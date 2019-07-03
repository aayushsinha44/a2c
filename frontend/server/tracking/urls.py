from django.urls import re_path
from tracking.views import start_process

urlpatterns = [
    re_path('start_process/', start_process),
]
