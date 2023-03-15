import time
import random
from enum import Enum
from typing import Union, List
from datetime import datetime

from selenium.common.exceptions import (NoSuchElementException,
										TimeoutException,
										ElementClickInterceptedException)

from perspective_automation.perspective import (ComponentInteractionException,
												PerspectiveComponent,
												PerspectiveElement,
												ElementNotFoundException)
from perspective_automation.selenium import Session, SelectAllKeys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select


class InputState(Enum):
	INVALID = False
	VALID = True


class AccordionHeaderType(Enum):
	TEXT = 1
	VIEW = 2


class AccordionHeader(PerspectiveElement):
	"""Accordion Header is a Perspective Component that can be expanded or collapsed.

	Attributes:
		session: Session,
		locator: By = By.CLASS_NAME,
		identifier: str = None,
		element: WebElement = None,
		parent: WebElement = None,
		timeout_in_seconds: Any | None = None
	"""

	# -> indicates the type the function will return
	def getHeaderType(self) -> AccordionHeaderType:
		"""Gets the type of the accordion Header created in Perspective by checking if it is a view or text.

		Args:
			None

		Returns:
			AccordianHeader (object): with configured text header (TEXT = 1) or a view header (VIEW = 2).
		"""
		if self.find_element_by_class_name("ia_accordionComponent__header__text"):
			return AccordionHeaderType.TEXT
		elif self.find_element_by_class_name("ia_accordionComponent__header__view"):
			return AccordionHeaderType.VIEW
		else:
			return None

	def isExpanded(self) -> bool:
		"""Checks if the Accordion Header is expanded or not.

		Args:
			None

		Returns:
			bool: True if the Accordion Header is expanded, False if it is collapsed.
		"""
		return "expanded" in self.find_element_by_partial_class_name(
			"ia_accordionComponent__header__chevron").get_attribute("class")

	def toggleExpansion(self) -> bool:
		"""Toggles the accordion Header without regard for the current state.

		Args:
			None

		Returns:
			bool: Updataed state of the accordion Header after toggleExpansion().
		"""
		self.click()
		return self.isExpanded

	def setExpansion(self, value: bool):    # argument is named value and is of type bool
		"""Toggles Accordion Header to expanded or collapsed based on the value passed in.

		Args:   
			value (bool): Current state of Accordion Header before setExpansion().

		Returns:
			None.
		"""
		currentState = self.isExpanded()
		if currentState != value:
			self.toggleExpansion()

	def getHeaderText(self) -> str:
		"""Gets text value of Accordion Header as a string. Raises an exception if the Accordion Header is not a text header.

		Args:
			None

		Returns:
			str: Text value of the Accordion Header.
		"""
		if self.getHeaderType() != AccordionHeaderType.TEXT:
			raise ComponentInteractionException(
				"Cannot get text of a non-text accordion header.")
		return self.text


class Accordion(PerspectiveComponent):
	"""The Accodion Perspective Component which consists of dropdown `AccordionHeader` elements and `AccordionBody` elements.
	"""

	# Lists are ordered, changeable, and allow duplicate members
	def getHeaderElements(self) -> List[WebElement]:
		"""Method that gets Accordion Headers as `WebElement` interface objects.

		Args:
			None

		Returns:
			List[WebElement]: List of Accordion Header `WebElement` objects.


		"""
		self.waitUntilClickable(By.CLASS_NAME, "ia_accordionComponent__header")
		return self.waitForElements(By.CLASS_NAME, "ia_accordionComponent__header")

	def getAccordionHeaders(self) -> List[AccordionHeader]:
		"""Method that gets the AccordionHeader objects associated with an Accordion Element.

		Args:
			None

		Returns:
			List[AccordionHeader]: List of Accordion Header objects.
		"""
		return [AccordionHeader(self.session, element=element) for element in self.getHeaderElements()]

	def getAccordionHeaderByText(self, searchText: str) -> AccordionHeader:
		"""Takes string (such as group number or process) and searches the AccordionHeaders for a match.
		If match is found, return the AccordionHeader element.

		Args:
			searchText (str): Text to search for in the AccordionHeaders.
		Returns:
			AccordianHeader (object): The AccordionHeader object that matches the searchText.
		"""
		headers = self.getAccordionHeaders()
		header_dict = {}

		for header in headers:
			try:
				header_dict[header.text] = header
			except ComponentInteractionException:
				""" This is not a text header """
				pass

		for key, value in header_dict.items():
			if searchText in key:
				return value
		raise ElementNotFoundException(
			"No header exists with the text \"%s\"." % searchText)

	def getBodyElements(self) -> List[WebElement]:
		"""Gets the WebElements of the Accordion Body.

		Args:
			None

		Returns:
			List[WebElement]: List of Accordion Body WebElement objects.
		"""
		self.waitUntilClickable(By.CLASS_NAME, "ia_accordionComponent__body")
		return self.waitForElements(By.CLASS_NAME, "ia_accordionComponent__body")

	def toggleBody(self, index: int) -> bool:
		"""Toggles the body of a specified AccordionHeader in the Accordion `WebElement`.

		Args:
			index (int): Index of the AccordionHeader to toggle.

		Returns:
			bool: Updated state of the AccordionHeader after toggleBody().
		"""
		return AccordionHeader(self.session, element=self.getHeaderElements()[index]).toggleExpansion()

	def expandAll(self) -> None:
		"""Expands all AccordionHeader elements in current Accordion.

		Args:
			None

		Returns:
			None
		"""
		headersElements = self.getHeaderElements()  # List of AccordionHeader WebElements
		headers = [AccordionHeader(self.session, element=element)   # Stores WebElements as AccordionHeader objects
				   for element in headersElements]

		for header in headers:  # Iterates through AccordionHeader objects and expands them
			if not header.isExpanded():
				header.toggleExpansion()

	def expandBody(self, index: int) -> None:
		"""Method that reveals body element of an AccordianHeader element.

		Args:
			inedx (int): Index of the AccordionBody element to expand/reveal.

		Returns:
			None
		"""
		headersElements = self.getHeaderElements()
		headers = [AccordionHeader(self.session, element=element)
				   for element in headersElements]

		if not headers[index].isExpanded():
			headers[index].toggleExpansion()


class Button(PerspectiveComponent):
	pass


