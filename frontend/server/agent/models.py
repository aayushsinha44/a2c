from django.db import models
from user.models import UserModel

# Create your models here.
class AgentIPModel(models.Model):

    id=models.AutoField(primary_key=True)
    username=models.OneToOneField(UserModel, on_delete=models.CASCADE)
    agent_ip=models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)

class VMModel(models.Model):

    id=models.AutoField(primary_key=True)
    username=models.ForeignKey(UserModel, on_delete=models.CASCADE)
    vm_hostname=models.CharField(max_length=100)
    vm_username=models.CharField(max_length=100)
    vm_password=models.CharField(max_length=255, null=True, blank=True)
    vm_port=models.CharField(max_length=100)
    vm_pKey=models.TextField(null=True, blank=True)
    vm_passphrase=models.CharField(max_length=100, null=True, blank=True)
    vm_no_replica=models.IntegerField()

    def __str__(self):
        str(self.id)

    class Meta:
        unique_together = (("username", "vm_hostname"),)
