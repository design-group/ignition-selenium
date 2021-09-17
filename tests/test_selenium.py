import time
import platform
from selenium.webdriver.common.by import By
from perspective_automation.selenium import Session, Label, TextBox, TextArea, NumericInput, Dropdown, Button

def test_session():
    URL = "http://localhost/data/perspective/client/MES/component-test-fixture"
    CREDENTIALS = {"username":"RATester01", "password":"N3verp@tch2021"}
    session = Session(URL, 10, CREDENTIALS)
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
   test_session()



