import pytest
from decorator import decorator
from perspective_automation.selenium import Session
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class ElementNotFoundException(Exception):
    pass


class ComponentInteractionException(Exception):
    pass

def Invasive(func):
    def wrapper(func, *args, **kwargs):
        config: dict[str] = args[0]
        if not config:
            pytest.skip("Config file could not be read.")
        elif not config.get("allow_invasive"):
            pytest.skip("Invasive tests are not allowed by config.")
        else:
            func(*args, **kwargs)
    return decorator(wrapper, func)


class PerspectiveElement(WebElement):
    def __init__(self, session: Session, locator: By = By.CLASS_NAME, identifier: str = None, element: WebElement = None, parent: WebElement = None, timeout_in_seconds=None):
        
        self.session = session
        if not element:
            if parent:
                element = WebElement(session, element=parent).waitForElement(
                    locator, identifier, timeout_in_seconds=timeout_in_seconds)
            else:
                element = self.session.waitForElement(identifier, locator, timeout_in_seconds=timeout_in_seconds)

        # I am not sure why w3c has to be true or this _.find_element_by_xxx fails?
        super().__init__(element.parent, element.id, w3c=True)

    def find_element_by_partial_class_name(self, name) -> WebElement:
        return super().find_element_by_xpath(".//*[contains(@class, '%s')]" % name)

    def find_elements_by_partial_class_name(self, name) -> list[WebElement]:
        return super().find_elements_by_xpath(".//*[contains(@class, '%s')]" % name)

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

    def waitToClick(self, locator: By, identifier: str, timeout_in_seconds=0) -> WebElement:
        raiseable_exception = ElementNotFoundException(
            "Unable to verify presence of %s: %s" % (locator, identifier))
        locatorMethod = ec.element_to_be_clickable((locator, identifier))
        return self.waitForMethod(locatorMethod, timeout_in_seconds, raiseable_exception)

        # return WebDriverWait(self.session.driver, timeout_in_seconds).until(locatorMethod)
        # return locatorMethod()
        # return self.waitForMethod(lambda x: locatorMethod((locator, identifier)), timeout_in_seconds, raiseable_exception)
        # try:
        #     locatorMethod = ec.element_to_be_clickable((locator, identifier))
        #     if timeout_in_seconds:
        #         return WebDriverWait(self.driver, timeout_in_seconds).until(locatorMethod)

        #     return self.wait.until(locatorMethod)
        # except TimeoutException:
        #     raise ElementNotFoundException(
        #         "Unable to verify presence of %s: %s" % (locator, identifier))
        # except:
        #     raise Exception("Error waiting for element %s: %s" %
        #                     (locator, identifier))
    
    def doubleClick(self) -> None:
        ActionChains(self.session.driver).double_click(self).perform()
        
    def getFirstChild(self) -> WebElement:
        return super().find_element_by_xpath("./child::*")

    def getChildren(self) -> list[WebElement]:
        return super().find_elements_by_xpath("./child::*")
    
    def getScreenshot(self):
        return self.screenshot_as_png()


class PerspectiveComponent(PerspectiveElement):
    def selectAll(self) -> None:
        self.send_keys(self.session.select_all_keys)
