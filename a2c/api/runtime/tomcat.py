from .runtime import Runtime

class Tomcat(Runtime):

    def __init__(self, process_id, ssh_client, proccess_name, process_port, docker_client):
        super().__init__(ssh_client, process_id, proccess_name, process_port, docker_client)
        self.CATALINA_HOME = None
        self.CATALINA_BASE = None
        self.TOMCAT_VERSION = None


    # Abstract class method
    def generate_container_file(self):
        # return docker file
        pass

    # Abstract method
    def get_code_folder_path(self):
        '''
            Transfers the files to local machine
            [
                {
                    "source": '/var/www/html'
                    "desitnation": 'var/www/html'
                    "is_folder": True,
                    "is_sudo: False
                }
            ]
        '''
        pass
        #self.get_data_in_format()

    def tomcat_version(self):
        '''
            This funtion sets the tomcat version variable:
            TOMCAT_VERSION
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
        _cmd = 'java -cp '+self.CATALINA_HOME+'/lib/catalina.jar org.apache.catalina.util.ServerInfo | sed -n \'1p\' | awk \'{print $2}\''
        _, output, error = ssh_client.exec_command(_cmd)

        ver = (output.split('/')[1]).split('.')
        version = ver[0]+"."+ver[1]

        self.TOMCAT_VERSION = version
    
    def set_env_variables(self):
        '''
            This function sets the environment variables in the following class variable:
                CATALINA_HOME, CATALINA_BASE
        '''
        _cmd_for_env_var = 'ps -ef | grep catalina | sed -n \'1p\''
        _, output, error = ssh_client.exec_command(_cmd_for_env_var)

        words = output.split()

        result = [i for i in words if i.startswith('-Dcatalina.home')]
        self.CATALINA_HOME = result[0].split('=')[1]

        result = [i for i in words if i.startswith('-Dcatalina.base')]
        self.CATALINA_BASE = result[0].split('=')[1]


        
