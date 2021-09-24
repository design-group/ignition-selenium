import pytest
import docker
import requests, time
from perspective_automation.perspective import Component
from perspective_automation.selenium import Session, Credentials
from selenium.webdriver.common.by import By

DEFAULT_IGNITION_PORT="8088/tcp"
IGNITION_DOCKER_IMAGE="inductiveautomation/ignition:latest"

class DockerTestingEnvironment():

    def __init__(self) -> None:
        self.client = docker.from_env()
        self.credentials = Credentials("admin", "password")
        self.container = self.getContainerImage()
        self.hostPort = self.getContainerPort(self.container)
        self.url = "http://localhost:%s" % self.hostPort

    def getContainerImage(self):
        container = self.client.containers.run(image=IGNITION_DOCKER_IMAGE
                        , ports={DEFAULT_IGNITION_PORT: None}
                        , environment={
                                        "ACCEPT_IGNITION_EULA": "Y",
                                        "GATEWAY_ADMIN_USERNAME": self.credentials.username,
                                        "GATEWAY_ADMIN_PASSWORD": self.credentials.password,
                                        "IGNITION_EDITION": "full"
                                        }
                        , detach=True)
        container.reload()
        return container

    def enableQuickStart(self):
        session = Session(self.url, "/", 10, credentials=self.credentials)
        quickStartContainer = Component(session,  By.ID, "quickStartOverlayContainer", timeout_in_seconds=60)


        quickStartButton = quickStartContainer.waitForElement("button primary-action start")
        quickStartButton.click()

        loginButton = quickStartContainer.waitForElement("button primary-action")
        loginButton.click()

        session.login()

        session.waitForElement("quickstart-panel", timeout_in_seconds=60)

        session.resetTrial()




    def getContainerPort(self, container):
        ports = container.ports
        return ports.get(DEFAULT_IGNITION_PORT)[0]['HostPort']

    def stop(self):
        self.container.remove(force=True)


# @pytest.fixture(autouse=True, scope='session')
def testing_container():
    container = DockerTestingEnvironment()
    container.enableQuickStart()

    # yield
    # container.stop()

if __name__ == "__main__":
    testing_container()