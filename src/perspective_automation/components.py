import time
import random
from enum import Enum
from typing import Union
from datetime import datetime

from selenium.common.exceptions import NoSuchElementException, TimeoutException

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
    def getHeaderType(self) -> AccordionHeaderType:
        if self.find_element_by_class_name("ia_accordionComponent__header__text"):
            return AccordionHeaderType.TEXT
        elif self.find_element_by_class_name("ia_accordionComponent__header__view"):
            return AccordionHeaderType.VIEW
        else:
            return None

    def isExpanded(self) -> bool:
        return "expanded" in self.find_element_by_partial_class_name("ia_accordionComponent__header__chevron").get_attribute("class")

    def toggleExpansion(self) -> bool:
        self.click()
        return self.isExpanded
    
    def setExpansion(self, value: bool):
        currentState = self.isExpanded()
        if currentState != value:
            self.toggleExpansion()

    def getHeaderText(self) -> str:
        """
        Checks if the Accordion Header is a text header, and if so, returns the text inside.
        """
        if self.getHeaderType() != AccordionHeaderType.TEXT:
            raise ComponentInteractionException("Cannot get text of a non-text accordion header.")
        return self.text


class Accordion(PerspectiveComponent):
    def getHeaderElements(self) -> list[WebElement]:
        self.waitUntilClickable(By.CLASS_NAME, "ia_accordionComponent__header")
        return self.waitForElements(By.CLASS_NAME, "ia_accordionComponent__header")

    def getAccordionHeaders(self) -> list[AccordionHeader]:
        return [AccordionHeader(self.session, element=element) for element in self.getHeaderElements()]
        
    def getAccordionHeaderByText(self, searchText: str) -> AccordionHeader:
        """
        Takes string such as group number or process and searches the AccordionHeaders for a match
        If match is found, return the AccordionHeader element
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
        raise ElementNotFoundException("No header exists with the text \"%s\"." % searchText)

    def getBodyElements(self) -> list[WebElement]:
        self.waitUntilClickable(By.CLASS_NAME, "ia_accordionComponent__body")
        return self.waitForElements(By.CLASS_NAME, "ia_accordionComponent__body")

    def toggleBody(self, index: int) -> bool:
        return AccordionHeader(self.session, element=self.getHeaderElements()[index]).toggleExpansion()

    def expandAll(self) -> None:
        headersElements = self.getHeaderElements()
        headers = [AccordionHeader(self.session, element=element)
                    for element in headersElements]
        for header in headers:
            if not header.isExpanded():
                header.toggleExpansion()

    def expandBody(self, index: int) -> None:
        headersElements = self.getHeaderElements()
        headers = [AccordionHeader(self.session, element=element)
                   for element in headersElements]

        if not headers[index].isExpanded():

            headers[index].toggleExpansion()


class Button(PerspectiveComponent):
    pass


class CheckBox(PerspectiveComponent):
    def getValue(self) -> bool:
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
                checkbox = self.find_element_by_partial_class_name("ia_checkbox__uncheckedIcon")
                return False
            except NoSuchElementException:
                checkbox = self.find_element_by_partial_class_name("ia_checkbox__checkedIcon")
                return True
        except Exception as e:
            """ Raise the original exception """
            raise e

    def toggle(self) -> bool:
        if self.get_attribute('class') == 'ia_checkbox':
            self.click()
        else:
            self.find_element_by_class_name("ia_checkbox").click()

        return self.getValue()

    def setValue(self, value: bool) -> None:
        if self.getValue() != value:
            self.toggle()


class Dropdown(PerspectiveComponent):
    def getValue(self) -> WebElement:
        try:
            return self.waitForElement(By.CLASS_NAME, "ia_dropdown__valueSingle", timeout_in_seconds=1)
        except ElementNotFoundException:
            """Unable to find any value in dropdown"""
            return ''
        
    def getValues(self) -> list[WebElement]:
        try:
            return self.waitForElements(By.CLASS_NAME, "ia_dropdown__valuePill", timeout_in_seconds=1)
        except ElementNotFoundException:
            """There currently isn't any values"""
            return []
        except:
            raise ComponentInteractionException("Unable to identifies values in dropdown")

    def clearData(self) -> None:
        try:
            self.waitForElement(
                By.CLASS_NAME, "iaDropdownCommon_clear_value", timeout_in_seconds=1).click()
        except:
            """No value currently set"""
            pass
    
    def setRandomValue(self) -> None:
        dropdownOptions = self.getOptions()
        ind = random.randrange(0, len(dropdownOptions))
        dropdownOptions[ind].click()
        return
        
    def setValue(self, option_text: str) -> None:
        dropdownOptions = self.getOptions()

        for option in dropdownOptions:
            if option.text == option_text:
                option.click()
                return

    def getOptions(self) -> list[WebElement]:
        self.click()  
        return self.waitForElements(By.XPATH, "//*[contains(@class, 'popup')]//child::a", timeout_in_seconds=15)
    
    def getOptionTexts(self) -> list[str]:
        dropdown_options = self.getOptions()
        return [dropdown_option.text for dropdown_option in dropdown_options]

    def setValues(self, option_texts: list[str]) -> None:
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
        '''
        Currently an invisible dropdown in the filter does not have a distinct class like the Menu "item-invisible" class
        An invisible element will have a height of 0; checks the element's height.
        '''
        return self.get_attribute("height") != 0


