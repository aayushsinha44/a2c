from .runtime import Runtime
import re

class Apache(Runtime):

    def __init__(self, process_id, ssh_client, proccess_name, process_port, docker_client):
        super().__init__(ssh_client, process_id, proccess_name, process_port, docker_client)
        self._conf_file_location = None
        self._files = []
        self._set_conf_file_location()
        self._search_for_files_to_copy()

    # abstract method
    def generate_container_file(self):
        # returns docker file

        _docker_file = [
            "FROM ubuntu:18.04",
            "RUN apt-get update ",
            "RUN apt-get install apache2",
        ]

        #Copy the required files by reading the apache2 conf file


        #EXPOSE the process port
        _docker_file.append("EXPOSE "+self.process_port)
        _docker_file.append("CMD [\"/usr/sbin/apache2\", \"-D\", \"FOREGROUND\"]")

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
        return self._files
        
    def _set_conf_file_location(self):
        '''
            Sets the object variable _conf_file_location to one of the following locations based on the installation
                /etc/apache2/httpd.conf
                /etc/apache2/apache2.conf
                /etc/httpd/httpd.conf
                /etc/httpd/conf/httpd.conf
        '''
        _cmd = "sudo find /etc -name \"apache2.conf\" | grep -c apache2.conf"
        _, output, _ = self.ssh_client.exec_command(_cmd, is_sudo=True)

        if int(output) == 1:
            _cmd = "sudo find /etc -name \"apache2.conf\""
            _, output, _ = self.ssh_client.exec_command(_cmd, is_sudo=True)

            self._conf_file_location = output
        else:
            _cmd = "sudo find /etc -name \"httpd.conf\""
            _, output, _ = self.ssh_client.exec_command(_cmd, is_sudo=True)

            self._conf_file_location = output


    def _search_for_files_to_copy(self):
        _cmd = "cat " + self._conf_file_location
        _, output, _ = self.ssh_client.exec_command(_cmd)

        _conf_file_content = self.remove_coments_and_emptylines(output)

    def remove_coments_and_emptylines(self, content):
        content = str(content)
        ret_val = re.sub(r'(?m)^ *#.*\n?', '', content) #removes the comments from content

        content = ""

        for line in ret_val.split('\n'):
            if re.match(r'^\s*$', line):
                continue
            content += line +'\n'
        
        return content


    def apache_version(self):
        '''
            
        '''