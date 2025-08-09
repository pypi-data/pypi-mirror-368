# libjam
A library jam for Python.

## Installing
libjam is available on [PyPI](https://pypi.org/project/libjam/), and can be installed using pip.
```
pip install libjam
```

## Modules
libjam consists of of 6 modules:

### Captain
Responsible for handling command-line arguments.

### Drawer
Responsible for file operations.

### Typewriter
Responsible for transforming and printing text.

### Clipboard
Responsible for working with lists.

### Notebook
Responsible for configuration.

### Flashcard
Responsible for getting user input from the command line.

## Example project
```python
#!/usr/bin/env python3

# Imports
import sys
from libjam import captain

class CLI:
  def hello(self, text):
    print(text)
    if options.get('world').get('enabled'):
      print('world!')

# Setting commands and options
app = "example"
description = "An example app for the libjam library"
commands = {
  'print': {
    'function': CLI.hello,
    'description': 'Prints given string',
  },
}
options = {
  'world': {
    'long': ['world'], 'short': ['w'],
    'description': 'Appends \'world\' after printing given input',
  },
}

# Generating help
help = captain.generate_help(app, description, commands, options)
# Interpreting user input
interpretation = captain.interpret(app, help, commands, options)
# Getting parsed output
function = interpretation.get('function')
options = interpretation.get('options')
# Executing function
exec(f"CLI().{function}")
```
