
from enum import Enum
from typing import Union

from selenium.common.exceptions import NoSuchElementException, TimeoutException

from perspective_automation.perspective import (Component,
                                                ComponentInteractionException,
                                                PerspectiveComponent,
                                                PerspectiveElement,
                                                ElementNotFoundException)
from perspective_automation.selenium import Session, SelectAllKeys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement


class InputState(Enum):
    INVALID = False
    VALID = True

class AccordionHeaderType(Enum):
    TEXT = 1
    VIEW = 2

class PagerType(Enum):
    """
    Denotes the type of pager. Possible values:
    - `SIMPLE`: A pager that does not have Next/Previous buttons, First/Last buttons, and the "Jump to" text field. Usually has less than 10 pages.
    - `ROBUST`: A pager that has Next/Previous buttons, First/Last buttons, and the "Jump to" text field. Usually has at least 10 pages.
    """
    SIMPLE = 1
    ROBUST = 2

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

    def getHeaderText(self) -> str:
        """
        Checks if the Accordion Header is a text header, and if so, returns the text inside.
        """
        if self.getHeaderType() != AccordionHeaderType.TEXT:
            raise ComponentInteractionException("Cannot get text of a non-text accordion header.")
        return self.text

class Accordion(PerspectiveComponent):
    def getHeaderElements(self) -> list[WebElement]:
        return self.waitForElements(By.CLASS_NAME, "ia_accordionComponent__header")

    def getAccordianHeaders(self) -> list[AccordionHeader]:
        return [AccordionHeader(self.session, element) for element in self.getHeaderElements()]

    def getBodyElements(self) -> list[WebElement]:
        return self.waitForElements(By.CLASS_NAME, "ia_accordionComponent__body")

    def toggleBody(self, index: int) -> bool:
        return AccordionHeader(self.session, self.getHeaderElements()[index]).toggleExpansion()

    def expandBody(self, index: int) -> None:
        headersElements = self.getHeaderElements()
        headers = [AccordionHeader(self.session, element)
                   for element in headersElements]

        if not headers[index].isExpanded():
            headers[index].toggleExpansion()

class Button(PerspectiveComponent):
    pass

class CheckBox(PerspectiveComponent):
    def getValue(self) -> bool:
        checkboxId = self.find_element_by_class_name(
            "icon").get_attribute("id")
        checkboxState = {
            "check_box": True,
            "check_box_outline_blank": False
        }
        return checkboxState.get(checkboxId)

    def toggle(self) -> bool:
        self.find_element_by_class_name("ia_checkbox").click()
        return self.getValue()

    def setValue(self, value: bool) -> None:
        if self.getValue() != value:
            self.toggle()

class Dropdown(PerspectiveComponent):
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

    def setValue(self, option_text: str) -> None:
        self.click()
        dropdownOptions = self.waitForElements(By.XPATH, "//*[contains(@class, 'ia_dropdown__option')]")

        for option in dropdownOptions:
            if option.text == option_text:
                option.click()
                return

    def setValues(self, option_texts: list[str]) -> None:
        if not "iaDropdownCommon_multi-select" in self.get_attribute("class"):
            raise ComponentInteractionException("Dropdown is not multi-select")

        currentValues = self.getValues()
        for value in currentValues:
            option_texts.remove(value.text)

        for option in option_texts:
            self.click()
            optionAdded = False
            option_elements = self.waitForElements(By.XPATH, "//*[contains(@class, 'ia_dropdown__option')]")
            for option_element in option_elements:
                if option_element.text == option:
                    optionAdded = True
                    option_element.click()
                    break

            if not optionAdded:
                raise ComponentInteractionException(
                    "Dropdown Value Not Present: %s" % option)

class Label(PerspectiveComponent):
    def getText(self) -> str:
        return self.text

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

