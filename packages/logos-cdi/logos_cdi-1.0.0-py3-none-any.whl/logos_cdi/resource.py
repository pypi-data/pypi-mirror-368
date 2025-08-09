from logos_cdi.abstract import AbstractResource, AbstractContext, AbstractReference, AbstractRegistry, AbstractContainer
from logos_cdi.container import Container
from importlib import import_module
from typing import Any, Union, Mapping, MutableMapping, Optional
from weakref import WeakKeyDictionary
from contextvars import ContextVar, copy_context
from threading import Lock

class Parameter(AbstractResource):
    def __init__(self, value: Any):
        super().__init__()
        self.value = value
        self._cache = ContextVar('_cache', default=None)
        self._lock = Lock()
        self._locks = WeakKeyDictionary()

    def _recursive(self, value: Any, context: AbstractContext):
        if isinstance(value, list):
            return [self._recursive(item, context) for item in value]
        if isinstance(value, dict):
            return {item_key: self._recursive(item_value, context) for item_key, item_value in value.items()}
        if isinstance(value, AbstractReference):
            return value.get(context)
        return value

    def _resolve(self, context, name):
        if self._cache.get() is None:
            self._cache.set(WeakKeyDictionary())

        with self._lock:
            if context not in self._locks:
                self._locks[context] = Lock()
        
        if context in self._cache.get().keys():
            return self._cache.get()[context]

        with self._locks[context]:
            if context in self._cache.get().keys():
                return self._cache.get()[context]

            if isinstance(self.value, dict):
                self._cache.get()[context] = {}
                self._cache.get()[context].update(self._recursive(self.value, context))
            elif isinstance(self.value, list):
                self._cache.get()[context] = []
                self._cache.get()[context].extend(self._recursive(self.value, context))
            else:
                self._cache.get()[context] = self._recursive(self.value, context)

            return self._cache.get()[context]

    def resolve(self, context, name='anonymous'):
        return copy_context().run(self._resolve, context, name)

class Service(AbstractResource):
    def __init__(self, class_path: Union[str, AbstractReference], parameters: Union[Mapping[str, Any], AbstractReference]):
        self.class_path = class_path
        self.parameters = parameters
        self._cache = ContextVar('_cache', default=None)
        self._lock = Lock()
        self._locks = WeakKeyDictionary()

    def _resolve(self, context, name):
        if self._cache.get() is None:
            self._cache.set(WeakKeyDictionary())

        with self._lock:
            if context not in self._locks:
                self._locks[context] = Lock()

        if context in self._cache.get().keys():
            return self._cache.get()[context]

        with self._locks[context]:
            if context in self._cache.get().keys():
                return self._cache.get()[context]

            class_path = self.class_path if isinstance(self.class_path, str) else self.class_path.get(context)
            parameters = Parameter(self.parameters if isinstance(self.parameters, dict) else self.parameters.get(context))
            module_path, class_name = class_path.rsplit('.', 1)
            cls = getattr(import_module(module_path), class_name)
            self._cache.get()[context] = object.__new__(cls)
            self._cache.get()[context].__init__(**parameters.resolve(context, name=name))

            return self._cache.get()[context]

    def resolve(self, context, name='anonymous'):
        return copy_context().run(self._resolve, context, name)

class Singleton(AbstractResource):
    def __init__(self, class_path, parameters):
        super().__init__()
        self._service = Service(
            class_path=class_path,
            parameters=parameters
        )
        self._instances = WeakKeyDictionary()
        self._lock = Lock()
        self._locks = WeakKeyDictionary()

    def resolve(self, context, name='anonymous'):
        with self._lock:
            if context not in self._locks:
                self._locks[context] = Lock()

        with self._locks[context]:
            if context not in self._instances.keys():
                self._instances[context] = self._service.resolve(context, name)

        return self._instances[context]
