from paramiko import SSHClient, AutoAddPolicy
from .constants import USERNAME, HOST, PASSWORD
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
        # print("SSH Out:", output)
        stderr=stderr.readlines()
        error=""
        for line in stderr:
            error=error+line
        # print("SSH err:", error)
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

    def scp(self, client_path, process_name, host_path=None, is_folder=False, is_sudo=False):
        '''
            Moves files to local system
        '''
        self.exec_command('mkdir .ssh')
        self.file_transfer('/home/'+USERNAME+'/.ssh/id_rsa', '/home/'+self.username+'/.ssh/id_rsa')
        self.file_transfer('/home/'+USERNAME+'/.ssh/id_rsa', '/home/'+self.username+'/.ssh/id_rsa.pub')
        self.exec_command('chmod 400 .ssh/id_rsa')
        _directory=os.path.abspath(self.username+"_"+self.hostname+"/"+process_name)
        if not os.path.exists(_directory):
            os.makedirs(_directory)
        if is_folder==True:
            cmd="scp -r "+client_path+" "+USERNAME+"@"+HOST+":"+_directory
        else:
            cmd="scp -i id_rsa "+client_path+" "+USERNAME+"@"+HOST+":"+_directory+"/"
        if host_path is not None:
            cmd += host_path + "/"
            _directory += host_path + "/"
        if not os.path.exists(_directory):
            os.makedirs(_directory)
        print("SCP command", cmd)
        stdin, stdout, stderr = self.client.exec_command(cmd)
        # stdin.write('yes'+'\n')
        # stdin.flush()
        stdout = stdout.readlines()
        output=""
        for line in stdout:
            output=output+line
        print("SSH Out:", output)
        stderr=stderr.readlines()
        error=""
        for line in stderr:
            error=error+line

        print("Output:", output)
        print("error:", error)

        self.exec_command('rm -rf id_rsa')


        # if error == "":
        #     # TODO also check directory is updated or not
        #     output
        #     return True
        
        # else:
        #     return False

    def file_transfer(self, localpath, remotepath):
        ssh=self.client
        sftp = ssh.open_sftp()
        sftp.put(localpath, remotepath)
        sftp.close()
            

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
