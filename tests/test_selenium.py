import time
from perspective_automation.selenium import Session
def test_session():
    URL = "https://lv1mesdevlap01.est1933.com:8043/data/perspective/client/MES"
    CREDENTIALS = {"username":"RATester01", "password":"N3verp@tch2021"}
    session = Session(URL, 10, CREDENTIALS)
    session.login()
    time.sleep(10)


if __name__ == "__main__":
   test_session()
