from .runtime import Runtime
import re


class Nginx(Runtime):

    def __init__(self, process_id, ssh_client, proccess_name, process_port, docker_client, vm_data):
        '''
            vm_data:
            {
                "172.22.6.161": [
                    {
                        "process_name": "mysqld",
                        "process_id": 123,
                        "process_port": 3306
                    }
                ]
            }
        '''
        super().__init__(ssh_client, process_id, proccess_name, process_port, docker_client)
        self._vm_data=vm_data
        self._critical_content = []
        self._nginx_conf_files = self.nginx_conf_file()
        

    # Abstract class method
    def generate_container_file(self):
        # return docker file
        _docker_file_data=self._dockerfile_configuration()
        _docker_file=[
            "FROM ubuntu:18.04",#+_docker_file_data["version"],
            "RUN apt-get update",
            "RUN apt-get -y install nginx",
        ]
        for i in range(len(_docker_file_data["conf_files_source"])):
            # _docker_file.append("COPY "+  \
            #     self._build_absolute_path(_docker_file_data["conf_files_destination"][i]) + " "  \
            #     + "/etc/nginx/conf.d/"+_docker_file_data["conf_files_destination"][i].split("/")[-1])
            _docker_file.append("COPY "+  \
                self._build_absolute_path(_docker_file_data["conf_files_destination"][i]) + " "  \
                +_docker_file_data["conf_files_destination"][i])
        for i in range(len(_docker_file_data["copy_location_source"])):
            _docker_file.append("COPY "+ \
                 self._build_absolute_path(_docker_file_data["copy_location_destination"][i]) \
                 + " " + _docker_file_data["copy_location_destination"][i])
        _docker_file.append("EXPOSE "+self.process_port)
        _docker_file.append("RUN apt clean")
        
        for data in self._critical_content:
            for vd in self._vm_data:
                # print(vd, self._vm_data[vd][0]["process_name"])
                _docker_file.append("RUN sed -i 's/"+vd+"/"+self._vm_data[vd][0]["process_name"]+"-service/g' "+data)

        # _docker_file.append('CMD ["service", "nginx", "start"]')
        _docker_file.append('RUN echo "daemon off;" >> /etc/nginx/nginx.conf')
        _docker_file.append('CMD ["nginx"]')
        _docker_file.append("")
        return '\n'.join(_docker_file)

    def _build_absolute_path(self, path):
        # _abs_path=self.ssh_client.get_user_data_path()
        # if _abs_path[-1]!='/':
        #     _abs_path += "/"
        # _abs_path = self.process_name
        # if path[0] != '/':
        #     _abs_path += '/'
        # return _abs_path + path
        return path[1:]
        

    # Abstract method
    def get_code_folder_path(self):
        '''
            Transfers the files to local machine
            [
                {
                    "source": '/var/www/html'
                    "desitnation": '/var/www/html'
                    "is_folder": True,
                    "is_sudo: False
                }
            ]
        '''
        return self._nginx_conf_files[0]+self._nginx_conf_files[1]

    def nginx_version(self):
        '''
            Returns version of nginx
        '''
        _, _, output = self.ssh_client.exec_command('nginx -v')
        output=output.split(" ")[-2].split('/')[-1]
        return output
    
    def nginx_conf_file(self):
        '''
            Extracts the root folder for the nginx process
            Algo:
                1. nginx -t
                2. get nginx.conf file
                3. search for all "include /var/www/"
                4. go to all folder and search every file for "root /var/www"
                5. find all path (/var/awww) -- files/folder, copy that too 
        '''

        files = []
        conf_files=[]

        _cmd="sudo nginx -t"
        _, output, _ = self.ssh_client.exec_command(_cmd, sudo=True)
        output=output.split('\n')
        # print(output)
        try:
            # if password login is not there
            _nginx_conf_file = output[0].split(' ')[4]
        except:
            _nginx_conf_file = output[2].split(' ')[4]
        conf_files.append(self.get_data_in_format(_nginx_conf_file, '/etc/nginx/nginx.conf', is_folder=False))
        _cmd="cat "+_nginx_conf_file
        _, output, _ = self.ssh_client.exec_command(_cmd, sudo=True)
        out=output
        self.__check_and_add_critical_content(out, '/etc/nginx/nginx.conf')
        # print(out, _cmd)
        x = re.findall('include /.*' , out)
        for line in x:
            for l in out.split('\n'):
                # not a comment
                if line in l and '#' not in l:
                    _path=line.split(' ')[-1][:-1]
                    if "*" in _path or ".conf" in _path:
                        _path = _path.split('/')[:-1]
                        _path = '/'.join(_path)
                    _path=_path.strip()
                    if _path[-1] == ';':
                        _path=_path[:-1]
                    # dependencies - modules-enabled
                    files.append(self.get_data_in_format(_path, _path, is_folder=True, is_sudo=False))
                    cmd="ls -p "+ _path +" | grep -v /" # files only
                    _, output, error = self.ssh_client.exec_command(cmd)
                    output=output.split('\n')
                    
                    if error == "":
                        # static files path
                        for file in output:
                            __path=_path
                            if _path != '/':
                                __path += '/'
                            cmd="cat "+__path+file
                            _, _out, _ = self.ssh_client.exec_command(cmd)
                            self.__check_and_add_critical_content(_out, __path+file)
                            # print("out", out)
                            # static files
                            _x = re.findall('root /.*' , _out)
                            for line in _x:
                                for l in _out.split('\n'):
                                    if line in l and '#' not in l:
                                        _path=line.split(' ')[-1][:-1]
                                        files.append(self.get_data_in_format(_path, _path, is_folder=True, is_sudo=False))

        # search for path
        x = re.findall('/.*/.*' , out)
        return files, conf_files

    def __check_and_add_critical_content(self, file_text, file_path):

        check_flag=False
        # check
        for _data in self._vm_data:
            if _data in file_text:
                check_flag=True
                break

        if check_flag:
            self._critical_content.append(file_path)
        # print(file_text)

        

    def _dockerfile_configuration(self):

        '''
            Generates docker file configuration as per local machine
        '''
        _nginx_conf_file=self._nginx_conf_files
        _nginx_conf_file_source=[]
        for i in _nginx_conf_file[1]:
            _nginx_conf_file_source.append(i["source"])

        _nginx_conf_file_destination=[]
        for i in _nginx_conf_file[1]:
            _nginx_conf_file_destination.append(i["destination"])

        _copy_location_source=[]
        for i in _nginx_conf_file[0]:
            _copy_location_source.append(i["source"])

        _copy_location_destination=[]
        for i in _nginx_conf_file[0]:
            _copy_location_destination.append(i["destination"])


        _docker_file = {
            "version": self.nginx_version(),
            "conf_files_source": _nginx_conf_file_source, # list
            "conf_files_destination": _nginx_conf_file_destination, # list
            "copy_location_source": _copy_location_source, # list
            "copy_location_destination": _copy_location_destination, # list
            "expose": self.process_port
        } 
        return _docker_file
