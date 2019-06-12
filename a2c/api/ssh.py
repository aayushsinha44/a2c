from paramiko import SSHClient, AutoAddPolicy
from log import Log
import os

class SSH:

    def __init__(self, hostname, port, username, password=None, pkey=None, passphrase=None):
        self.hostname=hostname
        self.port=port
        self.username=username
        self.password=password
        self.pkey=pkey
        self.passphrase=passphrase
        self.client=SSHClient()
        self.client.set_missing_host_key_policy(AutoAddPolicy())
        self.client.connect(self.hostname, 
                            self.port, 
                            self.username, 
                            self.password, 
                            self.pkey, 
                            self.passphrase)
        Log.log("Logged to VM: " + self.username+"@"+self.hostname)

    def exec_command(self, cmd, sudo=False):

        if sudo:
            stdin, stdout, stderr = self.client.exec_command(cmd, get_pty=True)
            stdin.write(self.password+'\n')
            stdin.flush()
        else:
            stdin, stdout, stderr=self.client.exec_command(cmd)
        stdout = stdout.readlines()
        output=""
        for line in stdout:
            output=output+line
        output=output.split('\n')
        try:
            if "[sudo]" and "password" in output[1]:
                output=output[2:]
        except:
            pass
        output='\n'.join(output)
        Log.log("Command executed: " + cmd)
        Log.log("Command output: " + output)
        stderr=stderr.readlines()
        error=""
        for line in stderr:
            error=error+line
        if error != "":
            Log.log("Command error: " + error, level="error")
        return stdin, output, error

    def close(self):
        self.client.close()

    def __del__(self):
        self.close()
    
    def get_activate_process_on_port(self):

        '''
        Returns: list of tuples
        tuple - (port, process_id, process_name)
        '''
        
        _cmd="sudo netstat -ltnp | grep LISTEN | awk \'{b=$4 \" \"$7;print b}\'"
        _, output, error=self.exec_command(_cmd, sudo=True)

        if error == "":
            data = set()
            out=[]
            output=output.split('\n')
            for line in output:
                if len(line.split(" ")) == 2:
                    out.append(line)
            for line in out:
                ip_port, process = line.split(" ")
                if len(process.split("/")) == 2:
                    data.add((ip_port.split(':')[-1], process.split('/')[0], process.split('/')[1][:-1]))
            return data
        
        else:
            return error


    def scp(self, client_path, process_path, host_path, is_folder=False, is_sudo=False):
        '''
            Moves files to local system
            client_path: Path of the folder which has to be moved to host_path
        '''

        _client_path=client_path
        if is_folder==False:
            _client_path = '/'.join(_client_path.split('/')[:-1])

        _, output, _ = self.exec_command("find "+_client_path+" -type d")
        output=output.split("\n")
        
        # Creating folder
        for line in output:
            _directory=os.path.abspath('user_files/'+self.username+"_"+self.hostname+"/"+process_path+"/"+line[1:])
            if not os.path.exists(_directory):
                os.makedirs(_directory)
                Log.log("Creating directory "+ _directory, level="debug")

        if is_folder:

            _, output, _ = self.exec_command("find "+_client_path+" -type f")
            output=output.split("\n")

            # Transfering files
            for line in output:
                if len(line) == 0:
                    continue
                _localpath=self.get_user_data_path()+'/'+process_path
                if line[0]!='/':
                    _localpath += '/'
                self.get_file(line, _localpath+line)
                Log.log("Transferring folder from "+line+" to "+_localpath+line, level="debug")

        else:
            _localpath=self.get_user_data_path()+'/'+process_path
            print("File ", client_path)
            print("path: ", _localpath+client_path)
            self.get_file(client_path, _localpath+host_path)
            Log.log("Transferring file from "+line+" to "+_localpath+host_path, level="debug")

        # TODO check success of file transfer


    def file_transfer(self, localpath, remotepath):
        ssh=self.client
        sftp = ssh.open_sftp()
        sftp.put(localpath, remotepath)
        Log.log("Transferring folder from local to remote: "+localpath+" --> "+remotepath)
        sftp.close()

    def get_file(self, remotepath, localpath):
        ssh=self.client
        sftp=ssh.open_sftp()
        sftp.get(remotepath, localpath)
        Log.log("Transferring folder from remote to local: "+remotepath+" --> "+localpath)
        sftp.close()

    def get_user_data_path(self, partial=False):
        '''
            if partial==False
                it returns complete path
                e.g. /home/ubuntu/a2c/user_files/ubuntu_172.22.6.140/
            else it returns partial data path
                e.g. user_files/ubuntu_172.22.6.140
        '''
        
        if partial==False:
            return os.path.abspath('user_files/'+self.username+"_"+self.hostname)
        
        else:
            return 'user_files/'+self.username+"_"+self.hostname+"/"
            

    def get_operating_system(self):
        # cat /etc/os-release
        # 
        # Sample Output
        # 
        # NAME="Ubuntu"
        # VERSION="17.10 (Artful Aardvark)"
        # ID=ubuntu
        # ID_LIKE=debian
        # PRETTY_NAME="Ubuntu 17.10"
        # VERSION_ID="17.10"
        # HOME_URL="https://www.ubuntu.com/"
        # SUPPORT_URL="https://help.ubuntu.com/"
        # BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
        # PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
        # VERSION_CODENAME=artful
        # UBUNTU_CODENAME=artful
        _, output, _ = self.exec_command("cat /etc/os-release")
        return output
