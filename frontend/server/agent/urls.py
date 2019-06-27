from django.urls import re_path
from agent.views import agent_ip, vm_cred

urlpatterns = [
    re_path('agent_ip/', agent_ip),
    re_path('vm_cred/(?P<id>[0-9]*)', vm_cred)
]