class CheckBox(PerspectiveComponent):
	"""The CheckBox Perspective Component which consists of a clickable box that can be toggled on or off.

	Attributes:
		state (bool): Current state of the CheckBox.
	"""

	def getValue(self) -> bool:
		"""Gets the current state of the checkbox.

		Args:
			None

		Returns:
			bool: True if the checkbox is checked, False if the checkbox is unchecked.

		Raises:
			NoSuchElementException: If the checkbox is not found after attepting to located by partial/class name.
		"""
		try:
			checkboxId = self.find_element_by_class_name(
				"icon").get_attribute("id")
			checkboxState = {
				"check_box": True,
				"check_box_outline_blank": False
				# "ia_checkbox__uncheckedIcon"
			}
			return checkboxState.get(checkboxId)

		except NoSuchElementException:
			"""Lets try another class set"""
			try:
				checkbox = self.find_element_by_partial_class_name(
					"ia_checkbox__uncheckedIcon")
				return False
			except NoSuchElementException:
				checkbox = self.find_element_by_partial_class_name(
					"ia_checkbox__checkedIcon")
				return True
		except Exception as e:
			""" Raise the original exception """
			raise e

	def toggle(self) -> bool:
		"""Toggles the state of the checkbox.

		Args:
			None

		Returns:
			bool: The updated state of the checkbox after the toggle.

		"""
		if self.get_attribute('class') == 'ia_checkbox':
			self.click()
		else:
			self.find_element_by_class_name("ia_checkbox").click()

		return self.getValue()

	def setValue(self, value: bool) -> None:
		"""Method to manually update the state of the checkbox to the specified value.

		Args:
			value (bool): The value to set the checkbox to.

		Returns:
			None
		"""
		if self.getValue() != value:
			self.toggle()


class Dropdown(PerspectiveComponent):
	"""The Dropdown Perspective Component containing a button to open list of options to select from.

		Attributes:
			Label (str): The label of the dropdown option that will be shown to the user.
			Value: The value of the dropdown option that will be returned.
	"""

	def getValue(self) -> WebElement:
		"""Method that will return the value of the targeted dropdown option.

		Args:
			None

		Returns:
			WebElement: The value of the dropdown option.

		Raises:
			ElementNotFoundException: If the dropdown option is not found after attempting to locate by class name.
		"""
		try:
			return self.waitForElement(By.CLASS_NAME, "ia_dropdown__valueSingle", timeout_in_seconds=1)
		except ElementNotFoundException:
			"""Unable to find any value in dropdown"""
			return ''

	def getValues(self) -> List[WebElement]:
		"""Method that will return the values available in the dropdown.

		Args:
			None

		Returns:
			List[WebElement]: All values associated with the dropdown's options.

		Raises:
			ElementNotFoundException: Dropdown was not able to be located or no values are present in options.

		"""
		try:
			return self.waitForElements(By.CLASS_NAME, "ia_dropdown__valuePill", timeout_in_seconds=1)
		except ElementNotFoundException:
			"""There currently isn't any values"""
			return []
		except:
			raise ComponentInteractionException(
				"Unable to identifies values in dropdown")

	def clearData(self) -> None:
		"""Clears the selection option in the dropdown.

		Args:
			None

		Returns:
			None
		"""
		try:
			self.waitForElement(
				By.CLASS_NAME, "iaDropdownCommon_clear_value", timeout_in_seconds=1).click()
		except:
			"""No value currently set"""
			pass

	def setRandomValue(self) -> None:
		"""Method selects a random option from the dropdown and updates the value of the dropdown to that option.
		Useful for testing the behavior of the dropdown is consistent no matter which option is selected by a user.

		Args:
			None

		Returns:
			None
		"""
		dropdownOptions = self.getOptions()
		ind = random.randrange(0, len(dropdownOptions))
		dropdownOptions[ind].click()
		return

	def setValue(self, option_text: str) -> None:
		"""Specify a value that the dropdown should be set to.

		Args:
			option_text (str): The text of the option that the dropdown should be set to.

		Returns:
			None        
		"""
		dropdownOptions = self.getOptions()

		for option in dropdownOptions:
			if option.text == option_text:
				option.click()
				return

	def getOptions(self) -> List[WebElement]:
		"""Method that collects all the options in a dropdown as a list of `WebElement` objects.

		Args:
			None

		Returns:
			List[WebElement]: A list of all the options in the dropdown.
		"""
		self.click()
		options_modal = PerspectiveElement(
			self.session, By.CLASS_NAME, "iaDropdownCommon_options")
		return options_modal.getChildren()

	def getOptionTexts(self) -> List[str]:
		"""Get the availalbe labels in the dropdown options.

		Args:
			None

		Returns:
			List[str]: A list of all the labels in the dropdown options.
		"""
		dropdown_options = self.getOptions()
		return [dropdown_option.text for dropdown_option in dropdown_options]

	def setValues(self, option_texts: List[str]) -> None:
		"""Set multiple values to a dropdown element. Specific to behavior for a multiSelect dropdown.

		Args:
			option_texts (List[str]): A list of the options to select in the dropdown.

		Returns:
			None

		Raises:
			ComponentInteractionException: The dropdown is not a multi-select dropdown.
		"""
		if not "iaDropdownCommon_multi-select" in self.get_attribute("class"):
			raise ComponentInteractionException("Dropdown is not multi-select")

		currentValues = self.getValues()
		for value in currentValues:
			option_texts.remove(value.text)

		for option in option_texts:
			optionAdded = False
			option_elements = self.getOptions()
			for option_element in option_elements:
				if option_element.text == option:
					optionAdded = True
					option_element.click()
					break

			if not optionAdded:
				raise ComponentInteractionException(
					"Dropdown Value Not Present: %s" % option)

	def isVisible(self) -> bool:
		"""Currently an invisible dropdown in the filter does not have a distinct class like the Menu "item-invisible" class
		An invisible element will have a height of 0; checks the element's height.

		Returns:
			bool: True if the dropdown is visible, False if the dropdown is not visible.
		"""
		return self.get_attribute("height") != 0


