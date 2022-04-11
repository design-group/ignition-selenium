from perspective_automation.perspective import (PerspectiveComponent, PerspectiveElement)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import time

class XPathNotFoundException(Exception):
    pass

class ToolBar(PerspectiveElement):
    """
    DESCRIPTION: This class is responsable for interacting with the Sepasoft ToolBar
    PARAMETERS: path (REQ, str) - divided by /'s to mark which button to drill into
    """      

class RowObject(PerspectiveElement):
    """
    DESCRIPTION: This class will allow for the expansion of sepasoft table items
    PARAMETERS: PerspectiveElement - pulls in the perspective element class as a child class
    """
    def get_label(self):
        """
        DESCRIPTION: Finds the text paired to class name and returns it
        """
        label = self.find_element_by_partial_class_name("MuiTypography-body")
        return label.text
   
    def toggle_row_expansion(self):
        """
        DESCRIPTION: Will expand collapsed row on sepasoft table
        """
        button = self.find_element_by_partial_class_name("mes_mesTable__expandButton")
        button.click()
        time.sleep(.2)

    def get_row_by_label(self, label):
        """
        DESCRIPTION: Will get the label of table row
        """
        rows = self.get_nested_rows()
        labels = self.get_nested_row_labels()
        row_index = labels.index(label)
        return rows[row_index]

    def get_nested_rows(self):
        """
        DESCRIPTION: Will find the rows nested in sepasoft table row
        """
        return [RowObject(session=self.session, element=element) for element  in self.waitForElements(By.XPATH, "//tr[@class='MuiTableRow-root']")]

    def get_nested_row_labels(self):
        """
        DESCRIPTION: Will find the names of the rows nested in the sepasoft table row
        """
        return [row.get_label() for row in self.get_nested_rows()]

    def expand_row_by_path(self, path):
        """
        DESCRIPTION: Will expand the table rows down the path input by users
        PARAMETERS: path - (str) the path from top level destination level
        """
        for label in path.split("/"):
            row = self.get_row_by_label(label)
            row.toggle_row_expansion()

    def select_row(self, label):
        """
        DESCRIPTION: Selects the final row after the expansion method is called
        PARAMETERS: label - (str) The label of the final level after the table expansion
        """
        row = self.get_row_by_label(label)
        row.click()

class UnorderedList(PerspectiveComponent):
    """
    DESCRIPTION: This class takes the unordered list that dropsdown from contextual menus and splits the list items into separate selectable entities
    PARAMETERS: PerspectiveComponents - Pulls in the perspective component class as a child class
    """
    def get_list_items(self):
        """
        DESCRIPTION: Fetch the list items that are nested within the unordered list
        """
        return [UnorderedList(session=self.session, element=element) for element in self.waitForElements(By.XPATH, "//div[@position='[object Object]']//ul[@role='menu']")]

    def get_list_labels(self):
        """
        DESCRIPTION: Fetch the labels of the list items that are nested within the unordered list
        """
        return [list_item.get_label() for list_item in self.get_list_items()]

    def get_label(self):
        """
        DESCRIPTION: Converts the list item label into text
        """
        label = self.find_element_by_partial_class_name("MuiTypography-body")
        return label.text

    def select_option_by_label(self, label):
        """
        DESCRIPTION: Allows the selection of list items based on their label
        PARAMENTERS: label (str) - The label of the list item that has been selected in the unordered list
        """
        list_items = self.get_list_items()
        labels = self.get_list_labels()
        label_index = labels.index(label)
        return list_items[label_index]

class EquipmentManager(PerspectiveComponent, RowObject, ToolBar):#This seems to be used in multiple views in the same ways, should make this more 
                                                                 #generic but cant think of a good name at the moment
    """
    DESCRIPTION: This class contains the functions that are used specifically within the equipment manager component of sepasoft
    PARAMETERS: PerspectiveComponent, RowObject - Takes in these two classes as children of this class
    """
    def next_page(self): #This will most likely be used in other places 
        """
        DESCRIPTION: Will click the next page button
        """
        xpath = "(//button[@aria-label='Next'])[1]"
        button = self.session.waitForElement(locator = By.XPATH, identifier = xpath)
        button.click()

    def back_page(self): #This will most likely be used in other places 
        """
        DESCRIPTION: Will click the back page button
        """
        xpath = "(//button[@aria-label='Previous'])[1]"
        button = self.session.waitForElement(locator = By.XPATH, identifier = xpath)
        button.click()

