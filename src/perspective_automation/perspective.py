from typing import Union
from perspective_automation.selenium import Session
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium import __version__ as SELENIUM_VERSION
from typing import List


class ElementNotFoundException(Exception):
	pass


class ComponentInteractionException(Exception):
	pass


class ElementNotUpdatedException(Exception):
	pass


class ElementTextChanges(object):
	"""An expectation for checking that an element's text attribute has changed.
	
	Args:
		element - the web element to use
		prev_text - the previous text

	Returns:
		the `WebElement` once its text is different from prev_text
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
	"""PerspectiveElement is a wrapper around the Selenium `WebElement` class.
	
	Params:
		session: Holds the `Session` object that include driver, base_url, page_path, and wait.
		locator: Takes specified option for locating the element on the page.
		identifier: Takes a string argument holding the value to be used to locate the element.

	"""
	def __init__(self, session: Session, locator: By = By.CLASS_NAME, identifier: str = None, element: WebElement = None, parent: WebElement = None, timeout_in_seconds=None):

		self.session = session
		if not element:
			if parent:
				element = PerspectiveElement(session, element=parent).waitForElement(
					locator, identifier, timeout_in_seconds=timeout_in_seconds)
			else:
				element = session.waitForElement(
					identifier, locator, timeout_in_seconds=timeout_in_seconds)

		SELENIUM_MAJOR_VERSION = int(str(SELENIUM_VERSION)[0])
		if SELENIUM_MAJOR_VERSION <= 3:
			# I am not sure why w3c has to be true or this _.find_element_by_xxx fails?
			super().__init__(element.parent, element.id, w3c=True)
		else:
			super().__init__(element.parent, element.id)

	# Class Methods -------------------------------------------------------------------------------------------------------------------

	def find_element_by_partial_class_name(self, name) -> WebElement:
		"""Locates a `WebElement` with a partial class name.

		Args:
			name: String argument holding the value to be used to locate the element.

		Returns:
			`WebElement` (object): The `WebElement` once it is located.
		"""
		return super().find_element_by_xpath(".//*[contains(@class, '%s')]" % name)

	def find_elements_by_partial_class_name(self, name) -> List[WebElement]:
		"""Locates a list of `WebElements` with a partial class name.

		Args:
			name: String argument holding the value to be used to locate the element.

		Returns:
			List[WebElement]: List of `WebElement`'s once they are located.
		"""

		return super().find_elements_by_xpath(".//*[contains(@class, '%s')]" % name)

	def waitForMethod(self, method, timeout_in_seconds = None, exception: Exception = None):
		"""Waits for method to execute but will raise an exception if the method does not execute within the timeout period.

		Args:
			method: The method to execute and wait for.

		Returns:
			bool: True if the method executes within the timeout period, False otherwise.

		Raises:
			Exception: If the method is not found within the timeout period.
		"""
		try:
			if not timeout_in_seconds:  # If timeout is None, the statement will be True
				return self.session.wait.until(method)  # Using selenium .until() method until method is true
			else:
				return WebDriverWait(self.session.driver, timeout_in_seconds).until(method)
		except TimeoutException:
			raise exception
		except Exception as e:
			raise Exception("Error waiting for method: %s" % (e))

	def waitForElement(self, locator: By, identifier: str, timeout_in_seconds=None) -> WebElement:
		"""Method to wait for element to be present in the current page.

		Args:
			locator: `By` strategy type.
			identifier: String argument holding the value to be used to locate the element.

		Returns:
			WebElement (object): The WebElement that is validated with waitForMethod().

		Raises:
			ElementNotFoundException: If the element is not found within the timeout period.
		
		"""
		raiseable_exception = ElementNotFoundException(
			"Unable to verify presence of %s: %s" % (locator, identifier))
		return self.waitForMethod(lambda x: self.find_element(locator, identifier), timeout_in_seconds, raiseable_exception)

	def waitForElements(self, locator: By, identifier: str, timeout_in_seconds=None) -> List[WebElement]:
		"""Waits for `Document Object Model (DOM)` elements to be present in the current page.
		
		Args: 
			locator: `By` locator type.

		Returns: 
			WebElement (object): List of WebElement's that are validated with waitForMethod().

		Raises:
			ElementNotFoundException: If the element is not found within the timeout period.
		"""
		raiseable_exception = ElementNotFoundException(
			"Unable to verify presence of %s: %s" % (locator, identifier))
		return self.waitForMethod(lambda x: self.find_elements(locator, identifier), timeout_in_seconds, raiseable_exception)

	def waitUntilClickable(self, locator: By, identifier: str, timeout_in_seconds=0) -> WebElement:
		"""Method that locates a WebElement with `By` class and a string Identifier and waits until it is clickable.

		Args:
			locator: The By locator type to use. May be: By.ID, By.NAME, By.TAG_NAME, By.CLASS_NAME, By.CSS_SELECTOR, By.LINK_TEXT, By.PARTIAL_LINK_TEXT, By.XPATH
			identifier: String argument holding the value to be used to locate the element.
			timeout_in_seconds: Zero seconds timeout as waitForMethod() handles timeout.

		Returns:
			`WebElement` (object): The `WebElement` once it is clickable.

		Raises:
			`ElementNotFoundException`: If the element is not found within the timeout period.
		"""
		raiseable_exception = ElementNotFoundException(
			"Unable to verify presence of %s: %s" % (locator, identifier))
		locatorMethod = ec.element_to_be_clickable((locator, identifier))
		return self.waitForMethod(locatorMethod, timeout_in_seconds, raiseable_exception)

	def waitForTextChange(self, element: WebElement, prev_text: Union[str, None] = None, timeout_in_seconds=None) -> WebElement:
		"""Will wait until `element.text != prev_text`. If `prev_text` is not specified, the element's current text will be used.

		Args:
			element: The element to check.
			prev_text: The previous text of the element.

		Returns:
			WebElement: The element once the text has changed validated with waitForMethod().
		"""
		if prev_text is None:
			prev_text = element.text
		raiseable_exception = ElementNotUpdatedException(
			"The text of Element %s did not change within %s seconds" % (element, timeout_in_seconds))
		locatorMethod = ElementTextChanges(element, prev_text)
		return self.waitForMethod(locatorMethod, timeout_in_seconds, raiseable_exception)

	def doubleClick(self) -> None:
		"""Double clicks on the element."""
		ActionChains(self.session.driver).double_click(self).perform()

	def getFirstChild(self) -> WebElement:
		"""Returns the first nested element of the parent element."""
		return super().find_element_by_xpath("./child::*")

	def getChildren(self) -> List[WebElement]:
		"""Returns a list of all nested elements of the parent element."""
		return super().find_elements_by_xpath("./child::*")

	def getScreenshot(self):
		"""Returns a screenshot of the element as a PNG file."""
		return self.screenshot_as_png()


class PerspectiveComponent(PerspectiveElement):
	def selectAll(self) -> None:
		"""Selects all elements in the component."""
		self.send_keys(self.session.select_all_keys)
