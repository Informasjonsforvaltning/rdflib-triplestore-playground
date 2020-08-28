"""Conftest module."""
import os
from os import environ as env
import time
from typing import Any

from dotenv import load_dotenv
import pytest
import requests
from requests.exceptions import ConnectionError

load_dotenv()
PORT = int(env.get("PORT", "3030"))
HOST = env.get("HOST", "fdk-fuseki-service")


def is_responsive(url: Any) -> Any:
    """Return true if respons from service is 200."""
    try:
        response = requests.get(url + "/$/ping")
        print("Trying to to connect to: " + url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope="session")
def http_service(docker_ip: Any, docker_services: Any) -> Any:
    """Ensure that HTTP service is up and responsive."""
    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for(HOST, PORT)
    url = "http://{}:{}".format(docker_ip, port)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_responsive(url)
    )
    time.sleep(3)  # to ensure the endpoints are up and running
    return url


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig: Any) -> Any:
    """Override default location of docker-compose.yml file."""
    return os.path.join(str(pytestconfig.rootdir), "./", "docker-compose.yml")
