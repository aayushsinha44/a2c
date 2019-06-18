from .runtime import Runtime

class MySQL(Runtime):

    def __init__(self, 
                process_id, 
                ssh_client, 
                proccess_name, 
                process_port, 
                docker_client, 
                mysql_db_username,
                mysql_db_password):
        super().__init__(ssh_client, process_id, proccess_name, process_port, docker_client)
        self.__mysql_db_username=mysql_db_username
        self.__mysql_db_password=mysql_db_password

        self.generate_dump

    def generate_container_file(self):
        _docker_file = [
            "FROM mysql:5.6"
        ]
        return '\n'.join(_docker_file)

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
        self.generate_dump()
        return [self.get_data_in_format(source='db_dump.sql', destination='db_dump.sql')]


    def generate_dump(self):
        _cmd=' mysqldump -u'+ self.__mysql_db_username + \
             ' -p'+self.__mysql_db_password + \
                 ' --events --routines --triggers --all-databases > db_dump.sql'
        self.ssh_client.exec_command(_cmd)