class DateTimeInput(PerspectiveComponent):
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
        if self.tag_name == 'input':
            return str(self.get_attribute('value'))
        else:
            inputTag: WebElement = self.find_element_by_tag_name('input')
            return inputTag.get_attribute('value')
    
    def getDateTimeModal(self) -> PerspectiveElement:
        return PerspectiveElement(self.session, By.CLASS_NAME, self.MODAL_CLASS_NAME)

    def getDatePicker(self) -> PerspectiveElement:
        modal = self.getDateTimeModal()
        return PerspectiveElement(self.session, By.CLASS_NAME, self.DATE_PICKER_CLASS_NAME, parent=modal)
    
    def getTimePicker(self) -> PerspectiveElement:
        modal = self.getDateTimeModal()
        return PerspectiveElement(self.session, By.CLASS_NAME, self.TIME_PICKER_CLASS_NAME, parent=modal)

    def getYear(self) -> int:
        self.click()
        yearSelectWrapper = PerspectiveElement(self.session, By.CLASS_NAME, self.YEAR_SELECT_CLASS_NAME, parent=self.getDatePicker())
        yearSelect = Select(yearSelectWrapper.find_element_by_tag_name('select'))
        selectedOptionTag: WebElement = yearSelect.first_selected_option
        val = int(selectedOptionTag.text)
        self.click()
        return val
    
    def _setYear(self, year: int):
        yearSelectWrapper = PerspectiveElement(self.session, By.CLASS_NAME, self.YEAR_SELECT_CLASS_NAME, parent=self.getDatePicker())
        yearSelect: WebElement = yearSelectWrapper.find_element_by_tag_name('select')
        optionToClick: WebElement = yearSelect.find_element_by_css_selector("option[value='%s']" % str(year))
        yearSelect.click()
        optionToClick.click()
        yearSelect.click()

    def _setMonth(self, month: int):
        monthSelectWrapper = PerspectiveElement(self.session, By.CLASS_NAME, self.MONTH_SELECT_CLASS_NAME, parent=self.getDatePicker())
        monthSelect: WebElement = monthSelectWrapper.find_element_by_tag_name('select')
        optionToClick: WebElement = monthSelect.find_element_by_css_selector("option[value='%s']" % str(month))
        monthSelect.click()
        optionToClick.click()
        monthSelect.click()
    
    def _setDayInCurrentMonth(self, day: int):
        datePicker = self.getDatePicker()
        calendar: WebElement = datePicker.find_element_by_class_name('calendar')
        dayToClick: WebElement = calendar.find_element_by_css_selector("div.%s[data-day='%s']" % (self.DAY_TILE_CLASS_NAME, str(day)))
        dayToClick.click()
    
    def _setTime(self, hour: int, minute: int):
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
        timePicker.waitToClick(By.CLASS_NAME, self.HOUR_FIELD_CLASS_NAME)
        hoursField = TextBox(self.session, By.CLASS_NAME, self.HOUR_FIELD_CLASS_NAME, parent=timePicker)
        hoursField.click()
        hoursField.selectAll()
        for char in str(hour):
            time.sleep(0.2)
            hoursField.setText(char, replace=False)

        # Minutes
        timePicker.waitToClick(By.CLASS_NAME, self.MINUTE_FIELD_CLASS_NAME)
        minutesField = TextBox(self.session, By.CLASS_NAME, self.MINUTE_FIELD_CLASS_NAME, parent=timePicker)
        minutesField.click()
        minutesField.selectAll()
        for char in str(minute):
            time.sleep(0.2)
            minutesField.setText(char, replace=False)

        # AM/PM
        selectAmPmWrapper = PerspectiveElement(self.session, By.CLASS_NAME, self.AM_PM_PICKER_CLASS_NAME, parent=timePicker)
        selectAmPm: WebElement = selectAmPmWrapper.find_element_by_tag_name('select')
        optionToClick: WebElement = selectAmPm.find_element_by_css_selector("option[value='%s']" % AM_OR_PM)
        selectAmPm.click()
        optionToClick.click()
        selectAmPm.click()


    def setDateTime(self, dateTime: datetime):
        self.click()
        self._setTime(dateTime.hour, dateTime.minute)
        self._setYear(dateTime.year)
        self._setMonth(dateTime.month)
        self._setDayInCurrentMonth(dateTime.day)


