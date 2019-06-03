from .constants import PASSWORD
import os

class Docker():

    def __init__(self, registry, username, password, ssh_client, dev=False):
        self._registry = registry
        self._username = username
        self._password = password
        self._ssh_client=ssh_client
        self.dev=dev
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
        if self.dev:
            os.system('echo %s|sudo -S %s' % (PASSWORD, _cmd))
        else:
            os.system(_cmd)

    def get_username(self):
        return self._username

    def build(self, process_name):
        '''
            Builds docker image
        '''
        user_path = self._ssh_client.get_user_data_path()
        _cmd="sudo docker build -t "+self._username +"/"+process_name+" ."
        root_path = os.getcwd()
        print("Root path:", root_path)
        os.chdir(user_path+"/"+process_name)
        print("Docker build command:", _cmd, os.getcwd())
        if self.dev:
            os.system('echo %s|sudo -S %s' % (PASSWORD, _cmd))
        else:
            os.system(_cmd)
        os.chdir(root_path)
        

    def push(self, process_name, version=None):
        if version is None:
            version='latest'
        _cmd="sudo docker push "+self._username+"/"+process_name
        print("Docker push command:", _cmd)
        if self.dev:
            os.system('echo %s|sudo -S %s' % (PASSWORD, _cmd))
        else:
            os.system(_cmd)

    def get_tag(self, process_name):
        return self._username+"/"+process_name



