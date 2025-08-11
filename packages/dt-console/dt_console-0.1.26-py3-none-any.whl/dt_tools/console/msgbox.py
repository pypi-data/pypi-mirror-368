"""
Helper to display tkinter Message box on display

Message boxes provided:

    - alert: Alert message box with message text and single OK button.
    - confirm: Confirmation message box with OK/Cancel buttons.  Returns caption of button clicked.
    - prompt: Display message box with text input and OK/Cancel buttons.  Returns text entered, or None if Cancel clicked.
    - password: Displays a passworkd message box and OK/Cancel buttons.  Input is masked. Returns text entered, or None if Cancel clicked.

Features:
    - Ability to set Timeout seconds.  Message box will return 'timeout' when triggered.
    - Confirm message box allows user to customize buttons available.

"""
import tkinter as tk
from typing import List, Tuple, Union
from enum import Enum
from loguru import logger as LOGGER

# This version derived from the below projects:

# Modified BSD License
# PyMsgBox - A simple, cross-platform, pure Python module for JavaScript-like message boxes.
#            By Al Sweigart al@inventwithpython.com

__version__ = "1.0.9"

# Modified BSD License
# Derived from Stephen Raymond Ferg's EasyGui http://easygui.sourceforge.net/
"""
The four functions in PyMsgBox:

 - alert(text='', title='', button='OK')

    Displays a simple message box with text and a single OK button. Returns the text of the button clicked on.

 - confirm(text='', title='', buttons=['OK', 'Cancel'])

    Displays a message box with OK and Cancel buttons. Number and text of buttons can be customized. Returns the text of the button clicked on.

 - prompt(text='', title='' , default='')

    Displays a message box with text input, and OK & Cancel buttons. Returns the text entered, or None if Cancel was clicked.

 - password(text='', title='', default='', mask='*')

    Displays a message box with text input, and OK & Cancel buttons. Typed characters appear as *. Returns the text entered, or None if Cancel was clicked.
"""

"""
TODO Roadmap:
- Be able to specify a custom icon in the message box.
- Be able to place the message box at an arbitrary position (including on multi screen layouts)
- Add mouse clicks to unit testing.
- progress() function to display a progress bar
- Maybe other types of dialog: open, save, file/folder picker, etc.
"""

rootWindowPosition = "+300+200"

class MB_FontFamily:
    """MsgBox Font Types."""
    PROPORTIONAL = ("MS", "Sans", "Serif")
    MONOSPACE = "Courier"

class MB_FontSize(Enum):
    """Font sizes for MsgBox fonts"""
    DEFAULT:int = -1
    PROPORTIONAL:int = 10
    MONOSPACE:int = 9  # a little smaller, because it it more legible at a smaller size
    TEXT:int = 12        # a little larger makes it easier to see


MSGBOX_WIDTH = 400

STANDARD_SELECTION_EVENTS = ["Return", "Button-1", "space"]

# constants for strings: (TODO: for internationalization, change these)
class MB_ButtonType:
    """Constants for Message box buttons (and captions)."""
    OK = "OK"
    CANCEL = "Cancel"
    YES = "Yes"
    NO = "No"
    RETRY = "Retry"
    ABORT = "Abort"
    IGNORE = "Ignore"
    TRY_AGAIN = "Try Again"
    CONTINUE = "Continue"

TIMEOUT_RETURN_VALUE = "Timeout"
"""Value returned when MsgBox times out."""

# Initialize some global variables that will be reset later
_used_font_family = MB_FontFamily.PROPORTIONAL
_used_font_size = MB_FontSize.PROPORTIONAL.value
__choiceboxMultipleSelect = None
__widgetTexts = None
__replyButtonText = None
__choiceboxResults = None
__firstWidget = None
__enterboxText = None
__enterboxDefaultText = ""
__multenterboxText = ""
choiceboxChoices = None
choiceboxWidget = None
entryWidget = None
boxRoot = None
buttonsFrame = None


def set_font(family: MB_FontFamily, size: MB_FontSize = MB_FontSize.DEFAULT):
    global _used_font_family, _used_font_size
    """Set font family and font size

    Arguments:
        family: MB_FontFamily.MONOSPACE or MB_FontFamily.PROPORTIONAL.
        size: Font size, typically 8-12.  If <= 0 will default to
          either MB_FontSize.MONOSPACE or MB_FontSize.PROPORTIONAL depending
          on select family. 
    """
    _used_font_family = family
    if size.value <= MB_FontSize.DEFAULT.value:
        _used_font_size = MB_FontSize.MONOSPACE.value if _used_font_family == MB_FontFamily.MONOSPACE else MB_FontSize.PROPORTIONAL.value
    else:
        _used_font_size = size.value


