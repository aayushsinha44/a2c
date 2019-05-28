from .runtime import Runtime
import re

class Nginx(Runtime):

    def __init__(self, proccess_id, ssh_client, proccess_name, process_port, docker_client):
        super().__init__(ssh_client, proccess_name, process_port, docker_client)
        self.proccess_id=proccess_id
        
    # Abstract class method
    def generate_container_file(self):
        # return docker file
        _docker_file_data=self._dockerfile_configuration()
        _docker_file=[
            "FROM nginx:"+_docker_file_data["version"],
            "RUN rm /etc/nginx/conf.d/*"
        ]
        for i in range(len(_docker_file_data["conf_files_source"])):
            _docker_file.append("COPY "+  \
                self._build_absolute_path(_docker_file_data["conf_files_destination"][i]) + " "  \
                + "/etc/nginx/conf.d/"+_docker_file_data["conf_files_destination"][i].split("/")[-1])
        for i in range(len(_docker_file_data["copy_location_source"])):
            _docker_file.append("COPY "+ \
                 self._build_absolute_path(_docker_file_data["copy_location_destination"][i]) \
                 + " " + _docker_file_data["copy_location_destination"][i])
        _docker_file.append("EXPOSE "+self.process_port)
        _docker_file.append("")
        return '\n'.join(_docker_file)

    def _build_absolute_path(self, path):
        # _abs_path=self.ssh_cleint.get_user_data_path()
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
        return self.nginx_conf_file()[0]+self.nginx_conf_file()[1]

    def nginx_version(self):
        '''
            Returns version of nginx
        '''
        _, _, output = self.ssh_cleint.exec_command('nginx -v')
        output=output.split(" ")[-2].split('/')[-1]
        return output
    
    def nginx_conf_file(self):
        '''
            Extracts the root folder for the nginx process
        '''

        cmd="ls -p /etc/nginx/sites-enabled | grep -v /" # files only
        _, output, _ = self.ssh_cleint.exec_command(cmd)
        output=output.split('\n')
        files = []
        conf_files=[]
        for file in output:
            cmd="cat /etc/nginx/sites-enabled/"+file
            if len(file) == 0:
                continue
            _data=file
            if ".conf" not in _data:
                _data+=".conf"
            conf_files.append(self.get_data_in_format(
                '/etc/nginx/sites-enabled/'+file,'/etc/nginx/sites-enabled/'+_data,
                is_folder=False, is_sudo=False))
            _, out, _ = self.ssh_cleint.exec_command(cmd)
            x = re.findall('root /.*' , out)
            for line in x:
                for l in out.split('\n'):
                    if line in l and '#' not in l:
                        _path=line.split(' ')[-1][:-1]
                        files.append(self.get_data_in_format(_path, _path, is_folder=True, is_sudo=False))
        return files, conf_files
        

    def _dockerfile_configuration(self):

        '''
            Generates docker file configuration as per local machine
        '''

        _nginx_conf_file_source=[]
        for i in self.nginx_conf_file()[1]:
            _nginx_conf_file_source.append(i["source"])

        _nginx_conf_file_destination=[]
        for i in self.nginx_conf_file()[1]:
            _nginx_conf_file_destination.append(i["destination"])

        _copy_location_source=[]
        for i in self.nginx_conf_file()[0]:
            _copy_location_source.append(i["source"])

        _copy_location_destination=[]
        for i in self.nginx_conf_file()[0]:
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

    def is_load_balancer(self):

        if len(self.nginx_conf_file()) == 0:
            return True

        return False
