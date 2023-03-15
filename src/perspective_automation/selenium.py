from enum import Enum
from dataclasses import dataclass
from platform import system
from typing import List

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class ElementNotFoundException(Exception):
	pass


class SessionConfigurationException(Exception):
	pass


@dataclass
class Credentials:
	username: None
	password: None


class LogSource(Enum):
	BROWSER = "browser"
	DRIVER = "driver"
	CLIENT = "client"
	SERVER = "server"


class SelectAllKeys(Enum):
	LINUX = Keys.CONTROL + "a"
	WINDOWS = Keys.CONTROL + "a"
	DARWIN = Keys.COMMAND + "a"


def getChromeDriver(**kwargs) -> WebDriver:
	chrome_options = webdriver.ChromeOptions()

	if kwargs.get('mobile'):
		mobile_emulation = {"deviceName": "iPhone X"}
		chrome_options.add_experimental_option(
			"mobileEmulation", mobile_emulation)

	if kwargs.get('headless', True):
		chrome_options.add_argument("--headless")

	# log_sources
	logSourceCapability = {}
	logSourceList = kwargs.get('log_sources', [])
	for logSource in logSourceList:
		logSourceCapability.setdefault(logSource, 'ALL')
	chrome_options.set_capability('goog:loggingPrefs', logSourceCapability)

	if kwargs.get('browser_executable_path'):
		return webdriver.Chrome(
			executable_path=kwargs.get('browser_executable_path'), options=chrome_options
		)
	else:
		return webdriver.Chrome(options=chrome_options)


def getSafariDriver(**kwargs) -> WebDriver:
	if kwargs.get('mobile'):
		return webdriver.Safari(desired_capabilities={"safari:useSimulator": True, "platformName": "ios"})

	return webdriver.Safari()


def getRemoteChromeDriver(**kwargs) -> WebDriver:
	chrome_options = webdriver.ChromeOptions()

	chrome_options.headless = kwargs.get('headless', True)

	remote_options = kwargs.get('remote', {})

	if remote_options.get('insecure', False):
		chrome_options.set_capability('acceptInsecureCerts', True)

	command_executor = remote_options.get('command_executor')
	if command_executor:
		return webdriver.Remote(command_executor, options=chrome_options)
	else:
		"""
		No command_executor specified in remote session.
		Defaulting to 'http://127.0.0.1:4444/wd/hub'.
		"""
		return webdriver.Remote(options=chrome_options)


BROWSERS = {
	"chrome": getChromeDriver,
	"safari": getSafariDriver,
	"remote": getRemoteChromeDriver
}


