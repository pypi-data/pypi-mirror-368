from abc import ABC, abstractmethod
from argparse import ArgumentParser
from typing import Optional, Mapping
from logos_cdi.abstract import AbstractReference, AbstractResource
from logos_cdi.application import AbstractModule, ModuleMixin
from logos_cdi.container import Container
from logos_cdi.resource import Service, Parameter, Singleton
from logos_cdi.reference import Reference, Parent, AllRegisteredReference


class AbstractCommand(ABC):

    def __init__(self, argument_parser: Optional[ArgumentParser] = None):
        self.argument_parser = argument_parser
    
    def define_arguments(self, argument_parser: ArgumentParser):
        self.argument_parser = argument_parser
    
    @property
    def arguments(self):
        return self.argument_parser.parse_known_args()[0]
    
    @abstractmethod
    def execute(self):
        ...


class DelegateCommand(AbstractCommand):

    def __init__(self, argument_parser: ArgumentParser, commands: Mapping[str, AbstractCommand]):
        super().__init__(argument_parser)
        self.commands = commands
        self.define_arguments(argument_parser)
    
    def define_arguments(self, argument_parser):
        parsers = argument_parser.add_subparsers(dest='command', required=True)
        for command_name, command in self.commands.items():
            command_parser: ArgumentParser = parsers.add_parser(command_name)
            command.define_arguments(command_parser)
        super().define_arguments(argument_parser)
    
    def execute(self):
        return self.commands[self.arguments.command].execute()

class Commands(AbstractModule):

    def define_context(self, context):
        return context.nested(
            Container({
                'commands.delegate_command.class': Parameter('logos_cdi.command.DelegateCommand'),
                'commands.registry': Singleton(
                    class_path='logos_cdi.registry.Registry',
                    parameters={
                        'parent': Parent('commands.registry'),
                        'type': AbstractReference
                    }
                ),
                'commands.argument_parser': Parameter(ArgumentParser()),
                'commands.command': Service(
                    class_path=Reference('commands.delegate_command.class'),
                    parameters={
                        'argument_parser': Reference('commands.argument_parser'),
                        'commands': AllRegisteredReference('commands.registry')
                    }
                )
            })
        )


class CommandModule(ModuleMixin):

    command_prefix = 'commands'

    @abstractmethod
    def define_commands(self) -> Mapping[str, AbstractResource]:
        ...

    def define_context(self, context):
        if context.has('commands.registry'):
            commands = self.define_commands()
            context = context.nested(Container({
                f'{self.command_prefix}.{name}': resource
                for name, resource in commands.items()
            }))

            registry = context.get('commands.registry')
            for name in commands.keys():
                registry.register(name, Reference(f'{self.command_prefix}.{name}'))
        return super().define_context(context)



def main():
    from logos_cdi.application import Application, AbstractModule
    from logos_cdi.container import Container
    from os import environ, getcwd
    from sys import path
    from importlib import import_module

    class ManagementCommand(AbstractCommand):

        def define_arguments(self, argument_parser):
            argument_parser.add_argument('--app-url', default=environ.get('LOGOS_APPLICATION_URL', 'main:app'))
            return super().define_arguments(argument_parser)
        
        def execute(self):
            path.append(getcwd())
            self.define_arguments(self.argument_parser)
            
            module_path, app_var = self.arguments.app_url.split(':')
            app: Application = getattr(import_module(module_path), app_var)

            has_event_emitter = app.has('events.emitter') 

            if has_event_emitter:
                app.get('events.emitter').emit('app:start', {})

            app.extends([
                ManagedModule()
            ]).get('commands.command').execute()

            if has_event_emitter:
                app.get('events.emitter').emit('app:stop', {})

    argument_parser = ArgumentParser(add_help=False)

    class ManagedModule(AbstractModule):

        def define_context(self, context):
            return context.nested(Container({
                'commands.argument_parser': Parameter(argument_parser)
            }))

    class ManagementModule(AbstractModule):

        def define_context(self, context):
            return context.nested(Container({
                'management.command': Parameter(ManagementCommand(
                    argument_parser=argument_parser
                ))
            }))


    app = Application([
        ManagementModule()
    ])

    app.get('management.command').execute()