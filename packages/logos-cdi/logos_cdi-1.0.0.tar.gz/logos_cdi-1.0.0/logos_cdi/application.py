from logos_cdi.abstract import AbstractContext, AbstractContainer
from logos_cdi.context import Context
from logos_cdi.container import Container
from logos_cdi.resource import Parameter
from abc import ABC, abstractmethod
from typing import Iterable


class AbstractModule(ABC):

    @abstractmethod
    def define_context(self, context: AbstractContext) -> AbstractContext:
        ...


class BaseModule(AbstractModule):

    def define_context(self, context):
        return context


class ModuleMixin:

    def define_context(self, context):
        return super().define_context(context)


class Application(AbstractContainer):

    def __init__(self, modules: Iterable[AbstractModule]):
        super().__init__()
        self._modules = modules 
        self._context = self._build_context(modules)
    
    def _build_context(self, modules: Iterable[AbstractModule]) -> AbstractContext:
        context = Context(Container({
            'application': Parameter(self),
        }))

        for module in modules:
            context = module.define_context(context)

        return context
    
    def has(self, name, context = None):
        return self._context.has(name, context)
    
    def get(self, name, context = None):
        return self._context.get(name, context)
    
    def resources(self, context = None):
        return super().resources(context)
    
    def extends(self, modules: Iterable[AbstractModule]):
        return Application([
            *self._modules,
            *modules
        ])

