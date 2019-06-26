from django.urls import re_path
from user.views.auth import register, login
from user.views.cred import docker_cred, kube_cred

urlpatterns = [
    re_path('register/', register),
    re_path('login/', login),
    re_path('docker_cred/', docker_cred),
    re_path('kube_cred/', kube_cred),
]
