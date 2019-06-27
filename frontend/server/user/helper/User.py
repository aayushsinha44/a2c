from user.models import UserModel, UserDockerCred, KubernetesConfigModel
from user.helper.constants import INVALID_ATTRIBUTES, USER_ADDED_SUCCESS, ADDED_SUCCESS, UPDATE_SUCESS \
    , USER_EXISTS, INVALID_STRUCTURE, DOESNOT_EXISTS

class User():

    def __init__(self, username):
        self.__username=username
        self.__check_username()

    @staticmethod
    def add_user(user_structure: dict):

        if User.check_user_structure(user_structure):

            if User.check_user_exists(user_structure["username"]):
                return USER_EXISTS
            
            UserModel.objects.create(username=user_structure["username"],
                                    name=user_structure["name"],
                                    password=user_structure["password"])

            return USER_ADDED_SUCCESS

        else:
            return INVALID_ATTRIBUTES

    @staticmethod
    def check_user_structure(user_structure: dict):
        
        __user_structure_param=["username", "password", "name"]

        for key in __user_structure_param:
            if key not in user_structure:
                return False
        return True

    @staticmethod
    def check_user_exists(username):

        if UserModel.objects.filter(username=username).count() > 0:
            return True
        return False

    @staticmethod
    def check_user(username, password):
        if UserModel.objects.filter(username=username, password=password).count() > 0:
            return True
        return False

    def __check_username(self):
        if UserModel.objects.filter(username=self.__username).count() == 0:
            raise ValueError("User doesnot exists")

    def get_user_object(self):
        return UserModel.objects.get(username=self.__username)

    def add_docker_cred(self, data_structure):
        if self.__check_docker_cred_structure(data_structure):

            return self.__add_docker_cred(data_structure["docker_registry_username"],
                                        data_structure["docker_registry_password"],
                                        data_structure["docker_registry"])
        else:
            return INVALID_STRUCTURE
        

    def __check_docker_cred_structure(self, data_structure):
        __structure_param=["docker_registry_username", "docker_registry_password", "docker_registry"]

        for key in __structure_param:
            if key not in data_structure:
                return False
        return True

    def __add_docker_cred(self, docker_registry_username, docker_registry_password, docker_registry):

        # check if exists
        if self.check_docker_cred_exists():
            _docker_cred=UserDockerCred.objects.get(username=self.get_user_object())
            _docker_cred.docker_registry=docker_registry
            _docker_cred.docker_registry_username=docker_registry_username
            _docker_cred.docker_registry_password=docker_registry_password
            _docker_cred.save()

            return UPDATE_SUCESS

        else:
            
            UserDockerCred.objects.create(username=self.get_user_object(),
                                        docker_registry=docker_registry,
                                        docker_registry_username=docker_registry_username,
                                        docker_registry_password=docker_registry_password)

            return ADDED_SUCCESS

    def get_docker_cred(self):

        if self.check_docker_cred_exists():
            
            return list(UserDockerCred.objects.filter(username=self.get_user_object()).values())[0]

        else:
            return DOESNOT_EXISTS
    
    def check_docker_cred_exists(self):
        if UserDockerCred.objects.filter(username=self.get_user_object()).count() == 0:
            return False
        return True

    def add_kubernetes_cred(self, data_structure):
        if self.__check_kubernetes_cred_structure(data_structure):

            return self.__add_kubernetes_cred(data_structure["kube_conf_file"])
        else:
            return INVALID_STRUCTURE
        

    def __check_kubernetes_cred_structure(self, data_structure):
        __structure_param=["kube_conf_file"]

        for key in __structure_param:
            if key not in data_structure:
                return False
        return True

    def __add_kubernetes_cred(self, kube_conf_file):

        # check if exists
        if self.check_kube_cred_exists():
            _kube_cred=KubernetesConfigModel.objects.get(username=self.get_user_object())
            _kube_cred.kube_conf_file=kube_conf_file
            _kube_cred.save()

            return UPDATE_SUCESS

        else:
            
            KubernetesConfigModel.objects.create(username=self.get_user_object(),
                                                kube_conf_file=kube_conf_file)

            return ADDED_SUCCESS

    def get_kubernetes_cred(self):

        if self.check_kube_cred_exists():
            
            return list(KubernetesConfigModel.objects.filter(username=self.get_user_object()).values())[0]

        else:
            return DOESNOT_EXISTS

    
    def check_kube_cred_exists(self):
        if KubernetesConfigModel.objects.filter(username=self.get_user_object()).count() == 0:
            return False
        return True
