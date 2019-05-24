
class Docker():

    def __init__(self, registry, username, password, ssh_client):
        self.registry = registry
        self.username = username
        self.password = password
        self.ssh_client = ssh_client

    def login(self):
        pass

    def pull(self):
        pass

    def build(self, name_with_tag):
        pass

    def push(self, name_with_tag, version=None):
        if version is None:
            version='latest'
        pass


