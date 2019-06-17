from .runtime import Runtime

class Tomcat(Runtime):

    def __init__(self, process_id, ssh_client, proccess_name, process_port, docker_client):
        super().__init__(ssh_client, process_id, proccess_name, process_port, docker_client)
        self._CATALINA_HOME = None
        self._CATALINA_BASE = None
        self._CATALINA_BASE_CONTAINER = "/usr/local/tomcat/"
        self._CATALINA_HOME_CONTAINER = "/usr/local/tomcat/"
        self._TOMCAT_VERSION = None
        self._conf_files = []
        self._files = []
        self._war_files=[]
        self.set_env_variables()
        self.tomcat_version()
        self.__populate_files()
        


    # Abstract class method
    def generate_container_file(self):
        # return docker file
        _docker_file = [
            "FROM tomcat:"+self._TOMCAT_VERSION+"",
        ]
        _docker_file.append("RUN rm -rf " + self._CATALINA_HOME_CONTAINER + "webapps/ROOT")
        for file in self._war_files:
            _docker_file.append("COPY "+self.build_path(file["destination"])+" " + self._CATALINA_HOME_CONTAINER + "webapps/" + file["source"].split('/')[-1])
        
        for file in self._conf_files:
            _docker_file.append("COPY "+self.build_path(file["destination"]) + " " + self._CATALINA_HOME_CONTAINER + "conf/" + file["source"].split('/')[-1])

        _docker_file.append("EXPOSE " + self.process_port)
        _docker_file.append("")

        return "\n".join(_docker_file)

    def build_path(self, path):
        if path[0] == '/':
            return path[1:]
        return path

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
        return self._files


    def __populate_files(self):
        _cmd_for_warfile = "ls -p "+self._CATALINA_HOME
        if _cmd_for_warfile[:-1] != '/':
            _cmd_for_warfile += '/'
        
        _cmd_for_warfile += "webapps/ | grep -v / | grep  \".war\""
        _, output, _ = self.ssh_client.exec_command(_cmd_for_warfile)

        for line in output.split('\n'):
            if len(line) == 0:
                continue
            _line=self._CATALINA_HOME + '/webapps/'+line
            self._war_files.append(self.get_data_in_format(source=_line, destination=_line, is_folder=False))
            self._files.append(self.get_data_in_format(source=_line, destination=_line, is_folder=False))
        
        #Copying server.xml, web.xml, tomcat-users.xml
        _address = self._CATALINA_HOME + '/conf/'
        self._conf_files.append(self.get_data_in_format(source=_address+'server.xml', destination=_address+'server.xml', is_folder=False))
        self._files.append(self.get_data_in_format(source=_address+'server.xml', destination=_address+'server.xml', is_folder=False))

        self._conf_files.append(self.get_data_in_format(source=_address+'web.xml', destination=_address+'web.xml', is_folder=False))
        self._files.append(self.get_data_in_format(source=_address+'web.xml', destination=_address+'web.xml', is_folder=False))

        self._conf_files.append(self.get_data_in_format(source=_address+'tomat-users.xml', destination=_address+'tomcat-users.xml', is_folder=False))
        self._files.append(self.get_data_in_format(source=_address+'tomcat-users.xml', destination=_address+'tomcat-users.xml', is_folder=False))

        
        



    def tomcat_version(self):
        '''
            This funtion sets the tomcat version variable:
            _TOMCAT_VERSION
        '''

        '''
            Output of the following command gives the version of tomcat

           $ cd $CATALINA_HOME/lib
           $ java -cp catalina.jar org.apache.catalina.util.ServerInfo
            Server version: Apache Tomcat/9.0.19
            Server built:   Apr 12 2019 14:22:48 UTC
            Server number:  9.0.19.0
            OS Name:        Linux
            OS Version:     4.18.0-20-generic
            Architecture:   amd64
            JVM Version:    11.0.3+7-Ubuntu-1ubuntu218.04.1
            JVM Vendor:     Oracle Corporation
        '''
        _cmd = 'java -cp '+self._CATALINA_HOME+'/lib/catalina.jar org.apache.catalina.util.ServerInfo | sed -n \'1p\' | awk \'{print $4}\''
        _, output, _ = self.ssh_client.exec_command(_cmd)

        ver = (output.split('/')[1]).split('.')
        version = ver[0]+"."+ver[1]

        self._TOMCAT_VERSION = version
    
    def set_env_variables(self):
        '''
            This function sets the environment variables in the following class variable:
                CATALINA_HOME, CATALINA_BASE
        '''
        _cmd_for_env_var = 'ps -ef | grep catalina | sed -n \'1p\''
        _, output, _ = self.ssh_client.exec_command(_cmd_for_env_var)

        words = output.split()

        result = [i for i in words if i.startswith('-Dcatalina.home')]
        self._CATALINA_HOME = result[0].split('=')[1]

        result = [i for i in words if i.startswith('-Dcatalina.base')]
        self._CATALINA_BASE = result[0].split('=')[1]