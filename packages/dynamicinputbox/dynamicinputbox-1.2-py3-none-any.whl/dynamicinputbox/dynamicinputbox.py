from tkinter import Frame, Radiobutton, StringVar, Tk, Button, Entry, Label, ttk, N, E, W
from tkinter.font import Font
from typing import Dict, List, Optional, Union

class SecureString:
    """A wrapper to hold sensitive data in memory that can be wiped."""
    def __init__( self, text: str ):
        self._buffer = bytearray( text, 'utf-8' )

    def get( self ) -> str:
        """Get the password value as a string."""
        return self._buffer.decode( 'utf-8' )

    def wipe( self ):
        """Overwrite the stored password in memory."""
        for i in range( len( self._buffer ) ):
            self._buffer[i] = 0

    def __del__( self ):
        self.wipe()

    def __repr__( self ):
        return "<SecureString [HIDDEN]>"

class dynamic_inputbox():
    def __init__( self,
                 title = "",
                 message = "",
                 input = False,
                 input_default = '',
                 input_show = None,
                 preset_text = None,
                 inputs: Optional[ List[ Dict[ str, Union[ str, None ] ] ] ] = None,
                 alternatives: Optional[ List[ Dict[ str, Union[ str, List[ str ] ] ] ] ] = None,
                 buttons: Optional[ List[ str ] ] = [ 'OK' ],
                 default_button: Optional[ str ] = None,
                 group_separator: Optional[ bool ] = False
                ):
        """
        A dynamic and customizable input dialog box using Tkinter.

        This class creates a GUI dialog that can display a message, 
        accept one or more text inputs (with optional presets, default values, 
        and masked input), offer grouped radio button alternatives, and allow 
        the user to respond via custom buttons.

        Parameters:
            title (str): The window title. Default is an empty string.
            message (str): An optional message to be displayed above inputs.
            input (bool): If True, a single text input field is displayed using input_default, input_show, and preset_text.
                        If False, 'inputs' must be used to specify fields. Default is False.
            input_default (str): Default value for the single input field (used only if 'input' is True).
            input_show (Optional[str]): Character used to mask input (e.g., '*') for the single input field.
            preset_text (Optional[str]): Greyed-out preset text for the single input field, replaced on key press.
            inputs (Optional[List[Dict[str, Union[str, None]]]]): A list of input definitions. Each input is a dict with optional keys:
                - 'label': Display label for the input field (required).
                - 'default': Pre-filled value.
                - 'show': Character to display instead of actual input (e.g., '*').
                - 'preset': Greyed-out prompt text, removed on typing.
            alternatives (Optional[List[Dict[str, Union[str, List[str]]]]]): A list of grouped radio button sets. Each group is a dict with:
                - 'label': Group name (required).
                - 'options': List of option strings (required).
                - 'default': Pre-selected option (defaults to the first in 'options').
            buttons (Optional[List[str]]): A list of button labels to display. The clicked button is returned. Default is ['OK'].
            default_button (Optional[str]): Which button should be pre-focused. If not set, the first button is focused (unless inputs exist).

        Returns:
            The class itself does not return a value upon instantiation. 
            To access the user's input after the dialog closes, use the `get()` method.

            - `get(dictionary=False)` returns a tuple:
                (inputs_dict, alternatives_dict, clicked_button)
                - inputs_dict: a dictionary mapping each input's label to the entered value.
                - alternatives_dict: a dictionary mapping each alternative group to the selected option.
                - clicked_button: the label of the button clicked by the user.

            - `get(dictionary=True)` returns a single dictionary:
                {
                    'inputs': {...},         # as above
                    'alternatives': {...},   # as above
                    'button': '...'          # clicked button label
                }
        """

        self._inputtext = ""
        self._clicked_button = default_button
        self._default_button_to_focus = None
        self._master = Tk()
        self._master.title( title )
        self._master.bind( "<Escape>", lambda event: self.cancel() )
        self._master.resizable( False, False )
        self.input_fields = {}
        self.alternatives_vars = {}
        self.firstentry = None
        self.group_separator = group_separator

        self.title = title
        self.message = message

        self.input = input
        self.input_show = input_show
        self.preset_text = preset_text
        self.input_default = input_default

        if input and not inputs:
            self.inputs = [ { 'label': 'Input', 'name': 'Input', 'default': input_default, 'show': input_show, 'preset': preset_text } ]
        else:
            self.inputs = inputs

        self.alternatives = alternatives

        self.buttons = buttons
        self.default_button = default_button

        self.show()

    def cancel( self ):
        """ Cancels the dialog and closing the window. """
        self._inputtext = { 'inputs': [], 'alternatives': [] }
        self._clicked_button = 'Aborted'
        self._master.destroy()

    def on_closing( self, button = None ):
        """Handles the closing of the dialog, collecting input data and clicked button."""
        inputs_result = []
        for name, field in self.input_fields.items():
            value = field[ 'entry' ].get()

            # Detect if this input is a password field (has 'show' set)
            input_def = next( ( item for item in self.inputs if item.get( 'name' ) == name ), None )
            if input_def and input_def.get( 'show' ):
                # Wrap securely
                value = SecureString( value )
                # Immediately clear the Entry widget to prevent later access
                field[ 'entry' ].delete( 0, 'end' )

            inputs_result.append( ( name, value ) )

        self._inputtext = {
            'inputs': inputs_result,
            'alternatives': [ ( label, var.get() ) for label, var in self.alternatives_vars.items() ]
        }

        if button is not None:
            self._clicked_button = button

        self.firstentry.delete( 0, 'end' )
        self._master.destroy()

    def preset_keypress( self, event ):
        widget = event.widget
        # Find which input this widget corresponds to (by comparing with self.input_fields)
        if Font( font = widget.cget( 'font' ) ).actual().get('slant') == 'italic':
            # Clear the preset text on first keypress
            widget.delete( 0, 'end' )

            # Restore font to normal style and color to black
            field_definition = next(
                ( val for val in self.input_fields.values() if val[ 'entry' ] ==  widget ),
                None
            )[ 'def' ]

            widget.config(
                font = ( 'Calibri', 12, 'normal' ),
                fg = '#000000',
                show = field_definition[ 'show' ] or ''
            )
            self._master.update_idletasks()

    def show( self ):
        """Displays the input dialog with the specified inputs, alternatives, and buttons."""
        row_index = 0
        title_font = Font( family = 'Calibri', size = 14, weight = 'bold' )
        ordinary_font = Font( family = 'Calibri', size = 12, weight = 'normal' )
        preset_font = Font( family = 'Calibri', size = 12, slant = 'italic' )

        # Setup columns for each button
        for i in range( len( self.buttons ) ):
            self._master.columnconfigure( i, weight = 1 )

        if self.message:
            m = Label( self._master, text = self.message, justify = 'left', font = ordinary_font )
            m.grid( row = 0, column = 0, columnspan = len( self.buttons ), padx = 10, pady = 5, sticky = ( N, W ) )
            row_index += 1

        if self.group_separator:
            separator = ttk.Separator( self._master, orient = 'horizontal' )
            separator.grid( row = row_index, columnspan = len( self.buttons ), sticky = ( W, E ), padx = 10, pady = 5 )
            row_index += 1

        # Track unnamed inputs
        unnamed_count = 0

        if self.inputs:
            for i, input_def in enumerate( self.inputs ):
                # Assign a safe name
                if not input_def.get( 'name' ):
                    unnamed_count += 1
                    name = f"Input{ unnamed_count }"
                else:
                    name = input_def[ 'name' ].strip()

                label_text = input_def.get( 'label', name ).strip()
                default = input_def.get( 'default', '' ).strip()
                show = input_def.get( 'show', None )
                preset = input_def.get( 'preset', None )

                lbl = Label( self._master, text = label_text, font = title_font, justify = 'left' )
                lbl.grid( row = row_index, sticky = W, padx = 10 )

                entry = Entry( self._master, font = ordinary_font )
                entry.insert( 0, default )
                entry.grid( row = row_index + 1, padx = 10, pady = 2, sticky = ( W, E ) )

                # Store entry widget by name
                self.input_fields[ name ] = { 'entry': entry , 'def': input_def }

                if self.firstentry is None:
                    self.firstentry = entry

                if preset and not default:
                    entry.insert( 0, preset )
                    entry.config( foreground = '#D3D3D3', font = ( 'Calibri', 12, 'italic' ) )
                elif show is not None:
                    entry.config( show = show[0] if show else None )

                entry.bind( "<KeyPress>", self.preset_keypress )
                row_index += 2

        if self.alternatives:
            if self.group_separator:
                separator = ttk.Separator( self._master, orient = 'horizontal' )
                separator.grid( row = row_index, columnspan = len( self.buttons ), sticky = ( W, E ), padx = 10, pady = [ 10, 5 ] )
                row_index += 1

            row_index += 1
            for j, alternative in enumerate( self.alternatives ):
                grp_frame = Frame( master = self._master )
                grp_frame.grid( row = row_index, column = 0, sticky = W )
                label = alternative.get( 'label', f'Group{ j }' ).strip()
                options = alternative.get( 'options', [] )
                default = alternative.get( 'default', options[ 0 ] if options else '' ).strip()
                var = StringVar( value = default )
                self.alternatives_vars[ label ] = var

                Label( master = grp_frame, text = label, font = title_font, justify = 'left' ).grid(
                    columnspan = len( options ), sticky = 'W', padx = 10
                )

                for i, option in enumerate( options ):
                    rb = Radiobutton( grp_frame, text = option, variable = var, value = option, font = ordinary_font, justify = 'left' )
                    rb.grid( row = row_index + j, column = 1 + i, sticky = W, padx = 5 )
                row_index += 1

        row_index += 1
        for i, btn_text in enumerate( self.buttons ):
            b = Button(
                master = self._master,
                text = btn_text,
                width = 10,
                command = lambda t = btn_text: self.on_closing( t ),
                font = ( 'Calibri', 12, 'bold' if btn_text == self.default_button else 'normal' )
            )
            b.bind( "<Return>", lambda event, t = btn_text: self.on_closing( t ) )
            b.grid( row = row_index, column = i, padx = 5, pady = 10 )
            if btn_text == self.default_button or ( self.default_button is None and i == 0 ):
                self._default_button_to_focus = b

        self._master.bind( '<Return>', lambda event: self.on_closing(
            self._clicked_button or self.default_button or self.buttons[0]
        ) )
        self._master.update_idletasks()
        width = self._master.winfo_width()
        frm_width = self._master.winfo_rootx() - self._master.winfo_x()
        win_width = width + 2 * frm_width
        height = self._master.winfo_height()
        titlebar_height = self._master.winfo_rooty() - self._master.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self._master.winfo_screenwidth() // 2 - win_width // 2
        y = self._master.winfo_screenheight() // 2 - win_height // 2
        self._master.geometry( f'{ width }x{ height }+{ x }+{ y }' )
        self._master.update_idletasks()

        self._master.attributes( '-topmost', True )
        self._master.protocol( "WM_DELETE_WINDOW", self.on_closing )

        self._master.focus_force()
        if self.inputs and len( self.inputs ) > 0:
            self.firstentry.focus()
        else:
            self._default_button_to_focus.focus()

        self._master.mainloop()

    def get( self, dictionary = False, wipe_after_get = False ):
        """
        Retrieves the input data and clicked button after the dialog is closed.

        Parameters:
            dictionary (bool): If True, returns a dictionary with inputs and alternatives.
            wipe_after_get (bool): If True, SecureString values are wiped from memory immediately 
                                after retrieval, and cannot be accessed again.
        """
        if not hasattr( self, "_passwords_wiped" ):
            self._passwords_wiped = False

        inputs_dict = dict( self._inputtext['inputs'] ) if self.inputs else None
        alternatives_dict = dict( self._inputtext['alternatives'] ) if self.alternatives else None

        if wipe_after_get:
            if not self._passwords_wiped and inputs_dict:
                for key, value in inputs_dict.items():
                    if isinstance( value, SecureString ):
                        val_str = value.get()  # retrieve before wiping
                        value.wipe()
                        inputs_dict[key] = val_str  # store as plain string
                self._passwords_wiped = True  # prevent future access
            else:
                # Passwords already wiped, return empty strings
                if inputs_dict:
                    for key, value in inputs_dict.items():
                        # Remove value if it is a SecureString
                        if isinstance( value, SecureString ):
                            inputs_dict[key] = ""

        if not dictionary:
            return ( inputs_dict, alternatives_dict, self._clicked_button )
        else:
            result = { 'button': self._clicked_button }
            if inputs_dict is not None:
                result[ 'inputs' ] = inputs_dict
            if alternatives_dict is not None:
                result[ 'alternatives' ] = alternatives_dict
            return result