class Calender(PerspectiveComponent):
    """
    DESCRIPTION: This class contains the code for manipulating sepasoft date and time components
    """
    def calender_click(self):
        """
        DESCRIPTION: Will click sepasoft calender icon
        """
        path = "button[class='MuiButtonBase-root MuiIconButton-root'] span[class='MuiIconButton-label']"
        button = self.session.waitForElement(locator = By.CSS_SELECTOR, identifier = path)
        button.click()

    def calender_day(self, day):
        """
        DESCRIPTION: Will click on a specific day on a sepasoft calender, thus selecting it
        PARAMETERS: Day (str) - User selected day they want selected
        """
        path = "//button[@class='MuiButtonBase-root MuiIconButton-root MuiPickersDay-day']//p[@class='MuiTypography-root MuiTypography-body2 MuiTypography-colorInherit'][normalize-space()='%s']" % day
        locator = self.session.waitForElement(locator = By.XPATH, identifier = path)
        locator.click()

    def month_scroll_back(self, number_of_months):
        """
        DESCRIPTION: There is no way to select a specific month other than cycling one at a time in a list, thus this method will click that cycle back button repeatably to get to the user desired month
        PARAMETERS: number_of_months (str) - The number of months the user want to move, ie if its march and you want to get to january, you would input '2'
        """
        path = "//div[@class='MuiPickersCalendarHeader-switchHeader']//button[1]"
        locator = self.session.waitForElement(locator = By.XPATH, identifier = path)
        i = 1
        while i <= number_of_months:
            locator.click()
            i = i +1
            time.sleep(.1)

    def month_scroll_forward(self, number_of_months):
        """
        DESCRIPTION: There is no way to select a specific month other than cycling one at a time in a list, thus this method will click that cycle forward button repeatably to get to the user desired month
        PARAMETERS: number_of_months (str) - The number of months the user want to move, ie if its january and you want to get to march, you would input '2'
        """
        path = "//div[@class='MuiPickersBasePicker-pickerView']//button[2]"
        locator = self.session.waitForElement(locator = By.XPATH, identifier = path)
        i = 1
        while i <= number_of_months:
            locator.click()
            i = i +1
            time.sleep(.1)           

    def year_change(self, year):
        """
        DESCRIPTION: This method will open the calenders drop down year list and will select the desired year
        PARAMETERS: year (str) - The user selected year
        """
        path = "(//span[@class='MuiButton-label'])[1]"
        locator = self.session.waitForElement(locator = By.XPATH, identifier = path)
        locator.click()
        time.sleep(.5)
        year_path = "//div[normalize-space()='%s']" %year
        year = self.session.waitForElement(locator = By.XPATH, identifier = year_path)
        year.click()

    def time_change(self, hour, minute):
        """
        DESCRIPTION: This method will allow for the user to select time on the sepasoft clock that in part of the calender component, 
                     the way this is done is a bit more involved so a lot of comments are included
        PARAMETERS: hour (str) - the desired hour
                    minute (str) - the desired minute
        """
        if hour > 12 : # The clock element takes in 24 hour format time but displays in 12 hour format, this if statement
            pm = True  # will take the user input 24 hour time, if its over 12, will subtract 12 and then mark that the time is in PM
            hour = hour - 12
        else:
            pm = False

        minute -= minute % 5 # Rounds the user input minute down to the nearest multiple of 5

        hour_path = "(//button[contains(@type,'button')])[13]" # this points at the button to input hours, the index is specific to the calender component so in this instance using index is somewhat safe
        hour_locator = self.session.waitForElement(locator = By.XPATH, identifier = hour_path)
        hour_locator.click()
        hour_selection_path = "//span[normalize-space()='%s']" % hour
        hour_selection_locator = self.session.waitForElement(locator = By.XPATH, identifier = hour_selection_path)
        ActionChains(self.session.driver).move_to_element(hour_selection_locator).click().perform() # action chains are implamented here to move the pointer of the mouse to the location of where we want to click, this is because when trying to preform
                                                                                                    # standard .click function has an error due to the layering sepasoft implaments, but the action chains version works fine                       
        minute_path = "(//button[contains(@type,'button')])[14]"#we could perhapses make the minute selection more precise via algorithm but due to scope may not matter, can improve on this later
        minute_locator = self.session.waitForElement(locator = By.XPATH, identifier = minute_path)
        minute_locator.click()
        minute_selection_path = "//span[normalize-space()='%s']" % minute
        minute_selection_locator = self.session.waitForElement(locator = By.XPATH, identifier = minute_selection_path)
        ActionChains(self.session.driver).move_to_element(minute_selection_locator).click().perform()

        if pm == True:
            path = "(//button[@type='button'])[16]" ###clicks the pm button if the user input hours were greater than 12
            locator = self.session.waitForElement(locator = By.XPATH, identifier = path)
            locator.click()
            return
        else: # clicks the am button if the user input hours are less than 13
            path = "(//button[contains(@type,'button')])[15]"
            locator = self.session.waitForElement(locator = By.XPATH, identifier = path)
            locator.click()  
            return

    def date_time_entry(self, date_entry, time_entry): # date expected in YYYY-MM-DD format, time in HH:MM
        """
        DESCRIPTION: This method allows for direct entry of date and time into a field, as opposed to manual selection via the calender component
        PARAMETERS: date_entry (str) - the user desired date
                    time_entry (str) - the user desired time
        """
        box_path  = "//div[@class='MuiInputBase-root MuiInput-root MuiInput-underline mes_workOrderTableEditView__underline MuiInputBase-formControl MuiInput-formControl MuiInputBase-adornedEnd']//*"
        box_path_locator = self.session.waitForElement(locator = By.XPATH, identifier = box_path)
        box_path_locator.click().key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(date_entry + ' ' + time_entry).preform() # This will highlight all the text currently in the text field so that the oncoming text can overwrite it and then send the text to the field

