import time
from selenium.webdriver.common.by import By
from perspective_automation.selenium import Session, Credentials
from perspective_automation.components import Label, TextBox, TextArea, NumericInput, Dropdown, Button

def test_tubCalculator():
    BASE_URL = "http://localhost"
    PAGE_PATH = "/data/perspective/client/MES/component-test-fixture"
    CREDENTIALS = Credentials("RATester01", "N3verp@tch2021")
    session = Session(BASE_URL, PAGE_PATH, 10, CREDENTIALS)
    session.login()

    viewPath = TextBox(session, By.ID, "viewPathTextField")
    viewPath.setText("Operations/Calculators/Tub")

    viewParams = TextArea(session, By.ID, "viewParamsTextBox")
    viewParams.setText({"WRK_ORD_LEG_N": 5,"WRK_ORD_SYS_I": 1958622,"stat": "IP" })
    
    numberOfAdds = Label(session, By.ID, "numberOfAddsLabel")
    startingAddCount = int(numberOfAdds.getText())

    dropdown = Dropdown(session, By.ID, "tubCalculatorDropdown")
    dropdown.setValue("Tub30")

    
    inchesToAdd = NumericInput(session, By.ID, "inchesToAdd")
    inchesToAdd.setValue(0.1)

    calculateButton = Button(session, By.ID, "calculateAdditionButton")
    calculateButton.click()

    # Wait for data to process
    time.sleep(3)
    finalAddCount = int(numberOfAdds.getText())

    if finalAddCount > startingAddCount:
        print("Test success!")

if __name__ == "__main__":
   test_tubCalculator()