class DateTimeInput(PerspectiveComponent):
	"""Class that represents the DateTimeInput component in Perspective.
	Consists of an input field and a DateTimePicker modal that appears to take input.
	"""

	DATE_TIME_INPUT_CLASS_NAME = 'ia_dateTimeInputComponent'
	MODAL_CLASS_NAME = 'ia_componentModal'
	DATE_PICKER_CLASS_NAME = 'iaDateRangePicker'
	MONTH_SELECT_CLASS_NAME = 'monthSelectorContainer'
	YEAR_SELECT_CLASS_NAME = 'yearSelectorContainer'
	DAY_CALENDAR_CLASS_NAME = 'calendar'
	DAY_TILE_CLASS_NAME = 'ia_dateRangePicker__calendar__dayTile'
	TIME_PICKER_CLASS_NAME = 'iaTimePickerInput'
	HOUR_FIELD_CLASS_NAME = 'hours'
	MINUTE_FIELD_CLASS_NAME = 'minutes'
	AM_PM_PICKER_CLASS_NAME = 'timePickerAmPmPicker'

	def getValue(self) -> str:
		"""Get the value of the input field.

		Args:
			None

		Returns:
			str: The date currently selected by the DateTimeInput.        
		"""

		if self.tag_name == 'input':
			return str(self.get_attribute('value'))
		else:
			# If the input is not declared, create a web element
			inputTag: WebElement = self.find_element_by_tag_name('input')
			return inputTag.get_attribute('value')

	def getDateTimeModal(self) -> PerspectiveElement:
		"""Gets the DateTimePicker modal that appears when the input field is clicked as a PerspectiveElement.

		Args:
			None

		Returns:
			PerspectiveElement: The DateTimePicker modal containing a calendar and time selector.
		"""
		return PerspectiveElement(self.session, By.CLASS_NAME, self.MODAL_CLASS_NAME)

	def getDatePicker(self) -> PerspectiveElement:
		"""Selects the DatePicker from the calendar modal as a PerspectiveElement.

		Args:
			None

		Returns:
			PerspectiveElement (object): Containing the date input field of the calendar modal.
		"""
		modal = self.getDateTimeModal()
		return PerspectiveElement(self.session, By.CLASS_NAME, self.DATE_PICKER_CLASS_NAME, parent=modal)

	def getTimePicker(self) -> PerspectiveElement:
		"""Selects the TimePicker from the calendar modal as a PerspectiveElement.

		Args:
			None

		Returns:
			PerspectiveElement (object): Containing the time input field of the calendar modal.
		"""
		modal = self.getDateTimeModal()
		return PerspectiveElement(self.session, By.CLASS_NAME, self.TIME_PICKER_CLASS_NAME, parent=modal)

	def getYear(self) -> int:
		"""Gets the value selected in the year input field of the calendar modal.

		Args:
			None

		Returns:
			int: The selected year.

		"""
		self.click()
		yearSelectWrapper = PerspectiveElement(
			self.session, By.CLASS_NAME, self.YEAR_SELECT_CLASS_NAME, parent=self.getDatePicker())
		yearSelect = Select(
			yearSelectWrapper.find_element_by_tag_name('select'))
		selectedOptionTag: WebElement = yearSelect.first_selected_option
		val = int(selectedOptionTag.text)
		self.click()
		return val

	def _setYear(self, year: int):
		"""Private method that sets the year in the calendar modal.

		Args:
			year (int): The year to set the calendar modal to.

		Returns:
			None        
		"""
		yearSelectWrapper = PerspectiveElement(
			self.session, By.CLASS_NAME, self.YEAR_SELECT_CLASS_NAME, parent=self.getDatePicker())
		yearSelect: WebElement = yearSelectWrapper.find_element_by_tag_name(
			'select')
		optionToClick: WebElement = yearSelect.find_element_by_css_selector(
			"option[value='%s']" % str(year))
		yearSelect.click()
		optionToClick.click()
		yearSelect.click()

	def _setMonth(self, month: int):
		"""Private method that sets the month in the calendar modal.

		Args:
			month (int): The month to set the calendar modal to.
		Returns:
			None
		"""
		monthSelectWrapper = PerspectiveElement(
			self.session, By.CLASS_NAME, self.MONTH_SELECT_CLASS_NAME, parent=self.getDatePicker())
		monthSelect: WebElement = monthSelectWrapper.find_element_by_tag_name(
			'select')
		optionToClick: WebElement = monthSelect.find_element_by_css_selector(
			"option[value='%s']" % str(month))
		monthSelect.click()
		optionToClick.click()
		monthSelect.click()

	def _setDayInCurrentMonth(self, day: int):
		"""Private method that sets the day in the calendar modal."""
		datePicker = self.getDatePicker()
		calendar: WebElement = datePicker.find_element_by_class_name(
			'calendar')
		dayToClick: WebElement = calendar.find_element_by_css_selector(
			"div.%s[data-day='%s']" % (self.DAY_TILE_CLASS_NAME, str(day)))
		dayToClick.click()

	def _setTime(self, hour: int, minute: int):
		"""Private method that sets the time in the calendar modal."""

		# Convert from 24h to 12h time
		if hour >= 12:
			AM_OR_PM = 'pm'
			hour -= 12
		else:
			AM_OR_PM = 'am'
		if hour == 0:
			hour = 12

		timePicker = self.getTimePicker()

		# Hours
		timePicker.waitUntilClickable(
			By.CLASS_NAME, self.HOUR_FIELD_CLASS_NAME)
		hoursField = TextBox(self.session, By.CLASS_NAME,
							 self.HOUR_FIELD_CLASS_NAME, parent=timePicker)
		hoursField.click()
		hoursField.selectAll()
		for char in str(hour):
			time.sleep(0.2)
			hoursField.setText(char, replace=False)

		# Minutes
		timePicker.waitUntilClickable(
			By.CLASS_NAME, self.MINUTE_FIELD_CLASS_NAME)
		minutesField = TextBox(self.session, By.CLASS_NAME,
							   self.MINUTE_FIELD_CLASS_NAME, parent=timePicker)
		minutesField.click()
		minutesField.selectAll()
		for char in str(minute):
			time.sleep(0.2)
			minutesField.setText(char, replace=False)

		# AM/PM
		selectAmPmWrapper = PerspectiveElement(
			self.session, By.CLASS_NAME, self.AM_PM_PICKER_CLASS_NAME, parent=timePicker)
		selectAmPm: WebElement = selectAmPmWrapper.find_element_by_tag_name(
			'select')
		optionToClick: WebElement = selectAmPm.find_element_by_css_selector(
			"option[value='%s']" % AM_OR_PM)
		selectAmPm.click()
		optionToClick.click()
		selectAmPm.click()

	def setDateTime(self, dateTime: datetime):
		"""Wrapper method that sets month, day, year, and time in the calendar modal.

		Args:
			dateTime (datetime): The datetime object to set the calendar modal to.

		Returns:
			None
		"""
		self.click()
		self._setTime(dateTime.hour, dateTime.minute)
		self._setYear(dateTime.year)
		self._setMonth(dateTime.month)
		self._setDayInCurrentMonth(dateTime.day)


