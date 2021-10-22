import time, json
import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from perspective_automation.perspective import PerspectiveElement
from perspective_automation.selenium import Session, Credentials
from perspective_automation.components import Label, View, TextBox, TextArea, Table, Button, CheckBox, Icon



def test_sampleTable():
    # Get user input for Work Order and Leg
    # ORDER_NUM = int(input("Enter the Sys ID (WRK_ORD_SYS_I) of a work order with a sample to send: "))
    # TANK_NUM = int(input("Enter the Sys ID (TNK_SYS_I) of the Tank with the samples for that work order: "))

    ORDER_NUM = 1990681
    TANK_NUM = 134

    BASE_URL = "https://lv1mesdevlap01.est1933.com:8043"
    PAGE_PATH = "/data/perspective/client/MES/component-test-fixture"
    CREDENTIALS = Credentials("RATester01", "N3verp@tch2021")
    with Session(BASE_URL, PAGE_PATH, 20, credentials=CREDENTIALS, headless=False) as session:
        viewPath = TextBox(session, By.ID, "viewPathTextField")
        viewPath.setText("Operations/Tasks/Body/Sample")

        viewParams = TextArea(session, By.ID, "viewParamsTextBox")
        # {   "TNK_SYS_I": 134,   "WRK_ORD_SYS_I": 1990681,   "sampleProcess": "CUO" }
        viewParams.setText(json.dumps({"WRK_ORD_SYS_I": ORDER_NUM,"TNK_SYS_I":TANK_NUM}))
        # Reset the focus off of the textArea
        viewPath.click()

        # Show all samples in table
        sampleView = View(session, element=session.waitForElement("Operations.Tasks.Body.Sample", By.ID))
        showAllToggle: PerspectiveElement = sampleView.find_element_by_class_name("ia_toggleSwitch")
        showAllToggle.click()

        # Get table reference and wait for complete loading
        sampleTable = Table(session, By.ID, "taskSampleTable", parent=sampleView)

        mes_status_column = sampleTable.getColumnTextsAsList('mesStatus')

        readySampleIndex = None
        for index, status in enumerate(mes_status_column):
            if status in ['', 'Delivered']:
                readySampleIndex = index
                break
        if not readySampleIndex:
            raise Exception("Could not find a sample that is ready to send")
        
        checkboxes = sampleTable.getColumnAsList('selected')
        # Select checkbox column:
        checkboxes[readySampleIndex].click()

        # Set the checkbox to true
        checkBox = CheckBox(session, By.CLASS_NAME, "ia_checkbox", parent=checkboxes[readySampleIndex])
        checkBox.click()
        time.sleep(1)

       # Click the "Request Selected" button to re-send the requested sample
        requestButton = Button(session, By.ID, "requestSampleButton")
        requestButton.click()
        time.sleep(1)

        # DockedView class not yet implemented in perspective_automation
        # View is fine in this case
        dockedView = View(session, By.ID, "General.Docked Input.Docked Container")

        # Verify label
        label = Label(session, By.CLASS_NAME, "ia_labelComponent", parent=dockedView)
        assert str(label.text).count("Please Enter:") > 0
        
        # Verify buttons
        buttonElems: list[PerspectiveElement] = dockedView.find_elements_by_tag_name("button")
        buttons: list[Button] = list(map(lambda buttonElem: Button(session, element=buttonElem), buttonElems))
        visibleButtons = list(filter(lambda button: button.is_displayed(), buttons))
        assert len(visibleButtons) == 2
        assert visibleButtons[0].text == "Close"
        assert visibleButtons[1].text == "Submit"

        # Submit the sample request
        visibleButtons[1].click()
        time.sleep(1)

        # Verify label
        label = Label(session, By.ID, "loaderTextLabel", parent=dockedView)
        assert str(label.text).count("Sending Samples for %s..." % ORDER_NUM) > 0

        loaderStatusIcon = Icon(session, By.ID, "loaderStatusIcon")

        try:
            loaderStatusIcon.waitForElement(By.ID, "check", timeout_in_seconds=60)
        except TimeoutException:
            loaderStatusIcon.waitForElement(By.ID, "warning", timeout_in_seconds=60)

        except Exception as e:
            raise e

    
if __name__ == "__main__":
    # "-s" tells pytest not to capture stdout/stdin
    # Use "-s" for all tests that require user input
    pytest.main(["-s", __file__])


