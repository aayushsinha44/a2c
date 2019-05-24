from .nginx import Nginx
from .constants import SUPPORTED_RUNTIME, NGINX

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
                print(_runtime.nginx_conf_file())
                print("Stared code saving")
                _runtime.save_code()
                print('code saved')

            # _runtime.save_container_info()
            # _runtime.save_code()

    