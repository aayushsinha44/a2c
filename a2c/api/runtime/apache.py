from .runtime import Runtime
import re

class Apache(Runtime):

    def __init__(self, process_id, ssh_client, proccess_name, process_port, docker_client, vm_data):
        super().__init__(ssh_client, process_id, proccess_name, process_port, docker_client)
        self.__vm_data=vm_data
        self._HTTPD_ROOT = None
        self._SERVER_CONFIG_FILE = None
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
        for file in self._files:
            _docker_file.append("COPY "+ self.build_path(file["destination"]) + " " + file["source"])


        #Source the envvars file
        _docker_file.append("RUN source " + self._HTTPD_ROOT +'/envvars')


        #EXPOSE the process port
        _docker_file.append("EXPOSE "+self.process_port)
        _docker_file.append("CMD [\"/usr/sbin/apache2ctl\", \"-D\", \"FOREGROUND\"]")

    def build_path(self, path):
        if path[0] == '/':
            return path[1:]
        return path

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
            Sets the value of _HTTPD_ROOT and _SERVER_CONFIG_FILE(relative to _HTTPD_ROOT) using the 
            following command:
            $ apache2 -V
            Server version: Apache/2.4.29 (Ubuntu)
            Server built:   2019-04-03T13:22:37
            Server's Module Magic Number: 20120211:68
            Server loaded:  APR 1.6.3, APR-UTIL 1.6.1
            Compiled using: APR 1.6.3, APR-UTIL 1.6.1
            Architecture:   64-bit
            Server MPM:
            Server compiled with....
            -D APR_HAS_SENDFILE
            -D APR_HAS_MMAP
            -D APR_HAVE_IPV6 (IPv4-mapped addresses enabled)
            -D APR_USE_SYSVSEM_SERIALIZE
            -D APR_USE_PTHREAD_SERIALIZE
            -D SINGLE_LISTEN_UNSERIALIZED_ACCEPT
            -D APR_HAS_OTHER_CHILD
            -D AP_HAVE_RELIABLE_PIPED_LOGS
            -D DYNAMIC_MODULE_LIMIT=256
            -D HTTPD_ROOT="/etc/apache2"
            -D SUEXEC_BIN="/usr/lib/apache2/suexec"
            -D DEFAULT_PIDLOG="/var/run/apache2.pid"
            -D DEFAULT_SCOREBOARD="logs/apache_runtime_status"
            -D DEFAULT_ERRORLOG="logs/error_log"
            -D AP_TYPES_CONFIG_FILE="mime.types"
            -D SERVER_CONFIG_FILE="apache2.conf"
        '''
        _cmd = 'apache2 -V | grep HTTPD_ROOT | awk -F \'=\"\' \'{print $2}\''
        _, output, _ = self.ssh_client.exec_command(_cmd)

        self._HTTPD_ROOT = output[:-1]

        _cmd = 'apache2 -V | grep SERVER_CONFIG_FILE | awk -F \'=\"\' \'{print $2}\''
        _, output, _ = self.ssh_client.exec_command(_cmd)

        self._SERVER_CONFIG_FILE = output[:-1]


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
        '''



    def _search_for_files_to_copy(self):
        '''
            Generates the _files array
        '''

        #_cmd = 'cat ' + self._HTTPD_ROOT + '/' + self._SERVER_CONFIG_FILE
        #_, output, _ = self.ssh_client.exec_command(_cmd)

        #remove the coments and empty lines
        #_conf_file_content = self.remove_coments_and_emptylines(output)

        
        #copy the main config file
        self._files.append(self.get_data_in_format(source=self._HTTPD_ROOT+'/'+self._SERVER_CONFIG_FILE, destination=self._HTTPD_ROOT+'/'+self._SERVER_CONFIG_FILE, is_folder=False))
        
        #copy the Include and IncludeOptional files written in the main config file
        _cmd_for_include_files = 'grep -E \'^Include*\' '+ self._HTTPD_ROOT + '/' + self._SERVER_CONFIG_FILE +' | awk \'{print $2}\''
        _, output, _ = self.ssh_client.exec_command(_cmd_for_include_files)

        for line in output.split('\n'):
            if(line[0] == '/'):
                self._files.append(self.get_data_in_format(source=line, destination=line, is_folder=False))
            else:
                self._files.append(self.get_data_in_format(source=self._HTTPD_ROOT+'/'+line, destination=self._HTTPD_ROOT+'/'+line, is_folder=False))
        
        #copy the envvars file
        self._files.append(self.get_data_in_format(source=self._HTTPD_ROOT+'/envvars', destination=self._HTTPD_ROOT+'/envvars', is_folder=False))

        #copy the LoadModule files written in the main config file
        _cmd_for_LoadModule_files = 'grep -E \'LoadModule*\' '+self._HTTPD_ROOT + '/' +self._SERVER_CONFIG_FILE + ' | awk \'{print $3}\''
        _, output, _ = self.ssh_client.exec_command(_cmd_for_LoadModule_files)

        for line in output.split('\n'):
            if(line[0] == '/'):
                self._files.append(self.get_data_in_format(source=line, destination=line, is_folder=False))
            else:
                self._files.append(self.get_data_in_format(source=self._HTTPD_ROOT+'/'+line, destination=self._HTTPD_ROOT+'/'+line, is_folder=False))
        
        #find all the DocumentRoot folders by reading the .conf files in sites-enabled folder and copy them
        _cmd_for_DocumentRoot_folder = 'grep -c -E \'*DocumentRoot*\' ' + self._HTTPD_ROOT + '/sites-enabled/*.conf'
        _, output, _ = self.ssh_client.exec_command(_cmd_for_DocumentRoot_folder)

        if int(output) > 1:
            _cmd_for_DocumentRoot_folder = 'grep -E \'*DocumentRoot*\' ' + self._HTTPD_ROOT + '/sites-enabled/*.conf | awk \'{print $3}\''
        else:
            _cmd_for_DocumentRoot_folder = 'grep -E \'*DocumentRoot*\' ' + self._HTTPD_ROOT + '/sites-enabled/*.conf | awk \'{print $2}\''
        
        _, output, _ = self.ssh_client.exec_command(_cmd_for_DocumentRoot_folder)

        for line in output.split('\n'):
            self._files.append(self.get_data_in_format(source=line, destination=line))


    def remove_coments_and_emptylines(self, content):
        content = str(content)
        ret_val = re.sub(r'(?m)^ *#.*\n?', '', content) #removes the comments from content

        content = ""

        for line in ret_val.split('\n'):
            if re.match(r'^\s*$', line):
                continue
            content += line +'\n'
        
        return content
