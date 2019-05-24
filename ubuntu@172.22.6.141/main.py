from api.ssh import SSH
from api.runtime.runtime_execution import RuntimeExecution

def system_setup():
    '''
        1. Install docker
        2. Install pyinstaller
    '''

    pass

if __name__ == '__main__':
    # main()
    password='intern1'
    username='ubuntu'
    hostname='172.22.6.140'

    ssh = SSH(hostname=hostname, port=22, username=username, password=password, pkey=None)
    

    print(ssh.get_operating_system())

    process_port_info = ssh.get_activate_process_on_port()
    for process_tuple in process_port_info:
        runtime_exec = RuntimeExecution(process_tuple[0], process_tuple[1], process_tuple[2], ssh)
        if runtime_exec.is_supported():
            print("Started:", process_tuple)
            runtime_exec.call_runtime()
        