class Icon(PerspectiveComponent):
    pass


class Label(PerspectiveComponent):
    def getText(self) -> str:
        return self.text


class MenuTree(PerspectiveComponent):
    menu_item_class = "menu-item"
    menu_label_class = "ia_menuTreeComponent__item__text"
    menu_invisible_class = "item-invisible"

    def getItems(self, include_invisible=False) -> list[WebElement]:
        try:
            menu_items_all = self.waitForElements(By.CLASS_NAME, self.menu_item_class)
            if include_invisible:
                return menu_items_all
            else:                
                menu_items_invisible = self.waitForElements(By.CLASS_NAME, self.menu_invisible_class)
                return [label for label in menu_items_all if label not in menu_items_invisible]
        except TimeoutException:
            raise ElementNotFoundException("Unable to find menu items")

    def getItemTexts(self, include_invisible=False) -> list[str]:
        try:
            menu_items = self.getItems(include_invisible=include_invisible)
            return [item.find_element(By.CLASS_NAME, self.menu_label_class).text for item in menu_items]
        except Exception as e:
            raise ElementNotFoundException("Unable to find menu items")

    def selectItem(self, name: str):
        menu_items = self.getItems()
        for item in menu_items:
            item_label: WebElement = item.find_element(By.CLASS_NAME, self.menu_label_class)
            if item_label.text == name:
                item.click()
                return
        raise ElementNotFoundException("Unable to find menu item: " + name)


