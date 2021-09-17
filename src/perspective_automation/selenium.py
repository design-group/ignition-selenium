import time, random, os, unittest, platform, enum
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

PLATFORM_VERSION = platform.system()

def selectAllKeys():
    return {
        "Linux": Keys.CONTROL + "a",
        "Windows": Keys.CONTROL + "a",
        "Darwin": Keys.COMMAND + "a"
    }.get(PLATFORM_VERSION)



class Session():
    def __init__(self, gateway_url, wait_timeout_in_seconds, credentials=None):

        self.driver = webdriver.Chrome()
        self.driver.get(gateway_url)
        self.wait = WebDriverWait(self.driver, wait_timeout_in_seconds)
        self.credentials = credentials

    def waitForElement(self, identifier, locator=By.CLASS_NAME, multiple=False):
        try:
            self.wait.until(ec.presence_of_element_located((locator, identifier)))
        except:
            raise Exception("Unable to verify presence of %s: %s" % (locator, identifier))
    
        if not multiple:    
            return self.driver.find_element(locator, identifier)
        else:
            return self.driver.find_elements(locator, identifier)

    def login(self):
        # Wait for the login panel to be present
        loginPanel = self.waitForElement("login-panel")

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


class component():
    def __init__(self, session: Session, locator: By, identifier):
        self.session = session
        self.locator = locator
        self.identifier = identifier
        self.element = self.getElement(self.identifier, self.locator)
        pass

    def getElement(self, identifier, locator):
        return self.session.waitForElement(identifier, locator)

    def send_keys(self, keys):
        self.element.send_keys(keys)

    def selectAll(self):
        self.send_keys(selectAllKeys())

    

class TextBox(component):
    def clearText(self):
        self.selectAll()
        self.send_keys(Keys.DELETE)

    def setText(self, text, withSubmit=False, replace=True):
        if replace:
            self.clearText()
        self.send_keys(str(text))
        if withSubmit:
            self.element.submit()

class TextArea(component):
    def clearText(self):
        self.selectAll()
        self.send_keys(Keys.DELETE)

    def setText(self, text, replace=True):
        if replace:
            self.clearText()

        self.send_keys(str(text))

class NumericInput(component):
    # def __init__(self, session: Session, locator: By, identifier):
    #     super(NumericInput, self).__init__(session, locator, identifier)
    def getInputBox(self):
        self.element.find_element_by_class_name("ia-numeral-input").click()
        return self.element.find_element_by_class_name("ia-numeral-input")

    def send_keys(self, keys):
        self.getInputBox().send_keys(keys)
    
    def clearValue(self):
        self.send_keys(selectAllKeys())
        self.send_keys(Keys.DELETE)

    def setValue(self, value, withSubmit=False, replace=True):
        if replace:
            self.clearValue()

        self.send_keys(str(value)) 

        if withSubmit:
            self.getInputBox().submit()


class Dropdown(component):
    def clearData(self):
        self.element.clear()
    
    def setValue(self, option_text):
        self.element.click()
        dropdownOptionPopup = self.session.waitForElement("ia_dropdown__optionsModal", By.CLASS_NAME)
        dropdownOptions = self.session.waitForElement("ia_dropdown__option", By.CLASS_NAME, multiple=True)


        for option in dropdownOptions:
            if option.text == option_text:
                option.click()
                return
        


