"""
Console utilities for controlling terminal screen.


Package contains two main classes for working with console windows and text.

- **ConsoleHelper**: Class to aid in console window control and text output including
    - writing to specific locations.
    - clearing portions of the screen
    - colorized output

- **ConsoleInputHelper**: Class providing input prompt with:
    - Input field editing (i.e. controlling valid input)
    - Wait time, timeout before default response is returned


Additionally, helper classes/namespaces provided:

- **ConsoleColor**: Color codes for ansi output 
    (see :func:`~dt_tools.console.console_helper.ConsoleHelper.cwrap()` function).
- **CursorShape**: Ansi codes for controlling cursor shape.

"""
import os
import re
import signal
import sys
import time
from enum import Enum
from typing import Final, List, Tuple, Union
import threading

from loguru import logger as LOGGER

from dt_tools.misc.helpers import StringHelper
from dt_tools.os.os_helper import OSHelper

# LOCK = threading.Lock()

if OSHelper.is_windows():
    import msvcrt
    from ctypes import byref, windll, wintypes  # noqa: F401
else:
    import termios
    import tty

# TODO:
#   update _output_to_terminal to allow for printing to stderr OR stdout (default)

class _ConsoleControl:
    """Console control characters."""
    ESC: Final = "\x1B"
    BELL: Final = '\a'
    CEND: Final = f'{ESC}[0m'

class ColorFG:
    """ Console font colors to be used with :func:`~dt_tools.console.console_helper.ConsoleHelper.cwrap()`."""
    DEFAULT: Final = f'{_ConsoleControl.ESC}[39m'
    BLACK: Final  = f'{_ConsoleControl.ESC}[30m'
    RED: Final    = f'{_ConsoleControl.ESC}[31m'
    GREEN: Final  = f'{_ConsoleControl.ESC}[32m'
    YELLOW: Final = f'{_ConsoleControl.ESC}[33m'
    BLUE: Final   = f'{_ConsoleControl.ESC}[34m'
    VIOLET: Final = f'{_ConsoleControl.ESC}[35m'
    BEIGE: Final  = f'{_ConsoleControl.ESC}[36m'
    WHITE: Final = f'{_ConsoleControl.ESC}[37m'

    GREY: Final    = f'{_ConsoleControl.ESC}[90m'
    RED2: Final    = f'{_ConsoleControl.ESC}[91m'
    GREEN2: Final  = f'{_ConsoleControl.ESC}[92m'
    YELLOW2: Final = f'{_ConsoleControl.ESC}[93m'
    BLUE2: Final   = f'{_ConsoleControl.ESC}[94m'
    VIOLET2: Final = f'{_ConsoleControl.ESC}[95m'
    BEIGE2: Final  = f'{_ConsoleControl.ESC}[96m'
    WHITE2: Final  = f'{_ConsoleControl.ESC}[97m'

class ColorBG:
    """Console background font colors to be used with :func:`~dt_tools.console.console_helper.ConsoleHelper.cwrap()`."""
    DEFAULT: Final = f'{_ConsoleControl.ESC}[49m'
    BLACK: Final   = f'{_ConsoleControl.ESC}[40m'
    RED: Final     = f'{_ConsoleControl.ESC}[41m'
    GREEN: Final   = f'{_ConsoleControl.ESC}[42m'
    YELLOW: Final  = f'{_ConsoleControl.ESC}[43m'
    BLUE: Final    = f'{_ConsoleControl.ESC}[44m'
    VIOLET: Final  = f'{_ConsoleControl.ESC}[45m'
    BEIGE: Final   = f'{_ConsoleControl.ESC}[46m'
    WHITE: Final   = f'{_ConsoleControl.ESC}[47m'

    GREY: Final    = f'{_ConsoleControl.ESC}[100m'
    RED2: Final    = f'{_ConsoleControl.ESC}[101m'
    GREEN2: Final  = f'{_ConsoleControl.ESC}[102m'
    YELLOW2: Final = f'{_ConsoleControl.ESC}[103m'
    BLUE2: Final   = f'{_ConsoleControl.ESC}[104m'
    VIOLET2: Final = f'{_ConsoleControl.ESC}[105m'
    BEIGE2: Final  = f'{_ConsoleControl.ESC}[106m'
    WHITE2: Final  = f'{_ConsoleControl.ESC}[107m'

