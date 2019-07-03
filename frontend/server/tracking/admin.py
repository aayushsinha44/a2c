from django.contrib import admin
from tracking.models import AgentStatusModel, VMGroupModel, \
    VMStatusModel, VMProcessModel, VMProcessStatusModel, VMPoolModel
# Register your models here.
admin.site.register(AgentStatusModel)
admin.site.register(VMGroupModel)
admin.site.register(VMStatusModel)
admin.site.register(VMProcessModel)
admin.site.register(VMProcessStatusModel)
admin.site.register(VMPoolModel)