import time
from selenium.webdriver.common.by import By
from perspective_automation.selenium import Session

def test_tableData():
    BASE_URL = "http://localhost"
    PAGE_PATH = "/data/perspective/client/MES"
    CREDENTIALS = {"username":"RATester01", "password":"N3verp@tch2021"}
    session = Session(BASE_URL, PAGE_PATH, 10, CREDENTIALS)
    session.login()

    



if __name__ == "__main__":
   test_tableData()



