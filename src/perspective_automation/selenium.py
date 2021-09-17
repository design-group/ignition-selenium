import time, random, os, unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

class Session():
    def __init__(self, gateway_url, wait_timeout_in_seconds, credentials=None):

        self.driver = webdriver.Chrome()
        self.driver.get(gateway_url)
        self.wait = WebDriverWait(self.driver, wait_timeout_in_seconds)
        self.credentials = credentials

    def waitForElement(self, identifier, byType=By.CLASS_NAME, multiple=False):
        try:
            self.wait.until(ec.presence_of_element_located((byType, identifier)))
        except:
            raise Exception("Unable to verify presence of %s" % identifier)
    
        if not multiple:    
            return self.driver.find_element(byType, identifier)
        else:
            return self.driver.find_elements(byType, identifier)

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

