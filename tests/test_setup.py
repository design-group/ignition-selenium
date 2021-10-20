import pytest
import docker
import time
from perspective_automation.perspective import Component
from perspective_automation.selenium import Session, Credentials
from selenium.webdriver.common.by import By

DEFAULT_IGNITION_PORT="8088/tcp"
IGNITION_DOCKER_IMAGE="inductiveautomation/ignition:latest"

class DockerTestingEnvironment:

    def __enter__(self):
        self.client = docker.from_env()
        self.credentials = Credentials("admin", "password")
        self.container = self.getContainerImage()
        self.hostPort = self.getContainerPort(self.container)
        self.url = "http://localhost:%s" % self.hostPort

        return self

    def __exit__(self ,type, value, traceback) -> None:
        self.container.stop()
        self.container.remove()
        

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
        # Stall to allow the container to reload
        time.sleep(10)
        return container

    def enableQuickStart(self):
        session = Session(self.url, "/", 10, credentials=self.credentials, headless=False, browser_executable_path="/usr/local/Caskroom/chromedriver/93.0.4577.63/chromedriver")
        quickStartContainer = Component(session,  By.ID, "quickStartOverlayContainer", timeout_in_seconds=60)

        quickStartButton = quickStartContainer.find_element_by_partial_class_name("primary-action")
        quickStartButton.click()

        loginButton = quickStartContainer.find_element_by_partial_class_name("primary-action")
        loginButton.click()

        session.login()

        session.waitForElement("quickstart-panel", timeout_in_seconds=60)


    def getContainerPort(self, container):
        ports = container.ports

        if len(ports.get(DEFAULT_IGNITION_PORT)) == 0:
            container.reload()

        return ports.get(DEFAULT_IGNITION_PORT)[0]['HostPort']

    def stop(self):
        self.container.remove(force=True)

def test_container():
    with DockerTestingEnvironment() as container:
        container.enableQuickStart()

if __name__ == "__main__":
    pytest.main()
    