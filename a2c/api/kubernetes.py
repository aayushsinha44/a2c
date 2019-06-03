

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

    def add_container(self, name, port, image):
        self._yaml=self._yaml + [
            "        - name: "+name,
            "          image: "+image,
            "          ports:",
            "            - containerPort: "+ port
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
            "      targetPort: "+port,
            "      protocol: TCP",
            "  selector:",
            "    app: "+name,
            "  type: "+service_type
        ]
        self._services.append(_service)

    def get_yaml_file(self):
        yaml=self._yaml
        for service in self._services:
            _tmp=["---"]
            yaml.append(_tmp)
            yaml = yaml + service
        return '\n'.join(yaml)