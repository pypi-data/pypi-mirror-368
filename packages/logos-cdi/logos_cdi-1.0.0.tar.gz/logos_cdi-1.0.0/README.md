# logos_cdi

LogosCDI is a dependency injection tool that allows you to create extensible and maintainable applications


## How to install
```sh
pip install logos_cdi
```

## Basic usage
First you need to create an object of the Application class
```py
from logos_cdi.application import Application

app = Application(
    modules=[

    ]
)
```
You may want to use some modules to improve productivity
```py
from logos_cdi.application import Application
from logos_cdi.command import Commands

app = Application(
    modules=[
        Commands()
    ]
)
```
The Commands Module gives you a basis for creating commands to be executed in the terminal.

You can call it with:

```sh
$ logos
usage: logos [--app-url APP_URL] {} ...
logos: error: the following arguments are required: command
```
Create your own modules with commands

```py
from logos_cdi.command import Commands, AbstractCommand, CommandModule

class TestCommand(AbstractCommand):

    def define_arguments(self, argument_parser):
        argument_parser.add_argument('--name', default='Anonymous')
        return super().define_arguments(argument_parser)

    def execute(self):
        return print('Hello', self.arguments.name)

class Tests(CommandModule, BaseModule):

    def define_commands(self):
        return {
            'test': Service(
                class_path='test_module.TestCommand',
                parameters={}
            )
        }

```
Add to your application

```py
from logos_cdi.application import Application
from logos_cdi.command import Commands
from test_module import Tests

app = Application(
    modules=[
        Commands(),
        Tests()
    ]
)
```

```sh
$ logos
usage: logos [--app-url APP_URL] {test} ...
logos: error: the following arguments are required: command

$ logos test --help
usage: logos test [-h] [--name NAME]

options:
  -h, --help   show this help message and exit
  --name NAME

$ logos test
Hello Anonymous

$ logo test --name=foo
Hello foo
```


