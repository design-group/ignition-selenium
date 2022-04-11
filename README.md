# Sepasoft - Selenium

## Description
This class allows for the use of selenium automation scipting on sepasoft specific components

# Classes
- `Xpath Exception `
    >This Class gives an exception handler for when try catch statements fail.
- `RowObject`
    >This class will allow for the expansion of sepasoft table items
    - `get_label`
        >Finds the text paired to class name and returns it
    - `toggle_row_expansion`
        >Will expand collapsed row on sepasoft table
    - `get_row_by_label`
        >Will get the label of table row
    - `get_nested_rows`
        >Will find the rows nested in sepasoft table row
    - `get_nested_row_labels`
        >Will find the names of the rows nested in the sepasoft table row
    - `expand_row_by_path`
        >Will expand the table rows down the path input by users
    - `select_row`
        >Selects the final row after the expansion method is called
- `UnorderedList`
    >This class takes the unordered list that dropsdown from contextual menus and splits the list items into separate selectable entities
    - `get_list_items`
        >Fetch the list items that are nested within the unordered list
    - `get_list_labels`
        >Fetch the labels of the list items that are nested within the unordered list
    - `get_label`
        >Converts the list item label into text
    - `select_option_by_label`
        >Allows the selection of list items based on their label
- `EquipmentManager`
    >This class contains the functions that are used specifically within the equipment manager component of sepasoft
    - `next_page`
    >Will click the next page button
    - `back_page`
    >Will click the back page button
- `Calender`
    >This class contains the code for manipulating sepasoft date and time components
    - `calender_click`
        >Will click sepasoft calender icon
    - `calender_day`
        >Will click on a specific day on a sepasoft calender, thus selecting it
    - `month_scroll_back`
        >There is no way to select a specific month other than cycling one at a time in a list, thus this method will click that cycle back button repeatably to get to the user desired month
    - `month_scroll_forward`
        >There is no way to select a specific month other than cycling one at a time in a list, thus this method will click that cycle forward button repeatably to get to the user desired month
    - `year_change`
        >This method will open the calenders drop down year list and will select the desired year
    - `time_change`
        >This method will allow for the user to select time on the sepasoft clock that in part of the calender component, the way this is done is a bit more involved so a lot of comments are included
    - `date_time_entry`
        >This method allows for direct entry of date and time into a field, as opposed to manual selection via the calender component
- `AnalysisSelector`
    >These handlers are specific to the analysis selector component, where the other button icons pressed call for @ title, these call for @ id, due to this it is prudent to create a new method for selecting these buttons
    - `selection_expansion_click`
        >This method will expand a selection via the name of the item
    - `selection_box_click`
        >This method will click the button that is attached to selection drop down items
- `Table`
    >This class is responsible for getting data from sepasoft tables and targeting the table cells
    - `get_cell`
        >this method will allow for the user to select a particular cell based on its x,y position in the table, sepasoft starts the row index offset by two so this is also adjusted for in a way that the user does not have to account for it
    - `get_text`
        >this method will allow for the user to select a particular cell based on its x,y position in the table, sepasoft starts the row index offset by two so this is also adjusted for in a way that the user does not have to account for it
- `SepasoftGeneral`
    >This class holds all the non component specific items that sepasoft uses
    - `drop_down_selector`
        >This handler allows accessing of sepasoft drop down selector
    - `button`
        >This method will click a button that contains text
    - `to_camel_case`
        >Converts a normal string to cammel case ie xxxxYyyyyyZzzzz
    - `sepasoft_case`
        >This handler takes the label from a page, appends the button type, and then transforms it into the sepasoft syntax
    - `chopper`
        >This handler simply removes the first letter off of the button labels, this is useful since sepasoft removed some of the labels themselves, allows for dynamic pathing
    - `click_icon`
        >This handler is responsable for hitting icons, this is done dynamically by taking a generic input name, ie. add, edit, delete, etc... and then will spawn a couple of names that will fit into the various different forms that sepasoft uses. The handler will then check to see if any of these names are used on the view, if not it will default to the full name ie add = add. This will also make it so that as new icons are discovered if missed, no new code needs to be added. 
        >
            - add
            - delete
            - edit
            - duplicate
            - import,
            - export
            - move
            - deactivate
            - toggle_column_visibility
            - save, cancel confirm
            - data_points_edit
            - filter_by_edit
            - group_by_edit
            - order_by_edit

    - `click_multi_instance_icon`
        >This handler is very specifically for when multiple instances of the same button appear on a single view
    - `click_button`
        >This will click the buttons that are embedded within the sepersoft component (ToolBar buttons are manipulated with ToolBar.click_icon)
    - `text_field`
        >This method will find a text field via the two ways that sepasoft addresses them
    - `radio_button`
        >This method will select a particular radio button
    - `hasxpath`
        >This handler check to see if a given xpath exists without causing the script to crash, this allows for much cleaner code implamentation