
from perspective_automation.perspective import Component, PerspectiveComponent, PerspectiveElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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
        self.element.clear()
    
    def setValue(self, option_text):
        self.element.click()
        dropdownOptions = self.session.waitForElement("ia_dropdown__option", By.CLASS_NAME, multiple=True)

        for option in dropdownOptions:
            if option.text == option_text:
                option.click()
                return
        

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
        self.getRowGroups()[rowIndex].doubleClick()

    def filterTable(self, keys):
        filterContainer = self.getElement("ia_tableComponent__filterContainer", root_element=self.element)
        self.getElement("ia_inputField", root_element=filterContainer).click()
        filterInputBox = self.getElement("ia_inputField", root_element=filterContainer)
        filterInputBox.send_keys(keys)

class View(Component):
    pass