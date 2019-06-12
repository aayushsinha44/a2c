from api.ssh import SSH
from api.runtime.constants import TOMCAT
from api.runtime.runtime_execution import RuntimeExecution
from api.docker import Docker
import os

def generate_sftp_build():

    os.system("rm -rf build/ dist/ stfp.spec")
    os.system("pyinstaller --onefile sftp.py")

if __name__ == '__main__':

    # main()
    password='intern1'
    username='ubuntu'
    hostname='172.22.6.141'

    docker_username="intaayushsinhaml"
    docker_password="aayushsinha"
    registry="https://index.docker.io/v1/"

    ssh = SSH(hostname=hostname, port=22, username=username, password=password, pkey=None)

    docker_client = Docker(registry, docker_username, docker_password, ssh, dev=True)
    docker_client.login()

    # Kubeconfig file
    # _kube_file = open('api/kube_config_file', 'r')
    # _kube_file_text=_kube_file.read()
    # _kube_file.close()

    BLACKLIST_PID = set()
    
    # try:
    _, output, error=ssh.exec_command('ps -ef | grep -c catalina')
    if int(output) > 1:
        _, output, error=ssh.exec_command('ps -ef | grep catalina | sed -n \'1p\' | awk \'{print $2}\'')
        # print(output)
        process_id = str(output.split('\n')[0])
        process_port='8080'
        runtime_exec = RuntimeExecution(process_port=process_port, 
                                        process_id=process_id, 
                                        process_name=TOMCAT, 
                                        ssh_client=ssh, 
                                        docker_client=docker_client)
        runtime_exec.call_runtime()
        BLACKLIST_PID.add(process_id)
    # except Exception as e:
    #     print(e)

    # print(ssh.get_operating_system())

    process_port_info = ssh.get_activate_process_on_port()
    for process_tuple in process_port_info:
        if process_tuple[1] in BLACKLIST_PID:
            continue
        runtime_exec = RuntimeExecution(process_port=process_tuple[0], 
                                        process_id=process_tuple[1], 
                                        process_name=process_tuple[2], 
                                        ssh_client=ssh, 
                                        docker_client=docker_client)
        if runtime_exec.is_supported():
            print("Started:", process_tuple)
            runtime_exec.call_runtime()

    # save kube config file
    # _path = ssh.get_user_data_path()+"/"
    # if os.path.exists(_path+"kube_config_file"):
    #     _kube_file = open(_path+"kube_config_file", 'w')
    # else:
    #     _kube_file = open(_path+"kube_config_file", 'x')
    # _kube_file.write(_kube_file_text)
    # _kube_file.close()

    # Create kubernetes deployment
    # kubectl --kubeconfig /home/ubuntu/a2c/api/kube_config_file get nodes

    # _path_partial=ssh.get_user_data_path(partial=True)+"/"
    # _path_partial+= 'kubernetes/'
    # for root, dirs, files in os.walk(_path_partial):
    #     path=root.split(os.sep)
    #     for file in files:
    #         _localpath = os.path.abspath(root+os.sep+file)
    #         print("kubernetes command:", 'kubectl --kubeconfig '+ _path+"kube_config_file create -f "+ _localpath)
            # os.system('kubectl --kubeconfig '+ _path+"kube_config_file create -f "+ _localpath)
        