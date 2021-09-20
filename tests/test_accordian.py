import time
from selenium.webdriver.common.by import By
from perspective_automation.selenium import Session, Credentials
from perspective_automation.components import View, Table, TextBox, Accordion

def test_tableData():
    BASE_URL = "http://localhost"
    PAGE_PATH = "/data/perspective/client/MES"
    CREDENTIALS = Credentials("RATester01", "N3verp@tch2021")
    session = Session(BASE_URL, PAGE_PATH, 10, CREDENTIALS)
    session.login()

    orderTable = Table(session, By.ID, "Operations.Orders.Embedded Views.Table")
    
    pageSettings = View(session, By.ID, "Operations.Orders.Embedded Views.PageSettings")
    pageSettingsTextFilter = TextBox(session, identifier="text-field", parent=pageSettings)
    pageSettingsTextFilter.setText("Base Blend")
    
    orderTable.doubleClickOnRow(0)

    jobAccordian = Accordion(session, By.ID, "Operations.Jobs.Overview")
    jobAccordian.toggleBody(4)
    

    time.sleep(5)
if __name__ == "__main__":
   test_tableData()