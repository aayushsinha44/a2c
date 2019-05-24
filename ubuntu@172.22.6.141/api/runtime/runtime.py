from abc import ABC, abstractmethod


class Runtime(ABC):

    def __init__(self, ssh_client, process_name):
        self.ssh_cleint=ssh_client
        self.process_name=process_name
    
    @abstractmethod
    def generate_container_file(self):
        # returns docker file
        pass

    def save_container_info(self):
        # save container_information in the local 
        self.ssh_cleint.scp(self.generate_container_file(), self.process_name)

        # TODO: check for success

    @abstractmethod
    def get_code_folder_path(self):
        pass


    def save_code(self):
        '''
            Transfers files to local machine
        '''
        path=self.get_code_folder_path()
        for p in path:
            self.ssh_cleint.scp(client_path=p, 
                                process_name=self.process_name,
                                host_path=p,
                                is_folder=True,
                                is_sudo=False)

            # TODO: check for success

    def build_container(self):
        pass

    def push_code_docker_registry(self):
        pass


