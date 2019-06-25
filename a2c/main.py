from api.ssh import SSH
from api.runtime.constants import TOMCAT, VOLUME_RUNTIME
from api.runtime.runtime_execution import RuntimeExecution
from api.docker import Docker
from api.kubernetes import Kubernetes, KubernetesTransferToVolume
import os
from xml.dom import minidom

def setup():
    if os.path.exists('file.log'):
        os.system('rm file.log')
    if os.path.exists('user_files/'):
        os.system('rm -rf user_files/')

def generate_sftp_build():

    os.system("rm -rf build/ dist/ stfp.spec")
    os.system("pyinstaller --onefile sftp.py")

def find_tomcat_port(process_id):
    tomcat_ports = []

    process_port_info = ssh.get_activate_process_on_port()

    #find tomcat ports
    for process_tuple in process_port_info:
        if process_tuple[1] == process_id:
            tomcat_ports.append(process_tuple[0])

    #code for finding http port
    _cmd_for_env_var = 'ps -ef | grep catalina | sed -n \'1p\''
    _, output, _ = ssh.exec_command(_cmd_for_env_var)

    words = output.split()

    result = [i for i in words if i.startswith('-Dcatalina.home')]
    _CATALINA_HOME = result[0].split('=')[1]

    result = [i for i in words if i.startswith('-Dcatalina.base')]
    _CATALINA_BASE = result[0].split('=')[1]

    _, output, _error = ssh.exec_command('cat ' + _CATALINA_HOME + '/conf/server.xml')

    xmldoc = minidom.parseString(output)
    connector_list = xmldoc.getElementsByTagName('Connector')
    #print(len(connector_list))

    ret_port = '8080'
    for c in connector_list:
        _port = c.attributes['port'].value
        _protocol = c.attributes['protocol'].value
        if(_protocol == 'HTTP/1.1' and _port in tomcat_ports):
            ret_port = _port
    
    return ret_port

if __name__ == '__main__':

    # setup()

    # main()
    # password='intern1'
    # username='ubuntu'
    # hostname='172.22.6.162'

    docker_username="intaayushsinhaml"
    docker_password="aayushsinha"
    registry="https://index.docker.io/v1/"

    mysql_db_username='aayush'
    mysql_db_password='aayush'

    client_data =[
        ('ubuntu', 'intern1', '172.22.6.161'),
        ('ubuntu', 'intern1', '172.22.6.162')
    ]

    for client_tuple in client_data:

        username=client_tuple[0]
        password=client_tuple[1]
        hostname=client_tuple[2]

        _client_data_excluded=[]
        for data in client_data:
            if client_data != data:
                _client_data_excluded.append(data)

        ssh = SSH(hostname=hostname, port=22, username=username, password=password, pkey=None)

        docker_client = Docker(registry, docker_username, docker_password, ssh, dev=True)
        docker_client.login()

        # Kubeconfig file
        _kube_file = open('kube_config_file', 'r')
        _kube_file_text=_kube_file.read()
        _kube_file.close()

        BLACKLIST_PID = set()
        
        try:
            _, output, error=ssh.exec_command('ps -ef | grep -c catalina')
            if int(output) > 1:
                _, output, error=ssh.exec_command('ps -ef | grep catalina | sed -n \'1p\' | awk \'{print $2}\'')
                
                process_id = str(output.split('\n')[0])
                process_port = find_tomcat_port(process_id)
                print("Found: Tomcat")
                runtime_exec = RuntimeExecution(process_port=process_port, 
                                                process_id=process_id, 
                                                process_name=TOMCAT, 
                                                ssh_client=ssh, 
                                                docker_client=docker_client,
                                                vm_data=_client_data_excluded)
                _runtime = runtime_exec.get_runtime()
                _runtime.save_code()
                _runtime.save_container_info()  
                _runtime.build_container()
                _runtime.push_container_docker_registry()
                
                kubernetes_object.add_container(_runtime.get_name(), _runtime.get_port(), _runtime.get_image())
                kubernetes_object.add_service(_runtime.get_name(), _runtime.get_port())
                kubernetes_object.save_file()
                kubernetes_object.kubectl_apply()
                print('deployed to kubernetes')
                BLACKLIST_PID.add(process_id)
        except Exception as e:
            print(e)

        # print(ssh.get_operating_system())

        process_port_info = ssh.get_activate_process_on_port()
        for process_tuple in process_port_info:
            if process_tuple[1] in BLACKLIST_PID:
                continue
            runtime_exec = RuntimeExecution(process_port=process_tuple[0], 
                                            process_id=process_tuple[1], 
                                            process_name=process_tuple[2], 
                                            ssh_client=ssh, 
                                            docker_client=docker_client,
                                            vm_data=_client_data_excluded)
            if runtime_exec.is_supported():
                print("Started:", process_tuple)
                kubernetes_object=Kubernetes('vm1', ssh)

                if process_tuple[2] in VOLUME_RUNTIME:
                    _runtime = runtime_exec.get_runtime(mysql_db_username=mysql_db_username,
                                                        mysql_db_password=mysql_db_password)
                    
                    _env = {
                        "name" : "MYSQL_ROOT_PASSWORD",
                        "value": "aayush"
                    }

                    _runtime.save_code()
                    _runtime.save_container_info()  
                    _runtime.build_container()
                    _runtime.push_container_docker_registry()
                    
                    kubernetes_object.add_container(_runtime.get_name(), _runtime.get_port(), _runtime.get_image(), _env,  mount_path='/var/lib/mysql')
                    kubernetes_object.add_service(_runtime.get_name(), _runtime.get_port())
                    kubernetes_object.add_volume(_runtime.get_name())
                    kubernetes_object.add_persistent_volume(_runtime.get_name())
                    kubernetes_object.save_file()
                    kubernetes_object.kubectl_apply()
                    
                    
                    _pod_name = kubernetes_object.get_pod_name()
                    _pod_name = _pod_name.strip()

                    _source=ssh.get_user_data_path(partial=True) + _runtime.get_process_path() + '/' + 'db_dump.sql'
                    _destination='/tmp/db_dump.sql'
                    _db_password=_env['value']
                    kubernetes_object.transfer_file_to_pod(_source, _destination, _pod_name, _db_password)
                    kubernetes_object.kubectl_restart_pod(_pod_name)

                
                else:
                    
                    _runtime = runtime_exec.get_runtime()
                    _runtime.save_code()
                    _runtime.save_container_info()  
                    _runtime.build_container()
                    _runtime.push_container_docker_registry()
                    
                    kubernetes_object.add_container(_runtime.get_name(), _runtime.get_port(), _runtime.get_image())
                    kubernetes_object.add_service(_runtime.get_name(), _runtime.get_port())
                    kubernetes_object.save_file()
                    kubernetes_object.kubectl_apply()
                    print('deployed to kubernetes')
