"""
Progress bar to provide visual feedback of process activity.

Features:
    - Customized display.
    - Optionally display elapsed time.
    - Progress bar reflects percent completion of process.

Example::

    from dt_tools.console.progress_bar import ProgressBar

    p_bar = ProgressBar("Sample Execution", bar_line=40, max_increments=100)
    for i in range(99):
        p_bar.display_progress(i+1)
        do something....
    p_bar.cancel_progress()
    
"""

import os
import time
from datetime import datetime as dt

from loguru import logger as LOGGER

from dt_tools.console.console_helper import ConsoleHelper


class ProgressBar():
    """
    Displays progress bar in the console.  
    """

    def __init__(self, caption: str, bar_length: int, max_increments: int, fill= '█', str_end = "\r", show_elapsed: bool = False, show_pct: bool = True):
        """
        Progress bar class instantiation

        Arguments:
            caption -- Caption text
            bar_length -- Length of progress bar, must be < console width
            max_increments -- Maximum number of progress segments

        Keyword Arguments:
            fill -- Progress fill character (default: {'█'})
            str_end -- End of progress bar string. default is progress remains fixed location (default: {"\r"})
            show_elapsed -- Append elapsed time at end of progress bar (default: {False})
            show_pct -- Append pct complete at end of progress bar (default: {True})
        Note:
            To update progress, call display_progress(inc) method to indicate current increment count.  
            When inc varible reaches max_increments value, progress bar will terminate.

        Example::
            from dt_tools.console.progress_bar import ProgressBar
            
            p_bar = ProgressBar("Sample Execution", bar_line=40, max_increments=100)
            for i in range(99):
                p_bar.display_progress(i+1)
                do something....
            p_bar.cancel_progress()

        """
        _, max_bar_len = ConsoleHelper.get_console_size()
        max_bar_len -= len(caption)
        if show_elapsed:
            max_bar_len -= 8  # len of elapsed str
        if show_pct:
            max_bar_len -= 5  # len of pct str

        self._caption = caption
        self._bar_len = min(max_bar_len, bar_length)
        self._max_increments = max_increments
        self._fill = fill
        self._str_end = str_end
        self._show_elapsed = show_elapsed
        self._show_pct: bool = show_pct
        
        self._start_time = dt.now()
        self._decimals = 1
        self._started = False
        self._elapsed_time = '00:00:00'
        self._finished = False
        self.console = ConsoleHelper()
        LOGGER.trace('ProgressBar initialized.')

    def display_progress(self, current_increment: int, suffix: str = ''):
        """
        Update the progress bar filling up to current increment.
        
        Parameters:
            current_increment: integer indication progress up to max_increments
            suffix:            text to display to right of progress bar, can be used to show status
        """
        if not self._started:
            self._start_time = dt.now()
            self._started = True
        if current_increment > self._max_increments:
            current_increment = self._max_increments

        self.console.cursor_off()
        self._finished = False
        term_columns = os.get_terminal_size().columns
        if ConsoleHelper.valid_console(): 
            filled_len = int(self._bar_len * current_increment // self._max_increments)
            bar = self._fill * filled_len + '-' * (self._bar_len - filled_len)
            
            display_line = f'\r{self._caption} [{bar}]'
            if self._show_pct and len(display_line) + 6 < term_columns:
                cur_percent = 100 * (current_increment / self._max_increments)
                dsply_percent = f'{cur_percent:5.1f}%'
                display_line += f' {dsply_percent}'
            
            if len(suffix) > 0 and len(display_line) + len(suffix)+1 < term_columns:
                display_line += f' {suffix}'

            self._elapsed_time = self._calculate_elapsed_time(dt.now(), self._start_time)
            if self._show_elapsed and len(display_line) + len(self.elapsed_time) + 1 < term_columns:
                display_line += f' {self._elapsed_time}'
            
            # if len(display_line) > self._term_columns:
            #     terminal_line = (display_line[:self._term_columns-7] + '...' + display_line[-3:]) 
            # else:
            #     terminal_line = display_line
            # terminal_line = (display_line[:self._term_columns-7] + '...' + display_line[-3:]) if len(display_line) > self._term_columns else display_line
            terminal_line = display_line
            print(terminal_line, end = self._str_end, flush=True)

        if current_increment >= self._max_increments:
            self.cancel_progress()

    def cancel_progress(self):
        """Turn off progress bar."""
        self._finshed = True
        self._elapsed_time = self._calculate_elapsed_time(dt.now(), self._start_time)
        self.console.cursor_on()
        self.console.print('')
        self._started = False

    @property
    def elapsed_time(self) -> str:
        """Return elapsed time in format hh:mm:ss."""
        return self._elapsed_time
    
    def _calculate_elapsed_time(self, end_time: float, start_time: float) -> str:
        diff = end_time - start_time
        hours = diff.seconds // 3600
        minutes = diff.seconds // 60 % 60
        seconds = diff.seconds % 60
        self._elapsed_time = f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"
        return self._elapsed_time


if __name__ == "__main__":
    print('')
    b_len = 80
    m_inc = 140
    pbar = ProgressBar("Test bar", bar_length=b_len, max_increments=m_inc, show_elapsed=False)
    for incr in range(1,m_inc+1):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(.05)    

    print('\nProgress bar with no pct complete...')
    pbar = ProgressBar("Test bar", bar_length=b_len, max_increments=m_inc, show_elapsed=False, show_pct=False)
    for incr in range(1,m_inc+1):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(.05)    

    print('\nProgress bar with elapsed time...')
    pbar = ProgressBar("Test bar", bar_length=b_len, max_increments=m_inc, show_elapsed=True)
    for incr in range(1,m_inc+1):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(.05)

