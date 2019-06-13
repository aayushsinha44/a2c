

class Kubernetes():

    def __init__(self, name, no_replicas=3):
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

    def add_container(self, name, port, image, mount_path=None):
        self._yaml=self._yaml + [
            "        - name: "+name,
            "          image: "+image,
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
