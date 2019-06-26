from django.contrib import admin
from user.models import UserModel, UserDockerCred, KubernetesConfigModel

# Register your models here.
admin.site.register(UserModel)
admin.site.register(UserDockerCred)
admin.site.register(KubernetesConfigModel)