from enum import Enum
from dataclasses import dataclass
from platform import system

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

class ElementNotFoundException(Exception):
    pass

@dataclass
class Credentials:
    username: None
    password: None

class SelectAllKeys(Enum):
    LINUX = Keys.CONTROL + "a"
    WINDOWS = Keys.CONTROL + "a"
    DARWIN = Keys.COMMAND + "a"

def getChromeDriver(mobile: bool=False) -> webdriver:
    chrome_options = webdriver.ChromeOptions()

    if mobile:
        mobile_emulation = {"deviceName": "iPhone X"}
        chrome_options.add_experimental_option(
            "mobileEmulation", mobile_emulation)

    return webdriver.Chrome(options=chrome_options)

def getSafariDriver(mobile: bool=False) -> webdriver:
    if mobile:
        return webdriver.Safari(desired_capabilities={"safari:useSimulator": True, "platformName": "ios"})
    return webdriver.Safari()

class Browsers(Enum):
    GOOGLE_CHROME = getChromeDriver
    SAFARI = getSafariDriver

class Session():
    def __init__(self, base_url, page_path, wait_timeout_in_seconds, credentials: Credentials = None, browser: Browsers =  Browsers.GOOGLE_CHROME, mobile: bool=False) -> None:

        self.driver = browser(mobile)
        self.base_url = base_url
        self.original_page_url = base_url + page_path
        self.navigateToUrl(self.original_page_url)
        self.wait = WebDriverWait(self.driver, wait_timeout_in_seconds)
        self.credentials = credentials
        self.platform_version = system().upper()
        self.select_all_keys = self.getSelectAllKeys()



    def getSelectAllKeys(self) -> Keys:
        return SelectAllKeys[self.platform_version].value

    def navigateToUrl(self, url=None) -> None:
        self.driver.get(url or self.base_url)

    def waitForElement(self, identifier, locator=By.CLASS_NAME, timeout_in_seconds=None) -> WebElement:
        try:
            return self.wait.until(ec.presence_of_element_located((locator, identifier)))
        except TimeoutException:
            raise ElementNotFoundException(
                "Unable to verify presence of %s: %s" % (locator, identifier))
        except:
            raise Exception("Error waiting for element %s: %s" %
                            (locator, identifier))
    
    def close(self):
        self.driver.quit()

    
    def login(self) -> None:
        # Wait for the login panel to be present
        try:
            loginPanel = self.waitForElement("login-panel")
        except ElementNotFoundException:
            trialPanel = self.waitForElement("not-licensed-header")

            if trialPanel:
                self.resetTrial()
                self.navigateToUrl(self.original_page_url)
                self.waitForElement(
                    "login-panel").find_element_by_class_name("submit-button").click()
                return

        # Click the opening "CONTINUE TO LOG IN" button
        loginPanel.find_element_by_class_name("submit-button").click()

        # Enter the username
        usernameField = self.waitForElement("username-field")
        usernameField.send_keys(self.credentials.username)
        self.waitForElement("submit-button").click()

        # Enter the password
        passwordField = self.waitForElement("password-field")
        passwordField.send_keys(self.credentials.password)
        self.waitForElement("submit-button").click()

    def openGatewayWebpage(self):
        self.navigateToUrl("%s/web/home" % self.base_url)

    def resetTrial(self):
        self.openGatewayWebpage()
        self.waitForElement("login-link", By.ID).click()
        self.login()
        self.waitForElement("reset-trial-anchor", By.ID).click()
