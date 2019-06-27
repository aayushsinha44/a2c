from django.contrib import admin
from agent.models import VMModel, AgentIPModel

# Register your models here.
admin.site.register(VMModel)
admin.site.register(AgentIPModel)