class Session(object):
	def __init__(self, base_url, page_path, wait_timeout_in_seconds, **kwargs) -> None:

		self.driver = BROWSERS[kwargs.get('browser', 'chrome')](**kwargs)
		self.base_url = base_url
		self.original_page_url = base_url + page_path
		self.navigateToUrl(self.original_page_url)
		self.wait = WebDriverWait(self.driver, wait_timeout_in_seconds)
		self.credentials = kwargs.get('credentials')
		self.platform_version = system().upper()
		self.select_all_keys = self.getSelectAllKeys()
		self.log_sources = kwargs.get('log_sources', [])

	def __enter__(self):
		# TODO: SOmeway of verifying if we need credentials or not
		
		if self.credentials:
			print("Authentication required, logging into the app")
			self.login()
		else:
			print("No authentication required, opening page directly")
		return self

	def __exit__(self, type, value, traceback):
		self.close()

	def getSelectAllKeys(self) -> Keys:
		return SelectAllKeys[self.platform_version].value

	def navigateToUrl(self, url=None) -> None:
		"""Method that will navigate to the provided URL.

		Args:
			url (str): The URL to navigate to.
		"""
		try:
			reloadButton = self.waitForElement("reload-button", By.ID)
			reloadButton.click()
		except:
			pass

		self.driver.get(url or self.base_url)

	def waitForElement(self, identifier, locator=By.CLASS_NAME, timeout_in_seconds=None) -> WebElement:
		"""Method that waits for webelement to be present on page as selenium scripts move faster than the content appears on the page.
		Does not require reference to the webdriver or expected conditions as it is handled by the method.

		Args:
			identifier (str): The identifier of the webelement.
			locator (By): The locator type of the webelement.
			timeout_in_seconds (int): The number of seconds to wait for the webelement to appear.

		Returns:
			WebElement: The webelement that should have appeared on the page.

		"""
		try:
			locatorMethod = ec.presence_of_element_located(
				(locator, identifier))
			if timeout_in_seconds:
				return WebDriverWait(self.driver, timeout_in_seconds).until(locatorMethod)

			return self.wait.until(locatorMethod)
		except TimeoutException:
			raise ElementNotFoundException(
				"Unable to verify presence of %s: %s" % (locator, identifier))
		except Exception as e:
			raise Exception(e)
			# raise Exception("Error waiting for element %s: %s" %
			# (locator, identifier))

	def waitToClick(self, identifier, locator=By.CLASS_NAME, timeout_in_seconds=None) -> WebElement:
		"""Method that will wait for an element to be visible on the page before interacting with it.

		Args:
			identifier (str): The identifier of the webelement.
			locator (By): The locator type of the webelement.
			timeout_in_seconds (int): The number of seconds to wait for the webelement to appear.

		Returns:
			WebElement: The webelement to be interacted with.

		"""
		try:
			locatorMethod = ec.element_to_be_clickable((locator, identifier))
			if timeout_in_seconds:
				return WebDriverWait(self.driver, timeout_in_seconds).until(locatorMethod)

			return self.wait.until(locatorMethod)
		except TimeoutException:
			raise ElementNotFoundException(
				"Unable to verify presence of %s: %s" % (locator, identifier))
		except:
			raise Exception("Error waiting for element %s: %s" %
							(locator, identifier))

	def close(self):
		self.driver.quit()

	def login(self) -> None:
		"""Login method that will handle quick start prompt and expired trials before entering credentials.        
		"""
		self.driver.delete_all_cookies()    # Clear cookies for a new session.
		self.openGatewayWebpage()
		# If login is obstructed by quick start overlay, start from scratch
		self.enableQuickStart()

		try:
			resetTrial = self.waitForElement("reset-trial-anchor", By.ID)
			print("Located reset trial link, signing in to reset")
			self.waitForElement("reset-trial-anchor", By.ID).click()
		except ElementNotFoundException:
			print("Reset trial link not found, signing in with login link instead.")

			try:
				self.waitForElement("login-link", By.ID).click()
				print("Located login link.")
			except ElementNotFoundException:
				print("Login link not found")

		# After pressing login, gateway will navigate to login and wait for the login panel element.
		try:
			loginPanel = self.waitForElement("login-panel")
			print("Located login panel, continuing to enter credentials.")
		except ElementNotFoundException:
			print("Login panel not found, erroring out.")

			# try:
			#     trialPanel = self.waitForElement("reset-trial-anchor")
			# except ElementNotFoundException:
			#     print("Demo panel not found, erroring out.")
			#     #Just errors out becasue the Demo panel is not found

			# # TODO: If we already have a session and we need credentials, this will fail because we wont have a trial panel

			# if trialPanel:
			#     self.resetTrial()
			#     self.navigateToUrl(self.original_page_url)
			#     self.waitToClick(By.CLASS_NAME, "submit-button")
			#     return

		# Click the opening "CONTINUE TO LOG IN" button
		loginPanel.find_element(By.CLASS_NAME, "submit-button").click()

		# Enter the username
		usernameField = self.waitForElement("username-field")
		usernameField.send_keys(self.credentials.username)
		self.waitToClick("submit-button").click()
		# self.waitForElement("submit-button").click()

		# Enter the password
		passwordField = self.waitToClick("password-field")
		passwordField.send_keys(self.credentials.password)
		self.waitToClick("submit-button").click()

		try:
			print("Resetting trial and returning to original session.")
			# Once logged in, handle resetting trial if expired.
			self.resetTrial()
			self.navigateToUrl(self.original_page_url)
		except ElementNotFoundException:
			print("No 'Reset Trial' link found, returning to perspective session.")
			self.navigateToUrl(self.original_page_url)

	def openGatewayWebpage(self):
		"""Returns to the gateway home page. Useful for logging in or opening projects.
		"""
		self.navigateToUrl("%s/web/home" % self.base_url)

	def enableQuickStart(self) -> None:
		"""Method that handles the quick start overlay that appears when a user logs in for the first time."""
		try:
			quickStart = self.waitForElement(
				"quickStartOverlayContainer", By.ID)
			print("Located 'Quick Start' overlay")

			# Click the "start from scratch" button
			quickStart.find_element(By.CLASS_NAME, "small").click()
		except ElementNotFoundException:
			print("No 'Quick Start' Overlay found")

	def resetTrial(self):
		self.openGatewayWebpage()
		self.waitToClick("reset-trial-anchor", By.ID).click()

	def getLogsFrom(self, logSource: LogSource):
		if self.log_sources.count(logSource.value) == 0:
			raise SessionConfigurationException(
				f"Cannot get {logSource.value} logs. Please include '{logSource.value}' the Session's 'log_sources' list kwarg to read the {logSource.value} logs."
			)
		else:
			return self.driver.get_log(logSource.value)

	def getBrowserLogs(self):
		return self.getLogsFrom(LogSource.BROWSER)

	def getDriverLogs(self):
		return self.getLogsFrom(LogSource.DRIVER)

	def getClientLogs(self):
		return self.getLogsFrom(LogSource.CLIENT)

	def getServerLogs(self):
		return self.getLogsFrom(LogSource.SERVER)

	def getWindowHandles(self) -> List[str]:
		return self.driver.window_handles

	def getCurrentWindowHandle(self) -> str:
		return self.driver.current_window_handle

	def switchToWindow(self, window_handle: str):
		return self.driver.switch_to.window(window_handle)

	def closeCurrentWindow(self):
		self.driver.close()