class Icon(PerspectiveComponent):
	pass


class Label(PerspectiveComponent):
	"""A label class for selecting label perspective components."""

	def getText(self) -> str:
		"""Gets the text of the label."""
		return self.text


class MenuTree(PerspectiveComponent):
	"""A menu tree class for selecting menu tree perspective component."""

	menu_item_class = "menu-item"
	menu_label_class = "ia_menuTreeComponent__item__text"
	menu_invisible_class = "item-invisible"
	back_button_class = "menu-back-action"

	def getItems(self, include_invisible=False) -> List[WebElement]:
		"""Gets the menu items in the menu tree each as `WebElement`.

		Args:
			include_invisible (bool): Whether to include invisible menu items in the list.

		Returns:
			List[WebElement]: A list of menu items as `WebElement`.

		Raises:
			ElementNotFoundException: If the menu items cannot be found.
		"""
		try:
			menu_items_all = self.waitForElements(
				By.CLASS_NAME, self.menu_item_class)
			if include_invisible:
				return menu_items_all
			else:
				try:
					menu_items_invisible = self.waitForElements(
						By.CLASS_NAME, self.menu_invisible_class, 3)
					return [label for label in menu_items_all if label not in menu_items_invisible]
				except ElementNotFoundException:
					return menu_items_all
		except ElementNotFoundException:
			raise ElementNotFoundException("Unable to find menu items")

	def getItemTexts(self, include_invisible=False) -> List[str]:
		"""Gets just the text of each menu item in the menu tree.

		Args:
			include_invisible (bool): Whether to include invisible menu items in the list.

		Returns:
			List[str]: A list of menu item texts.

		Raises:
			ElementNotFoundException: If the menu items cannot be found.        
		"""
		try:
			menu_items = self.getItems(include_invisible=include_invisible)
			return [item.find_element(By.CLASS_NAME, self.menu_label_class).text for item in menu_items]
		except Exception as e:
			raise ElementNotFoundException("Unable to find menu items")

	def selectItem(self, name: str):
		"""Method to click on a menu tree item and select it.

		Args:
			name (str): The name of the menu item to select.

		Raises:
			ElementNotFoundException: If the menu item cannot be found.        
		"""
		menu_items = self.getItems()
		for item in menu_items:
			item_label: WebElement = item.find_element(
				By.CLASS_NAME, self.menu_label_class)
			if item_label.text == name:
				item.click()
				return
		raise ElementNotFoundException("Unable to find menu item: " + name)

	def clickBackButton(self):
		"""Method to return to main view of menu tree.

		Raises:
			ElementNotFoundException: If the back button cannot be found.        
		"""
		try:
			self.waitForElement(
				By.CLASS_NAME, self.back_button_class, timeout_in_seconds=3).click()
		except ElementNotFoundException:
			raise ElementNotFoundException(
				"Back button not found. Please verify that the menu is not at the top level.")


class NumericInput(PerspectiveComponent):
	"""A perspective component class for interacting with numeric input components."""

	def getInputBox(self) -> WebElement:
		"""Method that gets the input box of the numeric input component.

		Args:
			None

		Returns:
			WebElement: The input box of the numeric input component.
		"""
		self.find_element_by_class_name("ia-numeral-input").click()
		return self.find_element_by_class_name("ia-numeral-input")

	def getInputState(self) -> InputState:
		"""Method to determine the state of the input box

		Returns:
			InputState: The state of the input box as either valid or invalid.
		"""
		self.getInputBox()
		try:
			invalidInputBox = self.find_element_by_partial_class_name(
				"ia-numeral-input psc-")
		except (ElementNotFoundException, NoSuchElementException):
			return InputState.VALID
		except Exception as e:
			raise ComponentInteractionException(
				"Unable to determine input state: %s" % e)

		if invalidInputBox:
			return InputState.INVALID
		return InputState.VALID

	def isInputValid(self):
		"""Method to determine if the input box is valid."""
		return self.getInputState() == InputState.VALID

	def send_keys(self, keys: str) -> None:
		"""Method to send keys to the input box.

		Args:
			keys (str): The keys to send to the input box.

		Returns:
			None
		"""
		self.getInputBox().send_keys(keys)

	def clearValue(self) -> None:
		"""Method to clear the value of the input box."""
		self.send_keys(self.session.select_all_keys + Keys.DELETE)

	def setValue(self, value: Union[int, float], withSubmit: bool = False, replace: bool = True) -> None:
		if replace:
			self.clearValue()
		self.send_keys(str(value))

		if withSubmit:
			self.getInputBox().submit()

	def getValue(self, forceFloat: bool = False) -> Union[int, float]:
		"""Method that collects value of the numeric input.

		Args:
			forceFloat (bool): Whether to force the value to be a float.

		Returns:
			Union[int, float]: The value of the numeric input as an int or float.
		"""
		if forceFloat is True:
			try:
				val = float(self.text)
			except ValueError:
				raise ValueError(
					"The NumericInput has an invalid value: " + self.text)
		else:
			try:
				val = int(self.text)
			except ValueError:
				try:
					val = float(self.text)
				except ValueError:
					raise ValueError(
						"The NumericInput has an invalid value: " + self.text)

		return val

	@property
	def text(self):
		"""Method that returns the text of the numeric input."""
		if self.tag_name == "input":
			return self.get_attribute("value")
		else:
			inputTag: WebElement = self.find_element_by_tag_name("input")
			return inputTag.get_attribute("value")


