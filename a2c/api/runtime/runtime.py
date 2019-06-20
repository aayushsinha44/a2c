from abc import ABC, abstractmethod
import os

class Runtime(ABC):

    def __init__(self, ssh_client, process_id, process_name, process_port, docker_client):
        self.ssh_client=ssh_client
        self.process_id=process_id
        self.process_name=process_name
        self.process_port=process_port
        self.docker_client=docker_client
    
    @abstractmethod
    def generate_container_file(self):
        # returns docker file
        pass

    def save_container_info(self):
        # save container_information in the local 
        
        _container_file = self.generate_container_file()
        _path = self.ssh_client.get_user_data_path() 
        if _path[-1] != "/":
            _path += "/" 
        _path += self.get_process_path() + "/"

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
            print("Moving data:", p)
            self.ssh_client.scp(client_path=p["source"], 
                                process_path=self.get_process_path(),
                                host_path=p["destination"],
                                is_folder=p["is_folder"],
                                is_sudo=p["is_sudo"])

            # TODO: check for success

    def get_process_path(self):
        return self.process_id+self.process_name

    def build_container(self):
        self.docker_client.build(self.get_process_path())

    def push_container_docker_registry(self):
        self.docker_client.push(self.get_process_path())

    def get_port(self):
        return self.process_port

    def get_image(self):
        return self.docker_client.get_username()+"/"+self.get_process_path()

    def get_name(self):
        return self.process_name

    def get_process_id(self):
        return self.process_id

    # def save_kubernetes_yaml(self):
    #     '''
    #         Save kubernetes yaml file for process
    #     '''
    #     _image=self.docker_client.get_tag(self.process_name)

    #     _yaml = generate_yaml(self.process_name, _image, str(self.process_port))
    #     _path = self.ssh_client.get_user_data_path() 
    #     print(_path)
    #     if _path[-1] != "/":
    #         _path += "/" 
    #     _path += 'kubernetes/'
    #     print(_path)
    #     if not os.path.exists(_path):
    #         os.makedirs(_path)

    #     _file = open(_path+self.process_name+'.yaml', 'w')
    #     _file.write(_yaml)
    #     _file.close()
        



def generate_yaml(name, image, port, no_replicas=3, service_type="LoadBalancer"):
    '''
        Returns kubernetes yaml file 
    '''

    _yaml = [
        "apiVersion: extensions/v1beta1",
        "kind: Deployment",
        "metadata:",
        "  name: "+name,
        "spec:",
        "  replicas: "+str(no_replicas),
        "  template: ",
        "    metadata: ",
        "      labels: ",
        "        app: "+name,
        "    spec:",
        "      containers:",
        "        - name: "+name,
        "          image: "+image,
        "          ports:",
        "            - containerPort: "+ port,
        "",
        "---",
        "apiVersion: v1",
        "kind: Service",
        "metadata:",
        "  name: "+name+"-service",
        "  labels:",
        "    name: "+name+"-service",
        "spec:",
        "  ports:",
        "    - port: "+port,
        "      targetPort: "+port,
        "      protocol: TCP",
        "  selector:",
        "    app: "+name,
        "  type: "+service_type
    ]
    return '\n'.join(_yaml)
    


