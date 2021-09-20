from selenium.webdriver.support.wait import WebDriverWait
from perspective_automation.selenium import Session
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
class Component(WebElement):
    def __init__(self, session: Session, locator: By = By.CLASS_NAME, identifier: str = None, element: WebElement=None, parent: WebElement=None):
        self.session = session
    
        if element:
            super().__init__(element.parent, element.id, w3c=True)
        else:
            element = self.session.waitForElement(identifier, locator, root_element=parent)
            super().__init__(element.parent, element.id, w3c=True)

    def find_element_by_partial_class_name(self, name) -> WebElement:
        return super().find_element_by_xpath("//*[contains(@class, '%s')]" % name)

    def find_elements_by_partial_class_name(self, name) -> list[WebElement]:
        return super().find_elements_by_xpath("//*[contains(@class, '%s')]" % name)

    def waitForElement(self, locator: By, identifier: str, timeout_in_seconds=None) -> WebElement:
        method = lambda x: self.find_element(locator, identifier)

        if not timeout_in_seconds:
            return self.session.wait.until(method)
        else:
            return WebDriverWait(self.session.driver, timeout_in_seconds).until(method)
        

    def waitForElements(self, locator: By, identifier: str, timeout_in_seconds=None) -> list[WebElement]:
        method = lambda x: self.find_elements(locator, identifier)

        if not timeout_in_seconds:
            return self.session.wait.until(method)
        else:
            return WebDriverWait(self.session.driver, timeout_in_seconds).until(method)

class PerspectiveComponent(Component):
    def selectAll(self) -> None:
        self.send_keys(self.session.select_all_keys)

class PerspectiveElement(Component):
    def __init__(self, session: Session, element: WebElement):
        super().__init__(session, element=element)

    def doubleClick(self) -> None:
        self.session.doubleClick(self)