class NumericInput(PerspectiveComponent):
    def getInputBox(self) -> WebElement:
        self.find_element_by_class_name("ia-numeral-input").click()
        return self.find_element_by_class_name("ia-numeral-input")

    def getInputState(self) -> InputState:
        self.getInputBox()
        try:
            invalidInputBox = self.find_element_by_partial_class_name("ia-numeral-input psc-")
        except (ElementNotFoundException, NoSuchElementException):
            return InputState.VALID
        except Exception as e:
            raise ComponentInteractionException("Unable to determine input state: %s" % e)
        
        if invalidInputBox:
            return InputState.INVALID
        return InputState.VALID

    def isInputValid(self):
        return self.getInputState() == InputState.VALID

    def send_keys(self, keys: str) -> None:
        self.getInputBox().send_keys(keys)

    def clearValue(self) -> None:
        self.send_keys(self.session.select_all_keys + Keys.DELETE)

    def setValue(self, value: Union[int, float], withSubmit: bool = False, replace: bool = True) -> None:
        if replace:
            self.clearValue()
        self.send_keys(str(value))

        if withSubmit:
            self.getInputBox().submit()
    
    def getValue(self, forceFloat: bool = False) -> Union[int, float]:
        if forceFloat is True:
            try:
                val = float(self.text)
            except ValueError:
                raise ValueError("The NumericInput has an invalid value: " + self.text)
        else:
            try:
                val = int(self.text)
            except ValueError:
                try:
                    val = float(self.text)
                except ValueError:
                    raise ValueError("The NumericInput has an invalid value: " + self.text)
        
        return val

    @property
    def text(self):
        if self.tag_name == "input":
            return self.get_attribute("value")
        else:
            inputTag: WebElement = self.find_element_by_tag_name("input")
            return inputTag.get_attribute("value")


class TabContainer(PerspectiveComponent):
    tab_class_name = "tab-menu-item"
    active_tab_class_name = "tab-active"
    tab_container_content_class_name = "ia_tabContainerComponent__content"

    def getTabs(self) -> list[WebElement]:
        return self.find_elements_by_partial_class_name(self.tab_class_name)

    def getTabNames(self) -> list[str]:
        tabs = self.getTabs()
        return [tab.text for tab in tabs]

    def getActiveTab(self) -> WebElement:
        return self.find_element_by_partial_class_name(self.active_tab_class_name)

    def switchToTab(self, name: str) -> WebElement:
        tabs = self.getTabs()
        for tab in tabs:
            if tab.text == name:
                tab.click()
                return tab
        raise ElementNotFoundException("No tab exists with the name \"%s\"." % name)

    def getContent(self) -> WebElement:
        containerContent = PerspectiveElement(self.session, self.find_element_by_partial_class_name(self.tab_container_content_class_name))
        elemInContainer = containerContent.getFirstChild()
        return elemInContainer