class TabContainer(PerspectiveComponent):
	"""A perspective component class for interacting with tab containers."""

	tab_class_name = "tab-menu-item"
	active_tab_class_name = "tab-active"
	tab_container_content_class_name = "ia_tabContainerComponent__content"

	def getTabs(self) -> List[WebElement]:
		"""Method that gets all the tabs in the tab container as a list of WebElements."""
		return self.find_elements_by_partial_class_name(self.tab_class_name)

	def getTabNames(self) -> List[str]:
		"""Method that gets all the tab names in the tab container as a list of strings."""
		tabs = self.getTabs()
		return [tab.text for tab in tabs]

	def getActiveTab(self) -> WebElement:
		"""Method that returns the active tab in the tab container as a WebElement."""
		return self.find_element_by_partial_class_name(self.active_tab_class_name)

	def switchToTab(self, name: str) -> WebElement:
		"""Method that switches to the specified tab in the tab container."""
		tabs = self.getTabs()
		for tab in tabs:
			if tab.text == name:
				tab.click()
				return tab
		raise ElementNotFoundException(
			"No tab exists with the name \"%s\"." % name)

	def getContent(self) -> WebElement:
		"""Method that returns the content of the active tab in the tab container as a WebElement."""
		containerContent = PerspectiveElement(
			self.session, self.find_element_by_partial_class_name(self.tab_container_content_class_name))
		elemInContainer = containerContent.getFirstChild()
		return elemInContainer


class _Pager(PerspectiveComponent):
	"""A private perspective component class for interacting with pagers."""

	page_class_name = "ia_pager__page"
	active_page_class_name = "ia_pager__page--active"
	next_page_class_name = "next"
	prev_page_class_name = "prev"
	first_page_class_name = "first"
	last_page_class_name = "last"
	disbaled_next_prev_class_name = "ia_pager__prevNext--disabled"
	disabled_first_last_class_name = "ia_pager__jumpFirstLast--disabled"
	jump_field_class_name = "ia_pager__jump"
	page_size_div_class_name = "ia_pager__pageSizeChooser"

	def getCurrentPage(self) -> int:
		"""Method that returns the current page number as an int."""
		activePageElem = self.waitForElement(
			By.CLASS_NAME, self.active_page_class_name)
		return int(activePageElem.text)

	def nextPage(self) -> int:
		"""Method that clicks the next page button and returns the new page number as an int.

		Raises:
			ComponentInteractionException: If the next page button is disabled.
		"""
		try:
			# If next button on screen
			nextButton: WebElement = self.find_element_by_class_name(
				self.next_page_class_name)
			if str(nextButton.get_attribute("class")).count(self.disbaled_next_prev_class_name) == 0:
				nextButton.click()
			else:
				raise ComponentInteractionException(
					"Cannot go to next page, already on last page")
		except NoSuchElementException:
			# No next button - every page num should be showing
			pageElems = self.waitForElements(
				By.CLASS_NAME, self.page_class_name)
			curPageIndex = self.getCurrentPage() - 1
			if curPageIndex != len(pageElems) - 1:
				pageElems[curPageIndex + 1].click()
			else:
				raise ComponentInteractionException(
					"Cannot go to next page, already on last page")
		return self.getCurrentPage()

	def prevPage(self) -> int:
		"""Method that clicks the previous page button.

		Returns:
			New page number as an int.

		Raises:
			ComponentInteractionException: If the previous page button is disabled.
		"""
		try:
			# If prev button on screen
			prevButton: WebElement = self.find_element_by_class_name(
				self.prev_page_class_name)
			if str(prevButton.get_attribute("class")).count(self.disbaled_next_prev_class_name) == 0:
				prevButton.click()
			else:
				raise ComponentInteractionException(
					"Cannot go to previous page, already on first page")
		except NoSuchElementException:
			# No prev button - every page num should be showing
			pageElems = self.waitForElements(
				By.CLASS_NAME, self.page_class_name)
			curPageIndex = self.getCurrentPage() - 1
			if curPageIndex != 0:
				pageElems[curPageIndex - 1].click()
			else:
				raise ComponentInteractionException(
					"Cannot go to previous page, already on first page")
		return self.getCurrentPage()

	def firstPage(self) -> None:
		"""Method that navigates to the first page."""
		try:
			# If first button on screen
			firstButton: WebElement = self.find_element_by_class_name(
				self.first_page_class_name)
			if str(firstButton.get_attribute("class")).count(self.disabled_first_last_class_name) == 0:
				firstButton.click()
			else:
				raise ComponentInteractionException("Already on first page")
		except NoSuchElementException:
			# No first button
			try:
				# If prev button on screen
				prevButton: WebElement = self.find_element_by_class_name(
					self.prev_page_class_name)
				while self.getCurrentPage() != 1:
					prevButton.click()
			except NoSuchElementException:
				# No prev button - every page num should be showing
				if self.getCurrentPage() != 1:
					pageElems = self.waitForElements(
						By.CLASS_NAME, self.page_class_name)
					pageElems[0].click()
				else:
					raise ComponentInteractionException(
						"Already on first page")

	def lastPage(self) -> None:
		"""Method that navigates to the last page."""
		try:
			# If last button on screen
			lastButton: WebElement = self.find_element_by_class_name(
				self.last_page_class_name)
			if str(lastButton.get_attribute("class")).count(self.disabled_first_last_class_name) == 0:
				lastButton.click()
			else:
				raise ComponentInteractionException("Already on last page")
		except NoSuchElementException:
			# No last button
			try:
				# If next button on screen
				nextButton: WebElement = self.find_element_by_class_name(
					self.next_page_class_name)
				while str(nextButton.get_attribute("class")).count(self.disbaled_next_prev_class_name) == 0:
					nextButton.click()
			except NoSuchElementException:
				# No next button - every page num should be showing
				if self.getCurrentPage() != 1:
					pageElems = self.waitForElements(
						By.CLASS_NAME, self.page_class_name)
					pageElems[-1].click()
				else:
					raise ComponentInteractionException("Already on last page")

	def jumpToPage(self, page: int) -> None:
		"""Method that jumps to a specific page.

		Args:
			page (int): Page number to jump to.

		Raises:
			ComponentInteractionException: If the page number is invalid.
		"""
		try:
			# "Jump to" text field on screen
			jumpTextField: WebElement = self.waitForElement(
				By.CLASS_NAME, self.jump_field_class_name)
			jumpTextField.clear()
			jumpTextField.send_keys(str(page))
			jumpTextField.send_keys(Keys.ENTER)
		except:
			# No "Jump to" text field
			try:
				# Next and prev buttons on screen
				nextButton: WebElement = self.find_element_by_class_name(
					self.next_page_class_name)
				prevButton: WebElement = self.find_element_by_class_name(
					self.prev_page_class_name)
				curPage = self.getCurrentPage()
				while curPage != page:
					if curPage < page:
						nextButton.click()
					elif curPage > page:
						prevButton.click()
			except:
				# No next and prev buttons on scren - every page num should be showing
				pageElems: List[WebElement] = self.waitForElements(
					By.CLASS_NAME, self.page_class_name)
				for pageElem in pageElems:
					if int(pageElem.text) == page:
						pageElem.click()
						break

		if self.getCurrentPage() != page:
			raise ComponentInteractionException(
				"Table page index out of range.")

	def getNumPages(self) -> int:
		"""Method that gets the number of pages to navigate in the pager."""
		try:
			# If the "next" button is visible, not every page is showing in the pager
			self.find_element_by_class_name(self.next_page_class_name)
		except NoSuchElementException:
			# No next button - every page num should be showing
			pageElems = self.waitForElements(
				By.CLASS_NAME, self.page_class_name)
			return len(pageElems)
		START_PAGE = self.getCurrentPage()
		self.lastPage()
		NUM_PAGES = self.getCurrentPage()
		self.jumpToPage(START_PAGE)
		return NUM_PAGES

	def getPageSizeSelect(self) -> Select:
		selectParent: WebElement = self.find_element_by_class_name(
			self.page_size_div_class_name)
		select = Select(selectParent.find_element_by_tag_name("select"))
		return select

	def getPageSize(self) -> int:
		select = self.getPageSizeSelect()
		selectedOption: WebElement = select.first_selected_option
		optionStr = str(selectedOption.text)
		pageSize = int(optionStr.split()[0])
		return pageSize

	def setPageSize(self, size: int):
		select = self.getPageSizeSelect()
		try:
			select.select_by_value(str(size))
		except NoSuchElementException:
			raise ComponentInteractionException(
				f"No option exists to show {str(size)} items per page")