class TextStyle:
    """Constants for formatting strings."""
    TRANSPARENT: Final = f'{_ConsoleControl.ESC}[0m' 
    RESET: Final       = f'{_ConsoleControl.ESC}[0m'
    BOLD: Final        = f'{_ConsoleControl.ESC}[1m'
    DIM: Final         = f'{_ConsoleControl.ESC}[2m]'
    ITALIC: Final      = f'{_ConsoleControl.ESC}[3m'
    UNDERLINE: Final   = f'{_ConsoleControl.ESC}[4m'
    BLINK: Final       = f'{_ConsoleControl.ESC}[5m'
    BLINK2: Final      = f'{_ConsoleControl.ESC}[6m'
    SELECTED: Final    = f'{_ConsoleControl.ESC}[7m'
    HIDDEN: Final      = f'{_ConsoleControl.ESC}[8m'
    STRIKETHRU: Final  = f'{_ConsoleControl.ESC}[9m'
    INVERSE: Final     = f'{_ConsoleControl.ESC}[k'
    SPACER: Final      = ' ͏'

class CursorShape(Enum):
    """Constants defining available cursor shapes."""
    DEFAULT             = f'{_ConsoleControl.ESC}[0 q'
    BLINKING_BLOCK      = f'{_ConsoleControl.ESC}[1 q'
    STEADY_BLOCK        = f'{_ConsoleControl.ESC}[2 q'
    BLINKING_UNDERLINE  = f'{_ConsoleControl.ESC}[3 q'
    STEADY_UNDERLINE    = f'{_ConsoleControl.ESC}[4 q'
    BLINKING_BAR        = f'{_ConsoleControl.ESC}[5 q'
    STEADY_BAR          = f'{_ConsoleControl.ESC}[6 q'

class _CursorAttribute(Enum):
    """Cursor control characters (Visability, Blink?)."""
    HIDE = f'{_ConsoleControl.ESC}[?25l'
    SHOW = f'{_ConsoleControl.ESC}[?25h'

class _CursorClear:
    EOS: Final = f'{_ConsoleControl.ESC}[0J'
    """Clear to End-Of-Screen."""
    BOS: Final = f'{_ConsoleControl.ESC}[1J'
    """Clear to Beginning-Of-Screen."""
    LINE: Final = f'{_ConsoleControl.ESC}[2K'
    """Clear current line."""
    EOL: Final = f'{_ConsoleControl.ESC}[0K'
    """Clear from current position to End-Of-Line."""
    BOL: Final = f'{_ConsoleControl.ESC}[1K'
    """Clear from current position to Beginning-Of-Line."""
    SCREEN: Final = f'{_ConsoleControl.ESC}[2J'
    """Clear entire screen."""

class WindowControl:
    """Window control characters (Hide/Show, Title)."""
    WINDOW_HIDE: Final  = f'{_ConsoleControl.ESC}[2t'
    WINDOW_SHOW: Final  = f'{_ConsoleControl.ESC}[1t'
    WINDOW_TITLE: Final = f'{_ConsoleControl.ESC}]2;%title%\a'


# https://docs.microsoft.com/en-us/windows/console/console-virtual-terminal-sequences
# https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
# https://invisible-island.net/xterm/ctlseqs/ctlseqs.html

