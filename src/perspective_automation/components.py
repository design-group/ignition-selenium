
from enum import Enum
from typing import Union

from perspective_automation.perspective import (Component,
                                                ComponentInteractionException,
                                                PerspectiveComponent,
                                                PerspectiveElement)
from perspective_automation.selenium import Session
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement


class AccordionHeaderType(Enum):
    TEXT: 1
    VIEW: 2


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
        return self.waitForElements(By.CLASS_NAME, "ia_dropdown__valuePill", timeout_in_seconds=1)

    def clearData(self) -> None:
        try:
            self.waitForElement(
                By.CLASS_NAME, "iaDropdownCommon_clear_value", timeout_in_seconds=1).click()
        except:
            """No value currently set"""
            pass

    def setValue(self, option_text: str) -> None:
        self.click()
        dropdownOptions = self.waitForElements(
            By.CLASS_NAME, "ia_dropdown__option")

        for option in dropdownOptions:
            if option.text == option_text:
                option.click()
                return

    def setValues(self, option_texts: list[str]) -> None:
        if not "iaDropdownCommon_multi-select" in self.get_attribute("class"):
            raise ComponentInteractionException("Dropdown is not multi-select")

        currentValues = self.getValues()
        if currentValues:
            for value in currentValues:
                option_texts.remove(value.text)

        for option in option_texts:
            self.click()
            optionAdded = False
            option_elements = self.waitForElements(
                By.CLASS_NAME, "ia_dropdown__option")
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

    def send_keys(self, keys: str) -> None:
        self.getInputBox().send_keys(keys)

    def clearValue(self) -> None:
        self.send_keys(self.session.select_all_keys)
        self.send_keys(Keys.DELETE)

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

class Table(PerspectiveComponent):
    header_cell_class_name = "ia_table__head__header__cell"
    row_group_class_name = "ia_table__body__rowGroup"
    cell_class_name = "ia_table__cell"
    table_filter_container_class_name = "ia_tableComponent__filterContainer"

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

    def getData(self) -> list[dict]:
        rowGroups = self.getRowData()
        rows = []

        for rowGroup in rowGroups:
            rowData = {}
            for cellElement in rowGroup:
                rowData[cellElement.getDataId()] = cellElement.getData()

            rows.append(rowData)

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
