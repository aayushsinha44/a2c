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

    def close(self):
        self.ssh.close()

    def __del__(self):
        self.close()

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

    # File
    if os.path.isfile(localpath):
        sftp.file_transfer(localpath, remotepath)
        # pass
    
    # Folder
    else:
        for root, dirs, files in os.walk(localpath):
            path=root.split(os.sep)
            for file in files:
                _localpath = os.path.abspath(root+os.sep+file)
                _remotepath = remotepath + root+os.sep+file
                print(_localpath, _remotepath)
                sftp.file_transfer(_localpath, _remotepath)


    