class Popup(PerspectiveElement):
	"""Perspective element class for popups."""

	def __init__(self, session: Session, identifier: str = None) -> None:
		super().__init__(session, By.ID, "popup-%s" % identifier)

	def getRoot(self) -> WebElement:
		"""Method that gets the root element of the popup."""
		return self.parent.parent.parent

	def close(self) -> None:
		"""Method that closes the popup."""
		self.find_element_by_class_name("close-icon").click()


class TableRowGroup(PerspectiveElement):
	"""Perspective element class for table row."""

	def getDataId(self) -> str:
		"""Method that gets the data id of the row as a string."""
		return self.get_attribute("data-column-id")


class TableCell(PerspectiveElement):
	"""Perspective element class for table cell."""

	def getDataId(self) -> str:
		"""Method that gets the data id of the cell as a string."""
		return self.get_attribute("data-column-id")

	def getData(self) -> str:
		"""Method that gets the data of the cell as a string."""
		return self.find_element_by_class_name("content").text


class Table(PerspectiveComponent):
	"""Perspective component class for configuration and returning data about a table."""

	header_cell_class_name = "ia_table__head__header__cell"
	row_group_class_name = "ia_table__body__rowGroup"
	cell_class_name = "ia_table__cell"
	table_filter_container_class_name = "ia_tableComponent__filterContainer"
	pager_class_name = "ia_pager"
	_pager = None

	def __init__(self, session: Session, locator: By = ..., identifier: str = None, element: WebElement = None, parent: WebElement = None, timeout_in_seconds=None):
		super().__init__(session, locator, identifier, element, parent, timeout_in_seconds)
		# Locating web element pager on the table perspective component
		try:
			pagers = self.waitForElements(
				By.CLASS_NAME, self.pager_class_name, timeout_in_seconds=2)
			if pagers:
				self._pager = _Pager(self.session, element=pagers[0])
		except (ElementNotFoundException, NoSuchElementException):
			""" The table likely does not have a pager visible """

	# Start _Pager Methods
	def getCurrentPage(self) -> int:
		"""Method that gets the current page of the table as an int."""
		return self._pager.getCurrentPage() if self.hasPager() else 1

	def nextPage(self) -> int:
		"""Method that gets the next page of the table as an int."""
		if not self.hasPager():
			raise ComponentInteractionException(
				"Page navigation is disabled for this table")
		return self._pager.nextPage()

	def prevPage(self) -> int:
		"""Method that gets the previous page of the table as an int."""
		if not self.hasPager():
			raise ComponentInteractionException(
				"Page navigation is disabled for this table")
		return self._pager.prevPage()

	def firstPage(self) -> None:
		"""Method that navigates to the first page of the table.."""
		if not self.hasPager():
			raise ComponentInteractionException(
				"Page navigation is disabled for this table")
		self._pager.firstPage()

	def lastPage(self) -> None:
		"""Method that navigates to the last page of the table."""
		if not self.hasPager():
			raise ComponentInteractionException(
				"Page navigation is disabled for this table")
		self._pager.lastPage()

	def jumpToPage(self, page: int) -> None:
		"""Method that navigates to the specified page of the table."""
		if not self.hasPager():
			raise ComponentInteractionException(
				"Page navigation is disabled for this table")
		self._pager.jumpToPage(page)

	def getNumPages(self) -> int:
		"""Method that gets the number of pages in the table as an int."""
		return self._pager.getNumPages() if self.hasPager() else 1

	def getPageSize(self) -> int:
		"""Method that gets the page size of the table as an int."""
		return self._pager.getPageSize() if self.hasPager() else len(self.waitForElements(By.CLASS_NAME, self.row_group_class_name))

	def setPageSize(self, size: int):
		"""Method that sets the page size of the table."""
		if not self.hasPager():
			raise ComponentInteractionException(
				"Setting the page size is disabled for this table")
		self._pager.setPageSize(size)
	# End _Pager Methods

	def getHeaders(self) -> List[TableCell]:
		"""Method that gets the headers of the table as a list of TableCells."""
		headerElements = self.waitForElements(
			By.CLASS_NAME, self.header_cell_class_name)
		return [TableCell(self.session, element=element) for element in headerElements]

	def getHeaderTexts(self) -> List[str]:
		"""Method that gets the text of the headers as a list of strings."""
		headerElements = self.waitForElements(
			By.CLASS_NAME, self.header_cell_class_name)
		return [element.text for element in headerElements]

	def getDataColumnIds(self) -> List[str]:
		"""Method that gets the data column ids of the table as a list of strings."""
		return [header.getDataId() for header in self.getHeaders()]

	def getRowCount(self) -> int:
		"""Method that gets the number of rows in the table as an int."""
		num_pages = self.getNumPages()
		num_rows = self.getPageSize()
		if num_pages > 1:
			self.lastPage()
			last_rows = len(self.getRowGroups())
			self.firstPage()
		else:
			last_rows = len(self.getRowGroups())
		return (num_pages - 1) * num_rows + last_rows

	def getRowGroups(self) -> List[TableRowGroup]:
		"""Method that gets the row groups of the table as a list of TableRowGroup objects."""
		rowGroupElements = self.waitForElements(
			By.CLASS_NAME, self.row_group_class_name)
		return [TableRowGroup(self.session, element=element) for element in rowGroupElements]

	def getRowData(self) -> List[List[TableCell]]:
		"""Method that returns the data of the table as a nested list of TableCells."""
		rowGroups = self.getRowGroups()

		rows = []
		for rowGroup in rowGroups:
			rowCells = [TableCell(self.session, element=element)
						for element in rowGroup.find_elements_by_class_name(self.cell_class_name)]
			rows.append(rowCells)
		return rows

	def getColumnAsList(self, dataId: str = None, columnIndex: int = None) -> List[WebElement]:
		"""Returns a list of WebElements for the column specified by dataId or columnIndex."""
		if dataId:
			return self.waitForElements(
				By.XPATH, ".//*[@class='tc ia_table__cell' and @data-column-id='%s']" % dataId, timeout_in_seconds=5)
		elif columnIndex:
			return self.waitForElements(
				By.XPATH, ".//*[@class='tc ia_table__cell' and @data-column-index='%s']" % columnIndex, timeout_in_seconds=5)
		else:
			raise ComponentInteractionException(
				"Must provide a column selector dataId or columnIndex")

	def getColumnTextsAsList(self, dataId: str = None, columnIndex: int = None) -> List[str]:
		"""Returns a list of strings for the column specified by dataId or columnIndex."""
		columnCells = self.getColumnAsList(dataId, columnIndex)
		return [cell.text for cell in columnCells]

	def getCurrentPageData(self) -> List[dict]:
		"""Collects the data from the current page of the table and returns it as a list of dictionaries."""
		rowGroups = self.getRowData()
		rows = []

		for rowGroup in rowGroups:
			rowData = {}
			for cellElement in rowGroup:
				rowData[cellElement.getDataId()] = cellElement.getData()

			rows.append(rowData)

		return rows

	def getAllData(self) -> List[dict]:
		"""Collects the data from all pages of the table and returns it as a list of dictionaries."""
		START_PAGE = self.getCurrentPage()
		self.firstPage()
		curPage = 1
		rows: List[dict] = []

		while True:
			curPage = self.getCurrentPage()
			curPageRows = self.getCurrentPageData()
			rows.extend(curPageRows)

			# Loop until can't go to next page
			if curPage == self.nextPage():
				break

		self.jumpToPage(START_PAGE)
		return rows

	def clickOnRow(self, rowIndex: int) -> None:
		self.getRowGroups()[rowIndex].click()

	def doubleClickOnRow(self, rowIndex: int) -> None:
		rowGroups = self.getRowGroups()

		if rowIndex > len(rowGroups):
			raise ComponentInteractionException(
				"Click index %s out of range: %s" % (rowIndex, len(rowGroups)))

		rowGroups[rowIndex].doubleClick()

	def clickOnOrderDetails(self, rowIndex: int) -> None:
		self.getColumnAsList("Details")[rowIndex].click()

	def filterTable(self, keys: str) -> None:
		"""Method that filters the table by the given keys."""
		filterContainer: WebElement = self.find_element_by_class_name(
			self.table_filter_container_class_name)
		filterContainer.find_element_by_class_name("ia_inputField").click()
		filterInputBox: WebElement = filterContainer.find_element_by_class_name(
			"ia_inputField")
		filterInputBox.send_keys(keys)

	def hasPager(self) -> bool:
		"""Method that returns True if the table has a pager, False otherwise."""
		return self._pager is not None

	def sortBy(self, columnId: str, direction: str = "up") -> None:
		"""Method that sorts the table by the given columnId and direction."""
		column_id = f"div[data-column-id=\"{columnId}\""
		try:
			column = self.find_element_by_css_selector(column_id)
			up = Button(self.session, By.CLASS_NAME, "sort-up", parent=column)
			down = Button(self.session, By.CLASS_NAME,
						  "sort-down", parent=column)
			up_classes = up.get_attribute("class")
			down_classes = down.get_attribute("class")

			if direction == 'up' and 'active' not in up_classes:
				up.click()
			elif direction == 'down' and 'active' not in down_classes:
				down.click()
		except ElementNotFoundException as e:
			raise e


