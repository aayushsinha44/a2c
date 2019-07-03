from tracking.models import AgentStatusModel, VMGroupModel, \
    VMStatusModel, VMProcessModel, VMProcessStatusModel, VMPoolModel
from agent.helper.agent import Agent
from agent.helper.vm import VM
from tracking.helper.constants import AGENT_IN_USE, SUCCESS, \
    DOCKER_CRED_DOESNOT_EXISTS, KUBE_CRED_DOESNOT_EXISTS, \
    AGENT_CRED_DOESNOT_EXISTS
import requests

class Tracking():

    def __init__(self, user, vm_id_list):
        self.__user=user
        self.__vm=VM(user)
        self.__agent=Agent(user)
        self.__vm_id_list=vm_id_list
        self.pool_id=None

    def create_vm_pool(self):
        vm_pool = VMPoolModel(username=self.__user.get_user_object())
        vm_pool.save()
        self.__pool_id = vm_pool.id
        self.pool_id=vm_pool.id
        self.__pool_object = VMPoolModel.objects.get(id=self.__pool_id)

    def __check_agent_lock(self):

        if AgentStatusModel.objects.filter(
            username=self.__user.get_user_object(),
            agent_hostname=self.__agent.get_agent_ip()).count() == 0:
            return False
        return True

    def __check_kube_config_file(self):
        return True

    def __check_docker_cred(self):
        return True

    def __check_agent_exist(self):
        return True

    def __vm_pool_completed(self):
        _vm_pool = VMPoolModel.objects.get(id=self.__pool_id)
        _vm_pool.in_use=False
        _vm_pool.save()

    # check system before starting process
    def check_system(self):

        if not self.__check_docker_cred():
            return DOCKER_CRED_DOESNOT_EXISTS

        if not self.__check_kube_config_file():
            return KUBE_CRED_DOESNOT_EXISTS

        if not self.__check_agent_exist():
            return AGENT_CRED_DOESNOT_EXISTS

        if self.__check_agent_lock() == False:
            return SUCCESS

        return AGENT_IN_USE

    def __lock_vm(self, vm_id):

        _vm_object=self.__vm.get_vm_object(vm_id)
        _user_object=self.__user.get_user_object()
        
        VMGroupModel.objects.create(
            vm=_vm_object,
            pool_id=self.__pool_object
        )

    def __unlock_vm(self, vm_id):

        _vm_object=self.__vm.get_vm_object(vm_id)
        _user_object=self.__user.get_user_object()

        _vm = VMGroupModel.objects.get(
            vm=_vm_object,
            pool_id=self.__pool_object
        )
        _vm.delete()

    def __lock_agent(self):
        
        _user_object=self.__user.get_user_object()
        _agent_ip=self.__agent.get_agent_ip()

        AgentStatusModel.objects.create(
            agent_hostname=_agent_ip,
            username=_user_object
        )

    def __unlock_agent(self):
        # delete agent in Agent status model
        _user_object=self.__user.get_user_object()
        _agent_ip=self.__agent.get_agent_ip()

        _agent_status = AgentStatusModel.objects.get(
            agent_hostname=_agent_ip,
            username=_user_object
        )
        _agent_status.delete()

    def __init_vm_status_model(self, vm_id):
        
        _vm_object=self.__vm.get_vm_object(vm_id)
        
        VMStatusModel.objects.create(
            vm=_vm_object,
            pool_id=self.__pool_object
        )


    def start(self):

        if self.check_system() == SUCCESS:

            # self.create_vm_pool()

            self.__agent_call=AgentCall(self.__agent.get_agent_ip())
            
            self.__lock_agent()

            # add docker cred
            self.__set_docker_cred()

            # add kubernetes cred
            self.__set_kubernetes_cred()

            for _vm_id in self.__vm_id_list:
                # print('vm id ', _vm_id)
                self.__lock_vm(_vm_id)
                
                self.__init_vm_status_model(_vm_id)

                username, hostname = self.__add_vm_to_agent(_vm_id)
                self.__vm_login(username, hostname)

                _vm_status_model=self.__get_vm_status_model(_vm_id)
                _vm_status_model.login_status=True
                _vm_status_model.save()

                # initialize kubernetes
                _no_rep=self.__vm.get_vm_cred(_vm_id)[0]["vm_no_replica"]
                self.__agent_call.request(
                    '/initialize_kubernetes/'+str(_vm_id)+'/'+str(_no_rep)
                )
                _vm_status_model=self.__get_vm_status_model(_vm_id)
                _vm_status_model.initialize_kubernetes=True
                _vm_status_model.save()
                

                _res = self.__discover_process()

                self.__handle_discoverd_process(_res["data"], _vm_id)

                # save and apply kubernetes
                self.__agent_call.request('/kubernetes/save')
                _vm_status_model=self.__get_vm_status_model(_vm_id)
                _vm_status_model.kubernetes_save_file=True
                _vm_status_model.save()

                self.__agent_call.request('/kubernetes/apply')
                _vm_status_model=self.__get_vm_status_model(_vm_id)
                _vm_status_model.kubernetes_apply=True
                _vm_status_model.save()

                # logout
                self.__vm_logout(username, hostname)

                self.__unlock_vm(_vm_id)
            self.__unlock_agent()
            
            self.__vm_pool_completed()

        else:
            print(self.check_system())
            return self.check_system()
        
    def __get_vm_status_model(self, vm_id):
        return VMStatusModel.objects.get(
            vm=self.__vm.get_vm_object(vm_id),
            pool_id=self.__pool_object)

    def __get_vm_process_model(self, vm_id):
        return VMProcessModel.objects.get(
            vm_id=self.__vm.get_vm_object(vm_id),
            pool_id=self.__pool_object
        )

    def __get_vm_process_status_model(self, vm_id, process_id):
        return VMProcessStatusModel.objects.get(
            vm_id=self.__vm.get_vm_object(vm_id),
            pool_id=self.__pool_object,
            process_id=self.__get_vm_process_model(vm_id)
        )

    def __set_docker_cred(self):
        _data = {}
        _docker_cred=self.__user.get_docker_cred()
        _data["username"]=_docker_cred["docker_registry_username"]
        _data["password"]=_docker_cred["docker_registry_password"]
        _data["registry"]=_docker_cred["docker_registry"]
        _res=self.__agent_call.request('/docker_registry_cred', method='POST', data=_data)

    def __set_kubernetes_cred(self):
        _data = {}
        _docker_cred=self.__user.get_kubernetes_cred()
        _data["config"]=_docker_cred["kube_conf_file"]
        _res=self.__agent_call.request('/kube_config_cred', method='POST', data=_data)

    def __handle_discoverd_process(self, res, vm_id):

        # save in db
        for process in res:
            VMProcessModel.objects.create(
                pool_id=self.__pool_object,
                vm_id=self.__vm.get_vm_object(vm_id),
                process_port=process["process_port"],
                process_id=process["process_id"],
                process_name=process["process_name"]
            )

            _vm_status_model=self.__get_vm_status_model(vm_id)
            _vm_status_model.process_discovery=True
            _vm_status_model.save()

            # create vm process status model
            VMProcessStatusModel.objects.create(
                pool_id=self.__pool_object,
                vm_id=self.__vm.get_vm_object(vm_id),
                process_id=self.__get_vm_process_model(vm_id)
            )

            self.__start_containerization(
                process["process_port"],
                process["process_id"],
                process["process_name"]
            )

            _vm_process_status=self.__get_vm_process_status_model(
                vm_id,
                process["process_id"])
            _vm_process_status.start_containerization=True
            _vm_process_status.save()


            # save code
            self.__agent_call.request('/save_code')
            _vm_process_status=self.__get_vm_process_status_model(
                vm_id,
                process["process_id"])
            _vm_process_status.save_code=True
            _vm_process_status.save()

            # save container info
            self.__agent_call.request('/save_container_info')
            _vm_process_status=self.__get_vm_process_status_model(
                vm_id,
                process["process_id"])
            _vm_process_status.save_container_info=True
            _vm_process_status.save()

            # build_container
            self.__agent_call.request('/build_container')
            _vm_process_status=self.__get_vm_process_status_model(
                vm_id,
                process["process_id"])
            _vm_process_status.build_container=True
            _vm_process_status.save()

            # push_container_docker_registry
            self.__agent_call.request('/push_container_docker_registry')
            _vm_process_status=self.__get_vm_process_status_model(
                vm_id,
                process["process_id"])
            _vm_process_status.push_container_docker_registry=True
            _vm_process_status.save()

            # kubernetes_add_container
            self.__agent_call.request('/kubernetes/add_container')
            _vm_process_status=self.__get_vm_process_status_model(
                vm_id,
                process["process_id"])
            _vm_process_status.kubernetes_add_container=True
            _vm_process_status.save()

            # kubernetes_add_service
            self.__agent_call.request('/kubernetes/add_service')
            _vm_process_status=self.__get_vm_process_status_model(
                vm_id,
                process["process_id"])
            _vm_process_status.kubernetes_add_service=True
            _vm_process_status.save()

            if process["process_name"] == 'mysqld':
                # kubernetes_add_volume
                self.__agent_call.request('/kubernetes/add_volume')
                _vm_process_status=self.__get_vm_process_status_model(
                    vm_id,
                    process["process_id"])
                _vm_process_status.kubernetes_add_volume=True
                _vm_process_status.save()

                # save and apply
                self.__agent_call.request('/kubernetes/save')
                self.__agent_call.request('/kubernetes/apply')

                # kubernetes_transfer_data_to_volume
                self.__agent_call.request('/kubernetes/transfer_data_to_volume')
                _vm_process_status=self.__get_vm_process_status_model(
                    vm_id,
                    process["process_id"])
                _vm_process_status.kubernetes_transfer_data_to_volume=True
                _vm_process_status.save()


    def __start_containerization(self, process_port, process_id, process_name):
        self.__agent_call.request('/start_containerization/'+\
            process_port+'/'+process_id+'/'+process_name)


    def __discover_process(self):
        _res=self.__agent_call.request('/discover_process')
        return _res

    def __vm_login(self, username, hostname):
        _res = self.__agent_call.request('/login_vm/'+username+'/'+hostname)
        
    def __vm_logout(self, username, hostname):
        _res = self.__agent_call.request('/logout_vm/'+username+'/'+hostname)
        

    def __add_vm_to_agent(self, _vm_id):
        _vm_data=self.__vm.get_vm_cred(_vm_id)[0]
        _data={}
        _data["hostname"]=_vm_data["vm_hostname"]
        _data["username"]=_vm_data["vm_username"]
        _data["password"]=_vm_data["vm_password"]
        _data["port"]=_vm_data["vm_port"]
        _data["pkey"]=_vm_data["vm_pKey"]
        _data["passphrase"]=_vm_data["vm_passphrase"]


        _res = self.__agent_call.request('/vm_cred', data=_data, method='POST')

        return _data["username"], _data["hostname"]
        
class AgentCall():

    def __init__(self, agent_ip):
        self.__agent_ip=agent_ip
        if self.__agent_ip[-1] == '/':
            self.__agent_ip = self.__agent_ip[:-1]

    def request(self, url, data={}, method='GET'):
        # print('url', url)
        if method=='POST':
            r = requests.post(self.__agent_ip+url, json=data)
        elif method == 'GET':
            r = requests.get(self.__agent_ip+url, json=data)
        out = r.json()
        # if out["code"] == 200:
        #     return SUCCESS
        print('request', url, out)
        return out
