import time
from selenium.webdriver.common.by import By
from perspective_automation.selenium import Session, Credentials
from perspective_automation.components import Button

def test_popups():
    BASE_URL = "http://localhost"
    PAGE_PATH = "/data/perspective/client/MES"
    CREDENTIALS = Credentials("RATester01", "N3verp@tch2021")
    session = Session(BASE_URL, PAGE_PATH, 10, CREDENTIALS)
    session.login()

    orderFilterIcon = Button(session, By.ID, "orderFilterIcon")
    orderFilterIcon.click()


    time.sleep(5)
if __name__ == "__main__":
   test_popups()