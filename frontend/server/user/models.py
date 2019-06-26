from django.db import models

# Create your models here.
class UserModel(models.Model):

    username=models.EmailField(unique=True, primary_key=True)
    name=models.CharField(max_length=100)
    password=models.CharField(max_length=255)

    def __str__(self):
        return str(self.username)

class UserDockerCred(models.Model):

    id=models.AutoField(primary_key=True)
    username=models.OneToOneField(UserModel, on_delete=models.CASCADE)
    docker_registry=models.CharField(max_length=100)
    docker_registry_username=models.CharField(max_length=100)
    docker_registry_password=models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)

class KubernetesConfigModel(models.Model):
    id=models.AutoField(primary_key=True)
    username=models.OneToOneField(UserModel, on_delete=models.CASCADE)
    kube_conf_file=models.TextField()

    def __str__(self):
        return str(self.id)
