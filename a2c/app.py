from flask import Flask, request, jsonify
from api.ssh import SSH
from api.runtime.runtime_execution import RuntimeExecution
from api.kubernetes import Kubernetes
from api.docker import Docker
from api.runtime.constants import TOMCAT
from xml.dom import minidom
import json
import os

HOST='0.0.0.0'
PORT='8090'
DEBUG=True

app = Flask(__name__)

# docker run -p 8090:8090 -v /var/run/docker.sock:/var/run/docker.sock intaayushsinhaml/env

'''
Endpoints:

/docker_registry_cred 
/kube_config_cred 

/vm_cred
/vm_cred/<username>/<hostname>

/login_vm/<username>/<hostname>

/get_os_info
/discover_process

/start_containerization/<process_id>/<process_name> - saves docker file
/save_code
/save_container_info
/build_container
/push_container_docker_registry

/initialize_kubernetes
/kubernetes/add_container
/kubernetes/add_service
/kubernetes/add_volume
/kubernetes/transfer_data_to_volume
/kubernetes/save
/kubernetes/apply

/get_docker_file/<process_id>/<process_name>
/get_kubernetes_file

/logout_vm

/terminate  -- clears all variable
'''

os.system("rm -rf user_files/")

DOCKER_USERNAME=None
DOCKER_PASSWORD=None
DOCKER_REGISTRY=None

VM_CRED=[]
CURRENT_VM=None
VM_PROCESS = dict()

ssh=None
docker_client=None
kubernetes_object=None
RUNTIME=None
PROCESS_LIST=[]
_env=None

def build_response(msg, code=200, success=True):
    msg["success"]=success
    msg["code"]=code
    resp=jsonify(msg)
    resp.status_code=code
    return resp

def check_vm_cred_exists(username, hostname):
    global VM_CRED
    for cred in VM_CRED:
        if cred["username"]==username and cred["hostname"]==hostname:
            return True
    return False

def get_vm_cred(username, hostname):
    global VM_CRED
    for cred in VM_CRED:
        if cred["username"]==username and cred["hostname"]==hostname:
            return cred
    return {}

def set_current_vm(username, hostname):
    global VM_CRED, CURRENT_VM
    for cred in VM_CRED:
        if cred["username"]==username and cred["hostname"]==hostname:
            CURRENT_VM=cred

def get_vm_list_excluded():
    global VM_CRED, CURRENT_VM
    _excluded_vm=[]
    for cred in VM_CRED:
        if cred != CURRENT_VM:
            _excluded_vm.append(cred)
    return _excluded_vm

def is_process_in_process_list(process_port, process_id, process_name):
    global PROCESS_LIST
    for i in PROCESS_LIST:
        if i["process_port"]==process_port and \
            i["process_id"]==process_id and \
            i["process_name"]==process_name:
            return True
    return False

def find_tomcat_port(process_id):
    global ssh
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

@app.route("/")
def home():
    return build_response({"message": "system is working"})

@app.route("/docker_registry_cred", methods=['POST'])
def docker_registry_cred():
    try:
        _json=request.json

        _req =["username", "password", "registry"]
        for r in _req:
            if r not in _json:
                return build_response({"message": "invalid data"}, code=400, success=False)

        _username=_json["username"]
        _password=_json["password"]
        _registry=_json["registry"]

        global DOCKER_USERNAME, DOCKER_PASSWORD, DOCKER_REGISTRY

        DOCKER_USERNAME=_username
        DOCKER_PASSWORD=_password
        DOCKER_REGISTRY=_registry

        return build_response({"message": "data added successfully"})

    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/kube_config_cred", methods=["POST"])
def kube_config_cred():
    try:
        _json=request.json

        if "config" not in _json:
            return build_response({"message": "invalid data"}, code=400, success=False)

        _config=_json["config"]

        if not os.path.exists('user_files/'):
            os.mkdir('user_files/')

        _path=''
        if os.path.exists(_path+"kube_config_file"):
            _kube_file = open(_path+"kube_config_file", 'w')
        else:
            _kube_file = open(_path+"kube_config_file", 'x')
        _kube_file.write(_config)
        _kube_file.close()      

        return build_response({"message": "kube_config file stored"})

    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/vm_cred", methods=["GET", "POST"])
def vm_cred():
    global VM_CRED
    if request.method == "GET":
        return build_response({"vm": VM_CRED})

    try:
        _json=request.json

        _req =["hostname", "username", "password", "port", "pkey", "passphrase"]
        for r in _req:
            if r not in _json:
                return build_response({"message": "invalid data"}, code=400, success=False)

        VM_CRED.append(_json)

        return build_response({"message": "added successfully"})

    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/vm_cred/<username>/<hostname>", methods=["GET", "PUT"])
