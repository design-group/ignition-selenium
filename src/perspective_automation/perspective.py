from typing import Union
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


class ElementTextChanges(object):
  """An expectation for checking that an element's text attribute has changed.

  element - the web element to use
  prev_text - the previous text
  returns the WebElement once its text is different from prev_text
  """
  def __init__(self, element: WebElement, prev_text: str):
    self.element: WebElement = element
    self.prev_text: str = prev_text

  def __call__(self, driver):
    if self.prev_text != self.element.text:
        return self.element
    else:
        return False


class PerspectiveElement(WebElement):
    def __init__(self, session: Session, locator: By = By.CLASS_NAME, identifier: str = None, element: WebElement = None, parent: WebElement = None, timeout_in_seconds=None):
        
        self.session = session
        if not element:
            if parent:
                element = PerspectiveElement(session, element=parent).waitForElement(
                    locator, identifier, timeout_in_seconds=timeout_in_seconds)
            else:
                element = session.waitForElement(identifier, locator, timeout_in_seconds=timeout_in_seconds)

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

    def waitUntilClickable(self, locator: By, identifier: str, timeout_in_seconds=0) -> WebElement:
        raiseable_exception = ElementNotFoundException(
            "Unable to verify presence of %s: %s" % (locator, identifier))
        locatorMethod = ec.element_to_be_clickable((locator, identifier))
        return self.waitForMethod(locatorMethod, timeout_in_seconds, raiseable_exception)
    
    def waitForTextChange(self, element: WebElement, prev_text: Union[str, None] = None, timeout_in_seconds=None) -> WebElement:
        """
        Will wait until `element.text != prev_text`.
        If `prev_text` is not specified, the element's current text will be used.
        """
        if prev_text is None:
            prev_text = element.text
        raiseable_exception = ElementNotFoundException(
            "The text of Element %s did not change within %s seconds" % (element, timeout_in_seconds))
        locatorMethod = ElementTextChanges(element, prev_text)
        return self.waitForMethod(locatorMethod, timeout_in_seconds, raiseable_exception)

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