class AnalysisSelector(PerspectiveComponent):
    """
    DESCRIPTION: These handlers are specific to the analysis selector component, where the other button icons pressed call for @ title, these call 
                 for @ id, due to this it is prudent to create a new method for selecting these buttons
    """      
    def selection_expansion_click(self, text):
        """
        DESCRIPTION: This method will expand a selection via the name of the item
        PARAMETERS: text (str) - The name of the field the user want to expand
        """
        id = "//span[@title='%s']/.." % text
        button = self.session.waitForElement(locator = By.XPATH, identifier = id)
        ActionChains(self.session.driver).move_to_element_with_offset(button,0,20).click().perform()# cant be comined with selection box click due to the offset difference in the action chains

    def selection_box_click(self, text):
        """
        DESCRIPTION: This method will click the button that is attached to selection drop down items
        PARAMETERS: text (str) - The name of the item the user wants to toggle the selection for
        """
        #Add comment why these methods are different
        id = "//span[@title='%s']/.." % text
        button = self.session.waitForElement(locator = By.XPATH, identifier = id)
        ActionChains(self.session.driver).move_to_element_with_offset(button,30,20).click().perform()

class Table(PerspectiveComponent):
    """
    DESCRIPTION: This class is responsible for getting data from sepasoft tables and targeting the table cells
    """
    def get_cell(self,column_name, row_number):
        """
        DESCRIPTION: this method will allow for the user to select a particular cell based on its x,y position in the table, sepasoft starts the row index offset by two so this is also adjusted for in a way that the user does not have to account for it
        PARAMETERS: column_name (str) - Ths name of the colum that the user wants to get data from
                    row_number (str) - the row that the user wants to get data from
        """
        row_number = row_number + 2
        id = "(//div[@data-column-id='{}'])[{}]".format(column_name, row_number)
        selector_locator = self.waitForElement(locator = By.XPATH, identifier = id)
        ActionChains(self.session.driver).move_to_element(selector_locator).click().perform()

    def get_text(self,column_name, row_number):
        """
        DESCRIPTION: this method will allow for the user to select a particular cell based on its x,y position in the table, sepasoft starts the row index offset by two so this is also adjusted for in a way that the user does not have to account for it
        PARAMETERS: column_name (str) - Ths name of the colum that the user wants to get data from
                    row_number (str) - the row that the user wants to get data from
        """
        row_number = row_number + 2
        id = "(//div[@data-column-id='{}'])[{}]".format(column_name, row_number)
        selector_locator = self.waitForElement(locator = By.XPATH, identifier = id)
        return selector_locator.text

