import pytest
import time
from selenium.webdriver.common.by import By
from perspective_automation.selenium import Session, Credentials
from perspective_automation.components import Menu, View
# import perspective_automation

def test_menu_instance_methods():
    BASE_URL = "http://localhost:4000"
    PAGE_PATH = "/data/perspective/client/MES/"
    CREDENTIALS = Credentials("RATester01", "N3verp@tch2021")
    SLEEP_TIME = 1

    session = Session(BASE_URL, PAGE_PATH, 20, credentials=CREDENTIALS, headless=False)
    time.sleep(SLEEP_TIME)
    session.login()

    # Click to open docked menu
    header = View(session, By.ID, "General.Headers.Default")
    sideMenuButton = header.find_element_by_tag_name('button')
    sideMenuButton.click()

    menu = Menu(session, By.CLASS_NAME, "menu-tree")
    print('all menu values')
    print(menu.getValues(include_invisible=True))
    print('visible menu values')
    print(menu.getValues())

    # menu.selectMenu('Boards')

    session.close()

if __name__ == "__main__":
   pytest.main(["-rP", __file__])











#     addOrderButton = Button(session, By.ID, "addCustomOrdersIcon")
#     addOrderButton.click()
#     time.sleep(SLEEP_TIME)

#     # Set value of opcode dropdown to "S-Misc"
#     orderCreator = View(session, By.ID, "Operations.Orders.Create.Overview")
#     opcodeDropdown = Dropdown(session, By.CLASS_NAME, "ia_dropdown", parent=orderCreator)
#     opcodeDropdown.setValue("S-Misc")
#     time.sleep(SLEEP_TIME)

#     # If task filter textbox has a value, clear it
#     # (As of writing, it sometimes displays a value of "null". Not good.)
#     taskFilter = TextBox(session, By.ID, "taskFilter")
#     taskFilter.clearText()
#     time.sleep(SLEEP_TIME)

#     # Click on a table row
#     taskTable = Table(session, By.ID, "taskTable")
#     taskTable.clickOnRow(0)
#     time.sleep(SLEEP_TIME)

#     # Set value of task dropdown
#     taskDropdown = Dropdown(session, By.ID, "taskDropdown")
#     taskDropdown.setValue("Create Separate Orders")
#     time.sleep(SLEEP_TIME)
    
#     # Verify that "Create Order" button is visible
#     createOrderButton = Button(session, By.ID, "createButton")
#     assert createOrderButton.get_attribute("display") != "none"

#     session.close()