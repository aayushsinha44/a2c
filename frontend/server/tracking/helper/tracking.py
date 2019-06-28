from tracking.models import AgentStatusModel
from agent.helper.agent import Agent
from agent.helper.vm import VM

class Tracking():

    def __init__(self, user):
        self.__user=user
        self.__vm=VM(user)
        self.__agent=Agent(user)

    def __check_agent_lock(self):

        if AgentStatusModel.objects.filter(
            username=self.__user.get_user_object(),
            agent_hostname=self.__agent.get_agent_ip()).count() == 0:
            return False
        return True

    def __check_kube_config_file(self):
        pass

    def __check_docker_cred(self):
        pass

    def __check_agent_exist(self):
        pass

    # check system before starting process
    def check_system(self):

        if self.__check_agent_lock() == False:
            pass
        pass

    def __lock_agent(self):
        
        _user_object=self.__user.get_user_object()
        _agent_ip=self.__agent.get_agent_ip()

        AgentStatusModel.objects.create(
            agent_hostname=_agent_ip,
            username=_user_object
        )

    def __unlock_agent(self):
        # delete agent in Agent status model
        pass

        
