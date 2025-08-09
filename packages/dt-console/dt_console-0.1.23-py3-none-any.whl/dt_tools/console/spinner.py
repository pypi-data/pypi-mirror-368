"""
Spinner control to provide visual feedback of process activity.

Features:
   - Customizable display.    
   - Optionally, display elapsed time.
   - Selectable spinner icons.

Example::
    from dt_tools.console.spinner import Spinner, SpinnerType

    spinner = Spinner("In progress", SpinnerType.DOTS, True)
    spinner.start_spinner()
    # Do some work....
    spinner.stop_spinner()
    
"""
import threading
import time
from datetime import datetime as dt
from enum import Enum

from loguru import logger as LOGGER
from dt_tools.console.console_helper import ConsoleHelper


class SpinnerType(Enum):
    """Spinner types, used in Spinner constructor"""
    NORMAL_SPINNER={"speed": .075, "char_list": ['|','/','-','\\']}
    ARC = {"speed": .075, "char_list":  ["◜","◠","◝","◞","◡","◟"]}
    BALL_BOUNCER = {"speed": .1, "char_list": ["( ●    )","(  ●   )","(   ●  )","(    ● )","(     ●)","(    ● )","(   ●  )","(  ●   )","( ●    )","(●     )"]}
    BALLOON = {"speed": .1, "char_list": [".","o","O","°","O","o","."]}
    BLOCK_BLINK={"speed": .25, "char_list": [' ','▓', '█']}
    BLOCK_BOUNCER = {"speed": .1, "char_list": ["▐⠂       ▌","▐⠈       ▌","▐ ⠂      ▌","▐ ⠠      ▌","▐  ⡀     ▌","▐  ⠠     ▌","▐   ⠂    ▌","▐   ⠈    ▌","▐    ⠂   ▌","▐    ⠠   ▌","▐     ⡀  ▌","▐     ⠠  ▌","▐      ⠂ ▌","▐      ⠈ ▌","▐       ⠂▌","▐       ⠠▌","▐       ⡀▌","▐      ⠠ ▌","▐      ⠂ ▌","▐     ⠈  ▌","▐     ⠂  ▌","▐    ⠠   ▌","▐    ⡀   ▌","▐   ⠠    ▌","▐   ⠂    ▌","▐  ⠈     ▌","▐  ⠂     ▌","▐ ⠠      ▌","▐ ⡀      ▌","▐⠠       ▌"]   }
    BLOCK_GROW_UP = {"speed": .1, "char_list": ["▁","▃","▄","▅","▆","▇","▆","▅","▄","▃"]}
    CIRCLE_SPIN = {"speed": .1,"char_list":["◐","◓","◑","◒"]}
    DOTS = {"speed": .1, "char_list": ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]}
    FADING_BOX = {"speed": .1, "char_list": ['█','▓','▒','░',' ']}
    FLIPPER = {"speed": .075, "char_list": ["_","_","_","-","`","`","'","´","-","_","_","_"] }
    MOON_PHASES = {"speed": .15, "char_list": ["🌑 ","🌒 ","🌓 ","🌔 ","🌕 ","🌖 ","🌗 ","🌘 "]}