def vm_cred_spec(username, hostname):
    global VM_CRED
    if request.method == 'GET':

        for cred in VM_CRED:
            if cred["username"]==username and cred["hostname"]==hostname:
                return build_response({"data": cred})
        
        return build_response({"message": "no such vm"}, code=200, success=False)

    try:
        _json=request.json
        _req =["hostname", "username", "password", "port", "private_key", "passphrase"]
        for r in _req:
            if r not in _json:
                return build_response({"message": "invalid data"}, code=400, success=False)

        VM_CRED.append(_json)

        return build_response({"message": "updated successfully"})

    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/login_vm/<username>/<hostname>")
def login_vm(username, hostname):
    global ssh, DOCKER_USERNAME, DOCKER_PASSWORD, DOCKER_REGISTRY, docker_client
    if not check_vm_cred_exists(username, hostname):
        return build_response({"message": "no such vm"}, code=400, success=False)

    try:
    
        vm_cred=get_vm_cred(username, hostname)
        ssh = SSH(hostname=vm_cred["hostname"], 
                port=vm_cred["port"], 
                username=vm_cred["username"], 
                password=vm_cred["password"], 
                pkey=vm_cred["pkey"], 
                passphrase=vm_cred["passphrase"])

        # login to docker also
        docker_client = Docker(DOCKER_REGISTRY, DOCKER_USERNAME, DOCKER_PASSWORD, ssh, dev=True)
        docker_client.login()

        set_current_vm(username, hostname)

        return build_response({"message": "login successful"})

    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/get_os_info")
def get_os_info():
    global ssh
    if ssh is None:
        return build_response({"message": "login into vm first"}, code=400, success=False)
    try:
        return build_response({"data": ssh.get_operating_system()})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)
        
@app.route("/discover_process")
def discover_process():
    global PROCESS_LIST, ssh, VM_PROCESS
    if ssh is None:
        return build_response({"message": "login into vm first"}, code=400, success=False)
    PROCESS_LIST=[]
    process_port_info = ssh.get_activate_process_on_port()
    for process_tuple in process_port_info:
        vm_data=get_vm_list_excluded()
        runtime_exec = RuntimeExecution(process_tuple[0], process_tuple[1], process_tuple[2], ssh, docker_client, vm_data)
        if runtime_exec.is_supported():
            PROCESS_LIST.append({"process_port": process_tuple[0], 
                            "process_id": process_tuple[1], 
                            "process_name": process_tuple[2]})
    try:
        _, output, _ = ssh.exec_command('ps -ef | grep -c catalina')
        if int(output) > 1:
            _, output, _=ssh.exec_command('ps -ef | grep catalina | sed -n \'1p\' | awk \'{print $2}\'')
            
            process_id = str(output.split('\n')[0])
            process_port = find_tomcat_port(process_id)
            PROCESS_LIST.append({
                "process_port": process_port,
                "process_id": process_id,
                "process_name": TOMCAT
            })
    except Exception as e:
        print(e)
    VM_PROCESS[CURRENT_VM["hostname"]] = PROCESS_LIST
    return build_response({"data": PROCESS_LIST})

@app.route("/start_containerization/<process_port>/<process_id>/<process_name>")
def start_containerization(process_port, process_id, process_name):
    global ssh, docker_client, RUNTIME, PROCESS_LIST, VM_PROCESS

    if ssh is None:
        return build_response({"message": "login into vm first"}, code=400, success=False)

    if not is_process_in_process_list(process_port, process_id, process_name):
        return build_response({"message": "invalid data"}, code=400, success=False)

    try:
        runtime_exec = RuntimeExecution(process_port, 
                                        process_id,
                                        process_name, 
                                        ssh, 
                                        docker_client,
                                        VM_PROCESS)
        if runtime_exec.is_supported():
            RUNTIME = runtime_exec.get_runtime()
            return build_response({"message": "started"})
        else:
            return build_response({"message": "process is not supported"}, code=400, success=False)

    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/save_code")
def save_code():
    global RUNTIME
    if RUNTIME is None:
        return build_response({"message": "containerization has not been started"}, code=400, success=False)

    try:
        RUNTIME.save_code()
        return build_response({"message": "code saved successfully"})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/save_container_info")
def save_container_info():
    global RUNTIME
    if RUNTIME is None:
        return build_response({"message": "containerization has not been started"}, code=400, success=False)

    try:
        RUNTIME.save_container_info()
        return build_response({"message": "container information saved successfully"})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/build_container")
def build_container():
    global RUNTIME
    if RUNTIME is None:
        return build_response({"message": "containerization has not been started"}, code=400, success=False)

    try:
        RUNTIME.build_container()
        return build_response({"message": "container build was successfully"})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/push_container_docker_registry")
