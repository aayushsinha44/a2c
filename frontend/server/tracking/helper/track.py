from tracking.models import VMPoolModel, VMGroupModel, \
    VMStatusModel, VMProcessModel, VMProcessStatusModel
from agent.helper.vm import VM

class Track():

    def __init__(self, user, pool_id):
        self.__user=user
        self.__pool_id=pool_id
        self.__vm=VM(user)

    def __get_pool_object(self):
        return VMPoolModel.objects.get(
            id=self.__pool_id,
            username=self.__user.get_user_object()
        )

    def get_pool_info(self):
        return list(VMPoolModel.objects.filter(
            id=self.__pool_id,
            username=self.__user.get_user_object()).values())[0]
    
    def get_vm_group_info(self):
        return list(VMGroupModel.objects.filter(
            pool_id=self.__get_pool_object()
        ).values())

    def get_vm_status_info(self):
        return list(VMStatusModel.objects.filter(
            pool_id=self.__get_pool_object()
        ).values())

    def get_vm_process_info(self):
        return list(VMProcessModel.objects.filter(
            pool_id=self.__get_pool_object()
        ).values())

    def get_vm_process_status_info(self):
        return list(VMProcessStatusModel.objects.filter(
            pool_id=self.__get_pool_object()
        ).values())

    def get_info(self):
        data={}
        data["pool_info"]=self.get_pool_info()
        data["vm_group_info"]=self.get_vm_group_info()
        data["vm_status_info"]=self.get_vm_status_info()
        data["vm_process_info"]=self.get_vm_process_info()
        data["vm_process_status_info"]=self.get_vm_process_status_info()
        return data
