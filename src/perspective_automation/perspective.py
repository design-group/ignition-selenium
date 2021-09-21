from perspective_automation.selenium import Session
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait


class ElementNotFoundException(Exception):
    pass

class ComponentInteractionException(Exception):
    pass

class Component(WebElement):
    def __init__(self, session: Session, locator: By = By.CLASS_NAME, identifier: str = None, element: WebElement = None, parent: WebElement = None):
        self.session = session
        if not element:
            if parent:
                element = Component(session, element=parent).waitForElement(
                    locator, identifier)
            else:
                element = self.session.waitForElement(identifier, locator)

        # I am not sure why w3c has to be true or this _.find_element_by_xxx fails?
        super().__init__(element.parent, element.id, w3c=True)

    def find_element_by_partial_class_name(self, name) -> WebElement:
        return super().find_element_by_xpath("//*[contains(@class, '%s')]" % name)

    def find_elements_by_partial_class_name(self, name) -> list[WebElement]:
        return super().find_elements_by_xpath("//*[contains(@class, '%s')]" % name)

    def waitForMethod(self, method, timeout_in_seconds=None, exception: Exception = None):
        try:
            if not timeout_in_seconds:
                return self.session.wait.until(method)
            else:
                return WebDriverWait(self.session.driver, timeout_in_seconds).until(method)
        except TimeoutException:
            raise exception
        except Exception as e:
            raise Exception("Error waiting for method: %s" % (e))

    def waitForElement(self, locator: By, identifier: str, timeout_in_seconds=None) -> WebElement:
        raiseable_exception = ElementNotFoundException(
            "Unable to verify presence of %s: %s" % (locator, identifier))
        return self.waitForMethod(lambda x: self.find_element(locator, identifier), timeout_in_seconds, raiseable_exception)

    def waitForElements(self, locator: By, identifier: str, timeout_in_seconds=None) -> list[WebElement]:
        raiseable_exception = ElementNotFoundException(
            "Unable to verify presence of %s: %s" % (locator, identifier))
        return self.waitForMethod(lambda x: self.find_elements(locator, identifier), timeout_in_seconds, raiseable_exception)


class PerspectiveComponent(Component):
    def selectAll(self) -> None:
        self.send_keys(self.session.select_all_keys)


class PerspectiveElement(Component):
    def __init__(self, session: Session, element: WebElement) -> None:
        super().__init__(session, element=element)

    def doubleClick(self) -> None:
        ActionChains(self.session.driver).double_click(self).perform()
