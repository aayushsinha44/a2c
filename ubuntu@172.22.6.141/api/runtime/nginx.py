from .runtime import Runtime
import re

class Nginx(Runtime):

    def __init__(self, proccess_id, ssh_client, proccess_name, process_port):
        super().__init__(ssh_client, proccess_name)
        self.proccess_id=proccess_id
        self.process_port=process_port
        
    # Abstract class method
    def generate_container_file(self):
        # return docker file
        return ""

    # Abstract method
    def get_code_folder_path(self):
        '''
            Transfers the static files to local machine
        '''
        return self.nginx_conf_file()

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
        for file in output:
            cmd="cat /etc/nginx/sites-enabled/"+file
            _, out, _ = self.ssh_cleint.exec_command(cmd)
            x = re.findall('root /.*' , out)
            for line in x:
                for l in out.split('\n'):
                    if line in l and '#' not in l:
                        files.append(line.split(' ')[-1][:-1])
        return files
        

    def _dockerfile_configuration(self):

        '''
            Generates docker file configuration as per local machine
        '''

        _docker_file = {
            "version": self.nginx_version(),
            "copy_location": self.nginx_conf_file(), # list
            "expose": self.process_port
        } 

    def is_load_balancer(self):

        if len(self.nginx_conf_file()) == 0:
            return True

        return False
