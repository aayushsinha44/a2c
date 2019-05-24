from .nginx import Nginx
from .apache import Apache
from .constants import SUPPORTED_RUNTIME, NGINX, APACHE

class RuntimeExecution():

    def __init__(self, process_port, process_id, process_name, ssh_client):
        self.process_name=process_name
        self.process_id=process_id
        self.process_name=process_name
        self.ssh_client=ssh_client
        self.process_port=process_port

    def is_supported(self):
        '''
        Returns: True/False
        True: if runtime is supported
        False: if runtime is not supported
        '''
        if self.process_name in SUPPORTED_RUNTIME:
            return True
        return False

    def call_runtime(self):

        if self.is_supported():

            if self.process_name == NGINX:
                _runtime = Nginx(self.process_id, self.ssh_client, self.process_name[:-1], self.process_port)
                if _runtime.is_load_balancer():
                    return

            elif self.process_name == APACHE:
                _runtime = Apache(self.process_id, self.ssh_client, self.process_name, self.process_port)

            _runtime.save_container_info()
            _runtime.save_code()

    