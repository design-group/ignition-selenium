import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from perspective_automation.selenium import Session, Credentials
from perspective_automation.components import Button, Label, Table, TextArea, TextBox, View

@pytest.fixture(name="params")
def getParamsFromUser() -> str:
    """
    Gets view params from user input, and returns them as a JSON string. 
    
    The following params are necessary for this test:
    - WRK_ORD_SYS_I
    - TNK_SYS_I
    """
    params = {}

    print("")  # for formatting within pytest
    params["WRK_ORD_SYS_I"] = input("Enter a WRK_ORD_SYS_I that has a sample whose 'MES Status' is 'Requested': ")
    params["TNK_SYS_I"] = input("Enter the TNK_SYS_I of the tank that this sample is part of: ")

    # As of test creation, these the following two work order and tank combinations are suitable for testing.
    # Use one of these and comment out the above if you would rather not have user input.

    # Example 1
    # params["WRK_ORD_SYS_I"] = 1990681
    # params["TNK_SYS_I"] = 134

    # Example 2
    # params["WRK_ORD_SYS_I"] = 1988716
    # params["TNK_SYS_I"] = 235187

    return str(params)

def test_sampleReprintPrompt(params: str):
    BASE_URL = "http://localhost:4000"
    PAGE_PATH = "/data/perspective/client/MES/component-test-fixture"
    CREDENTIALS = Credentials("RATester01", "N3verp@tch2021")
    session = Session(BASE_URL, PAGE_PATH, wait_timeout_in_seconds=20, credentials=CREDENTIALS, headless=False)
    session.login()
    
    viewPath = TextBox(session, By.ID, "viewPathTextField")
    viewPath.setText("Operations/Tasks/Body/Sample")

    viewParams = TextArea(session, By.ID, "viewParamsTextBox")
    viewParams.setText(params)

    # Show all samples in table
    sampleView = View(session, element=session.waitForElement("Operations.Tasks.Body.Sample", By.ID))
    showAllToggle: WebElement = sampleView.find_element_by_class_name("ia_toggleSwitch")
    showAllToggle.click()
    time.sleep(3)  # give time to load

    # Get table reference and wait for complete loading
    sampleTable = Table(session, By.ID, "taskSampleTable", parent=sampleView)

    # Get cells of "MES Status" column
    MES_STATUS_DATA_COLUMN_ID = "mesStatus"
    MES_STATUS_SELECTOR = f"div[data-column-id=\"{MES_STATUS_DATA_COLUMN_ID}\""
    mesStatusCells: list[WebElement] = sampleTable.find_elements_by_css_selector(MES_STATUS_SELECTOR)[1:]

    # Verify there is at least one sample with an MES Status of "Requested"
    # and save the index of the first one we find
    requestedSampleIndex = -1
    for i in range(0, len(mesStatusCells)):
        if mesStatusCells[i].text == "Requested":
            requestedSampleIndex = i
            break
    if requestedSampleIndex == -1:
        raise Exception("Could not find sample with MES Status 'Requested'")
    
    # Select the sample at requestedSampleIndex
    SELECT_DATA_COLUMN_ID = "selected"
    SELECT_SELECTOR = f"div[data-column-id=\"{SELECT_DATA_COLUMN_ID}\""
    selectCells: list[WebElement] = sampleTable.find_elements_by_css_selector(SELECT_SELECTOR)[1:]
    requestedSampleSelectCell = selectCells[requestedSampleIndex]
    requestedSampleSelectCell.click()
    checkbox: WebElement = requestedSampleSelectCell.find_element_by_class_name("ia_checkbox")
    checkbox.click()
    time.sleep(0.5)

    # Click the "Request Selected" button to re-send the requested sample
    requestButton = Button(session, By.ID, "requestSampleButton")
    requestButton.click()
    time.sleep(1)

    # DockedView class not yet implemented in perspective_automation
    # View is fine in this case
    dockedView = View(session, By.ID, "General.Docked Input.Docked Container")

    # Verify label
    label = Label(session, By.CLASS_NAME, "ia_labelComponent", parent=dockedView)
    assert str(label.text).count("Are you sure you want to re-send the following non-delivered samples:") > 0
    
    # Verify buttons
    buttonElems: list[WebElement] = dockedView.find_elements_by_tag_name("button")
    buttons: list[Button] = list(map(lambda buttonElem: Button(session, element=buttonElem), buttonElems))
    visibleButtons = list(filter(lambda button: button.is_displayed(), buttons))
    assert len(visibleButtons) == 2
    assert visibleButtons[0].text == "Close"
    assert visibleButtons[1].text == "Submit"


if __name__ == "__main__":
    pytest.main(["-s", __file__])