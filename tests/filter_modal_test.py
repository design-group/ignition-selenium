import time
import pytest
from selenium.webdriver.common.by import By
from perspective_automation.selenium import Session, Credentials
from perspective_automation.components import Table, View, Button, Dropdown, TextBox

def test_sample_filter():
    BASE_URL = "https://lv1mesdevlap01.est1933.com:8043"
    PAGE_PATH = "/data/perspective/client/MES/Sampling"
    CREDENTIALS = Credentials("RATester01", "N3verp@tch2021")

    with Session(BASE_URL, PAGE_PATH, 20, credentials=CREDENTIALS, headless=False) as session:
        SLEEP_TIME = 1
        # click order filter button
        filter_button = View(session, By.ID, "orderFilterIcon")
        filter_button.click()
        time.sleep(SLEEP_TIME)
        popup_container = View(session, By.ID, "Operations.Orders.Embedded Views.Filters")
        # get dropdown filter options
        process_dropdown = Dropdown(session, By.ID, "sampleProcessDropdown")
        print(process_dropdown.getOptionTexts())
        # process_dropdown.click()
        # process_dropdown.waitForElements(By.XPATH, "//*[contains(@class, 'ia_dropdown__option')]")

        # process_dropdown.setValue("Arrest")
        # print(dropdown_options.getValues())
        # dropdown_menu = popup_container.find_element_by_partial_class_name("material-icons")
        # dropdown_menu = popup_container.find_element_by_xpath("//*[name()='svg']")
        # dropdown_field = View(session, By.ID, "areaDropdown")
        # dropdown_menu = popup_container.find_element_by_partial_class_name("md-24")
        # dropdown_menu = popup_container.find_element_by_id("expand_more")
        # dropdown_menu = popup_container.find_element_by_css_selector("use[*|href='#expand_more'")
        # dropdown_menu.click()
        # dropdown_options = popup_container.find_element_by_class_name("ia_componentModal")
        # print(dropdown_options.get_attribute('innerHTML'))
        # clear any existing filters and close filter modal
        # the line below was written using Selenium 4.0.0
        # clear_values = popup_container.find_elements(By.CLASS_NAME, "iaDropdownCommon_remove_value")
        clear_values = popup_container.find_elements_by_class_name("iaDropdownCommon_remove_value")
        if clear_values:
            for value in clear_values:
                value.click()
        close_icon = View(session, By.CLASS_NAME, "close-icon")
        close_icon.click()
    
if __name__ == "__main__":
    pytest.main(["-rP", __file__])