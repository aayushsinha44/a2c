import os
from log import Log
import subprocess

class Kubernetes():

    def __init__(self, name, ssh_client, no_replicas=1):
        self.name=name
        self.no_replicas=no_replicas
        self._yaml=[
            "apiVersion: extensions/v1beta1",
            "kind: Deployment",
            "metadata:",
            "  name: "+name,
            "spec:",
            "  replicas: "+str(no_replicas),
            "  template: ",
            "    metadata: ",
            "      labels: ",
            "        app: "+name,
            "    spec:",
            "      containers:",
        ]
        self._services=[]
        self._persistent_volumes=[]
        self._volumes=["      volumes:"]
        self._ssh_client=ssh_client

    def add_container(self, name, port, image, env=None, mount_path=None, volume_name=None):
        if volume_name is None:
            volume_name=name
        self._yaml=self._yaml + [
            "        - name: "+name,
            "          image: "+image,
        ]

        if env is not None:
            self._yaml=self._yaml + [
                "          env:",
            ]

            '''
                sample env
                {
                    "name" : "MYSQL_ROOT_PASSWORD",
                    "value": "aayush"
                }
            '''
            _cnt=0
            for key in env:
                value=env[key]
                if _cnt == 0:
                    self._yaml=self._yaml+[
                        '            - '+key+': '+ value
                    ]
                else:
                    self._yaml=self._yaml+[
                        '              '+key+': '+ value
                    ]
                _cnt += 1


        if port is not None:
            self._yaml=self._yaml + [
                "          ports:",
                "            - containerPort: "+ port
            ]

        
        if mount_path is not None:
            self._yaml += [
                "          volumeMounts:",
                "            - name: "+volume_name+"-persistent-storage",
                "              mountPath: "+mount_path,
            ]

    def add_volume(self, name):
        self._volumes += [
            "          - name: "+name+"-persistent-storage",
            "            persistentVolumeClaim:",
            "              claimName: "+name+"-volumeclaim"
        ]

    def add_service(self, name, port, service_type="LoadBalancer"):
        _service=[
            "apiVersion: v1",
            "kind: Service",
            "metadata:",
            "  name: "+name+"-service",
            "  labels:",
            "    name: "+name+"-service",
            "spec:",
            "  ports:",
            "    - port: "+port,
            # "      targetPort: "+port,
            # "      protocol: TCP",
            "  selector:",
            "    app: "+name,
            "  type: "+service_type
        ]
        self._services.append(_service)

    def add_persistent_volume(self, name, memory='4'):
        _pt=[
            "kind: PersistentVolumeClaim",
            "apiVersion: v1",
            "metadata:",
            "  name: "+name+"-volumeclaim",
            "spec:",
            "  accessModes:",
            "    - ReadWriteOnce",
            "  resources:",
            "    requests:",
            "      storage: "+memory+"Gi"
        ]
        self._persistent_volumes.append(_pt)

    def get_yaml_file(self):
        yaml=[]
        for pt in self._persistent_volumes:
            yaml = yaml + pt
        yaml=yaml+['---']
        yaml=yaml+self._yaml
        # for v in self._volumes:
        #     yaml += v
        if len(self._volumes) > 1:
            yaml += self._volumes
        for service in self._services:
            _tmp=["---"]
            yaml = yaml + _tmp
            yaml = yaml + service
        return '\n'.join(yaml)

    def save_file(self, name='kube.yaml'):
        _yaml = self.get_yaml_file()
        _path_partial=self._ssh_client.get_user_data_path(partial=True)
        _path_partial+= 'kubernetes/'
        self.__file_path=_path_partial+name
        if not os.path.exists(_path_partial):
            os.makedirs(_path_partial)
        if os.path.exists(self.__file_path):
            _kube_file = open(self.__file_path, 'w')
        else:
            _kube_file = open(self.__file_path, 'x')
        _kube_file.write(_yaml)
        _kube_file.close()

    def get_kube_config_path(self):
        return ''

    def kubectl_apply(self):
        '''
            get kube_config_path from ssh_client
        '''
        _cmd='kubectl --kubeconfig '+ self.get_kube_config_path() \
            +"kube_config_file apply -f "+ self.__file_path
        print(_cmd)
        Log.log('cmd:'+ _cmd)
        _cmd=_cmd.split(' ')
        p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out is not None:
            Log.log('output:'+str(out.decode()))
        if err is not None:
            Log.log('error:'+ str(err.decode()))
        

    def kubectl_delete(self, delete=False):
        _cmd='kubectl --kubeconfig '+ self.get_kube_config_path() \
            +"kube_config_file delete -f "+ self.__file_path
        Log.log('cmd:'+ _cmd)
        _cmd=_cmd.split(' ')
        p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out is not None:
            Log.log('output:'+str(out.decode()))
        if err is not None:
            Log.log('error:'+ str(err.decode()))
        
        # delete file
        if delete:
            _cmd = "rm "+self.__file_path
            Log.log('cmd:'+ _cmd)
            _cmd=_cmd.split(' ')
            p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if out is not None:
                Log.log('output:'+str(out.decode()))
            if err is not None:
                Log.log('error:'+ str(err.decode()))
            


class KubernetesTransferToVolume():

    '''
    Algorithm:
        1. Create a temp pod
        2. Attach volume to that pod
        3. Transfer data to that pod
        4. Delete the pod
    '''

    def __init__(self, pod_name, volume_name, ssh_client, _env):
        self.__pod_name = pod_name + '-temp'
        self.__kubernetes = Kubernetes(name=self.__pod_name, ssh_client=ssh_client, no_replicas=1)
        self.__volume_name = volume_name
        self.ssh_client = ssh_client
        self._env=_env

    def save_yaml_file(self):

        self.__kubernetes.add_container(self.__pod_name, None, 'mysql:5.6', env=self._env, mount_path='/docker-entrypoint-initdb.d', volume_name=self.__pod_name.split('-')[0])
        self.__kubernetes.add_volume(self.__pod_name.split('-')[0])
        self.__kubernetes.save_file(name='kube_temp.yaml')

    def apply_temp_file(self):
        self.__kubernetes.kubectl_apply()

    def copy_from_client_to_host(self, source, destination, process_path, is_folder=False, is_sudo=False):
        self.ssh_client.scp(client_path=source,
                            process_path=process_path,
                            host_path=destination,
                            is_folder=is_folder,
                            is_sudo=is_sudo,
                            is_relative=True)

    def copy_data_to_volume(self, source, destination):

        _cmd = 'kubectl --kubeconfig ' \
            +"kube_config_file cp "+source+' default/'+self.__pod_name+':'+destination
        print(_cmd)
        Log.log('cmd:'+ _cmd)
        _cmd=_cmd.split(' ')
        p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out is not None:
            Log.log('output:'+str(out.decode()))
        if err is not None:
            Log.log('error:'+ str(err.decode()))
        

    def delete_pod(self):
        self.__kubernetes.kubectl_delete(delete=False)
