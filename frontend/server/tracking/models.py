from django.db import models
from user.models import UserModel
from agent.models import VMModel

class AgentStatusModel(models.Model):
    id=models.AutoField(primary_key=True)
    agent_hostname=models.CharField(max_length=100)
    username=models.ForeignKey(UserModel, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class VMPoolModel(models.Model):

    username=models.ForeignKey(UserModel, on_delete=models.CASCADE)
    in_use=models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

class VMGroupModel(models.Model):
    id=models.AutoField(primary_key=True)
    vm=models.ForeignKey(VMModel, on_delete=models.CASCADE)
    pool_id=models.ForeignKey(VMPoolModel, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)

class VMStatusModel(models.Model):

    id=models.AutoField(primary_key=True)
    pool_id=models.ForeignKey(VMPoolModel, on_delete=models.CASCADE)
    vm=models.ForeignKey(VMModel, on_delete=models.CASCADE)
    login_status=models.BooleanField(default=False)
    process_discovery=models.BooleanField(default=False)
    initialize_kubernetes=models.BooleanField(default=False)
    kubernetes_save_file=models.BooleanField(default=False)
    kubernetes_apply=models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class VMProcessModel(models.Model):

    id=models.AutoField(primary_key=True)
    pool_id=models.ForeignKey(VMPoolModel, on_delete=models.CASCADE)
    vm_id=models.ForeignKey(VMModel, on_delete=models.CASCADE)
    process_port=models.IntegerField()
    process_id=models.IntegerField()
    process_name=models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)


class VMProcessStatusModel(models.Model):

    id=models.AutoField(primary_key=True)
    pool_id=models.ForeignKey(VMPoolModel, on_delete=models.CASCADE)
    vm_id=models.ForeignKey(VMModel, on_delete=models.CASCADE)
    process_id=models.ForeignKey(VMProcessModel, on_delete=models.CASCADE)
    start_containerization=models.BooleanField(default=False)
    save_code=models.BooleanField(default=False)
    save_container_info=models.BooleanField(default=False)
    build_container=models.BooleanField(default=False)
    push_container_docker_registry=models.BooleanField(default=False)

    kubernetes_add_container=models.BooleanField(default=False)
    kubernetes_add_service=models.BooleanField(default=False)
    kubernetes_add_volume=models.BooleanField(default=False, null=True, blank=True)
    kubernetes_transfer_data_to_volume=models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return str(self.id)