def _alertTkinter(text="", title="", button=MB_ButtonType.OK, root=None, timeout=None):
    """
    Displays a simple message box with text and a single OK button. 

    Keyword Arguments:
        text: Text content of the message box (default: {""})
        title: Title bar text (default: {""})
        button: Button caption (default: {MB_ButtonType.OK})
        root: Base window (default: {None})
        timeout: Number of seconds to display box (default: {None})

    Returns:
        The text of the button clicked on.
    """
    text = str(text)
    retVal = _buttonbox(
        msg=text, title=title, choices=[str(button)], root=root, timeout=timeout
    )
    return button if retVal is None else retVal

alert = _alertTkinter


def _confirmTkinter(
    text="", title="", buttons=(MB_ButtonType.OK, MB_ButtonType.CANCEL), root=None, timeout=None):
    """
    Displays a Confirmation message box with text and Ok / Cancel buttons. 

    Keyword Arguments:
        text: Text content of the message box (default: {""})
        title: Title bar text (default: {""})
        buttons: A list of button text (default: {(MB_ButtonType.OK, MB_ButtonType.CANCEL)})
        root: Base window (default: {None})
        timeout: Number of seconds to display box (default: {None})

    Returns:
        The text of the button clicked on.
    """

    text = str(text)
    resp = _buttonbox(
        msg=text,
        title=title,
        choices=[str(b) for b in buttons],
        root=root,
        timeout=timeout,
    )

    return resp

confirm = _confirmTkinter


def _promptTkinter(text="", title="", default="", root=None, timeout=None):
    """
    Displays a message box with text input, and OK & Cancel buttons. 

    Keyword Arguments:
        text: Text content of the message box (default: {""})
        title: Title bar text (default: {""})
        default: Default text on timeout (default: {""})
        root: Base window (default: {None})
        timeout: Number of seconds to display box (default: {None})

    Returns:
        Returns the text entered, or None if Cancel was clicked.
    """
    text = str(text)
    return __fillablebox(
        text, title, default=default, mask=None, root=root, timeout=timeout
    )


prompt = _promptTkinter


def _passwordTkinter(text="", title="", default="", mask="*", root=None, timeout=None):
    """
    Displays a message box with text input, and OK & Cancel buttons. 
    
    By default, typed characters are masked as an asterisk(\*) symbol. 

    Keyword Arguments:
        text: Text content of the message box (default: {""})
        title: Title bar text (default: {""})
        mask: Mask character to display on user keystrokes (default: {"*"})
        default: Default text on timeout (default: {""})
        root: Base window (default: {None})
        timeout: Number of seconds to display box (default: {None})

    Returns:
        Returns the text entered, or None if Cancel was clicked.
    """
    text = str(text)
    return __fillablebox(text, title, default, mask=mask, root=root, timeout=timeout)

password = _passwordTkinter


def timeoutBoxRoot():
    global boxRoot, __replyButtonText, __enterboxText
    try:
        boxRoot.destroy() # timeoutBoxRoot
    except Exception as ex:
        LOGGER.trace(f'timeoutBoxRoot()-{repr(ex)}')

    __replyButtonText = TIMEOUT_RETURN_VALUE
    __enterboxText = TIMEOUT_RETURN_VALUE


