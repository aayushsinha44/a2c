from api.ssh import SSH
from api.runtime.runtime_execution import RuntimeExecution
from api.docker import Docker
import os

def system_setup():
    '''
        1. Install docker
        2. Install pyinstaller
    '''

    pass

def generate_sftp_build():

    os.system("rm -rf build/ dist/ stfp.spec")
    os.system("pyinstaller --onefile sftp.py")

if __name__ == '__main__':

    generate_sftp_build()

    # main()
    password='intern1'
    username='ubuntu'
    hostname='172.22.6.140'

    docker_username="intaayushsinhaml"
    docker_password="aayushsinha"
    registry="https://index.docker.io/v1/"

    ssh = SSH(hostname=hostname, port=22, username=username, password=password, pkey=None)

    docker_client = Docker(registry, docker_username, docker_password, ssh)
    docker_client.login()

    # Kubeconfig file
    _kube_file = open('api/kube_config_file', 'r')
    _kube_file_text=_kube_file.read()
    _kube_file.close()

    

    print(ssh.get_operating_system())

    process_port_info = ssh.get_activate_process_on_port()
    for process_tuple in process_port_info:
        runtime_exec = RuntimeExecution(process_tuple[0], process_tuple[1], process_tuple[2], ssh, docker_client)
        if runtime_exec.is_supported():
            print("Started:", process_tuple)
            runtime_exec.call_runtime()

    # save kube config file
    _path = ssh.get_user_data_path()+"/"
    if os.path.exists(_path+"kube_config_file"):
        _kube_file = open(_path+"kube_config_file", 'w')
    else:
        _kube_file = open(_path+"kube_config_file", 'x')
    _kube_file.write(_kube_file_text)
    _kube_file.close()

    # Create kubernetes deployment
    # kubectl --kubeconfig /home/ubuntu/a2c/api/kube_config_file get nodes

    _path_partial=ssh.get_user_data_path(partial=True)+"/"
    _path_partial+= 'kubernetes/'
    for root, dirs, files in os.walk(_path_partial):
        path=root.split(os.sep)
        for file in files:
            _localpath = os.path.abspath(root+os.sep+file)
            print("kubernetes command:", 'kubectl --kubeconfig '+ _path+"kube_config_file create -f "+ _localpath)
            # os.system('kubectl --kubeconfig '+ _path+"kube_config_file create -f "+ _localpath)
        