class TextArea(PerspectiveComponent):
	"""Class that represents a text area perspective component."""

	def clearText(self) -> None:
		self.selectAll()
		self.send_keys(Keys.DELETE)

	def isReadonly(self) -> bool:
		"""Method that returns True if the text area is readonly, False otherwise."""
		return self.get_attribute("readonly") == "true"

	def setText(self, text: str, replace: bool = True) -> None:
		"""Method that sets the text of the text area."""
		if replace:
			self.clearText()

		self.send_keys(str(text))


class TextBox(PerspectiveComponent):
	"""Class that represents a text box perspective component."""

	def clearText(self) -> None:
		"""Method that clears the text of the text box."""
		self.click()
		self.selectAll()
		self.send_keys(Keys.DELETE)

	def setText(self, text: str, withSubmit: bool = False, replace: bool = True) -> None:
		"""Method that sets the text of the text box with provided text argument."""
		if replace:
			self.clearText()
		else:
			self.click()
		self.send_keys(str(text))
		if withSubmit:
			self.submit()


class ToggleSwitch(PerspectiveComponent):
	"""Class that represents a toggle switch perspective component.
	Can be used to toggle the switch and get/set the current value."""

	def getValue(self) -> bool:
		track: WebElement = self.find_element_by_class_name(
			"ia_toggleSwitch__track")
		return "--selected" in track.get_attribute("class")

	def toggle(self) -> bool:
		"""Method that toggles the toggle switch."""
		self.click()
		return self.getValue()

	def setValue(self, value: bool) -> None:
		"""Method that sets the toggle switch to the given value."""
		if self.getValue() != value:
			self.toggle()


class View(PerspectiveElement):
	pass