def _buttonbox(msg: str, title: str, choices: Union[List,Tuple], root=None, timeout=None):
    """
    Display a msg, a title, and a set of buttons.

    The buttons are defined by the members of the choices list.

    Arguments:
        msg: Text content of the message box
        title: Title bar text
        choices: A list or tuple of the choices to be displayed

    Keyword Arguments:
        root: Base window (default: {None})
        timeout: Number of seconds to display box (default: {None})

    Returns:
        Text caption of the Button clicked.
    """

    global boxRoot, __replyButtonText, __widgetTexts, buttonsFrame

    # Initialize __replyButtonText to the first choice.
    # This is what will be used if the window is closed by the close button.
    __replyButtonText = choices[0]

    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)
        boxRoot.withdraw()
    else:
        boxRoot = tk.Tk()
        boxRoot.withdraw()

    boxRoot.title(title)
    boxRoot.iconname("Dialog")
    boxRoot.geometry(rootWindowPosition)
    boxRoot.minsize(400, 100)

    # ------------- define the messageFrame ---------------------------------
    messageFrame = tk.Frame(master=boxRoot)
    messageFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the buttonsFrame ---------------------------------
    buttonsFrame = tk.Frame(master=boxRoot)
    buttonsFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # -------------------- place the widgets in the frames -----------------------
    messageWidget = tk.Message(messageFrame, text=msg, width=MSGBOX_WIDTH)
    # messageWidget.configure(font=(MB_FontFamily.PROPORTIONAL, MB_FontSize.PROPORTIONAL))
    messageWidget.configure(font=(_used_font_family, _used_font_size))
    messageWidget.pack(side=tk.TOP, expand=tk.YES, fill=tk.X, padx="3m", pady="3m")

    __put_buttons_in_buttonframe(choices)

    # -------------- the action begins -----------
    # put the focus on the first button
    __firstWidget.focus_force()
    boxRoot.attributes("-topmost", True)  # agd
    boxRoot.deiconify()
    _timeout_id: str = None
    if timeout is not None:
        _timeout_id = boxRoot.after(timeout, timeoutBoxRoot)
    boxRoot.mainloop()

    if _timeout_id is not None:
        boxRoot.after_cancel(_timeout_id)

    try:
        boxRoot.destroy()
    except tk.TclError:
        if __replyButtonText != TIMEOUT_RETURN_VALUE:
            __replyButtonText = None

    if root:
        root.deiconify()
    return __replyButtonText


def __put_buttons_in_buttonframe(choices):
    """Put the buttons in the buttons frame"""
    global __widgetTexts, __firstWidget, buttonsFrame

    __firstWidget = None
    __widgetTexts = {}

    i = 0

    for buttonText in choices:
        tempButton = tk.Button(buttonsFrame, takefocus=1, text=buttonText)
        _bindArrows(tempButton)
        tempButton.pack(
            expand=tk.YES, side=tk.LEFT, padx="1m", pady="1m", ipadx="2m", ipady="1m"
        )

        # remember the text associated with this widget
        __widgetTexts[tempButton] = buttonText

        # remember the first widget, so we can put the focus there
        if i == 0:
            __firstWidget = tempButton
            i = 1

        # for the commandButton, bind activation events to the activation event handler
        commandButton = tempButton
        handler = __buttonEvent
        for selectionEvent in STANDARD_SELECTION_EVENTS:
            commandButton.bind("<%s>" % selectionEvent, handler)

        if MB_ButtonType.CANCEL in choices:
            commandButton.bind("<Escape>", __cancelButtonEvent)


def _bindArrows(widget, skipArrowKeys=False):
    widget.bind("<Down>", _tabRight)
    widget.bind("<Up>", _tabLeft)

    if not skipArrowKeys:
        widget.bind("<Right>", _tabRight)
        widget.bind("<Left>", _tabLeft)


def _tabRight(event):
    boxRoot.event_generate("<Tab>")


def _tabLeft(event):
    boxRoot.event_generate("<Shift-Tab>")


def __buttonEvent(event):
    """
    Handle an event that is generated by a person clicking a button.
    """
    global boxRoot, __widgetTexts, __replyButtonText
    __replyButtonText = __widgetTexts[event.widget]
    boxRoot.quit()  # quit the main loop


def __cancelButtonEvent(event):
    """Handle pressing Esc by clicking the Cancel button."""
    global boxRoot, __widgetTexts, __replyButtonText
    __replyButtonText = MB_ButtonType.CANCEL
    boxRoot.quit()


