from agent.models import AgentIPModel
from agent.helper.constants import DOESNOT_EXISTS, ALREADY_EXISTS, \
    ADDED_SUCCESS, UPDATE_SUCCESS

class Agent():

    def __init__(self, user_object):
        self.__user_object=user_object

    def get_agent_cred(self):
        
        if not self.__check_user_exists_in_agent_ip():
            return DOESNOT_EXISTS
        
        return list(AgentIPModel.objects.filter(
            username=self.__user_object.get_user_object()).values())

    def add_agent_cred(self, agent_ip):

        if self.__check_user_exists_in_agent_ip():
            _vm_object=self.get_agent_ip_model_object()
            _vm_object.vm_ip=agent_ip
            _vm_object.save()
            return UPDATE_SUCCESS

        else:
            AgentIPModel.objects.create(username=self.__user_object.get_user_object(), 
                                    agent_ip=agent_ip)
            return ADDED_SUCCESS

    def __check_user_exists_in_agent_ip(self):
        if AgentIPModel.objects.filter(username=self.__user_object.get_user_object()).count() == 0:
            return False
        return True

    def get_agent_ip_model_object(self):
        return AgentIPModel.objects.get(username=self.__user_object.get_user_object())

    def get_agent_ip(self):
        if not self.__check_user_exists_in_agent_ip():
            return DOESNOT_EXISTS

        return list(AgentIPModel.objects.filter(
            username=self.__user_object.get_user_object()).values())[0]["agent_ip"]