class _Pager(PerspectiveComponent):
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
        activePageElem = self.waitForElement(By.CLASS_NAME, self.active_page_class_name)
        return int(activePageElem.text)
    
    def nextPage(self) -> int:
        try:
            # If next button on screen
            nextButton: WebElement = self.find_element_by_class_name(self.next_page_class_name)
            if str(nextButton.get_attribute("class")).count(self.disbaled_next_prev_class_name) == 0:
                nextButton.click()
            else:
                raise ComponentInteractionException("Cannot go to next page, already on last page")
        except NoSuchElementException:
            # No next button - every page num should be showing
            pageElems = self.waitForElements(By.CLASS_NAME, self.page_class_name)
            curPageIndex = self.getCurrentPage() - 1
            if curPageIndex != len(pageElems) - 1:
                pageElems[curPageIndex + 1].click()
            else:
                raise ComponentInteractionException("Cannot go to next page, already on last page")
        return self.getCurrentPage()

    def prevPage(self) -> int:
        try:
            # If prev button on screen
            prevButton: WebElement = self.find_element_by_class_name(self.prev_page_class_name)
            if str(prevButton.get_attribute("class")).count(self.disbaled_next_prev_class_name) == 0:
                prevButton.click()
            else:
                raise ComponentInteractionException("Cannot go to previous page, already on first page")
        except NoSuchElementException:
            # No prev button - every page num should be showing
            pageElems = self.waitForElements(By.CLASS_NAME, self.page_class_name)
            curPageIndex = self.getCurrentPage() - 1
            if curPageIndex != 0:
                pageElems[curPageIndex - 1].click()
            else:
                raise ComponentInteractionException("Cannot go to previous page, already on first page")
        return self.getCurrentPage()
    
    def firstPage(self) -> None:
        try:
            # If first button on screen
            firstButton: WebElement = self.find_element_by_class_name(self.first_page_class_name)
            if str(firstButton.get_attribute("class")).count(self.disabled_first_last_class_name) == 0:
                firstButton.click()
            else:
                raise ComponentInteractionException("Already on first page")
        except NoSuchElementException:
            # No first button
            try:
                # If prev button on screen
                prevButton: WebElement = self.find_element_by_class_name(self.prev_page_class_name)
                while self.getCurrentPage() != 1:
                    prevButton.click()
            except NoSuchElementException:
                # No prev button - every page num should be showing
                if self.getCurrentPage() != 1:
                    pageElems = self.waitForElements(By.CLASS_NAME, self.page_class_name)
                    pageElems[0].click()
                else:
                    raise ComponentInteractionException("Already on first page")
    
    def lastPage(self) -> None:
        try:
            # If last button on screen
            lastButton: WebElement = self.find_element_by_class_name(self.last_page_class_name)
            if str(lastButton.get_attribute("class")).count(self.disabled_first_last_class_name) == 0:
                lastButton.click()
            else:
                raise ComponentInteractionException("Already on last page")
        except NoSuchElementException:
            # No last button
            try:
                # If next button on screen
                nextButton: WebElement = self.find_element_by_class_name(self.next_page_class_name)
                while str(nextButton.get_attribute("class")).count(self.disbaled_next_prev_class_name) == 0:
                    nextButton.click()
            except NoSuchElementException:
                # No next button - every page num should be showing
                if self.getCurrentPage() != 1:
                    pageElems = self.waitForElements(By.CLASS_NAME, self.page_class_name)
                    pageElems[-1].click()
                else:
                    raise ComponentInteractionException("Already on last page")

    def jumpToPage(self, page: int) -> None:
        try:
            # "Jump to" text field on screen
            jumpTextField: WebElement = self.waitForElement(By.CLASS_NAME, self.jump_field_class_name)
            jumpTextField.clear()
            jumpTextField.send_keys(str(page))
            jumpTextField.send_keys(Keys.ENTER)
        except:
            # No "Jump to" text field
            try:
                # Next and prev buttons on screen
                nextButton: WebElement = self.find_element_by_class_name(self.next_page_class_name)
                prevButton: WebElement = self.find_element_by_class_name(self.prev_page_class_name)
                curPage = self.getCurrentPage()
                while curPage != page:
                    if curPage < page:
                        nextButton.click()
                    elif curPage > page:
                        prevButton.click()
            except:
                # No next and prev buttons on scren - every page num should be showing
                pageElems: list[WebElement] = self.waitForElements(By.CLASS_NAME, self.page_class_name)
                for pageElem in pageElems:
                    if int(pageElem.text) == page:
                        pageElem.click()
                        break
           
        if self.getCurrentPage() != page:
            raise ComponentInteractionException("Table page index out of range.")
    
    def getNumPages(self) -> int:
        try:
            # If the "next" button is visible, not every page is showing in the pager
            self.find_element_by_class_name(self.next_page_class_name)
        except NoSuchElementException:
            # No next button - every page num should be showing
            pageElems = self.waitForElements(By.CLASS_NAME, self.page_class_name)
            return len(pageElems)
        START_PAGE = self.getCurrentPage()
        self.lastPage()
        NUM_PAGES = self.getCurrentPage()
        self.jumpToPage(START_PAGE)
        return NUM_PAGES

    def getPageSizeSelect(self) -> Select:
        selectParent: WebElement = self.find_element_by_class_name(self.page_size_div_class_name)
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
            raise ComponentInteractionException(f"No option exists to show {str(size)} items per page")
        

