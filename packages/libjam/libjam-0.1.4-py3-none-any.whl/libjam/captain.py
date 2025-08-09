# Imports
import sys
from inspect import signature
from .typewriter import Typewriter

typewriter = Typewriter()


# Processes command line arguments
class Captain:
  def get_args(self) -> list:
    args = sys.argv
    args.pop(0)
    return args

  # Returns a list of args a function requires.
  def get_function_args(self, function) -> list:
    args = str(signature(function))
    args = args.removeprefix('(').removesuffix(')').replace(' ', '').split(',')
    if 'self' in args:
      args.remove('self')
    return args

  # Returns a generated a help page based on provided inputs.
  def generate_help(
    self, app: str, description: str, commands: dict, options: dict = None
  ) -> str:
    offset = 2
    offset_string = ' ' * offset
    commands_list = []
    for command in commands:
      command_desc = commands.get(command).get('description')
      commands_list.append(f'{command}')
      commands_list.append(f'- {command_desc}')
    commands_list.append('help')
    commands_list.append('- Prints this page')
    commands_string = typewriter.list_to_columns(commands_list, 2, offset)
    if options is not None:
      options_list = []
      for option in options:
        option_desc = options.get(option).get('description')
        long = ', --'.join(options.get(option).get('long'))
        short = ', -'.join(options.get(option).get('short'))
        options_list.append(f'-{short}, --{long}')
        options_list.append(f'- {option_desc}')
      options_string = typewriter.list_to_columns(options_list, 2, offset)
    # Creating the help string
    help_string = ''
    # Adding description
    help_string += f'{typewriter.bolden("Description:")}\n'
    help_string += f'{offset_string}{description}\n'
    # Adding synopsys
    help_string += f'{typewriter.bolden("Synopsis:")}\n'
    help_string += f'{offset_string}{app} [OPTIONS] [COMMAND]\n'
    # Adding commands
    help_string += f'{typewriter.bolden("Commands:")}\n'
    help_string += commands_string.rstrip()
    # Adding options
    if options is not None:
      help_string += f'\n{typewriter.bolden("Options:")}\n'
      help_string += options_string.rstrip()
    # Returning
    return help_string

  # Interprets input arguments.
  def interpret(
    self,
    app: str,
    help: str,
    commands: dict,
    options: dict = None,
    arguments: list = None,
  ) -> dict:
    if arguments is None:
      arguments = self.get_args()
    chosen_command = None
    self.function = None
    self.arbitrary_args = False
    self.required_args = 0
    self.command_args = []

    # Creating option bools
    if options is not None:
      for option in options:
        options[option]['enabled'] = False
    # Parsing arguments
    for argument in arguments:
      if argument.startswith('-'):
        if options is not None:
          self.arg_found = False

          # Long options
          if argument.startswith('--'):
            argument = argument.removeprefix('--')
            if argument == '':
              print(f"Invalid option '--'. Try {app} help")
              sys.exit(-1)
            for option in options:
              strings = options.get(option).get('long')
              if argument in strings:
                options[option]['enabled'] = True
                self.arg_found = True
            if self.arg_found is False:
              print(f"Option '{argument}' unrecognised. Try {app} help")
              sys.exit(-1)

          # Short options
          else:
            argument = argument.removeprefix('-')
            if argument == '':
              print(f"Invalid option '-'. Try {app} help")
              sys.exit(-1)
            arguments = list(argument)
            for argument in arguments:
              command_found = False
              for option in options:
                strings = options.get(option).get('short')
                if argument in strings:
                  options[option]['enabled'] = True
                  command_found = True
            if command_found is False:
              print(f"Option '{argument}' unrecognised. Try {app} help")
              sys.exit(-1)

      # Commands
      else:
        if chosen_command is None:
          if argument == 'help':
            print(help)
            sys.exit(0)
          elif argument in commands:
            chosen_command = argument
            command_function = commands.get(chosen_command).get('function')
            command_function_args = self.get_function_args(command_function)
            if '*args' in command_function_args:
              command_function_args.remove('*args')
              self.arbitrary_args = True
            self.required_args = len(command_function_args)
          else:
            print(f"Command '{argument}' unrecognised. Try {app} help")
            sys.exit(-1)

        # Command arguments
        else:
          if self.arbitrary_args is False:
            if self.required_args == 0:
              print(f"Command '{chosen_command}' does not take arguments.")
              sys.exit(-1)
            elif len(self.command_args) >= self.required_args:
              s = ''
              if self.required_args > 1:
                s = 's'
              print(
                f"Command '{chosen_command}' requires only {self.required_args} argument{s}."
              )
              sys.exit(-1)
          self.command_args.append(argument)
    if self.arbitrary_args is False and self.required_args > len(
      self.command_args
    ):
      print(
        f"Command '{chosen_command}' requires {self.required_args} arguments."
      )
      sys.exit(-1)

    # Checking if command is specified
    if chosen_command is None:
      print(f'No command specified. Try {app} help')
      sys.exit(0)

    function = commands.get(chosen_command).get('function')
    function_name = function.__name__
    function_params = ''
    for item in self.command_args:
      function_params += f"'{item}', "
    function = f'{function_name}({function_params})'

    return {'function': function, 'options': options}
