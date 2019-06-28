from django.db import models
from user.models import UserModel
from agent.models import VMModel

class AgentStatusModel(models.Model):
    id=models.AutoField(primary_key=True)
    agent_hostname=models.CharField(max_length=100)
    username=models.ForeignKey(UserModel, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class VMGroupModel(models.Model):
    id=models.AutoField(primary_key=True)
    vm=models.ForeignKey(VMModel, on_delete=models.CASCADE)
    in_use=models.BooleanField()

    def __str__(self):
        return str(self.id)

class VMStatusModel(models.Model):

    id=models.AutoField(primary_key=True)
    vm=models.ForeignKey(VMModel, on_delete=models.CASCADE)
    login_status=models.BooleanField()
    process_discovery=models.BooleanField()
    initialize_kubernetes=models.BooleanField()
    kubernetes_save_file=models.BooleanField()
    kubernetes_apply=models.BooleanField()

    def __str__(self):
        return str(self.id)

class VMProcessModel(models.Model):

    id=models.AutoField(primary_key=True)
    vm_id=models.ForeignKey(VMStatusModel, on_delete=models.CASCADE)
    process_port=models.IntegerField()
    process_id=models.IntegerField()
    process_name=models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)


class VMProcessStatusModel(models.Model):

    id=models.AutoField(primary_key=True)

    vm_id=models.ForeignKey(VMStatusModel, on_delete=models.CASCADE)
    start_containerization=models.BooleanField()
    save_code=models.BooleanField()
    save_container_info=models.BooleanField()
    build_container=models.BooleanField()
    push_container_docker_registry=models.BooleanField()

    kubernetes_add_container=models.BooleanField()
    kubernetes_add_service=models.BooleanField()
    kubernetes_add_volume=models.BooleanField(null=True, blank=True)
    kubernetes_transfer_data_to_volume=models.BooleanField(null=True, blank=True)

    def __str__(self):
        return str(self.id)


