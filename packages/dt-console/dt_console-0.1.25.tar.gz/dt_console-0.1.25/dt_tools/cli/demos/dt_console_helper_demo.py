"""
This module will demo the dt_tools.console.console_helper capabilities including:

- cursor positioning (move to, print at, ...)
- console clearing (screen, line, to EOL, to BOL,...)
- setting FG and BG colors, wrapping words with color, ...

"""
from dt_tools.console.console_helper import ColorBG, ColorFG, TextStyle, _CursorAttribute, CursorShape
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.console.console_helper import ConsoleInputHelper as console_input
from dt_tools.os.os_helper import OSHelper
import time

def demo():
    OSHelper.enable_ctrl_c_handler()
    wait_seconds = 2

    console.cursor_set_shape(CursorShape.BLINKING_UNDERLINE)
    console.clear_screen(cursor_home=True)
    row, col = console.cursor_current_position()
    console_size = console.get_console_size()
    console.set_console_viewport(1,console_size[0]-1)
    console.print_with_wait(f'Console size: {console_size}, cur pos: {row},{col}', wait_seconds, eol='\n\n')
    console.cursor_save_position()

    console.print_line_separator('Test color attributes', 40)
    token = console.cwrap('string', fg=ColorFG.RED, bg=ColorBG.WHITE, style=TextStyle.ITALIC)
    console.print(f'This {token} is Red Italic on White BG')
    console.print(f'RAW: This {token} is Red Italic on White BG', as_bytes=True)
    print(f'This {console.cwrap("string", ColorFG.GREEN)} is Green')
    print(f'This {console.cwrap("string", ColorFG.RED)} is Red')
    print(f'This {console.cwrap("string", ColorFG.RED, None, TextStyle.ITALIC)} is Italic Red')
    print(f'This {console.cwrap("string", ColorFG.RED, None, TextStyle.BOLD)} is Bold Red\n')
    console_input.get_input_with_timeout('Press ENTER to continue ', timeout_secs=10)
    
    console.cursor_restore_position()
    console.clear_to_EOS()

    console.print_line_separator('Test cursor attributes', 40)
    for attr in _CursorAttribute:
        console.debug_display_cursor_location()
        console.print_with_wait(f'CURSOR: {attr}', eol=' ')
        console.cursor_set_attribute(attr)
        console.print_with_wait('', wait_seconds, eol='')
        print('')
    print('')
    
    console_input.get_input_with_timeout('Press ENTER to continue ', timeout_secs=10)
    console.cursor_restore_position()
    console.clear_to_EOS()

    console.print_line_separator('Test cursor shape...', 40)
    for shape in CursorShape:
        console.debug_display_cursor_location()
        console.cursor_set_shape(shape)
        console.print(f'CURSOR: {shape}', eol= ' ')
        console.print_with_wait('', wait_seconds, eol='')
        # console.print_with_wait(f'CURSOR: {shape} {shape.value}', wait_seconds, eol = ' ')
        print('')
    
    console_input.get_input_with_timeout('Press ENTER to continue ', timeout_secs=10)
    console.clear_screen()

    console.cursor_set_shape(CursorShape.STEADY_BLOCK)            
    console.display_status('Test Rows...')
    for row in range(1, console_size[0]):
        console.print_at(row, 60, f'Row {row}', eol='')
    console.cursor_move(row=1,column=1)
    console.print_with_wait(f'Console size: {console_size} and current position: {row},{col}', wait_seconds)
    console.cursor_move(5,1)
    print(f'Look at the beautiful {console.cwrap("blue",ColorFG.BLUE2, style=TextStyle.BOLD)} sky')
    console.debug_display_cursor_location(f'After {console.cwrap("blue",ColorFG.BLUE2, style=TextStyle.BOLD)} sky')
    time.sleep(wait_seconds)

    print('Check cursor positioning...')
    console.print_at(10, 5, "Should print at  location 10,5 xxxxxxx", eol='')
    console.debug_display_cursor_location()
    time.sleep(wait_seconds)
    console.cursor_left(7)

    console.clear_to_EOL()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('EOL',ColorFG.GREEN2, style=TextStyle.BOLD)}")
    time.sleep(wait_seconds)

    print('abc', end='')
    console.debug_display_cursor_location()
    time.sleep(wait_seconds)

    console.clear_to_BOL()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('BOL',ColorFG.GREEN2, style=TextStyle.BOLD)}")
    time.sleep(wait_seconds)

    console.clear_to_BOS()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('BOS',ColorFG.GREEN2, style=TextStyle.BOLD)}")
    time.sleep(wait_seconds)

    console.cursor_move(12,1)
    console.debug_display_cursor_location( "Moved to 12,1")
    time.sleep(wait_seconds)

    console.clear_to_EOS()
    console.debug_display_cursor_location(f"Clear to {console.cwrap('EOS',ColorFG.GREEN2, style=TextStyle.BOLD)}")
    time.sleep(wait_seconds)

    console.print_with_wait(f'Console size: {console_size}, cur pos: {row},{col}', wait_seconds, eol='\n\n')

    console.clear_screen()
    console.set_console_viewport(start_row=2, end_row=console_size[0]-1)
    console.print_line_separator('Check scrolling...', 40)
    for row in range(1, 50):
        console.print(f'Row {row}')    
        if row % 5 == 0:
            console.debug_display_cursor_location('Scrolling...')
            time.sleep(.5)
    console_input.get_input_with_timeout('Press ENTER to continue ', timeout_secs=10)

    console.set_console_viewport()
    console.clear_screen()
    console.print_line_separator('Display color palette, codes are [style,fg,bg]...', 40)
    console.print('')
    time.sleep(wait_seconds)
    console._display_color_palette()

    console.cursor_set_shape(CursorShape.DEFAULT)
    print(f"End of {console.cwrap('ConsoleHelper', ColorFG.YELLOW)} demo.")

if __name__ == '__main__':
    demo()