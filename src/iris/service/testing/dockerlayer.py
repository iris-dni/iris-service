import logging
import os

from lovely.pytest.docker.compose import Services

from . import testing_path

COMPOSE_FILE = testing_path('docker', 'docker-compose.yml')


class DockerLayer(object):
    """A layer that runs docker-compose"""

    __bases__ = ()

    def __init__(self, name, compose_files,
                 docker_host="localhost"):
        self.__name__ = name
        self.services = Services(compose_files, docker_host, name)
        self.keep_alive = os.environ.get("KEEP_ALIVE") == "1"

    def start_http_service(self, service, internal_port):
        self.services.start(service)
        public_port = self.services.wait_for_service(service, internal_port)
        return self.services.docker_ip, public_port

    def run(self, service, *cmd):
        """Call run on docker compse on the given service

        :param service: the name of the service as defined in compose file
        :param cmd: list of command parts to execute
        """
        return self.services._docker_compose.execute('run', '-T', service, *cmd)

    def tearDown(self, *args):
        if self.keep_alive:
            logging.warning("Docker KEEP_ALIVE enabled not shutting down services")
        else:
            self.services._docker_compose.execute('down', '-vt0')


DOCKER_LAYER = DockerLayer('iris_service_test_docker', [COMPOSE_FILE])