class SepasoftGeneral(PerspectiveComponent):
    """
    DESCRIPTION: This class holds all the non component specific items that sepasoft uses
    """
    def drop_down_selector(self, selector_name, selection):
        
        if self.hasxpath(xpath = "(//label[normalize-space()='%s'])[1]" % selector_name):
            path = "(//label[normalize-space()='%s'])[1] "% selector_name 
        elif self.hasxpath(xpath = "//span[contains(text(),'%s')]" % selector_name):
            path = "//label[normalize-space()='%s']/following-sibling::div" % selector_name
            
        selector_locator = self.waitForElement(locator = By.XPATH, identifier = path)
        ActionChains(self.session.driver).move_to_element(selector_locator).click().perform()
        selection_path = "//li[normalize-space()='%s']" % selection
        selection_locator = self.waitForElement(locator = By.XPATH, identifier = selection_path)
        ActionChains(self.session.driver).move_to_element(selection_locator).click().perform()

    def button(self, text):
        """
        DESCRIPTION: This method will click a button that contains text
        PARAMETERS: text (str) - the text that is on the button
        """  
        if self.hasxpath(xpath = "//span[contains(text(),'%s')]" % text):
            id = "//span[contains(text(),'%s')]"  % text    
        elif self.hasxpath(xpath = "(//div[@class='text'][normalize-space()='%s'])[1]" % text):
            id = "(//div[@class='text'][normalize-space()='%s'])[1]"  % text

        else:
            raise XPathNotFoundException()    
        button = self.session.waitForElement(locator = By.XPATH, identifier = id)
        ActionChains(self.session.driver).move_to_element(button).click().perform()

    def to_camel_case(text):
        """
        DESCRIPTION: Converts a normal string to cammel case ie xxxxYyyyyyZzzzz
        PARAMETERES: text (str) - the original string that is passed in
        """
        for i in text:
            if i == '-' or i == '_' or i == ' ':               
                text = text.replace(text[text.index(i):text.index(i)+2], text[text.index(i)+1].upper(), 1)
                text = text[0].lower() + text[1:]
        return text  

    def sepasoft_case(self, button_type): 
        """
        DESCRIPTION: This handler takes the label from a page, appends the button type, and then transforms it into the sepasoft syntax
        PARAMETERS: button_type (str) - the name of the button type ie. add, edit, delete, etc.
        """
        label = self.find_element_by_partial_class_name("MuiSelect-root mes_selectComponent__select")
        regular_title = label.text
        full_regular_title = button_type + regular_title
        cammel_title = SepasoftGeneral.to_camel_case(full_regular_title)
        result = []
        i = 0
        while i < len(cammel_title):
             ch = cammel_title[i]
             if not ch.isupper():
                result.append(ch)
             if ch.isupper == True: # if character is uppercase then remove that character
                result.remove(ch)
             i =  i + 1
        result = result[1:] # Take the string starting at index 1 (the second character)
        return ''.join(result)  # puts all the characters together from array into single string   

    def chopper(self, button_type):
        """
        DESCRIPTION: This handler simply removes the first letter off of the button labels, this is useful since sepasoft removed some of the labels themselves, allows for dynamic pathing
        PARAMETERS: button_type (str) - The name of the button to be clicked, ie. add, edit delete, etc...
        """
        result = button_type[1:] # Take the string starting at index 1 (the second character)
        return ''.join(result) # puts all the characters together from array into single string

    def toggle_button(self, name):
        """
        DESCRIPTION: allows the selection of boolean toggle buttons
        PARAMETERS: name (str) - the name of the button that the user wishes to toggle
        """
        if self.hasxpath(xpath = "//span[normalize-space()='%s']" % name):
            path = "//span[normalize-space()='%s']" % name
        elif self.hasxpath(xpath = "(//label[normalize-space()='%s'])[1]" % name):
            path = "(//label[normalize-space()='%s'])[1]" % name # some times sepasoft will not assign ids based on the label text on relative xpaths, but it does on index... the index never changes
        else:
            raise XPathNotFoundException()  
        field = self.session.waitForElement(locator = By.XPATH, identifier = path)
        field.click()

    def click_icon(self, icon_name, label = None):
        """
        DESCRIPTION: This handler is responsable for hitting icons, this is done dynamically by taking a generic input name, ie. add, edit, delete, etc... and then will spawn a couple of names 
                     that will fit into the various different forms that sepasoft uses. The handler will then check to see if any of these names are used on the view, if not it will default to the full name 
                    ie add = add. This will also make it so that as new icons are discovered if missed, no new code needs to be added. 
        PARAMETERS: icon_name (str) - This is the name of the icon, ie. add, edit, etc... expected in lowercase
                    label (str) - This argument is to click an additional button that drops down from this, ie, if you click add and then it asks
                                  what you want to add. Pass the name in as a positional argument to click the button
        BUTTON_NAMES: add, delete, edit, duplicate, import, export, move, deactivate, toggle_column_visibility, save, cancel confirm, data_points_edit, filter_by_edit, group_by_edit, order_by_edit
        """
        
        regular = icon_name
        chopped = SepasoftGeneral.chopper(self, icon_name)
        sepasofted = SepasoftGeneral.sepasoft_case(self, icon_name)    
          
        if SepasoftGeneral.hasxpath(self, xpath = "//div[@role='none presentation']"): # The top part of the if statment handles popup windows, without it, the script will keep trying to click on the 
            if SepasoftGeneral.hasxpath(self, xpath = "//button[@title='{}']".format(regular)):  #underlying window
                icon_name = regular
                key = 'title'
            elif SepasoftGeneral.hasxpath(self, xpath = "//button[@id='{}']".format(regular)):
                icon_name = regular
                key = 'id'
        else:                                                                              # This part of the script clicks on the main view
            if SepasoftGeneral.hasxpath(self, xpath = "//button[@title='{}']".format(chopped)):
                icon_name = chopped
                key = 'title'
            elif SepasoftGeneral.hasxpath(self, xpath = "//button[@id='{}']".format(chopped)):
                icon_name = chopped
                key = 'id'
            elif SepasoftGeneral.hasxpath(self, xpath = "//button[@title='{}']".format(sepasofted)):
                icon_name = sepasofted       
                key = 'title'               
            elif SepasoftGeneral.hasxpath(self, xpath = "//button[@id='{}']".format(sepasofted)):
                icon_name = sepasofted  
                key = 'id'    
            else:
                raise XPathNotFoundException()  
           
        path = "//button[@{}='{}']".format(key, icon_name) # formats the path found in the above if tree, both the attribute type and name are dynamic 
        button = self.session.waitForElement(locator = By.XPATH, identifier = path)
        ActionChains(self.session.driver).move_to_element(button).click().perform()

        if label: # this is specifically for when a button has a dropdown list of choices, will click the choice entered by user
            path = "//span[normalize-space()='%s']" % label
            button = self.session.waitForElement(locator = By.XPATH, identifier = path)
            button.click()                  

    def click_multi_instance_icon(self, icon_name, instance_number):
        """
        DESCRIPTION: This handler is very specifically for when multiple instances of the same button appear on a single view
        PARAMETERS: id (str) - the name of the button
                    instance_number (id) - the number of button occurrence
        """
        path = "(//*[name()='g'][@id='{}}'])[{}}]".format(icon_name, instance_number)
        button = self.session.waitForElement( locator = By.XPATH, identifier = path )
        ActionChains(self.session.driver).move_to_element(button).click().perform()

    def click_button(self, label):
        """
        DESCRIPTION: This will click the buttons that are embedded within the sepersoft component (ToolBar buttons are manipulated with ToolBar.click_icon)
        PARAMETERS: path (REQ, str) - The particular button is referenced be index
        """
        xpath = "//span[contains(text(),'%s')]" % label
        button = self.session.waitForElement(locator = By.XPATH, identifier = xpath)
        button.click()

    def text_field(self, field_name, message):
        """
        DESCRIPTION: This method will find a text field via the two ways that sepasoft addresses them
        PARAMETERS: field_name (str) - pass in the name that is present either above or in the target text field
                    message (str) - pass in the message the user want to input into the text field
        """
        if SepasoftGeneral.hasxpath(self, xpath = "//label[normalize-space()='%s']"% field_name):
            path = "//label[normalize-space()='%s']" % field_name
        elif SepasoftGeneral.hasxpath(self, xpath = "//span[normalize-space()='%s']" % field_name):
            path = "//span[normalize-space()='%s']" % field_name
        else:
            raise XPathNotFoundException()  
        text_box = self.waitForElement(locator = By.XPATH, identifier = path)
        ActionChains(self.session.driver).move_to_element(text_box).click().key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(message).perform()

    def radio_button(self, operator): ## This method is different than the regular click button since it is for specifically operators, they have the attribute of value
        """
        DESCRIPTION: This method will select a particular radio button
        PARAMETERS: operator (str) - The desired radio button to be selected, this is input by passing in the text of the label
        """
        id = "//input[@value='%s']" % operator
        button = self.session.waitForElement(locator = By.XPATH, identifier = id)
        ActionChains(self.session.driver).move_to_element(button).click().perform()    

    def hasxpath(self, xpath):
        """
        DESCRIPTION: This handler check to see if a given xpath exists without causing the script to crash, this allows for much cleaner code implamentation
        PARAMETERS: xpath (str) - the xpath that is passed in for testing for existence
        """
        try:
            self.session.waitForElement(locator = By.XPATH, identifier = xpath)
            return True
        except:
            return False