# ==========================================================================================================
class ConsoleHelper():
    """
    Class to assist with console output.  
    
    Methods to:

        - Set cursor shape and visibility.
        - Set console window title.
        - Clear functions.
        - Cursor control (up, down, left, right, move to location,...).

    Example::
        from dt_tools.console.console_helper import ConsoleHelper, ConsoleColors

        con = ConsoleHelper()
        con.clear_screen(cursor_home=True)

        console_size = con.get_console_size()
        row, col = con.cursor_current_position()
        con.print_at(5,5, f'Console size: {console_size}, cur pos: {row},{col}', eol='\\n')
        
        token = f'Test {con.cwrap("Yellow", ConsoleColors.CYELLOW)} string')
        con.print_at(5, 10, token)
        
    """
    LAST_CONSOLE_STR: str = None
    
    @classmethod
    def cursor_set_attribute(cls, attr: Union[_CursorAttribute, str]):
        token = attr.value if isinstance(attr, _CursorAttribute) else attr
        cls._output_to_terminal(token)

    @classmethod
    def cursor_set_shape(cls, shape: Union[CursorShape, str]):
        token = shape.value if isinstance(shape, CursorShape) else shape
        cls._output_to_terminal(token)

    @classmethod
    def get_console_size(cls) -> Tuple[int, int]:
        """
        Return console size in rows and columns.

        Returns:
            Size as (rows, columns).
        """
        try:
            size = os.get_terminal_size()
            rows = int(size.lines)
            columns = int(size.columns)
        except OSError:
            rows = 0
            columns = 0
        return (rows, columns)

    @classmethod
    def valid_console(cls) -> bool:
        try:
            _ = os.get_terminal_size()
            return True
        except OSError:
            return False
        
    @classmethod
    def console_hide(cls):
        """Minimize console/terminal window"""
        cls._output_to_terminal(WindowControl.WINDOW_HIDE)
    
    @classmethod
    def console_show(cls):
        """Restore console/terminal window"""
        cls._output_to_terminal(WindowControl.WINDOW_SHOW)
        
    @classmethod
    def set_console_viewport(cls, start_row: int = None, end_row: int = None):
        """
        Set console scrollable area to start_row / end_row.  Default is whole screen.

        The viewport defines area (rows) text scrolls within.  If no
        arguments provided, viewport is defaulted to whole screen.

        Keyword Arguments:
            start_row: Staring row of viewport (default: {None}).
            end_row: Ending row of viewport (default: {None}).

        Raises:
            ValueError: Invalid start|end row.
        """

        max_row, max_col = cls.get_console_size()
        starting_row = 1 if start_row is None else start_row
        ending_row = int(max_row) if end_row is None else end_row
        if starting_row < 1 or starting_row > ending_row or starting_row > max_row:
            raise ValueError(f"set_viewport(): Invalid start row: {start_row}")
        if ending_row > max_row:
            raise ValueError(f'set_viewport(): Invalid end row: {end_row}')

        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{starting_row};{ending_row}r')

    @classmethod
    def console_title(cls, title: str):
        """
        Set the console/window title.

        Arguments:
            title: String to be displayed on the title bar.
        """
        title_cmd = WindowControl.WINDOW_TITLE.replace("%title%", title)
        print(title_cmd)
        cls._output_to_terminal(title_cmd)

    @classmethod
    def cursor_current_position(cls) -> Tuple[int, int]:
        """
        Current cursor location.

        Returns:
            Cusor location: (row, col).
        """
        if OSHelper.is_windows():
            return cls._get_windows_cursor_position()
        
        return cls._get_linux_cursor_position()
            

    @classmethod
    def cursor_save_position(cls):
        """
        Save cursor position, can be restored with restore_position() call.
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[s')

    @classmethod
    def cursor_restore_position(cls):
        """
        Restore cursor position, saved with the save_position() call.
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[u')

    @classmethod
    def cursor_off(cls):
        cls._output_to_terminal(_CursorAttribute.HIDE.value)

    @classmethod
    def cursor_on(cls):
        """Turn console cursor on"""
        cls._output_to_terminal(_CursorAttribute.SHOW.value)

    @classmethod
    def clear_screen(cls, cursor_home: bool = True):
        """
        Clear screen and home cursor.

        Keyword Arguments:
            cursor_home: If true home cursor else leave at current position (default: {True}).
        """
        cls._output_to_terminal(_CursorClear.SCREEN)
        if cursor_home:
            cls.cursor_move(1, 1)

    @classmethod
    def clear_to_EOS(cls):
        """Clear from cursor to end of screen"""
        cls._output_to_terminal(_CursorClear.EOS)

    @classmethod
    def clear_to_BOS(cls):
        """Clear from cursor to beginning of screen"""
        cls._output_to_terminal(_CursorClear.BOS)

    @classmethod
    def clear_line(cls, row_offset: int = 0):
        """
        Clear console line, and position cursor at beginning of line.

        Args:
            row_offset (int, optional): Offset of line to clear. Defaults to 0.
        """
        if row_offset < 0:
            cls.cursor_up(abs(row_offset))
        elif row_offset > 0:
            cls.cursor_down(row_offset)
        cls._output_to_terminal(_CursorClear.LINE)
        cls.cursor_move(-1, 1)

    @classmethod
    def clear_to_EOL(cls):
        """Clear from cursor to end of line"""
        cls._output_to_terminal(_CursorClear.EOL)
    
    @classmethod
    def clear_to_BOL(cls):
        """Clear from cursor to beginning of line"""
        cls._output_to_terminal(_CursorClear.BOL)

    @classmethod
    def cursor_up(cls, steps: int = 1):
        """
        Move cursor up.

        Keyword Arguments:
            steps: Number of rows to move up (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}A')

    @classmethod
    def cursor_down(cls, steps: int = 1):
        """
        Move cursor down.

        Keyword Arguments:
            steps: Number of rows to move down (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}B')

    @classmethod
    def cursor_right(cls, steps: int = 1):
        """
        Move cursor right.

        Keyword Arguments:
            steps: Number of columns to move right (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}C')

    @classmethod
    def cursor_left(cls, steps: int = 1):
        """
        Move cursor left.

        Keyword Arguments:
            steps: Number of columns to move left (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}D')

    @classmethod
    def cursor_scroll_up(cls, steps: int = 1):
        """
        Scroll screen contents up.

        Keyword Arguments:
            steps: Number of row to scroll up (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}S')

    @classmethod
    def cursor_scroll_down(cls, steps: int = 1):
        """
        Scroll screen contents down.

        Keyword Arguments:
            steps: Number of row to scroll down (default: {1}).
        """
        cls._output_to_terminal(f'{_ConsoleControl.ESC}[{steps}T')

    @classmethod
    def cursor_move(cls, row:int = -1, column:int = -1) -> bool:
        """
        Move cursor to spefic location on console.

        If row or column is not set, current position (row or column) will be used.

        Keyword Arguments:
            row: Row to move cursor (default: {-1}).
            column: Column to move cursor (default: {-1}).

        Returns:
            True if successful, False if location not valid.
        """

        cur_row, cur_col = cls.cursor_current_position()
        if  row <= 0:
            row = int(cur_row)
        if column <= 0:
            column = int(cur_col)
        max_rows, max_columns = cls.get_console_size()
        if row <= 0 or column <= 0:
            LOGGER.debug('cursor_move - row/column must be > 0')
            return False
        if max_rows > 0 and max_columns > 0:
            if column > max_columns or row > max_rows:
                LOGGER.debug((f'cursor_move - row > {max_rows} or col > {max_columns}'))
                return False
        
        cls._output_to_terminal(f"{_ConsoleControl.ESC}[%d;%dH" % (row, column))    
        return True

    @classmethod
    def print(cls, msg, eol='\n', as_bytes:bool = False, to_stderr:bool = False, 
              fg: ColorFG = ColorFG.DEFAULT, bg: ColorBG = ColorBG.DEFAULT, style: TextStyle = TextStyle.TRANSPARENT): # type: ignore
        """
        Print msg to console.

        Arguments:  
            msg (any): Message to print to console.  
            eol (str, optional): End of line character. Defaults to '\\n'.  
            as_bytes (bool, optional): Output as bytes (ie. raw string). Defaults to False.  
            to_stderr (bool, optional): Print to stderr (instead of stdout). Defaults to False.  

        """
        out_msg = cls.cwrap(msg, fg=fg, bg=bg, style=style)
        cls._output_to_terminal(out_msg, eol=eol, as_bytes=as_bytes, to_stderr=to_stderr)

    @classmethod
    def print_at(cls, row: int, col: int, text: str, eol='', as_bytes: bool = False, to_stderr:bool = False) -> bool:
        """
        Print text at specific location on console.

        No new-line will occur unless eol parameter is specifed as '\\n'.

        Arguments:
            row: Target row.
            col: Target column.
            text: String to write to console.

        Keyword Arguments:
            eol: End of line character (default: {''}).
            as_bytes: Output msg as bytes (default: {False}).
            to_stderr: Output to stderr (instead of stdout) (default: {False}).

        Returns:
            True if print to console successful, False if invalid location.
        """
        if cls.cursor_move(row, col):
            cls._output_to_terminal(text, eol=eol, as_bytes=as_bytes, to_stderr=to_stderr)
            return True
        return False
        
    @classmethod
    def print_with_wait(cls, text: str, wait: float = 0.0, eol='\n'):
        """
        Print text at current location and wait specified number of seconds.

        Arguments:
            text: Text to be printed.

        Keyword Arguments:
            wait: Number of seconds to wait (default: {0.0}).
            eol: EndOfLine character (default: {'\\n'}).

        """
        print(text, end=eol, flush=True)
        if wait > 0:
            time.sleep(wait)

    @classmethod
    def display_status(cls, text, wait: int = 0, status_eyecatcher: bool = True):
        """
        Display status message on last row of screen.

        Arguments:
            text: Status message to be displayed.

        Keyword Arguments:
            wait: Number of seconds to wait/pause (default: {0}).
        """
        max_row, max_col = cls.get_console_size()
    
        save_row, save_col = cls.cursor_current_position()
        if status_eyecatcher:
            eyecatcher_style = f'{ColorBG.GREY}{ColorFG.WHITE2}'
            # inverse_token = f'{eyecatcher_style}{TextStyle.INVERSE}'
            text = f'{eyecatcher_style}{text.replace(TextStyle.RESET, f"{TextStyle.RESET}{eyecatcher_style}")}'
            # cls.print(text, as_bytes=True)
            
        cls.print_at(max_row, 1, f'{text}', eol='')     
        cls.clear_to_EOL()
        cls.print_at(1, 1, TextStyle.RESET)   
        cls.cursor_move(save_row, save_col)
        if wait > 0:
            time.sleep(wait)
    
    @classmethod
    def print_line_separator(cls, text: str = '', length: int = -1):
        """
        Print line separator at current cursor position.

        Keyword Arguments:
            text: Text to be displayed within the separator line (default: {''}).
            length: Lenght of the separator line  (default: {-1}).
            if < 0, use console width.
        """
        print(cls.sprint_line_separator(text, length))

    @classmethod
    def sprint_line_separator(cls, text: str = '', length: int = -1) -> str:
        """
        Return string underline (separator) with optional text.

        Keyword Arguments:
            text: Text to be displayed within the separator line (default: {''}).
            length: Length of the separator line  (default: {-1}).
            if < 0, use console width.

        Returns:
            Separator line string.
        """
        if length < 0:
            row, col = cls.cursor_current_position()
            max_rows, max_cols = cls.get_console_size()
            length = max_cols - col
        fill_len = length - len(cls.remove_nonprintable_characters(text))
        if TextStyle.RESET in text:
            color_code = cls.color_code(style=TextStyle.UNDERLINE, fg=ColorFG.DEFAULT, bg=ColorBG.DEFAULT)
            text = text.replace(TextStyle.RESET, f'{TextStyle.RESET}{color_code}')
        # cls.print(text, as_bytes=True)
        line_out = f'{TextStyle.UNDERLINE}{text}{" "*(fill_len-1)}{TextStyle.RESET}'
        return line_out

    @classmethod
    def remove_nonprintable_characters(cls, text: str) -> str:
        """
        Return the length of strings printable characters

        Args:
            text (str): Input string

        Returns:
            int: Number of printable characters
        """
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        result = ansi_escape.sub('', text)    
        return result
    
    @classmethod
    def debug_display_cursor_location(cls, msg:str = ""):
        """
        Display current location (row, col) in status area.

        Keyword Arguments:
            msg: Message text to append after current location (default: {""}).
        """
        cls.display_status(f'Cursor: {str(ConsoleHelper().cursor_current_position())}  {msg}')

    @classmethod
    def cwrap(cls, text: str, fg: ColorFG = None, bg: ColorBG = None, style: Union[List[TextStyle],TextStyle] = None, length: int = -1) -> str:
        """ 
        Wrap text with color codes for console display.
        
        See ConsoleFG, ConsoleBG and ConsoleStyle for control codes

        Arguments:
            **text**: req - String containing text to be colorized.
            **fg**: req -  The FG color OR color string (see ColorFG)
            **bg**: opt - The BG color (see ColorBG)
            **style**: opt - The style to be applied (see TextStyleControls)
            **length**" opt - Length of string. Pad right with spaces, -1 = len(text).

        Returns:
            Updated string.
        """
        w_text = str(text)
        if length < 0:
            length = len(w_text)

        color_code = ''
        if fg and bg and style:
            color_code = ConsoleHelper.color_code(style, fg, bg)
        else:
            if fg:
                color_code += fg
            if bg:
                color_code += bg
            if style:
                if isinstance(style, list):
                   style = ''.join(style) 
                color_code += style

        padded_str = StringHelper.pad_r(w_text, length)
        ret_str =  f'{color_code}{padded_str}{_ConsoleControl.CEND}'
        # cls._output_to_terminal(ret_str, eol='\n', as_bytes=True)
        return ret_str
    

    @classmethod
    def color_code(cls, style: Union[List[TextStyle], TextStyle] = TextStyle.TRANSPARENT, fg: ColorFG = None, bg: ColorBG= None) -> str:
        """
        Create ANSI color code for style, fg color and bg color

        If any parameter (style, fg or bg) is None, current value will be used.

        Args:
            
            **style**: (:class:`~TextStyleControls`, optional): Font style (ie. bold, italic,...).  
            **fg**: (:class:`~ColorFG`, optional): Foreground text color.  
            **bg**: (:class:`~ColorBG`, optional): Background color.  

        Returns:
            str: The ANSI code representing the desired ANSI atributes.
            
        """
        codes = []
        if isinstance(style, list):
            style = ''.join(style) # type: ignore
        codes = [str(style), str(fg), str(bg)]
        format = ';'.join([x.removeprefix(f'{_ConsoleControl.ESC}[').removesuffix('m') for x in codes if x != 'None'])
        code = f'{_ConsoleControl.ESC}[{format}m'
        return code

    # == Private Function ================================================================================= 
    @classmethod   
    def _output_to_terminal(cls, token: str, eol:str='', as_bytes: bool = False, to_stderr: bool = False):
    
        output_str = bytes(token,'utf-8') if as_bytes else token
        if to_stderr:
            print(output_str, end=eol, flush=True, file=sys.stderr)
        else:
            try:
                print(output_str, end=eol, flush=True)
            except UnicodeEncodeError:
                # stderr will escape non-printable characters
                print(output_str, end=eol, flush=True, file=sys.stderr)
                
        cls.LAST_CONSOLE_STR = token

    @classmethod
    def _display_color_palette(cls):
        """
        prints table of formatted text format options
        """
        for style in range(8):
            for fg in range(30, 38):
                token = ''
                for bg in range(40, 48):
                    format = ';'.join([str(style), str(fg), str(bg)])
                    token += '\x1b[%sm %s \x1b[0m' % (format, format)
                print(token)
            print('\n')

    @classmethod
    def _get_windows_cursor_position(cls) -> Tuple[int, int]:
        valid_coords = False
        val_errcnt = 0
        row: int = -1
        col: int = -1
        while not valid_coords and val_errcnt < 3:
            sys.stdout.write("\x1b[6n")
            sys.stdout.flush()
            buffer = bytes()
            while msvcrt.kbhit():
                buffer += msvcrt.getch()
            hex_loc = buffer.decode().replace('\x1b[','').replace('R','')
            # print(hex_loc)
            token = hex_loc.split(';')
            try:
                row = int(token[0])
                col = int(token[1])
                valid_coords = True
            except ValueError as ve:
                val_errcnt += 1
                if val_errcnt == 3:
                    LOGGER.debug(f'cursor_current_postion()-Invalid row/col (hex_loc): {hex_loc} | {token} - {ve}')
        return row, col
    
    @classmethod
    def _get_linux_cursor_position(cls) -> Tuple[int, int]:
        """Gets the current cursor position on the terminal."""

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        row = -1
        col = -1
        try:
            tty.setraw(sys.stdin.fileno())
            sys.stdout.write("\x1b[6n")
            sys.stdout.flush()

            response = ""
            while True:
                char = sys.stdin.read(1)
                if char == "R":
                    break
                response += char

            row, col = map(int, response[2:].split(";"))
        except Exception as e:
            LOGGER.debug(f'cursor_current_position() - Error getting cursor position: {e}')
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)        
        
        return row, col


# ==========================================================================================================
class ConsoleInputHelper():
    """
    Helper for getting input from the console.

    Example::

        from dt_tools.console.console_helper import ConsoleInputHelper

        ih = ConsoleInputHelper()
        resp = ih.get_input_with_timeout(prompt='Pick a color > ', 
            valid_responses=['Red', 'Blue', 'Green'], 
            default='Blue', 
            timeout_secs=5)
        print(f'You selected: {resp}')    

    """

    YES_NO_RESPONSE: Final[List[str]] = ['Y','y', 'N', 'n']
    """Yes/No valid_argument list constant"""

    @classmethod
    def get_input_with_timeout(cls, prompt: str, valid_responses: list = [],  
                               default: str = None, timeout_secs: int = -1, 
                               parms_ok: bool = False) -> Union[str, Tuple[str, list]]:
        """
        Display a prompt for use input.  
        
        If valid_responses is supplied:
            - input will be validated.  User will be re-prompted on bad input. 
            - default response will be returned after timeout (if specified).

        Arguments:
            **prompt**: Text to be displayed as prompt.
            **valid_responses**: A list of valid responses (default: {[]}).
              User input must match one of the values. 
              If list is empty, all input will be accepted.
            **default**: Default value to be return on timeout (default: {None}).
            **timeout_secs**: Number of seconds to wait for response (default: {-1}).  
              If <0, no timeout, wait until user presses enter.
            **parms_ok**: Allow extra parameter input (default: {False}).
              If True, allows user to provide additional text after the valid response.

        Returns:
            User input or default value (if timeout).

        Example::

            from dt_tools.console.console_helper input ConsoleInputHelper

            ih = ConsoleInputHelper()
            resp = ih.get_input_with_timeout(prompt='Pick a color > ', 
                valid_responses=['Red', 'Blue', 'Green'], 
                default='Blue', 
                timeout_secs=5)
            print(f'You selected: {resp}')

        """
        response: str = ''
        chk_response = ''
        response_params: List = None
        valid_input = False
        while not valid_input:
            if timeout_secs < 0:
                response = input(prompt)
            else:
                try:
                    if OSHelper.is_windows():
                        response = cls._input_with_timeout_win(prompt, timeout_secs, default)
                    else:
                        response = cls._input_with_timeout_nix(prompt, timeout_secs, default)
                except TimeoutError:
                    response = default
                    valid_input = True
            
            if not parms_ok:
                chk_response = response
                response_params = None
            else:
                token = response.split()
                if len(token) > 0:
                    chk_response = token[0]
                    response_params = token[1:]
                else:
                    chk_response = response
                    response_params = None

            if not valid_responses:
                LOGGER.trace('no valid responses to check')
                valid_input = True
            elif chk_response in valid_responses:
                    valid_input = True

        if parms_ok:
            return chk_response, response_params
        
        return chk_response

    @classmethod
    def wait_with_bypass(cls, secs: int):
        """
        Pause execution for specified number of seconds.
        
        User may press enter to resume prior to timeout seconds.

        Arguments:
            secs: Number of seconds to wait.
        """
        cls.get_input_with_timeout("", timeout_secs=secs)

    @classmethod
    def _input_with_timeout_nix(cls,prompt: str, timeout_secs: int, default: str) -> str:
        # set signal handler for *nix systems
        LOGGER.trace("_input_with_timeout_nix()")
        signal.signal(signal.SIGALRM, ConsoleInputHelper._alarm_handler)
        signal.alarm(timeout_secs) # produce SIGALRM in `timeout` seconds

        response = default
        try:
            response = input(prompt)
        finally:
            signal.alarm(0) # cancel alarm
            return response

    @classmethod
    def _input_with_timeout_win(cls, prompt: str, timeout_secs: int,  default: str= None) -> str:
        LOGGER.trace("_input_with_timeout_win()")
        sys.stdout.write(prompt)
        sys.stdout.flush()
        timer = time.monotonic
        endtime = timer() + timeout_secs
        result = []
        while timer() < endtime:
            if msvcrt.kbhit():
                result.append(msvcrt.getwche()) #XXX can it block on multibyte characters?
                endtime = timer() + timeout_secs  # Reset timer each time a key is pressed.
                if result[-1] == '\r':   #XXX check what Windows returns here
                    print('')
                    return ''.join(result[:-1])
            time.sleep(0.04) # just to yield to other processes/threads
        if result:
            print('')
            return ''.join(result)
        elif default:
            print(default)
        raise TimeoutError('Time Expired.')

    def _alarm_handler(signum, frame):
        raise TimeoutError('time expired.')



if __name__ == "__main__":
    from dt_tools.cli.demos.dt_console_demo import console_helper_demo as demo
    from dt_tools.console.console_helper import ColorFG, ConsoleHelper
    demo()
    # print("ConsoleHelper.cwrap('This is a test', style=TextStyle.UNDERLINE, length=30)")
    # token = ConsoleHelper.cwrap('This is a test', style=TextStyle.UNDERLINE, length=30)
    # token2 = ConsoleHelper.remove_nonprintable_characters(token)
    # print(token)
    print("That's all folks!")