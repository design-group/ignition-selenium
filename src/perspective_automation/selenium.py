from platform import system
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import ActionChains



class ElementNotFoundException(Exception):
    pass


SELECT_ALL_KEY_DICT = {
            "Linux": Keys.CONTROL + "a",
            "Windows": Keys.CONTROL + "a",
            "Darwin": Keys.COMMAND + "a"
        }
class Session():
    def __init__(self, base_url, page_path, wait_timeout_in_seconds, credentials=None):
        self.driver = webdriver.Chrome()
        self.base_url = base_url
        self.original_page_url = base_url + page_path
        self.navigateToUrl(self.original_page_url)
        self.wait = WebDriverWait(self.driver, wait_timeout_in_seconds)
        self.credentials = credentials
        self.platform_version = system()
        self.select_all_keys = self.selectAllKeys()
        self.action = ActionChains(self.driver)
    
    
    def selectAllKeys(self) -> Keys:
        return SELECT_ALL_KEY_DICT.get(self.platform_version)

    def navigateToUrl(self, url = None):
        self.driver.get(url or self.base_url)

    def waitForElement(self, identifier, locator=By.CLASS_NAME, multiple=False, root_element: WebElement=None):
        if root_element:
            xPathDict = {
                By.CLASS_NAME: "@class",
                By.ID: "@id"
            }

            if root_element.get_attribute("id"):
                parentIdentifier =  "//*[@id='%s']" % root_element.get_attribute("id")
            elif root_element.get_attribute("class"):
                parentIdentifier = "//*[@class='%s']" % root_element.get_attribute("class")

            identifier = "%s//*[contains(%s, '%s')]" % (parentIdentifier, xPathDict.get(locator), identifier)
            locator = By.XPATH

        # print("Waiting for element by %s: %s" % (locator, identifier))
        try:
            self.wait.until(ec.presence_of_element_located((locator, identifier)))
        except TimeoutException:
            raise ElementNotFoundException("Unable to verify presence of %s: %s" % (locator, identifier))
        except:
             raise Exception("Error waiting for element %s: %s" % (locator, identifier))


        if not multiple:    
            return self.driver.find_element(locator, identifier)
        else:
            return self.driver.find_elements(locator, identifier)

    def login(self):
        # Wait for the login panel to be present
        try:
            loginPanel = self.waitForElement("login-panel")
        except ElementNotFoundException:
            trialPanel = self.waitForElement("not-licensed-header")

            if trialPanel:
                self.resetTrial()
                self.navigateToUrl(self.original_page_url)
                self.waitForElement("login-panel").find_element_by_class_name("submit-button").click()
                return

        # Click the opening "CONTINUE TO LOG IN" button
        loginPanel.find_element_by_class_name("submit-button").click()

        # Enter the username
        usernameField = self.waitForElement("username-field")
        usernameField.send_keys(self.credentials.get('username'))
        self.waitForElement("submit-button").click()

        # Enter the password
        passwordField = self.waitForElement("password-field")
        passwordField.send_keys(self.credentials.get('password'))
        self.waitForElement("submit-button").click()

    def open_gateway_webpage(self):
        self.navigateToUrl("%s/web/home" % self.base_url)

    def resetTrial(self):
        self.open_gateway_webpage()
        self.waitForElement("login-link", By.ID).click()
        self.login()
        self.waitForElement("reset-trial-anchor", By.ID).click()
    
    def doubleClick(self, element):
        self.action.double_click(element).perform()