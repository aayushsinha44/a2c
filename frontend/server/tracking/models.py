from django.db import models
from user.models import UserModel
from agent.models import VMModel

class VMStateModel(models.Model):

    vm=models.ForeignKey(VMModel, on_delete=models.CASCADE)
    logging_status=models.BooleanField()
    process_discovery=models.BooleanField()

    start_containerization=models.BooleanField()
    save_code=models.BooleanField()