def push_container_docker_registry():
    global RUNTIME
    if RUNTIME is None:
        return build_response({"message": "containerization has not been started"}, code=400, success=False)

    try:
        RUNTIME.push_container_docker_registry()
        return build_response({"message": "container was successfully pushed to docker registry"})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/initialize_kubernetes/<name>/<no_replica>")
def initialize_kubernetes_file(name, no_replica):
    try:
        global kubernetes_object, ssh
        if ssh is None:
            return build_response({"message": "login into vm first"}, code=400, success=False)
        kubernetes_object=Kubernetes(name, no_replica, ssh)
        return build_response({"message": ""})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/kubernetes/add_container")
def kubernetes_add_container():
    try:
        global kubernetes_object, RUNTIME, _env
        if RUNTIME is None:
            return build_response({"message": "containerization has not been started"}, code=400, success=False)
        if kubernetes_object is None:
            return build_response({"message": "initailize kubernetes first"}, code=400, success=False)
        _json=request.json
        _env=_json
        if "name" in _json and "value" in _json:
            kubernetes_object.add_container(RUNTIME.get_name(), RUNTIME.get_port(), RUNTIME.get_image(), _json,  mount_path='/var/lib/mysql')
        else:
            kubernetes_object.add_container(RUNTIME.get_name(), RUNTIME.get_port(), RUNTIME.get_image())
            kubernetes_object.add_service(RUNTIME.get_name(), RUNTIME.get_port())
        return build_response({"message": "container added"})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/kubernetes/add_service")
def kubernetes_add_service():
    try:
        global kubernetes_object, RUNTIME
        if RUNTIME is None:
            return build_response({"message": "containerization has not been started"}, code=400, success=False)
        if kubernetes_object is None:
            return build_response({"message": "initailize kubernetes first"}, code=400, success=False)
        
        kubernetes_object.add_service(RUNTIME.get_name(), RUNTIME.get_port())
        return build_response({"message": "service added"})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/kubernetes/add_volume")
def add_volume():
    try:
        global kubernetes_object, RUNTIME
        if RUNTIME is None:
            return build_response({"message": "containerization has not been started"}, code=400, success=False)
        if kubernetes_object is None:
            return build_response({"message": "initailize kubernetes first"}, code=400, success=False)
        kubernetes_object.add_volume(RUNTIME.get_name())
        kubernetes_object.add_persistent_volume(RUNTIME.get_name())
        return build_response({"message": "volume is added"})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/kubernetes/transfer_data_to_volume")
def transfer_data_to_volume():
    try:
        global kubernetes_object, RUNTIME, _env
        if RUNTIME is None:
            return build_response({"message": "containerization has not been started"}, code=400, success=False)
        if kubernetes_object is None:
            return build_response({"message": "initailize kubernetes first"}, code=400, success=False)
        
        _pod_name = kubernetes_object.get_pod_name()
        _pod_name = _pod_name.strip()

        _source=ssh.get_user_data_path(partial=True) + RUNTIME.get_process_path() + '/' + 'db_dump.sql'
        _destination='/tmp/db_dump.sql'
        _db_password=_env['value']
        kubernetes_object.transfer_file_to_pod(_source, _destination, _pod_name, _db_password)
        kubernetes_object.kubectl_restart_pod(_pod_name)

        return build_response({"message": "data transfered successfully"})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)


@app.route("/kubernetes/save")
def save_kubernetes_file():
    try:
        global kubernetes_object, RUNTIME
        if RUNTIME is None:
            return build_response({"message": "containerization has not been started"}, code=400, success=False)
        if kubernetes_object is None:
            return build_response({"message": "initailize kubernetes first"}, code=400, success=False)
        kubernetes_object.save_file()
        return build_response({"message": "saved"})
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/kubernetes/apply")
def apply_kubernetes_file():
    try:
        global kubernetes_object
        if kubernetes_object is None:
            return build_response({"message": "initailize kubernetes first"}, code=400, success=False)
        kubernetes_object.kubectl_apply()
        return build_response({"message": "applied"})
    
    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

@app.route("/logout_vm/<username>/<hostname>")
def logout_vm(username, hostname):
    global ssh
    if not check_vm_cred_exists(username, hostname):
        return build_response({"message": "no such vm"}, code=400, success=False)
    if ssh is None:
        return build_response({"message": "not logged in"}, code=400, success=False)
    try:
    
        ssh.close()
        clear()
        return build_response({"message": "logout successful"})

    except Exception as e:
        return build_response({"message": str(e)}, code=500, success=False)

def clear():
    global RUNTIME, ssh, docker_client, PROCESS_LIST, kubernetes_object, _env
    ssh=None
    docker_client=None
    RUNTIME=None
    PROCESS_LIST=[]
    kubernetes_object=None
    _env=None

if __name__ == '__main__':

    app.run(HOST, PORT, DEBUG)
