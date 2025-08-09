"""
This module will demo the dt_tools.console.progress_bar capabilities including:

- Display progress bar 
- Display progress bar with elapsed time


To run this demo standalone:
    `poetry run python -m dt_tools.cli.dt_progress_bar_demo`

"""
from dt_tools.console.console_helper import ColorFG, TextStyle
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.console.progress_bar import ProgressBar
import time

def demo():    
    console.print('')
    console.print_line_separator('ProgressBar Demo', 40)
    console.print('')

    console.print(console.cwrap('Plain progress bar', style=TextStyle.BOLD))
    console.print(console.cwrap('code:', style=[TextStyle.ITALIC]))
    console.print(console.cwrap('  pbar = ProgressBar("Progress bar", bar_length=40, max_increments=50, show_elapsed=False)', style=[TextStyle.ITALIC]))
    console.print(console.cwrap('  for incr in range(1,51):', style=[TextStyle.ITALIC]))
    console.print(console.cwrap('      pbar.display_progress(incr, f"incr [{incr}]")', style=[TextStyle.ITALIC]))
    console.print(console.cwrap('      time.sleep(sleep_time)\n', style=[TextStyle.ITALIC]))

    sleep_time = .15
    pbar = ProgressBar("Progress bar", bar_length=40, max_increments=50, show_elapsed=False)
    for incr in range(1,51):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(sleep_time)    

    console.print('')
    console.print(console.cwrap('Progress bar w/elapsed time', style=TextStyle.BOLD))
    console.print(console.cwrap('code:', style=[TextStyle.ITALIC]))
    console.print(console.cwrap('  pbar = ProgressBar("Progress bar", bar_length=40, max_increments=50, show_elapsed=True)', style=[TextStyle.ITALIC]))
    console.print(console.cwrap('  for incr in range(1,51):', style=[TextStyle.ITALIC]))
    console.print(console.cwrap('      pbar.display_progress(incr, f"incr [{incr}]")', style=[TextStyle.ITALIC]))
    console.print(console.cwrap('      time.sleep(sleep_time)\n', style=[TextStyle.ITALIC]))
    pbar = ProgressBar("Progress bar", bar_length=40, max_increments=50, show_elapsed=True)
    for incr in range(1,51):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(sleep_time)
    
    console.print('')
    console.print(f"End of {console.cwrap('ProgressBar', ColorFG.YELLOW)} demo.")

    input('\nPress Enter to continue...')

if __name__ == '__main__':
    demo()