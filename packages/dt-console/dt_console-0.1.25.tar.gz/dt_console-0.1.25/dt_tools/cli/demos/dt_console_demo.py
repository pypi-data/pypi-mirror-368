"""
Driver for the Console Demos.

This module will walk you thru each dt_tools.console control and demo
the capabilities.

- Console manipulation: console_helper :func:`~dt_tools.cli.dt_console_helper_demo.demo()`
- Console input: console_input_helper :func:`~dt_tools.cli.dt_console_input_helper_demo.demo()`
- GUI Messagebox: msgbox :func:`~dt_tools.cli.msgbox_demo.demo()`
- Progress Bar control: progress_bar :func:`~dt_tools.cli.dt_progress_bar_demo.demo()`
- Spinner control: spinner :func:`~dt_tools.cli.dt_spinner_demo.demo()`

To Run:
    `poetry run python -m dt_tools.cli.dt_console_demo`

"""
import dt_tools.logger.logging_helper as lh
from dt_tools.cli.demos.dt_console_helper_demo import demo as console_helper_demo
from dt_tools.cli.demos.dt_console_input_helper_demo import demo as console_input_helper_demo
from dt_tools.cli.demos.dt_msgbox_demo import demo as message_box_demo
from dt_tools.cli.demos.dt_progress_bar_demo import demo as progress_bar_demo
from dt_tools.cli.demos.dt_spinner_demo import demo as spinner_demo
from dt_tools.console.console_helper import ColorFG, TextStyle
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.console.console_helper import ConsoleInputHelper as console_input
from dt_tools.os.project_helper import ProjectHelper

def run_demos():
    lh.configure_logger(log_level="INFO")
    DEMOS = {
        "ConsoleHelper": console_helper_demo,
        "ConsoleInputHelper": console_input_helper_demo,
        "MessageBox": message_box_demo,
        "ProgressBar": progress_bar_demo,
        "Spinner": spinner_demo
    }
    console.clear_screen()
    console.print_line_separator('', 80)
    version = f'v{console.cwrap(ProjectHelper.determine_version("dt-console"), style=TextStyle.ITALIC)}'
    console.print_line_separator(f'dt_console_demo {version}', 80)
    console.print('')
    for name, demo_func in DEMOS.items():
        demo_name = console.cwrap(name, ColorFG.YELLOW)
        resp = console_input.get_input_with_timeout(f'Demo {demo_name} Functions (y/n) > ', 
                                                console_input.YES_NO_RESPONSE, default='n', 
                                                timeout_secs=10).lower()
        if resp == 'y':
            demo_func()
            console.print('')

    console.print('Console demo complete!')
    
if __name__ == '__main__':
    run_demos()