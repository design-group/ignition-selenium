import time
from selenium.webdriver.common.by import By
from perspective_automation.selenium import Session
from perspective_automation.components import Dropdown, Table, View, TextBox, Button

def test_tableData():
    BASE_URL = "http://localhost"
    PAGE_PATH = "/data/perspective/client/MES"
    CREDENTIALS = {"username":"RATester01", "password":"N3verp@tch2021"}
    session = Session(BASE_URL, PAGE_PATH, 10, CREDENTIALS)
    session.login()

    orderTable = Table(session, By.ID, "Operations.Orders.Embedded Views.Table")
    pageSettings = View(session, By.ID, "Operations.Orders.Embedded Views.PageSettings")
    pageSettingsTextFilter = TextBox(session, identifier="text-field", parent=pageSettings)
    pageSettingsTextFilter.setText("BLEND OTS")

    orderFilterIcon = Button(session, By.ID, "orderFilterIcon", parent=pageSettings)
    orderFilterIcon.click()

    orderFilterPopup = View(session, By.ID, "Operations.Orders.Embedded Views.Filters")
    areaDropdown = Dropdown(session, By.ID, "areaDropdown", parent=orderFilterPopup)
    areaDropdown.setValue("Blending")
    print(1)




    # //*[@id='Operations.Orders.Embedded Views.Table']//*[contains(@class, 'ia_table__body__rowGroup')]
    # //*[@id,'Operations.Orders.Embedded Views.Table']//*[@class, 'ia_table__body__rowGroup']
if __name__ == "__main__":
   test_tableData()



