from .runtime import Runtime
import re

class Python(Runtime):

    def __init__(self, process_id, ssh_client, proccess_name, process_port, docker_client):
        super().__init__(ssh_client, process_id, proccess_name, process_port, docker_client)
        self._DJANGO='django'
        self._FLASK='flask'
        self._PYTHON='python'  # python socket

    def get_runtime(self):
        '''
            Returns the python runtime DJANGO, FLASK, PYTHON
        '''
        return self._DJANGO

    def operate(self):
        _runtime=self.get_runtime()

        if _runtime == self._DJANGO:
            pass

        elif _runtime == self._FLASK:
            pass

        elif _runtime == self._PYTHON:
            # python socket
            pass

class Django():

    def __init__(self):
        pass

    def get_method_of_inception(self):
        '''
            whether it was started by python manage.py runserver
            or uwsgi server
        '''
        pass

class Flask():

    pass

class PythonSockets():
    pass