import os
from .constants import PASSWORD

class Docker():

    def __init__(self, registry, username, password, ssh_client):
        self._registry = registry
        self._username = username
        self._password = password
        self._ssh_client=ssh_client
        # self._client=docker.from_env()

    def login(self):
        '''
            Login to docker register
        '''
        # for this, then chown ubuntu for all folders
        # self.client.login(username=self.username, 
        #                 password=self.password, 
        #                 registry=self.registry)
        _cmd = "sudo docker login -u "+self._username+" -p "+self._password+" "+self._registry
        os.system('echo %s|sudo -S %s' % (PASSWORD, _cmd))

    def build(self, process_name):
        '''
            Builds docker image
        '''
        user_path = self._ssh_client.get_user_data_path()
        _cmd="sudo docker build -t "+self._username +"/"+process_name+" ."
        root_path = os.getcwd()
        os.chdir(user_path+"/"+process_name)
        print("Docker build command:", _cmd)
        os.system('echo %s|sudo -S %s' % (PASSWORD, _cmd))
        os.chdir(root_path)
        

    def push(self, process_name, version=None):
        if version is None:
            version='latest'
        _cmd="sudo docker push "+self._username+"/"+process_name
        print("Docker push command:", _cmd)
        os.system('echo %s|sudo -S %s' % (PASSWORD, _cmd))

    def get_tag(self, process_name):
        return self._username+"/"+process_name