class Spinner():
    """
    Create a console spinner for visual effect.  
    
    The spinner runs on a seperate thread, so the caller can perform 
    processing while the spinner displays.
    
    Example::
    
        from dt_tools.console.spinner import Spinner, SpinnerType

        spinner = Spinner("In progress", SpinnerType.DOTS, True)
        spinner.start_spinner()
        # Do some work....
        spinner.stop_spinner()
        
    Parameters:
        caption     : string prefixing spinner graphic
        spinner     : type of spinner pattern
        show_elapsed: suffix displaying elapsed h:m:s
    """
    def __init__(self, caption: str, spinner: SpinnerType = SpinnerType.NORMAL_SPINNER, show_elapsed: bool = False, str_end = ''):
        self._caption = caption
        self._suffix = ''
        self._last_suffix = ''
        self._spinner = spinner
        self._cursor_list = self._spinner.value['char_list']     
        self._cursor_list_len = len(self._cursor_list)
        self._show_elapsed = show_elapsed
        self._elapsed_time = '00:00:00'
        self._start_time = dt.now()
        self._str_end = str_end
        self._idx = 99
        self._finished = False
        self._spinner_thread = None
        # self.console = ConsoleHelper()
        LOGGER.trace("Spinner initialized.")

    def start_spinner(self, caption_suffix: str = ''):
        """
        Start spinner in console.

        Keyword Arguments:
            caption_suffix:  Text to append to spinner line (default: {''})
        """
        if self._spinner_thread:
            # If spinner is currently running, kill it.
            if self._spinner_thread.is_alive():
                self.stop_spinner()

        ConsoleHelper.cursor_off()
        if ConsoleHelper.valid_console():
            self._suffix = caption_suffix
            self._spinner_thread = threading.Thread(target=self._display_spinner, daemon=True)
            self._start_time = dt.now()
            self._elapsed_time = '00:00:00'
            self._spinner_thread.start()
    
    def stop_spinner(self):
        """
        Stop spinner when running

        Spinner line will be cleared and cursor will be positioned 
        in column 1 of that row
        """
        if self._spinner_thread is not None and self._spinner_thread.is_alive():
            self._finished = True
            self._spinner_thread.join()
            self._elapsed_time = self._calculate_elapsed_time(dt.now(), self._start_time)
            self._finished = False
        ConsoleHelper.clear_line()
        ConsoleHelper.cursor_on()

    def caption_suffix(self, suffix: str):
        """
        Text to append at end of spinner line.

        Use this to provide updated status text as the spinner is running.

        Arguments:
            caption_suffix:  Text to append to spinner line
        """
        self._suffix = suffix

    @property
    def elapsed_time(self) -> str:
        """
        Elapsed time since spinner started.

        Returns:
            String in format hh:mm:ss
        """
        return self._elapsed_time


    def _calculate_elapsed_time(self, end_time: float, start_time: float) -> str:
        diff = end_time - start_time
        hours = diff.seconds // 3600
        minutes = diff.seconds // 60 % 60
        seconds = diff.seconds % 60
        elapsed_time = f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
        return elapsed_time

    def _display_spinner(self):
        delay = self._spinner.value['speed']
        loopcnt = 0
        elapsed_break = int(1 / delay) # 1 seconds
        elapsed_display = ' '*len(self._elapsed_time)
        spinner_row,_ = ConsoleHelper.cursor_current_position()

        while not self._finished and threading.main_thread().is_alive():
            cursor = self._get_cursor_shape()

            if self._show_elapsed and loopcnt % elapsed_break == 0:
                self._elapsed_time = self._calculate_elapsed_time(dt.now(), self._start_time) # type: ignore
                elapsed_display = self._elapsed_time
            
            terminal_line = f'{self._caption} {cursor}  {elapsed_display} {self._suffix}'
            ConsoleHelper.print(terminal_line, eol='')
            ConsoleHelper.clear_to_EOL()
            while not ConsoleHelper.cursor_move(spinner_row, column=1):
                time.sleep(.01)
            time.sleep(delay)
            loopcnt += 1

        ConsoleHelper.clear_line()

    def _get_cursor_shape(self):
        self._idx += 1
        if self._idx >= self._cursor_list_len:
            self._idx = 0
        return self._cursor_list[self._idx]


if __name__ == "__main__":
    for spinner_type in SpinnerType:
        spinner = Spinner(f'Demo of spinner type: {spinner_type.name}', spinner_type, True)
        spinner.start_spinner("Begin")
        for cnt in range(1,25):
            if cnt % 5 == 0:
                spinner.caption_suffix(f'Executing iteration {cnt}')
            time.sleep(.25)
        spinner.stop_spinner()
