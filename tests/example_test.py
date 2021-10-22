import time, json
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import webelement
from perspective_automation.selenium import Session, Credentials
from perspective_automation.components import Label, TextBox, TextArea, Table, Button, CheckBox



def test_sampleTable():
    # Get user input for Work Order and Leg
    # ORDER_NUM = int(input("Enter the Sys ID (WRK_ORD_SYS_I) of a work order with a sample to send: "))
    # TANK_NUM = int(input("Enter the Sys ID (TNK_SYS_I) of the Tank with the samples for that work order: "))
    # TEST_PROCESS = str(input("Enter the test process for the sample you want to send: "))
    # TEST_CODE = str(input("Enter the test code for the sample you want to send: "))

    ORDER_NUM = 1990681
    TANK_NUM = 134
    TEST_PROCESS = "CUO"
    TEST_CODE = "TSO2F"


    BASE_URL = "https://lv1mesdevlap01.est1933.com:8043"
    PAGE_PATH = "/data/perspective/client/MES/component-test-fixture"
    CREDENTIALS = Credentials("RATester01", "N3verp@tch2021")
    session = Session(BASE_URL, PAGE_PATH, 20, credentials=CREDENTIALS, headless=False)
    session.login()

    viewPath = TextBox(session, By.ID, "viewPathTextField")
    viewPath.setText("Operations/Tasks/Body/Sample")

    viewParams = TextArea(session, By.ID, "viewParamsTextBox")
    # {   "TNK_SYS_I": 134,   "WRK_ORD_SYS_I": 1990681,   "sampleProcess": "CUO" }
    viewParams.setText(json.dumps({"WRK_ORD_SYS_I": ORDER_NUM,"TNK_SYS_I":TANK_NUM, "sampleProcess":TEST_PROCESS}))
    # Reset the focus off of the textArea
    viewPath.click()

    sampleTable = Table(session, By.ID, "taskSampleTable")
    # Wait for the table to load
    time.sleep(2)
    test_codes = sampleTable.getColumnAsList('LIMS_ACODE')
    rowIndex = None
    for index, test in enumerate(test_codes):
        if test == TEST_CODE:
            rowIndex = index
            break
    
    checkboxes: list[webelement.WebElement] = sampleTable.getColumnAsList('expandSubview')
    checkBox = CheckBox(session, By.CLASS_NAME, "ia_checkbox", parent=checkboxes[rowIndex])
    checkBox.setValue(True)

    time.sleep(5)
    # rowGroups = sampleTable.getRowGroups()
    # tableData = sampleTable.getCurrentPageData()

    # for index, row in enumerate(tableData):
    #     if row.get('Test') == TEST_CODE:
    #         rowGroups[index].

    # numberOfAdds = Label(session, By.ID, "numberOfAddsLabel")
    # startingAddCount = int(numberOfAdds.getText())

    # dropdown = Dropdown(session, By.ID, "tubCalculatorDropdown")
    # dropdown.setValue("Tub30")
    
    # inchesToAdd = NumericInput(session, By.ID, "inchesToAdd")
    # inchesToAdd.setValue(9999)
    # assert inchesToAdd.isInputValid() == False, "Input is considered valid when invalid is expected"
    # inchesToAdd.setValue(0.1)
    # assert inchesToAdd.isInputValid() == True, "Input is considered invalid when valid is expected"

    # calculateButton = Button(session, By.ID, "calculateAdditionButton")
    # calculateButton.click()

    # # Wait for data to process
    # time.sleep(3)
    # finalAddCount = int(numberOfAdds.getText())

    # assert finalAddCount > startingAddCount, "Final add count not updated"

    session.close()
    
if __name__ == "__main__":
    # "-s" tells pytest not to capture stdout/stdin
    # Use "-s" for all tests that require user input
    pytest.main(["-s", __file__])


