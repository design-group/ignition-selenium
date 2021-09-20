import time
from selenium.webdriver.common.by import By
from perspective_automation.selenium import Session
from perspective_automation.components import Popup, Button

def test_popups():
    BASE_URL = "http://localhost"
    PAGE_PATH = "/data/perspective/client/MES"
    CREDENTIALS = {"username":"RATester01", "password":"N3verp@tch2021"}
    session = Session(BASE_URL, PAGE_PATH, 10, CREDENTIALS)
    session.login()

    orderFilterIcon = Button(session, By.ID, "orderFilterIcon")
    orderFilterIcon.click()


    time.sleep(5)
if __name__ == "__main__":
   test_popups()