def __fillablebox(msg, title="", default="", mask=None, root=None, timeout=None):
    """
    Show a box in which a user can enter some text.
    You may optionally specify some default text, which will appear in the
    enterbox when it is displayed.
    Returns the text that the user entered, or None if he cancels the operation.
    """

    global boxRoot, __enterboxText, __enterboxDefaultText
    global cancelButton, entryWidget, okButton

    if title is None:
        title == ""
    if default is None:
        default = ""
    __enterboxDefaultText = default
    __enterboxText = __enterboxDefaultText

    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)
        boxRoot.withdraw()
    else:
        boxRoot = tk.Tk()
        boxRoot.withdraw()

    boxRoot.title(title)
    boxRoot.iconname("Dialog")
    boxRoot.geometry(rootWindowPosition)
    boxRoot.bind("<Escape>", __enterboxCancel)

    # ------------- define the messageFrame ---------------------------------
    messageFrame = tk.Frame(master=boxRoot)
    messageFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the buttonsFrame ---------------------------------
    buttonsFrame = tk.Frame(master=boxRoot)
    buttonsFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the entryFrame ---------------------------------
    entryFrame = tk.Frame(master=boxRoot)
    entryFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the buttonsFrame ---------------------------------
    buttonsFrame = tk.Frame(master=boxRoot)
    buttonsFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # -------------------- the msg widget ----------------------------
    messageWidget = tk.Message(messageFrame, width="4.5i", text=msg)
    # messageWidget.configure(font=(MB_FontFamily.PROPORTIONAL, MB_FontSize.PROPORTIONAL))
    messageWidget.configure(font=(_used_font_family, _used_font_size))
    messageWidget.pack(side=tk.RIGHT, expand=1, fill=tk.BOTH, padx="3m", pady="3m")

    # --------- entryWidget ----------------------------------------------
    entryWidget = tk.Entry(entryFrame, width=40)
    _bindArrows(entryWidget, skipArrowKeys=True)
    # entryWidget.configure(font=(MB_FontFamily.PROPORTIONAL, TEXT_ENTRY_FONT_SIZE))
    entryWidget.configure(font=(_used_font_family, MB_FontSize.TEXT.value))
    if mask:
        entryWidget.configure(show=mask)
    entryWidget.pack(side=tk.LEFT, padx="3m")
    entryWidget.bind("<Return>", __enterboxGetText)
    entryWidget.bind("<Escape>", __enterboxCancel)

    # put text into the entryWidget and have it pre-highlighted
    if __enterboxDefaultText != "":
        entryWidget.insert(0, __enterboxDefaultText)
        entryWidget.select_range(0, tk.END)

    # ------------------ ok button -------------------------------
    okButton = tk.Button(buttonsFrame, takefocus=1, text=MB_ButtonType.OK)
    _bindArrows(okButton)
    okButton.pack(expand=1, side=tk.LEFT, padx="3m", pady="3m", ipadx="2m", ipady="1m")

    # for the commandButton, bind activation events to the activation event handler
    commandButton = okButton
    handler = __enterboxGetText
    for selectionEvent in STANDARD_SELECTION_EVENTS:
        commandButton.bind("<%s>" % selectionEvent, handler)

    # ------------------ cancel button -------------------------------
    cancelButton = tk.Button(buttonsFrame, takefocus=1, text=MB_ButtonType.CANCEL)
    _bindArrows(cancelButton)
    cancelButton.pack(
        expand=1, side=tk.RIGHT, padx="3m", pady="3m", ipadx="2m", ipady="1m"
    )

    # for the commandButton, bind activation events to the activation event handler
    commandButton = cancelButton
    handler = __enterboxCancel
    for selectionEvent in STANDARD_SELECTION_EVENTS:
        commandButton.bind("<%s>" % selectionEvent, handler)

    # ------------------- time for action! -----------------
    entryWidget.focus_force()  # put the focus on the entryWidget
    boxRoot.attributes("-topmost", True)     # agd
    boxRoot.deiconify()
    _timeout_id: str = None
    if timeout is not None:
        _timeout_id = boxRoot.after(timeout, timeoutBoxRoot)
        # boxRoot.after(timeout, )
    boxRoot.mainloop()  # run it!

    # -------- after the run has completed ----------------------------------
    if _timeout_id is not None:
        boxRoot.after_cancel(_timeout_id)

    if root:
        root.deiconify()
    try:
        boxRoot.destroy()  # button_click didn't destroy boxRoot, so we do it now
    except tk.TclError:
        if __enterboxText != TIMEOUT_RETURN_VALUE:
            return None

    return __enterboxText


def __enterboxGetText(event):
    global __enterboxText

    __enterboxText = entryWidget.get()
    boxRoot.quit()


def __enterboxRestore(event):
    global entryWidget

    entryWidget.delete(0, len(entryWidget.get()))
    entryWidget.insert(0, __enterboxDefaultText)


def __enterboxCancel(event):
    global __enterboxText

    __enterboxText = None
    boxRoot.quit()

if __name__ == "__main__":
    alert('This is an alert box', 'ALERT1')
    _used_font_family = MB_FontFamily.MONOSPACE
    _used_font_size = MB_FontSize.MONOSPACE.value

    # MSGBOX_WIDTH = 600
    txt = ''
    for k,v in tk.__dict__.items():
        if not k.startswith('_') and isinstance(v, int):
            txt += f'{k:20} {v}\n'
    
    alert(txt,"ALERT2-MULTILINE")

    confirm('this is a confirm box, no timeout', "CONFIRM")
    confirm('this is a confirm box, 5 sec timeout', "CONFIRM", timeout=5000)
    prompt('This is a prompt box', 'PROMPT', 'default')
    password('This is a password box', 'PASSWORD', 'default')
