PePy statistics 
[![PyPI Downloads](https://static.pepy.tech/badge/dynamicinputbox)](https://pepy.tech/projects/dynamicinputbox)

# About
A dynamic and customizable input dialog box using Tkinter.

Creates a dialog window that can display a message, 
accept one or more text inputs (with optional presets, default values, 
and masked input), offer grouped radio button alternatives, and allow 
the user to respond via custom buttons.

## Parameters
  * title (str): The window title. Default is an empty string.
  * message (str): An optional message to be displayed above inputs.
  * input (bool): **[Deprecated]**
    * If True, a single text input field is displayed using input_default, input_show, and preset_text.
    * If False, 'inputs' must be used to specify fields. Default is False.
  * input_default (str): **[Deprecated]** Default value for the single input field (used only if 'input' is True).
  * input_show (Optional[str]): **[Deprecated]** Character used to mask input (e.g., '*') for the single input field.
  * preset_text (Optional[str]): **[Deprecated]** Greyed-out preset text for the single input field, replaced on key press.
  * inputs (Optional[List[Dict[str, Union[str, None]]]]): A list of input definitions. Each input is a dict with optional keys:
    * 'label': Display label for the input field (required).
    * 'default': Pre-filled value.
    * 'show': Character to display instead of actual input (e.g., '*').
    * 'preset': Greyed-out prompt text, removed on typing.
  * alternatives (Optional[List[Dict[str, Union[str, List[str]]]]]): A list of grouped radio button sets. Each group is a dict with:
     * 'label': Group name (required).
     * 'options': List of option strings (required).
     * 'default': Pre-selected option (defaults to the first in 'options').
  * buttons (Optional[List[str]]): A list of button labels to display. The clicked button is returned. Default is ['OK'].
  * default_button (Optional[str]): Which button should be pre-focused. If not set, the first button is focused (unless inputs exist).
  * separator (Optional[bool]): Is a separator to be placed between each widget group

## Returns
The class itself does not return a value upon instantiation.

To access the user's input after the dialog closes, use the `get()` method.

**get( dictionary = False )** returns a tuple:

( inputs_dict, alternatives_dict, clicked_button )

  * _inputs_dict_: a dictionary mapping each input's label to the entered value.
  * _alternatives_dict_: a dictionary mapping each alternative group to the selected option.
  * _clicked_button_: the label of the button clicked by the user.

**get( dictionary = True )** returns a dictionary:

{ 'button': 'Clicked button' , 'inputs': {} , 'alternatives: {} }

  * 'button': '...': text of the button that was clicked
  * 'inputs': {...}: a dictionary mapping each input's label to the entered value.
  * 'alternatives': {...}: a dictionary mapping each alternative group to the selected option.
