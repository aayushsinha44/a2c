from agent.models import VMModel
from agent.helper.constants import UPDATE_SUCCESS, \
     ADDED_SUCCESS, INVALID_ACCESS, INVALID_PARAMETER_STRUCTURE, \
     DELETE_SUCCESS

class VM():

    def __init__(self, user_object):
        self.__user_object=user_object

    def get_vm_object(self, id=None):
        if id==None:
            return VMModel.objects.get(
                username=self.__user_object.get_user_object())
        else:
            return VMModel.objects.get(
                username=self.__user_object.get_user_object(),
                id=id)

    def get_all_vm_cred(self):
        return list(VMModel.objects.filter(
            username=self.__user_object.get_user_object()).values())
    
    def get_vm_cred(self, id):
        return list(VMModel.objects.filter(
            username=self.__user_object.get_user_object(),
            id=id).values())

    def add_vm_cred(self, data_structure):
        if not self.__check_structure(data_structure):
            return INVALID_PARAMETER_STRUCTURE

        VMModel.objects.create(vm_username=data_structure["vm_username"],
                vm_hostname=data_structure["vm_hostname"],
                vm_password=data_structure["vm_password"],
                vm_port=data_structure["vm_port"],
                vm_pKey=data_structure["vm_pKey"],
                vm_passphrase=data_structure["vm_passphrase"],
                username=self.__user_object.get_user_object())
        
        return ADDED_SUCCESS

    def update_vm_cred(self, id, data_structure):
        
        if VMModel.objects.filter(
            username=self.__user_object.get_user_object(),
            id=id).count() == 0:
            return INVALID_ACCESS

        if not self.__check_structure(data_structure):
            return INVALID_PARAMETER_STRUCTURE
        
        _vm_object=self.get_vm_object(id=id)
        _vm_object.vm_username = data_structure["vm_username"]
        _vm_object.vm_hostname = data_structure["vm_hostname"]
        _vm_object.vm_password = data_structure["vm_password"]
        _vm_object.vm_port = data_structure["vm_port"]
        _vm_object.vm_pKey = data_structure["vm_pKey"]
        _vm_object.vm_passphrase = data_structure["vm_passphrase"]
        _vm_object.save()
        return UPDATE_SUCCESS

    def __check_structure(self, data_structure):
        _param_struct=["vm_username", "vm_hostname",
                    "vm_password", "vm_port", "vm_pKey", "vm_passphrase"]

        for key in _param_struct:
            if key not in data_structure:
                return False
        return True

    def delete_vm(self, id):
        if VMModel.objects.filter(
            username=self.__user_object.get_user_object(),
            id=id).count() == 0:
            return INVALID_ACCESS
        _vm_object=self.get_vm_object(id=id)
        _vm_object.delete()
        return DELETE_SUCCESS
    