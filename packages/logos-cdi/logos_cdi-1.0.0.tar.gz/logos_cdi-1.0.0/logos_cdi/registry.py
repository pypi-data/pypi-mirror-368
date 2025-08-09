from typing import Optional, Type
from logos_cdi.abstract import AbstractRegistry
from threading import Lock


class Registry[T](AbstractRegistry[T]):

    def __init__(self, parent: Optional[AbstractRegistry], type: Optional[Type[T]]):
        super().__init__()
        self._parent = parent
        self._registry = {}
        self._type = type
        self._lock = Lock()
    
    def register(self, name, _):
        if not isinstance(_, self._type):
            raise ValueError(f'instance of {self._type} expected, {type(_)} given')
        with self._lock:
            self._registry[name] = _
        return self

    def all(self):
        all = self._parent.all() if self._parent is not None else {}
        all.update(self._registry)
        return all


