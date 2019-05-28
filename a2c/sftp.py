from paramiko import SSHClient, AutoAddPolicy
from api.constants import USERNAME, HOST, PASSWORD
import sys, getopt
import os


"""
This code is used from transferring files.
This will be moved to SSH'ed machine and will be 
executed there.
"""

class SFTP():

    def __init__(self, hostname, port, username, password):
        self.hostname=hostname
        self.port=port
        self.username=username
        self.password=password
        self.ssh=SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(self.hostname,
                        self.port,
                        self.username,
                        self.password)

    def __del__(self):
        self.ssh.close()

    def file_transfer(self, localpath, remotepath):
        sftp=self.ssh.open_sftp()
        sftp.put(localpath, remotepath)
        sftp.close()

def arg_handler(argv):
    localpath=''
    remotepath=''

    try:
        opts, _ = getopt.getopt(argv, "l:r:", ["ilocal=", "iremote="])
    except getopt.GetoptError as e:
        print("error:", e)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-l", "ilocal"):
            localpath = arg
        elif opt in ("-r", "iremote"):
            remotepath = arg

    return localpath, remotepath

if __name__ == '__main__':
    sftp=SFTP(HOST, 22, USERNAME, PASSWORD)
    localpath, remotepath = arg_handler(sys.argv[1:])
    print("SFTP")
    print("local path:", localpath)
    print("remote path:", remotepath)

    # File
    if os.path.isfile(localpath):
        sftp.file_transfer(localpath, remotepath)
    
    # Folder
    else:
        if remotepath[0]=='/' and localpath[-1]=='/':
            localpath=localpath[:-1]
        elif remotepath[0]!='/' and localpath[-1]!='/':
            localpath += '/'
        for root, dirs, files in os.walk(localpath):
            path=root.split(os.sep)
            for file in files:
                _localpath = os.path.abspath(root+os.sep+file)
                _remotepath = remotepath+os.sep+_localpath.split('/')[-1]
                print(_localpath, _remotepath)
                sftp.file_transfer(_localpath, _remotepath)


# Usage
# ./sftp -l /var/www/html -r /home/ubuntu/a2c/ubuntu_172.22.6.140/nginx/
# ./sftp -l django_app/ -r /home/ubuntu/a2c/ubuntu_172.22.6.140/python/