class Popup(PerspectiveElement):
    def __init__(self, session: Session, identifier: str = None) -> None:
        super().__init__(session, By.ID, "popup-%s" % identifier)

    def getRoot(self) -> WebElement:
        return self.parent.parent.parent

    def close(self) -> None:
        self.find_element_by_class_name("close-icon").click()


class TableRowGroup(PerspectiveElement):
    def getDataId(self) -> str:
        return self.get_attribute("data-column-id")


class TableCell(PerspectiveElement):
    def getDataId(self) -> str:
        return self.get_attribute("data-column-id")

    def getData(self) -> str:
        return self.find_element_by_class_name("content").text


class Table(PerspectiveComponent):
    header_cell_class_name = "ia_table__head__header__cell"
    row_group_class_name = "ia_table__body__rowGroup"
    cell_class_name = "ia_table__cell"
    table_filter_container_class_name = "ia_tableComponent__filterContainer"
    pager_class_name = "ia_pager"
    _pager = None

    def __init__(self, session: Session, locator: By = ..., identifier: str = None, element: WebElement = None, parent: WebElement = None, timeout_in_seconds=None):
        super().__init__(session, locator, identifier, element, parent, timeout_in_seconds)
        try:
            pagers = self.waitForElements(By.CLASS_NAME, self.pager_class_name, timeout_in_seconds=2)
            if pagers:
                self._pager = _Pager(self.session, element=pagers[0])
        except (ElementNotFoundException, NoSuchElementException):
            """ The table likely does not have a pager visible """

    # Start _Pager Methods
    def getCurrentPage(self) -> int:
        return self._pager.getCurrentPage() if self.hasPager() else 1

    def nextPage(self) -> int:
        if not self.hasPager():
            raise ComponentInteractionException("Page navigation is disabled for this table")
        return self._pager.nextPage()

    def prevPage(self) -> int:
        if not self.hasPager():
            raise ComponentInteractionException("Page navigation is disabled for this table")
        return self._pager.prevPage()

    def firstPage(self) -> None:
        if not self.hasPager():
            raise ComponentInteractionException("Page navigation is disabled for this table")
        self._pager.firstPage()

    def lastPage(self) -> None:
        if not self.hasPager():
            raise ComponentInteractionException("Page navigation is disabled for this table")
        self._pager.lastPage()

    def jumpToPage(self, page: int) -> None:
        if not self.hasPager():
            raise ComponentInteractionException("Page navigation is disabled for this table")
        self._pager.jumpToPage(page)

    def getNumPages(self) -> int:
        return self._pager.getNumPages() if self.hasPager() else 1

    def getPageSize(self) -> int:
        return self._pager.getPageSize() if self.hasPager() else len(self.waitForElements(By.CLASS_NAME, self.row_group_class_name))

    def setPageSize(self, size: int):
        if not self.hasPager():
            raise ComponentInteractionException("Setting the page size is disabled for this table")
        self._pager.setPageSize(size)
    # End _Pager Methods

    def getHeaders(self) -> list[TableCell]:
        headerElements = self.waitForElements(By.CLASS_NAME, self.header_cell_class_name)
        return [TableCell(self.session, element=element) for element in headerElements]

    def getDataColumnIds(self) -> list[str]:
        return [header.getDataId() for header in self.getHeaders()]

    def getRowCount(self) -> int:
        num_pages = self.getNumPages()
        num_rows = self.getPageSize()
        if num_pages > 1:
            self.lastPage()      
            last_rows = len(self.getRowGroups())
            self.firstPage()
        else:
            last_rows = len(self.getRowGroups())
        return ((num_pages - 1) * num_rows + last_rows)

    def getRowGroups(self) -> list[TableRowGroup]:
        rowGroupElements = self.waitForElements(By.CLASS_NAME, self.row_group_class_name)
        return [TableRowGroup(self.session, element=element) for element in rowGroupElements]

    def getRowData(self) -> list[list[TableCell]]:
        rowGroups = self.getRowGroups()

        rows = []
        for rowGroup in rowGroups:
            rowCells = [TableCell(self.session, element=element)
                        for element in rowGroup.find_elements_by_class_name(self.cell_class_name)]
            rows.append(rowCells)
        return rows
    
    def getColumnAsList(self, dataId: str=None, columnIndex: int=None) -> list[WebElement]:
        if dataId:
            return self.waitForElements(By.XPATH, ".//*[@class='tc ia_table__cell' and @data-column-id='%s']" % dataId, timeout_in_seconds=5)
        elif columnIndex:
            return self.waitForElements(By.XPATH, ".//*[@class='tc ia_table__cell' and @data-column-index='%s']" % columnIndex, timeout_in_seconds=5)
        else:
            raise ComponentInteractionException("Must provide a column selector dataId or columnIndex")

    def getColumnTextsAsList(self, dataId: str=None, columnIndex: int=None) -> list[str]:
        columnCells = self.getColumnAsList(dataId, columnIndex)
        return [cell.text for cell in columnCells]

    def getCurrentPageData(self) -> list[dict]:
        rowGroups = self.getRowData()
        rows = []

        for rowGroup in rowGroups:
            rowData = {}
            for cellElement in rowGroup:
                rowData[cellElement.getDataId()] = cellElement.getData()

            rows.append(rowData)

        return rows
    
    def getAllData(self) -> list[dict]:
        START_PAGE = self.getCurrentPage()
        self.firstPage()
        curPage = 1
        rows: list[dict] = []

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
        filterContainer: WebElement = self.find_element_by_class_name(self.table_filter_container_class_name)
        filterContainer.find_element_by_class_name("ia_inputField").click()
        filterInputBox: WebElement = filterContainer.find_element_by_class_name(
            "ia_inputField")
        filterInputBox.send_keys(keys)
    
    def hasPager(self) -> bool:
        return self._pager is not None

    def sortBy(self, columnId:str, direction:str = "up") -> None:
        column_id = f"div[data-column-id=\"{columnId}\""
        try:
            column = self.find_element_by_css_selector(column_id)
            up = Button(self.session, By.CLASS_NAME, "sort-up", parent=column)
            down = Button(self.session, By.CLASS_NAME, "sort-down", parent=column)
            up_classes = up.get_attribute("class")
            down_classes = down.get_attribute("class")

            if direction == 'up' and 'active' not in up_classes:
                up.click()
            elif direction == 'down' and 'active' not in down_classes:
                down.click()
        except ElementNotFoundException as e:
            raise e


class TextArea(PerspectiveComponent):
    def clearText(self) -> None:
        self.selectAll()
        self.send_keys(Keys.DELETE)
        
    def isReadonly(self) -> bool:
       return self.get_attribute("readonly") == "true"

    def setText(self, text: str, replace: bool = True) -> None:
        if replace:
            self.clearText()

        self.send_keys(str(text))


class TextBox(PerspectiveComponent):
    def clearText(self) -> None:
        self.selectAll()
        self.send_keys(Keys.DELETE)

    def setText(self, text: str, withSubmit: bool = False, replace: bool = True) -> None:
        if replace:
            self.clearText()
        self.send_keys(str(text))
        if withSubmit:
            self.submit()


class ToggleSwitch(PerspectiveComponent):
    def getValue(self) -> bool:
        track: WebElement = self.find_element_by_class_name("ia_toggleSwitch__track")
        return "--selected" in track.get_attribute("class")

    def toggle(self) -> bool:
        self.click()
        return self.getValue()

    def setValue(self, value: bool) -> None:
        if self.getValue() != value:
            self.toggle()


class View(PerspectiveElement):
    pass
