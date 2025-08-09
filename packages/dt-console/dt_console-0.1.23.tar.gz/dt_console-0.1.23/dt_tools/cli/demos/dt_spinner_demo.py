"""
This module will demo the dt_tools.console.spinner capabilities including:

- Spinner with and without elapsed time
- Showcase different spinner types

To run this demo standalone:
    `poetry run python -m dt_tools.cli.dt_spinner_demo`

"""
import time

import dt_tools.logger.logging_helper as lh
from dt_tools.console.console_helper import ColorFG, TextStyle
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.console.spinner import Spinner, SpinnerType
from dt_tools.os.os_helper import OSHelper

def demo():    
    OSHelper.enable_ctrl_c_handler()
    console.print('')
    console.print_line_separator('Spinner Demo', 40)
    console.print('')
    
    console.print(console.cwrap("Basic code example:", style=TextStyle.ITALIC))
    console.print(console.cwrap("  spinner = Spinner(caption='Generating... ' , spinner=SpinnerType.NORMAL_SPINNER, show_elapsed=True)", style=TextStyle.ITALIC))
    console.print(console.cwrap("  spinner.start('begin work')", style=TextStyle.ITALIC))
    console.print(console.cwrap("     do some work...", style=TextStyle.ITALIC))
    console.print(console.cwrap("  spinner.caption_suffix('still working...)", style=TextStyle.ITALIC))
    console.print(console.cwrap("     do some more work...", style=TextStyle.ITALIC))
    console.print(console.cwrap("  spinner.stop_spinner()", style=TextStyle.ITALIC))
    console.print('')

    console.print(console.cwrap('Spinner, no elapsed time or status information:', style=TextStyle.UNDERLINE))
    spinner = Spinner(caption='Basic Spinner', spinner=SpinnerType.NORMAL_SPINNER)
    spinner.start_spinner()
    time.sleep(10)
    spinner.stop_spinner()
    console.clear_line(-1)

    console.print(console.cwrap('Spinner, with elapsed time:', style=TextStyle.UNDERLINE))
    spinner = Spinner(caption='Basic Spinner w/Elapsed time', spinner=SpinnerType.NORMAL_SPINNER, show_elapsed=True)
    spinner.start_spinner()
    time.sleep(10)
    spinner.stop_spinner()
    console.clear_line(-1)

    console.print(console.cwrap('Loop thru all spinner types, with elapsed time', style=TextStyle.UNDERLINE))
    sleep_time = .25
    max_range = 25
    for spinner_type in SpinnerType:
        spinner = Spinner(caption=spinner_type, spinner=spinner_type, show_elapsed=True)
        spinner.start_spinner()
        for cnt in range(1, max_range + 1):
            if cnt % 5 == 0:
                spinner.caption_suffix(f'working... {cnt} of {max_range}')
            time.sleep(sleep_time)
        spinner.stop_spinner()
    console.clear_line(-1)
    
    console.print('')
    console.print(f"End of {console.cwrap('Spinner',ColorFG.YELLOW)} demo.")

    input('\nPress Enter to continue...')

if __name__ == '__main__':
    lh.configure_logger(log_level='INFO')
    demo()