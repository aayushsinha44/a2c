import os
from log import Log

class Kubernetes():

    def __init__(self, name, ssh_client, no_replicas=3):
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
        self._volumes=["      containers:"]
        self._ssh_client=ssh_client

    def add_container(self, name, port, image, mount_path=None):
        self._yaml=self._yaml + [
            "        - name: "+name,
            "          image: "+image,
        ]

        if port is not None:
            self._yaml=self._yaml + [
                "          ports:",
                "            - containerPort: "+ port
            ]

        
        if mount_path is not None:
            self._yaml += [
                "          volumeMounts:",
                "            - name: "+name+"-persistent-storage",
                "              mountPath: "+mount_path,
            ]

    def add_volume(self, name):
        self._volumes += [
            "            - name: "+name+"-persistent-storage",
            "              persistentVolumeClaim:",
            "                claimName: "+name+"-volumeclaim"
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

    def add_persistent_volume(self, name, memory='200'):
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
        yaml=self._yaml
        for v in self._volumes:
            yaml += v
        for service in self._services:
            _tmp=["---"]
            yaml = yaml + _tmp
            yaml = yaml + service
        for pt in self._persistent_volumes:
            _tmp=['---']
            yaml = yaml + _tmp
            yaml = yaml + pt
        return '\n'.join(yaml)

    def save_file(self):
        _yaml = self.get_yaml_file()
        _path_partial=self._ssh_client.get_user_data_path(partial=True)+"/"
        _path_partial+= 'kubernetes/'
        self.__file_path=_path_partial+'kube.yaml'
        if not os.path.exists(_path_partial):
            os.makedirs(_path_partial)
        if os.path.exists(self.__file_path):
            _kube_file = open(self.__file_path, 'w')
        else:
            _kube_file = open(self.__file_path, 'x')
        _kube_file.write(_yaml)
        _kube_file.close()

    def kubectl_apply(self):
        '''
            get kube_config_path from ssh_client
        '''
        _cmd='kubectl --kubeconfig '+ self._ssh_client.get_kube_config_path() \
            +"kube_config_file apply -f "+ self.__file_path
        Log.log(_cmd)
        os.system(_cmd)

    def kubectl_delete(self, delete=False):
        _cmd='kubectl --kubeconfig '+ self._ssh_client.get_kube_config_path() \
            +"kube_config_file delete -f "+ self.__file_path
        Log.log(_cmd)
        os.system(_cmd)
        
        # delete file
        if delete:
            _cmd = "rm "+self.__file_path
            Log.log(_cmd)
            os.system(_cmd)


class KubernetesTransferToVolume():

    '''
    Algorithm:
        1. Create a temp pod
        2. Attach volume to that pod
        3. Transfer data to that pod
        4. Delete the pod
    '''

    def __init__(self, pod_name, volume_name, ssh_client):
        self.__pod_name = pod_name + '_temp'
        self.__kubernetes = Kubernetes(name=self.__pod_name, ssh_client=ssh_client, no_replicas=1)
        self.__volume_name = volume_name

    def save_yaml_file(self):

        self.__kubernetes.add_container(self.__pod_name, None, 'ubuntu', mount_path=self.__volume_name)
        self.__kubernetes.save_file()

    def apply_temp_file(self):
        self.__kubernetes.kubectl_apply()

    def copy_data(self, source, destination):
        
        _cmd = 'kubectl cp '+source+' '+self.__pod_name+':'+destination
        Log.log(_cmd)
        os.system(_cmd)

    def delete_pod(self):
        self.__kubernetes.kubectl_delete(delete=True)
