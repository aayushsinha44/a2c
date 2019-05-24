from .runtime import Runtime

class Apache(Runtime):

    def __init__(self, proccess_id, ssh_client, proccess_name, process_port):
        super().__init__(ssh_client, proccess_name)
        self.proccess_id=proccess_id
        self.process_port=process_port

    # abstract method
    def generate_container_file(self):
        # returns docker file
        pass

    # abstract method
    def get_code_folder_path(self):
        '''
            Returns:
                [
                    {
                        "source": '/var/www/html'
                        "desitnation": '/var/www/html'
                        "is_folder": True,
                        "is_sudo: False
                    }
                ]
        '''
        pass