class Dashboard(PerspectiveElement):
	"""Class containing methods for interacting and retreiving components from a dashboard element.
	"""

	MODAL_CLASS = 'ia_componentModal'
	MODAL_ENTRY_CLASS = 'ia_dashboardComponent__addWidgetModal__menu__category__item'
	MODAL_ENTRY_TITLE_CLASS = 'widgetMenuItemTitle'
	DASHBOARD_COMPONENT_CLASS = 'ia_dashboardComponent__widget'

	def getDashboardColumns(self) -> int:
		"""Returns the amount columns in the dashboards grid array as an int."""
		# creating a local variable 'grid_array' of WebElement type to use .find_element(By.) method
		grid_array: WebElement = self.find_element(
			By.CSS_SELECTOR, "div.gridCommon__grid")
		s = grid_array.get_attribute("style").split(';')

		if "grid-template-columns" in s[1]:
			return int(s[1].split(":")[1].split("repeat(")[1].split(",")[0])

	def getDashboardRows(self) -> int:
		"""Returns the rows in the dashboards grid array."""
		grid_array: WebElement = self.find_element(
			By.CSS_SELECTOR, "div.gridCommon__grid")
		s = grid_array.get_attribute("style").split(';')

		if "grid-template-rows" in s[2]:
			return int(s[2].split(":")[1].split("repeat(")[1].split(",")[0])

	def openWidgetModal(self, row: int, col: int) -> None:
		"""Opens the widget modal by clicking where row/col specify on the dashboard."""
		add_cell = self._getCell(row, col)
		# gets the specified cell or a cell that is empty
		add_cell.click()

	def closeWidgetModal(self) -> None:
		"""Closes the widget modal by clicking the close button."""
		try:
			widget_modal = self._getAddWidgetModal()
			widget_modal.find_element(
				By.CSS_SELECTOR, "button.ia_button--secondary").click()
		except ElementNotFoundException:
			raise ElementNotFoundException("Widget modal not found.")

	def placeWidget(self, row: int, col: int, new_widget: str) -> None:
		"""Adds a widget to the dashboard at the given row and column.
		
		Args:
			row (int): The row to add the widget to.
			col (int): The column to add the widget to.
			new_widget (str): The name of the widget to add.

		"""
		self.openWidgetModal(row, col)

		try:
			# Retrieve a list of all the widget entries in the modal
			widget_modal = self._getAddWidgetModal()
			widget_entries = self._getWidgetModalEntries(widget_modal)

			for entry in widget_entries:
				title = entry.find_element(
					By.CLASS_NAME, self.MODAL_ENTRY_TITLE_CLASS).text

				if title == new_widget:
					print(title)
					entry.click()
					break

			widget_modal.find_element(
				By.CSS_SELECTOR, "button.ia_button--primary").click()

		except ElementNotFoundException:
			raise ElementNotFoundException("Widget modal not found.")

	def addRandomWidget(self) -> None:
		"""Automatically add a widget to a random spot if no row and col are specified.
		Current implementation may break if selenium tries to click on a cell that already has a widget.
		"""
		# Selects a random cell within the dashboard area.
		dashboard_index = [random.randrange(0, self.getDashboardRows()),
			random.randrange(0, self.getDashboardColumns())]

		self.openWidgetModal(dashboard_index[0], dashboard_index[1])

		try:
			widget_modal = self._getAddWidgetModal()
			widget_entries = self._getWidgetModalEntries(widget_modal)

			ind = random.randrange(0, len(widget_entries))
			widget_entries[ind].click()
			widget_modal.find_element(By.CSS_SELECTOR, "button.ia_button--primary").click()

		except ElementNotFoundException:
			raise ElementNotFoundException("Widget modal not found.")


	def _getAddWidgetModal(self) -> PerspectiveElement:
		"""Gets the AddWidget modal that appears when an empty cell is clicked.

		Args:
			None

		Returns:
			PerspectiveElement: The DateTimePicker modal containing a calendar and time selector.
		"""
		return PerspectiveElement(self.session, By.CLASS_NAME, self.MODAL_CLASS)

	def _getWidgetModalEntries(self, widget_modal: PerspectiveElement) -> List[PerspectiveElement]:
		"""Gets the list of PerspectiveElements that are entries in the AddWidget modal.

		Args:
			widget_modal (PerspectiveElement): The current AddWidget modal.

		Returns:
			List[PerspectiveElement]: The list of PerspectiveElements that are entries in the AddWidget modal.
		"""
		return widget_modal.waitForElements(By.CLASS_NAME, self.MODAL_ENTRY_CLASS)

	def _getCell(self, row: int, col: int) -> WebElement:

		# TODO: Check that a widget is not already in the specified cell, check
		# the size of the widget in cases where the area is larger than X1 / Y1 / X2 / Y2

		# NOTE: Functional for .placeWidget() but does not have automatic placement for .addRandomWidget()

		# Retrieve a random spot within the dashboard area
		dashboard_area = [self.getDashboardRows(), self.getDashboardColumns()]

		if row > dashboard_area[0] or col > dashboard_area[1]:
			print("Row or column is out of bounds. Resetting to first cell.")
			row = 1
			col = 1

		# Coordinates that should match the style attribute of the specified cell
		coordinates = ("grid-area: " + str(row) + " / " +
						str(col) + " / " + str(row + 1) + " / " + str(col + 1))

		# Collects all clickable cells from the dashboard grid
		empty_cells = self.find_elements(
			By.CSS_SELECTOR, "div.gridCommon__grid__cell")

		# Check if there is a dashboard widget already in the specified cell
		# TODO: Instead of comparing the style for each cell, compare the starting/ ending coordinates.
		# Have to split the coordinates from the style to make comparison easier. 
		try:
			# Retrieves all cells that are already used by a widget as a list of WebElements
			used_cells = self.find_elements(
				By.CLASS_NAME, self.DASHBOARD_COMPONENT_CLASS)

			for widget_element in used_cells:
				widget_style = widget_element.get_attribute("style")
				# print(widget_style)

				if coordinates in widget_style:
					print("Widget already exists in this cell.")


		except ElementNotFoundException:
			print("No widgets found on dashboard returning first cell.")
			return empty_cells[0]

		# Retrieve the style for each 
		for element in empty_cells:
			# loop through each retrieved empty element and get the style attribute
			style = element.get_attribute("style")

			if coordinates in style:
				return element         
