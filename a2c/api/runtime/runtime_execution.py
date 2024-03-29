from .nginx import Nginx
from .apache import Apache
from .tomcat import Tomcat
from .mysql import MySQL
from .constants import SUPPORTED_RUNTIME, NGINX, APACHE, TOMCAT, MYSQL

class RuntimeExecution():

    def __init__(self, process_port, process_id, process_name, ssh_client, docker_client, vm_data):
        self.process_name=process_name
        self.process_id=process_id
        self.process_name=process_name
        self.ssh_client=ssh_client
        self.process_port=process_port
        self.docker_client=docker_client
        self.vm_data=vm_data

    def is_supported(self):
        '''
        Returns: True/False
        True: if runtime is supported
        False: if runtime is not supported
        '''
        if self.process_name in SUPPORTED_RUNTIME:
            return True
        return False

    def get_runtime(self, mysql_db_username=None, mysql_db_password=None):

        if self.is_supported():
            if self.process_name == NGINX:
                _runtime = Nginx(self.process_id, 
                                self.ssh_client, 
                                self.process_name, 
                                self.process_port, 
                                self.docker_client,
                                self.vm_data)
                
            elif self.process_name == TOMCAT:
                _runtime = Tomcat(self.process_id, 
                                self.ssh_client, 
                                self.process_name, 
                                self.process_port, 
                                self.docker_client,
                                self.vm_data)

            elif self.process_name == MYSQL:
                _runtime = MySQL(self.process_id, 
                                self.ssh_client, 
                                self.process_name, 
                                self.process_port, 
                                self.docker_client,
                                self.vm_data,
                                mysql_db_username,
                                mysql_db_password)

            elif self.process_name == APACHE:
                _runtime = Apache(self.process_id, 
                                self.ssh_client, 
                                self.process_name, 
                                self.process_port, 
                                self.docker_client,
                                self.vm_data)
            
            else:
                _runtime=None
            return _runtime


    def call_runtime(self, mysql_db_username=None, mysql_db_password=None):

        if self.is_supported():
            if self.process_name == NGINX:
                _runtime = Nginx(self.process_id, 
                                self.ssh_client, 
                                self.process_name, 
                                self.process_port, 
                                self.docker_client,
                                self.vm_data)
                
            elif self.process_name == TOMCAT:
                _runtime = Tomcat(self.process_id, 
                                self.ssh_client, 
                                self.process_name, 
                                self.process_port, 
                                self.docker_client,
                                self.vm_data)

            elif self.process_name == MYSQL:
                _runtime = MySQL(self.process_id, 
                                self.ssh_client, 
                                self.process_name, 
                                self.process_port, 
                                self.docker_client,
                                self.vm_data,
                                mysql_db_username,
                                mysql_db_password)

            elif self.process_name == APACHE:
                _runtime = Apache(self.process_id, 
                                self.ssh_client, 
                                self.process_name, 
                                self.process_port, 
                                self.docker_client,
                                self.vm_data)
            
            else:
                _runtime=None
            
            _runtime.save_code()
            _runtime.save_container_info()  
            _runtime.build_container()
            _runtime.push_container_docker_registry()
            # _runtime.save_kubernetes_yaml()

            # elif self.process_name == APACHE:
            #     pass
                # _runtime = Apache(self.process_id, self.ssh_client, self.process_name, self.process_port)

            # _runtime.save_container_info()
            # _runtime.save_code()

    