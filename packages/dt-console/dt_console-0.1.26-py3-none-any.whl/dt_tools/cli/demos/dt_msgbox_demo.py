"""
This module will demo the dt_tools.console.msgbox capabilities including:

- Showing the 4 types of message boxes (Alert, Confirmation, Prompt and Password)
- Show message boxes with default timeouts
- Show multi-line boxes
- Show how to retrieve message box input, both visible and hidden (i.e. password)

To run this demo standalone:
    `poetry run python -m dt_tools.cli.dt_msgbox_demo`

"""
from dt_tools.console.console_helper import ColorFG
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.os.os_helper import OSHelper

import tkinter as tk

import dt_tools.console.msgbox as msgbox

def demo():
    OSHelper.enable_ctrl_c_handler()

    console.print('')
    console.print_line_separator('Alert box (no timeout)', 40)

    resp = msgbox.alert('This is an alert box', 'ALERT no timeout')
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')

    console.print('')
    console.print_line_separator('Alert box (w/timeout, 3 sec)', 40)
    resp = msgbox.alert('This is an alert box', 'ALERT w/Timeout', timeout=3000)
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')

    txt = ''
    for k,v in tk.__dict__.items():
        if not k.startswith('_') and isinstance(v, int):
            txt += f'{k:20} {v}\n'
    
    console.print('')
    console.print_line_separator('Alert box (multi-line)', 40)
    msgbox.set_font(msgbox.MB_FontFamily.MONOSPACE, msgbox.MB_FontSize.MONOSPACE)
    resp = msgbox.alert(txt,"ALERT-MULTILINE (no timeout)")
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    console.print('')
    console.print_line_separator('Confirmation box (no timeout)', 40)
    msgbox.set_font(msgbox.MB_FontFamily.PROPORTIONAL, msgbox.MB_FontSize.PROPORTIONAL)
    resp = msgbox.confirm('this is a confirm box, no timeout', "CONFIRM")
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    console.print('')
    console.print_line_separator('Confirmation box (3 sec timeout)', 40)
    resp = msgbox.confirm('this is a confirm box, 3 sec timeout', "CONFIRM", timeout=3000)
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    console.print('')
    console.print_line_separator('Prompt box (no timeout)', 40)
    resp = msgbox.prompt('This is a prompt box', 'PROMPT', 'default')
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    console.print('')
    console.print_line_separator('Prompt box (3 sec timeout)', 40)
    resp = msgbox.prompt('This is a prompt box', 'PROMPT (3 sec timeout)', 'default', timeout=3000)
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')
    
    console.print('')
    console.print_line_separator('Password box (no timeout)', 40)
    resp = msgbox.password('This is a password box', 'PASSWORD', 'SuperSecretPassword')
    console.print(f'  returns: {console.cwrap(resp, ColorFG.GREEN)}')

    console.print('')
    console.print(f"End of {console.cwrap('MessageBox', ColorFG.YELLOW)} demo.")

    input('\nPress Enter to continue...')


if __name__ == '__main__':
    demo()