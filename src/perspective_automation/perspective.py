from perspective_automation.selenium import Session
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

class Component():
    def __init__(self, session: Session, locator: By = By.CLASS_NAME, identifier: str = None, element: WebElement=None, parent: WebElement=None):
        self.session = session
        self.locator = locator
        self.identifier = identifier

        if isinstance(parent, Component):
            self.parent = parent.element
        else:
            self.parent = parent

        if not element:
            self.element = self.getElement(self.identifier, self.locator, root_element= self.parent)
        else:
            self.element = element
    
    def getElement(self, identifier, locator=By.CLASS_NAME, multiple=False, root_element: WebElement=None):
        if root_element:
            return self.session.waitForElement(identifier, locator, multiple=multiple, root_element=root_element)

        return self.session.waitForElement(identifier, locator, multiple)

class PerspectiveComponent(Component):
    def send_keys(self, keys):
        self.element.send_keys(keys)

    def selectAll(self):
        self.send_keys(self.session.select_all_keys)

class PerspectiveElement():
    def __init__(self, session: Session, element: WebElement):
        self.element = element
        self.session = session

    def get_attribute(self, attribute):
        return self.element.get_attribute(attribute)
    
    def find_element_by_class_name(self, class_name):
        return self.element.find_element_by_class_name(class_name)

    def find_elements_by_class_name(self, class_name):
        return self.element.find_elements_by_class_name(class_name)
    
    def doubleClick(self):
        self.session.doubleClick(self.element)
    
    def click(self):
        self.element.click()