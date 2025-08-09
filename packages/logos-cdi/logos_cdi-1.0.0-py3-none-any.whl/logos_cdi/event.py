from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, MutableMapping, Any, Callable
from threading import Lock
from functools import wraps
from logos_cdi.abstract import AbstractContext
from logos_cdi.application import AbstractModule
from logos_cdi.container import Container
from logos_cdi.resource import Singleton, Parameter
from logos_cdi.reference import Parent, Reference, Context


class AbstractEventEmitter(ABC):

    @abstractmethod
    def emit(self, event: str, data: MutableMapping[str, Any]):
        ...

    @abstractmethod
    def on(self, event: str, handler: Callable[[MutableMapping[str, Any]], None]):
        ...

    @abstractmethod
    def once(self, event: str, handler: Callable[[MutableMapping[str, Any]], None]):
        ...


class EventEmitter(AbstractEventEmitter):
    
    def __init__(self, parent: Optional[AbstractEventEmitter], context: AbstractContext):
        super().__init__()
        self._parent = parent
        self._context = context
        self._registry = {}
        self._lock = Lock()
    
    def emit(self, event, data):
        listeners = []
        with self._lock:
            listeners = self._registry.setdefault(event, set())
            data.setdefault('contexts', []).insert(0, self._context)

        for listener in listeners:
            listener(data)
        
        if not data.get('stop_propagation', False) and self._parent:
            self._parent.emit(event, data)

    
    def on(self, event, handler):
        with self._lock:
            self._registry.setdefault(event, set()).add(handler)
    
    def once(self, event, handler):
        @wraps(handler)
        def wrapper(data):
            self._registry.setdefault(event, set()).remove(wrapper)
            return handler(data)
        self.on(event, wrapper)



class Events(AbstractModule):

    def define_context(self, context):
        return context.nested(Container({
            'events.emitter.class': Parameter('logos_cdi.event.EventEmitter'),
            'events.emitter': Singleton(
                class_path=Reference('events.emitter.class'),
                parameters={
                    'parent': Parent('events.emitter'),
                    'context': Context()
                }
            )
        }))