class Popup(Component):
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

    def getPagerType(self) -> PagerType:
        centerElem = self.waitForElement(By.CLASS_NAME, 'center')
        return PagerType.ROBUST if str(centerElem.get_attribute('class')).count('auto-margin-right') == 0 else PagerType.SIMPLE

    def getCurrentPage(self) -> int:
        activePageElem = self.waitForElement(By.CLASS_NAME, self.active_page_class_name)
        return int(activePageElem.text)
    
    def nextPage(self) -> int:
        if self.getPagerType() == PagerType.SIMPLE:
            # < 10 pages
            pageElems = self.waitForElements(By.CLASS_NAME, self.page_class_name)
            curPageIndex = self.getCurrentPage() - 1
            if curPageIndex != len(pageElems) - 1:
                pageElems[curPageIndex + 1].click()
            else:
                """Cannot go to next page, already on last page"""
        else:
            # >= 10 pages
            nextButton = self.waitForElement(By.CLASS_NAME, self.next_page_class_name)
            if str(nextButton.get_attribute("class")).count(self.disbaled_next_prev_class_name) == 0:
                nextButton.click()
            else:
                """Cannot go to next page, already on last page"""
        return self.getCurrentPage()

    def prevPage(self) -> int:
        if self.getPagerType() == PagerType.SIMPLE:
            # < 10 pages
            pageElems = self.waitForElements(By.CLASS_NAME, self.page_class_name)
            curPageIndex = self.getCurrentPage() - 1
            if curPageIndex != 0:
                pageElems[curPageIndex - 1].click()
            else:
                """Cannot go to previous page, already on first page"""
        else:
            # >= 10 pages
            prevButton = self.waitForElement(By.CLASS_NAME, self.prev_page_class_name)
            if str(prevButton.get_attribute("class")).count(self.disbaled_next_prev_class_name) == 0:
                prevButton.click()
            else:
                """Cannot go to previous page, already on first page"""
        return self.getCurrentPage()
    
    def firstPage(self) -> None:
        if self.getPagerType() == PagerType.SIMPLE:
            # < 10 pages
            if self.getCurrentPage() != 1:
                pageElems = self.waitForElements(By.CLASS_NAME, self.page_class_name)
                pageElems[0].click()
            else:
                """Already on first page"""
        else:
            # >= 10 pages
            firstButton = self.waitForElement(By.CLASS_NAME, self.first_page_class_name)
            if str(firstButton.get_attribute("class")).count(self.disabled_first_last_class_name) == 0:
                firstButton.click()
            else:
                """Already on first page"""
    
    def lastPage(self) -> None:
        if self.getPagerType() == PagerType.SIMPLE:
            # < 10 pages
            pageElems = self.waitForElements(By.CLASS_NAME, self.page_class_name)
            if self.getCurrentPage() != len(pageElems):
                pageElems[-1].click()
            else:
                """Already on last page"""
        else:
            # >= 10 pages
            lastButton = self.waitForElement(By.CLASS_NAME, self.last_page_class_name)
            if str(lastButton.get_attribute("class")).count(self.disabled_first_last_class_name) == 0:
                lastButton.click()
            else:
                """Already on last page"""

    def jumpToPage(self, page: int) -> None:
        if self.getPagerType() == PagerType.SIMPLE:
            # < 10 pages
            pageElems: list[WebElement] = self.waitForElements(By.CLASS_NAME, self.page_class_name)
            for pageElem in pageElems:
                if int(pageElem.text) == page:
                    pageElem.click()
                    break
        else:
            # >= 10 pages
            jumpTextField: WebElement = self.waitForElement(By.CLASS_NAME, self.jump_field_class_name)
            jumpTextField.clear()
            jumpTextField.send_keys(str(page))
            jumpTextField.send_keys(Keys.ENTER)
           
        if self.getCurrentPage() != page:
            raise ComponentInteractionException("Table page index out of range.")
            
    # TODO: Get/Set page size

    # TODO: Get number of pages

    # TODO: Determine pager visibility
        

class Table(PerspectiveComponent):
    header_cell_class_name = "ia_table__head__header__cell"
    row_group_class_name = "ia_table__body__rowGroup"
    cell_class_name = "ia_table__cell"
    table_filter_container_class_name = "ia_tableComponent__filterContainer"
    pager_class_name = "ia_pager"
    _pager = None

    def __init__(self, session: Session, locator: By = ..., identifier: str = None, element: WebElement = None, parent: WebElement = None, timeout_in_seconds=None):
        super().__init__(session, locator, identifier, element, parent, timeout_in_seconds)
        self._pager = _Pager(self.session, element=self.waitForElement(By.CLASS_NAME, self.pager_class_name, timeout_in_seconds))

    # _Pager Methods
    def getCurrentPage(self) -> int:
        return self._pager.getCurrentPage()
    def nextPage(self) -> int:
        return self._pager.nextPage()
    def prevPage(self) -> int:
        return self._pager.prevPage()
    def firstPage(self) -> None:
        return self._pager.firstPage()
    def lastPage(self) -> None:
        return self._pager.lastPage()
    def jumpToPage(self, page: int) -> None:
        return self._pager.jumpToPage(page)

    def getHeaders(self) -> list[TableCell]:
        headerElements = self.waitForElements(By.CLASS_NAME, self.header_cell_class_name)
        return [TableCell(self.session, element).getDataId() for element in headerElements]

    def getRowGroups(self) -> list[TableRowGroup]:
        rowGroupElements = self.waitForElements(By.CLASS_NAME, self.row_group_class_name)
        return [TableRowGroup(self.session, element) for element in rowGroupElements]

    def getRowData(self) -> list[list[TableCell]]:
        rowGroups = self.getRowGroups()

        rows = []
        for rowGroup in rowGroups:
            rowCells = [TableCell(self.session, element)
                        for element in rowGroup.find_elements_by_class_name(self.cell_class_name)]
            rows.append(rowCells)
        return rows

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

            # temp
            print(f"Page {curPage}")

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

    def filterTable(self, keys: str) -> None:
        filterContainer: WebElement = self.find_element_by_class_name(self.table_filter_container_class_name)
        filterContainer.find_element_by_class_name("ia_inputField").click()
        filterInputBox: WebElement = filterContainer.find_element_by_class_name(
            "ia_inputField")
        filterInputBox.send_keys(keys)


class TextArea(PerspectiveComponent):
    def clearText(self) -> None:
        self.selectAll()
        self.send_keys(Keys.DELETE)

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

class View(Component):
    pass
