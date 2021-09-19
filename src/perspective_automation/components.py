
from selenium.webdriver.remote.webelement import WebElement
from perspective_automation.perspective import Component, PerspectiveComponent, PerspectiveElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class ComponentInteractionException(Exception):
    pass

class View(Component):
    pass

class Label(PerspectiveComponent):
    def getText(self):
        return self.element.text

class TextBox(PerspectiveComponent):
    def clearText(self):
        self.selectAll()
        self.send_keys(Keys.DELETE)

    def setText(self, text, withSubmit=False, replace=True):
        if replace:
            self.clearText()
        self.send_keys(str(text))
        if withSubmit:
            self.element.submit()

class TextArea(PerspectiveComponent):
    def clearText(self):
        self.selectAll()
        self.send_keys(Keys.DELETE)

    def setText(self, text, replace=True):
        if replace:
            self.clearText()

        self.send_keys(str(text))

class CheckBox(PerspectiveComponent):
    def getValue(self):
        checkboxId = self.element.find_element_by_class_name("icon").get_attribute("id")
        checkboxState = {
            "check_box": True,
            "check_box_outline_blank": False
        }
        return checkboxState.get(checkboxId)

    def toggle(self):
        self.element.find_element_by_class_name("ia_checkbox").click()

    def setValue(self, value: bool):
        if self.getValue() != value:
            self.toggle()

class NumericInput(PerspectiveComponent):
    def getInputBox(self):
        self.element.find_element_by_class_name("ia-numeral-input").click()
        return self.element.find_element_by_class_name("ia-numeral-input")

    def send_keys(self, keys):
        self.getInputBox().send_keys(keys)
    
    def clearValue(self):
        self.send_keys(self.session.select_all_keys)
        self.send_keys(Keys.DELETE)

    def setValue(self, value, withSubmit=False, replace=True):
        if replace:
            self.clearValue()

        self.send_keys(str(value)) 

        if withSubmit:
            self.getInputBox().submit()


class Dropdown(PerspectiveComponent):
    def clearData(self):
        self.session.waitForElement("iaDropdownCommon_clear_value", By.CLASS_NAME, root_element=self).click()
    
    def setValue(self, option_text):
        self.element.click()
        dropdownOptions = self.session.waitForElement("ia_dropdown__option", By.CLASS_NAME, multiple=True)

        for option in dropdownOptions:
            if option.text == option_text:
                option.click()
                return
    
    def setValues(self, option_texts):
        if not "iaDropdownCommon_multi-select" in self.element.get_attribute("class"):
            raise ComponentInteractionException("Dropdown is not multi-select")

        self.clearData()
        for option in option_texts:
            self.element.click()
            optionAdded = False
            option_elements = self.session.waitForElement("ia_dropdown__option", By.CLASS_NAME, multiple=True)
            for option_element in option_elements:
                if option_element.text == option:
                    optionAdded = True
                    option_element.click()
                    break
            
            if not optionAdded:
                raise ComponentInteractionException("Dropdown Value Not Present: %s" % option)
        

class Button(PerspectiveComponent):
    def click(self):
        self.element.click()

class TableRowGroup(PerspectiveElement):
    def getDataId(self):
        return self.get_attribute("data-column-id")

class TableCell(PerspectiveElement):
    def getDataId(self):
        return self.get_attribute("data-column-id")
    
    def getData(self):
        return self.find_element_by_class_name("content").text
    

class Table(PerspectiveComponent):
    header_cell_class_name = "ia_table__head__header__cell"
    row_group_class_name = "ia_table__body__rowGroup"
    cell_class_name = "ia_table__cell"
    table_filter_container_class_name = "ia_tableComponent__filterContainer"

    def getHeaders(self):
        headerElements = self.getElement(self.header_cell_class_name, multiple=True, root_element=self.element)
        return [TableCell(self.session, element).getDataId() for element in headerElements]

    def getRowGroups(self):        
        rowGroupElements = self.getElement(self.row_group_class_name, multiple=True, root_element=self.element)
        return [TableRowGroup(self.session, element) for element in rowGroupElements]


    def getRowData(self):
        rowGroups = self.getRowGroups()

        rows = []
        for rowGroup in rowGroups:
            rowCells = [TableCell(self.session, element) for element in rowGroup.find_elements_by_class_name(self.cell_class_name)]
            rows.append(rowCells)
        return rows

    def getData(self):
        rowGroups = self.getRowData()
        rows = []

        for rowGroup in rowGroups:
            rowData = {}
            for cellElement in rowGroup:
                rowData[cellElement.getDataId()] = cellElement.getData()

            rows.append(rowData)

        return rows
    
    def clickOnRow(self, rowIndex):
        self.getRowGroups()[rowIndex].click()
    
    def doubleClickOnRow(self, rowIndex):
        rowGroups = self.getRowGroups()

        if rowIndex > len(rowGroups):
            raise ComponentInteractionException("Click index %s out of range: %s" % (rowIndex, len(rowGroups)))

        rowGroups[rowIndex].doubleClick()

    def filterTable(self, keys):
        filterContainer = self.getElement(self.table_filter_container_class_name, root_element=self)
        self.getElement("ia_inputField", root_element=filterContainer).click()
        filterInputBox = self.getElement("ia_inputField", root_element=filterContainer)
        filterInputBox.send_keys(keys)


class AccordionHeader(PerspectiveElement):
    def getHeaderType(self):
        if self.find_element_by_class_name("ia_accordionComponent__header__text"):
            return "text"
        elif self.find_element_by_class_name("ia_accordionComponent__header__view"):
            return "view"
        else:
            return None
    
    def isExpanded(self):
        return "expanded" in self.find_element_by_partial_classname("ia_accordionComponent__header__chevron").get_attribute("class")
    
    def toggleExpansion(self):
        self.element.click()

class Accordion(PerspectiveComponent):
    def getHeaderElements(self):
        return self.getElement("ia_accordionComponent__header", multiple=True, root_element=self, strict_identifier=True)

    def getAccordianHeaders(self):
        return [AccordionHeader(self.session, element) for element in self.getHeaderElements()]

    def getBodyElements(self):
        return self.getElement("ia_accordionComponent__body", multiple=True, root_element=self, strict_identifier=True)

    def toggleBody(self, index):
        AccordionHeader(self.session, self.getHeaderElements()[index]).toggleExpansion()

    def expandBody(self, index):
        headersElements = self.getHeaderElements()
        headers = [AccordionHeader(self.session, element) for element in headersElements]

        if not headers[index].isExpanded():
            headers[index].toggleExpansion()