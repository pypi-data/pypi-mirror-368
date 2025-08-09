# dt-console

dt-console is a Python library to simplify CLI input and output for your python apps/scripts.  It has been tested in Windows and Linux.

Features include:
<ul>
    <li><b>ConsoleHelper</b> - manage window and cursor control</li>
    <ul>
        <li>Set console window title</li>
        <li>Show/Hide console window, set fg/bg colors</li>
        <li>Set cursor style, location, ...</li>
        <li>Routines to print and colorize output text</li>
    </ul>
    <li><b>ConsoleInputHelper</b> - Keyboard input prompts with validation and timeouts.</li>
    <li><b>MessageBox</b> - GUI messsagebox (alert, confirm, input, password)</li>
    <li><b>ProgressBar</b> - Display visual progress on screen via configurable progress bar</li>
    <li><b>Spinner</b> - Display visual progress on screen via configuable spinner control</li>
</ul>

Package donumentation can be found [here](https://htmlpreview.github.io/?https://github.com/JavaWiz1/dt-console/blob/develop/docs/html/index.html).

## Installation

### Download source code from githup via git
```bash
git clone https://github.com/JavaWiz1/dt-console.git
```
Note, when downloading source, [Poetry](https://python-poetry.org/docs/) was used as the package manager.  Poetry 
handles creating the virtual environment and all dependent packages installs with proper versions.

To setup virtual environment with required production __AND__ dev ([sphinx](https://www.sphinx-doc.org/en/master/)) dependencies:
```bash
poetry install
```

with ONLY production packages (no sphinx):
```bash
poetry install --without dev
```


### use the package manager [pip](https://pip.pypa.io/en/stable/) to install dt-console.

```bash
pip install dt-console [--user]
```

## Usage
A demo cli has been included to show how these modules can be used.  The demo selectively displays each control (console tools, input prompt, messagebox, ProgressBar and Spinner) and source is provided to review for implementation details.

See [dt_tools.cli.dt_console_demos.py](https://github.com/JavaWiz1/dt-console/blob/develop/dt_tools/cli/dt_console_demos.py) for detailed demo examples (runnable demo)

To run the demo type:
```bash
python -m dt_tools.cli.dt_console_demos

# or if via source (and poetry)
poetry run python -m dt_tools.cli.dt_console_demos
```

Developer package documentation contains details on all classes and supporting code (i.e. constant namespaces and enums) use for method calls.  Docs can be found [here](https://htmlpreview.github.io/?https://github.com/JavaWiz1/dt-console/blob/develop/docs/html/index.html).


### Main classes/modules Overview

#### ConsoleHelper
ConsoleHelper provides methods for managing the console windows.  

```python
    from dt_tools.console.console_helper import ConsoleHelper
    import time

    console.clear_screen(cursor_home=True)
 
    console_size = console.get_console_size()
    row, col = console.cursor_current_position()
    print(f'Console size: {console_size}, cur pos: {row},{col}')
 
    console.print_at(row=3, col=5, msg="Here we are at row 3, column 5", eol='\n\n')
    time.sleep(.5)
 
    blue = console.cwrap('blue', cc.CBLUE)
    brown = console.cwrap('brown', cc.CBEIGE)
    green = console.cwrap('green', cc.CGREEN)
    text = f"The {blue} skies and the {brown} bear look wonderful in the {green} forest!"
    print(text)
 
    row, col = console.cursor_current_position()
    print(f'         at ({row},{col})', flush=True)
    time.sleep(2)
    console.print_at(row,col,'Finished')
```

#### ConsoleInputHelper
ConsoleInputHelper provides a customizable input prompt.

```python
    from dt_tools.console.console_helper import ConsoleInputHelper

    console_input = ConsoleInputHelper()

    resp = console_input.get_input_with_timeout(prompt='Do you want to continue (y/n) > ', 
                                                valid_responses=console_input.YES_NO_RESPONSE, 
                                                default='y', 
                                                timeout_secs=5)
    print(f'  returns: {resp}')

```

#### MessageBox
Message box implements Alert, Confirmation, Input Prompt, Password Prompt message boxes.  

```python
    import dt_tools.console.msgbox as msgbox

    resp = msgbox.alert(text='This is an alert box', title='ALERT no timeout')
    print(f'  mxgbox returns: {resp}')

    resp = msgbox.alert(text='This is an alert box', title='ALERT w/Timeout', timeout=3000)
    print(f'  mxgbox returns: {resp}')

```

#### ProgressBar
ProgressBar is an easy to use, customizable console ProgressBar which displays percentage complete and elapsed time.

```python
    from dt_tools.console.progress_bar import ProgressBar
    import time

    print('Progress bar...')
    pbar = ProgressBar(caption="Test bar 1", bar_length=40, max_increments=50, show_elapsed=False)
    for incr in range(1,51):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(.15)    

    print('\nProgress bar with elapsed time...')
    pbar = ProgressBar(caption="Test bar 2", bar_length=40, max_increments=50, show_elapsed=True)
    for incr in range(1,51):
        pbar.display_progress(incr, f'incr [{incr}]')
        time.sleep(.15)
```

#### Spinner
Spinner is an easy to use, customizable console Spinner control which displays spinning icon and elapsed time.

```python
    from dt_tools.console.spinner import Spinner, SpinnerType
    import time

    # Example to display all spinner types for approx 5 sec. apiece
    for spinner_type in SpinnerType:
        spinner = Spinner(caption=spinner_type, spinner=spinner_type, show_elapsed=True)
        spinner.start_spinner()
        
        # Do long task...
        for cnt in range(1,20):
            time.sleep(.25)

        spinner.stop_spinner()
```


## License
[MIT](https://choosealicense.com/licenses/mit/)

The MessageBox code was derived from:  
PyMsgBox - BSD for PyMsgBox (see source for msgbox.py)
