"""
This module will demo the dt_tools.console.input_helper capabilities including:

- Prompt with timeout and default response
- Wait with Timout prompt
- Validate input prompt

To run this demo standalone:
    `poetry run python -m dt_tools.cli.dt_console_input_helper_demo`

"""
from dt_tools.console.console_helper import ColorFG, TextStyle
from dt_tools.console.console_helper import ConsoleHelper as console
from dt_tools.console.console_helper import ConsoleInputHelper as console_input
from dt_tools.os.os_helper import OSHelper


def demo():    
    OSHelper.enable_ctrl_c_handler()
    timeout = 10
    console.print('')
    console.print_line_separator('ConsoleInputHelper Demo', 40)
    
    console.print('')
    test_name = console.cwrap('Input with Timeout', style=[TextStyle.ITALIC, TextStyle.BOLD])    
    console.print(f'{test_name}: default response is y, timeout {timeout} secs...')
    console.print(console.cwrap("code:\n  resp = console_input.get_input_with_timeout('Test prompt (y/n) > ', console_input.YES_NO_RESPONSE, default='y', timeout_secs=timeout)\n",TextStyle.ITALIC))
    resp = console_input.get_input_with_timeout('Test prompt (y/n) > ', console_input.YES_NO_RESPONSE, default='y', timeout_secs=timeout)
    console.print(f'  returns: {resp}')

    console.print("")
    test_name = console.cwrap('Wait with Timeout', style=[TextStyle.ITALIC, TextStyle.BOLD] )
    console.print(f'\n{test_name}: Wait with bypass -  {timeout} seconds')
    console.print(console.cwrap("code:\n  resp = console_input.wait_with_bypass(timeout)\n",TextStyle.ITALIC))
    console.print(f'Waiting {timeout} seconds, or press ENTER to abort wait', eol='')
    if console_input.wait_with_bypass(timeout):
        console.print('\n  Prompt timed out.')
    else:
        console.print('  User aborted wait')

    console.print('')
    test_name = console.cwrap('Validate input (with timeout)', style=[TextStyle.ITALIC, TextStyle.BOLD])
    console.print(f'\n{test_name}: Wait {timeout} seconds, validate user enters proper input, if timeout return default value.')
    console.print(console.cwrap("code:\n  resp = console_input.get_input_with_timeout('Valid input is [a,b,c,d] > ', valid_responses=['a','b','c','d'], default='z', timeout_secs=timeout)\n",TextStyle.ITALIC))
    resp = console_input.get_input_with_timeout('Valid input is [a,b,c,d] > ', valid_responses=['a','b','c','d'], default='z', timeout_secs=timeout)
    print(f'  returns: {resp}')
    
    console.print('')
    console.print(f"End of {console.cwrap('ConsoleInputHelper', ColorFG.YELLOW)} demo.")

    input('\nPress Enter to continue...')

if __name__ == '__main__':
    demo()