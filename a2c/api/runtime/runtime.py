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
        
        _container_file = self.generate_container_file()
        _path = self.ssh_cleint.get_user_data_path() 
        if _path[-1] != "/":
            _path += "/" 
        _path += self.process_name + "/"

        _file = open(_path+'Dockerfile', 'w')
        _file.write(_container_file)
        _file.close()

        # TODO: check for success

    @abstractmethod
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

    def get_data_in_format(self, source, destination, is_folder=True, is_sudo=False):
        _tmp_data={}
        _tmp_data["source"]=source
        _tmp_data["destination"]=destination
        _tmp_data["is_folder"]=is_folder
        _tmp_data["is_sudo"]=is_sudo
        return _tmp_data


    def save_code(self):
        '''
            Transfers files to local machine
        '''
        path=self.get_code_folder_path()
        # print(path, '==========================')
        for p in path:
            print("------Saving code:", p)
            self.ssh_cleint.scp(client_path=p["source"], 
                                process_name=self.process_name,
                                host_path=p["destination"],
                                is_folder=p["is_folder"],
                                is_sudo=p["is_sudo"])

            # TODO: check for success

    def build_container(self):
        pass

    def push_code_docker_registry(self):
        pass


